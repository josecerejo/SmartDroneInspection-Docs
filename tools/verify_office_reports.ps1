param(
    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory,
    [switch]$ExportPdf
)

$ErrorActionPreference = 'Stop'
$directory = (Resolve-Path -LiteralPath $OutputDirectory).Path
$manifestPath = Join-Path $directory 'manifest.json'
$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$previewDirectory = Join-Path $directory 'pdf-previews'
if ($ExportPdf) {
    if (Test-Path -LiteralPath $previewDirectory) {
        throw 'Use a fresh preview directory; existing previews will not be overwritten.'
    }
    New-Item -Path $previewDirectory -ItemType Directory | Out-Null
}
$results = @()
$word = $null
$excel = $null

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3
    $word.Options.UpdateLinksAtOpen = $false

    foreach ($artifact in $manifest.artifacts) {
        if ($artifact.status -ne 'generated') { continue }
        $path = (Resolve-Path -LiteralPath $artifact.output).Path
        $pdfPath = Join-Path $previewDirectory ([IO.Path]::GetFileNameWithoutExtension($path) + '.pdf')
        $before = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash
        $document = $null
        $workbook = $null
        try {
            if ([IO.Path]::GetExtension($path) -eq '.docx') {
                # ConfirmConversions=false, ReadOnly=true, AddToRecentFiles=false.
                Write-Output ($artifact.report + ': opening in Word')
                $document = $word.Documents.Open($path, $false, $true, $false)
                Write-Output ($artifact.report + ': updating table of contents')
                for ($tocIndex = 1; $tocIndex -le $document.TablesOfContents.Count; $tocIndex++) {
                    $toc = $document.TablesOfContents.Item($tocIndex)
                    $toc.Update()
                    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($toc)
                }
                Write-Output ($artifact.report + ': reading page count')
                $pages = $document.ComputeStatistics(2)
                if ($ExportPdf) {
                    Write-Output ($artifact.report + ': exporting PDF')
                    $document.ExportAsFixedFormat($pdfPath, 17)
                }
                $results += [pscustomobject]@{
                    report = $artifact.report
                    opened = $true
                    pages = $pages
                    pdf = $(if ($ExportPdf) { $pdfPath } else { $null })
                    tocCount = $document.TablesOfContents.Count
                }
                Write-Output ($artifact.report + ': Word opened; ' + $pages + ' pages; PDF requested=' + [bool]$ExportPdf)
            }
            elseif ([IO.Path]::GetExtension($path) -eq '.xlsx') {
                # Create Excel only when needed; a long Word pass can leave an
                # idle Excel instance busy with activation/background work.
                if (-not $excel) {
                    $excel = New-Object -ComObject Excel.Application
                    $excel.Visible = $false
                    $excel.DisplayAlerts = $false
                    $excel.AskToUpdateLinks = $false
                    $excel.AutomationSecurity = 3
                }
                Write-Output ($artifact.report + ': opening in Excel')
                # UpdateLinks=0, ReadOnly=true. Do not fetch template external links.
                $workbook = $excel.Workbooks.Open($path, 0, $true)
                $excel.CalculateFullRebuild()
                $sheetNames = @()
                foreach ($sheet in $workbook.Worksheets) {
                    $sheetNames += $sheet.Name
                    if ($ExportPdf) {
                        $sheet.PageSetup.PrintArea = $sheet.UsedRange.Address()
                        $sheet.PageSetup.Zoom = $false
                        $sheet.PageSetup.FitToPagesWide = 1
                        $sheet.PageSetup.FitToPagesTall = $false
                    }
                }
                $result = [ordered]@{
                    report = $artifact.report
                    opened = $true
                    sheets = $sheetNames
                    pdf = $(if ($ExportPdf) { $pdfPath } else { $null })
                }
                if ($artifact.report -eq 'report5') {
                    $featureSheets = @($sheetNames | Where-Object { $_ -match '^Feature [1-8]$' })
                    if ($featureSheets.Count -ne 8) {
                        throw ('Expected eight Report 5 feature sheets; found ' + $featureSheets.Count)
                    }
                    $statistics = $workbook.Worksheets.Item('Test Statistics')
                    $feature = $workbook.Worksheets.Item('Feature 3')
                    $result['totalCases'] = $statistics.Range('H19').Value2
                    $result['passed'] = $statistics.Range('D19').Value2
                    $result['coverage'] = $statistics.Range('E21').Value2
                    $result['successfulCoverage'] = $statistics.Range('E22').Value2
                    $result['round1Passed'] = $statistics.Range('D19').Value2
                    $result['round2Pending'] = 0
                    $result['round3Pending'] = 0
                    foreach ($sheetName in @('Feature 1', 'Feature 2', 'Feature 3', 'Feature 4', 'Feature 5', 'Feature 6', 'Feature 7', 'Feature 8')) {
                        $featureRound = $workbook.Worksheets.Item($sheetName)
                        $result['round2Pending'] += $featureRound.Range('D7').Value2
                        $result['round3Pending'] += $featureRound.Range('D8').Value2
                    }
                    $result['date'] = $feature.Range('G12').Text
                    $result['tester'] = $feature.Range('H12').Text
                    if ($result.totalCases -ne 65 -or $result.passed -ne 60 -or
                        $result.round3Pending -ne 65) {
                        throw 'Report 5 calculated values do not match its source evidence.'
                    }
                }
                if ($ExportPdf) { $workbook.ExportAsFixedFormat(0, $pdfPath) }
                $results += [pscustomobject]$result
                Write-Output ($artifact.report + ': Excel opened/recalculated; PDF requested=' + [bool]$ExportPdf)
            }
        }
        finally {
            if ($document) {
                $document.Close(0)
                [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($document)
            }
            if ($workbook) {
                $workbook.Close($false)
                [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($workbook)
            }
            if ($excel) {
                try { $excel.Quit() } catch { Write-Warning ('Excel cleanup: ' + $_.Exception.Message) }
                [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($excel)
                $excel = $null
            }
        }
        $after = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash
        if ($before -ne $after) { throw ('Office modified the generated package: ' + $path) }
    }
}
finally {
    if ($word) {
        try { $word.Quit() } catch { Write-Warning ('Word cleanup: ' + $_.Exception.Message) }
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)
    }
    if ($excel) {
        try { $excel.Quit() } catch { Write-Warning ('Excel cleanup: ' + $_.Exception.Message) }
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($excel)
    }
}

$results | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $directory 'office-verification.json') -Encoding UTF8
Write-Output ('Verified artifacts: ' + $results.Count)
