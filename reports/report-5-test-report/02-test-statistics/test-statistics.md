# Test Statistics sheet source

This table mirrors the `Test Statistics` sheet. Keep the workbook's summary
formulas and labels; update the values from the feature files after each test
round.

## Project metadata

| Field | Value |
| --- | --- |
| Project Name | SmartDroneInspection |
| Project Code | SEP490 — *confirm with project owner* |
| Test round | Week 3 verification: Round 1 baseline, Round 2 WF3-002 CI recheck, and Round 2 WF3-004 narrative config/provenance recheck |
| Last updated | 2026-09-28 |

## Module summary

| No | Module code | Passed | Failed | Pending | N/A | Number of test cases |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | Feature 1 sheet (FE-02/WF1 + FE-03/WF2; FE-01 gate separate) | 0 | 0 | 8 | 0 | 8 |
| 2 | Feature 2 sheet (FE-04–FE-07; WF3 + WF4) | 4 | 0 | 3 | 0 | 7 |
| **Subtotal** |  | **4** | **0** | **11** | **0** | **15** |

## Supporting FE-01 verification (not workbook cases)

Supporting gates are excluded from the functional workbook totals. On
2026-09-24, 19 role-to-screen policy tests and 26 browser-auth frontend tests
passed; the full frontend suite passed 52/52, including three shared API
envelope checks and the WF3 inspection/report page tests. Backend API-envelope
and Problem Details checks passed as part of `mvnw verify`; mobile envelope
checks passed as part of `flutter test`, and `flutter analyze` reported no
issues. Browser-auth checks use a mocked HTTP transport; this delivery did not
execute a live browser-to-auth-API end-to-end test. On 2026-09-28, the backend
client self-registration persistence gate passed: `POST /api/v1/auth/register`
returns 201 and persists organization, user, `CLIENT` role, and the
`CLIENT_REGISTRATION` audit row in one transaction
(`ClientRegistrationApiIntegrationTest`, part of the 165/165 `mvnw verify`
run). On 2026-09-28, the backend admin user creation persistence gate passed:
`POST /api/v1/platform/users` returns 201 and persists the user, role
assignment, and the `USER_CREATED` audit row in one transaction
(`AdminUserApiIntegrationTest`, part of the 167/167 `mvnw verify` run).
See `03-features/fe-01-identity-access-governance.md` for the detailed
procedure and scope.

These are workbook-sheet totals, not FE totals. The eight detailed sources are
organized by FE; FE-08 has no assigned functional case in this baseline and is
not included in the 15-case denominator.

## Coverage summary

The summary counts each unique workbook case once using its latest completed
result across recorded rounds. The WF3-002 Round 2 recheck and the WF3-004
Round 2 narrative config/provenance recheck are not additional cases, so the
total remains 15. Both WF3-004 rounds completed as `Passed`, so the Feature 2
`Passed` count is unchanged at 4.

Use the same definitions as the workbook:

- **Test coverage** = cases with a recorded status (`Passed`, `Failed`, or
  `N/A`) ÷ total cases.
- **Successful coverage** = `Passed` cases ÷ total cases.

| Measure | Value at baseline | Formula/source |
| --- | ---: | --- |
| Test coverage | 4 / 15 = 26.7% | Count non-`Pending` statuses in Feature 1 and Feature 2. |
| Successful coverage | 4 / 15 = 26.7% | Count `Passed` statuses in Feature 1 and Feature 2. |

The two module rows are workbook-sheet totals, not SRS feature totals. This is
why the Feature 2 sheet legitimately contains `WF4-001`–`WF4-003`: those cases
map to FE-07 and WF4, even though they share the fixed Feature 2 sheet with
the WF3/FE-04–FE-06 cases.

## Update rules

1. Update the Round 1/2/3 status in the feature source first.
2. Recount `Passed`, `Failed`, `Pending`, and `N/A` per feature.
3. Update the two module rows and subtotal row above.
4. Recalculate coverage; never mark a pending case as passed just to improve
   the percentage.
