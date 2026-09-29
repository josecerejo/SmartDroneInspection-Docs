---
title: SmartDroneInspection Capstone Business Flow
document_type: business-flow-reference
purpose: AI-readable WF1-WF4 business-flow companion
updated: 2026-09-28
---

# SmartDroneInspection Capstone Business Flow

> This Markdown file is the searchable business-flow reference. It preserves the WF1-WF4 actors, preconditions, exceptions, decision loops, outputs, and detailed sequence tables.

## Canonical role vocabulary

Admin, Service Manager, Inspector, Maintenance Engineer, and Client are the five current workflow roles. `Inspector Author` and `Inspector Peer Reviewer` describe responsibilities within the Inspector role; they are not additional roles.

## Evidence and platform boundary

Inspection evidence is uploaded through the web or mobile application, stored in MinIO, and optionally analyzed by YOLO. AI output remains a candidate until an Inspector confirms or modifies it. Drone flight control is outside SmartDroneInspection.

---

## Client Organization Onboarding

The first Client representative may self-register a new organization and create the first Client account. The system creates the organization and account in one transaction, activates both immediately, and assigns only the `CLIENT` role in the `CUSTOMER_ORGANIZATION` actor zone. There is no email-verification or administrator-approval gate in v1. The registration response contains the organization and user profile but no access or refresh token; the Client signs in through the normal login flow.

Registration does not allow a user to create or select Admin, Service Manager, Inspector, or Maintenance Engineer roles. Email and organization-code uniqueness, password policy, rate limits, organization isolation, and the `CLIENT_REGISTRATION` audit event are enforced by the backend. Additional accounts remain an Admin-managed operation in the current release.

### Onboarding output

An active customer organization with its first Client account, ready for WF1.

---

## WF1 — Asset Registration and Periodic Inspection Scheduling

**Source owner:** hiếu

Purpose: Quản lý tài sản và tự động tạo yêu cầu kiểm tra định kỳ.

Primary actors: Client, Service Manager, Admin, System.

### Preconditions

Organization và Client đã được kích hoạt.

Admin đã cấu hình asset categories, checklist templates và chu kỳ gợi ý cho từng category.

Client chỉ được quản lý tài sản thuộc organization của mình.

### Main flow

| Step | Role / Lane | Detailed Main Activity | Output |
| --- | --- | --- | --- |
| WF1-01 | Client | Tạo hồ sơ tài sản (khai báo thông tin tài sản, thông số mặc định cho kiểm tra: phạm vi, mức ưu tiên, ràng buộc tiếp cận, liên hệ) và tải lên tài liệu liên quan. | Tài sản chờ duyệt |
| WF1-02 | Service Manager | Duyệt hoặc từ chối hồ sơ tài sản. | Tài sản được kích hoạt hoặc bị từ chối |
| WF1-03 | System | Sinh các đề nghị chu kỳ kiểm tra từ cấu hình của category. | Danh sách đề nghị chu kỳ |
| WF1-04 | Service Manager | Xem xét, điều chỉnh và duyệt các đề nghị chu kỳ. | Đề nghị đã được duyệt |
| WF1-05 | Client | So sánh và chọn một đề nghị chu kỳ. | Lịch kiểm tra định kỳ đang hoạt động |
| WF1-06 | System | Theo dõi lịch và phát yêu cầu kiểm tra định kỳ khi tới hạn (kế thừa thông tin từ Asset và gửi thông báo cho Client). | Yêu cầu kiểm tra định kỳ sẵn sàng cho WF2 |

### Exception cases

Nếu category chưa có chu kỳ gợi ý hoặc checklist template đang hoạt động, không sinh được đề nghị.

Nếu hồ sơ tài sản không ở trạng thái chờ duyệt, không thể duyệt lại.

Nếu tài sản chưa được kích hoạt hoặc đã có lịch đang hoạt động, Client không thể chọn đề nghị.

Nếu cùng một chu kỳ đã phát yêu cầu, hệ thống không phát lại.

### WF1 output

Một yêu cầu kiểm tra định kỳ hợp lệ sẵn sàng đi vào WF2.

## WF2 — Periodic Inspection Request Review, Service Order and Inspector Assignment

**Source owner:** Quốc

Purpose: Tiếp nhận yêu cầu kiểm tra định kỳ tự động, chuyển thành một service order đã được xác nhận và một Inspector assignment đã được chấp nhận.

Primary actors: Client, Service Manager, Inspector, System.

### Preconditions

Asset đang active và thuộc đúng organization của Client.

Lịch kiểm tra định kỳ (PERIODIC schedule) đang hoạt động và tới hạn chu kỳ (từ WF1-06).

(Ghi chú: Trường hợp kiểm tra lại sau bảo trì WF4-19 được thực hiện qua liên kết re-inspection chuyên biệt).

### Main flow

| Step | Role / Lane | Detailed Main Activity | Output |
| --- | --- | --- | --- |
| WF2-01 | System | Khởi tạo yêu cầu kiểm tra định kỳ (PERIODIC) khi tới hạn với thông tin kế thừa từ hồ sơ tài sản (phạm vi, mức ưu tiên, ràng buộc tiếp cận, thông tin liên hệ, tài liệu); tính toán thời hạn mong muốn (preferred deadline) từ chu kỳ; đồng thời gửi thông báo tạo yêu cầu kiểm tra định kỳ tới Client kèm thời hạn phản hồi hủy. | Yêu cầu kiểm tra định kỳ & thông báo tới Client |
| WF2-02 | Client / System | Cơ chế xác nhận tự động hoặc hủy yêu cầu: Nếu Client không thao tác gì, hệ thống tự động chấp nhận (auto-accepted) đợt kiểm tra theo lịch khi hết thời hạn phản hồi; nếu Client gửi yêu cầu hủy kèm lý do, hệ thống chuyển trạng thái yêu cầu sang CANCELLED và kết thúc đợt kiểm tra chu kỳ này. | Yêu cầu được tự động chấp nhận hoặc bị hủy (CANCELLED) |
| WF2-03 | Service Manager | Với yêu cầu được chấp nhận, xem xét tính khả thi của phạm vi kiểm tra, checklist áp dụng và năng lực cung cấp dịch vụ. | Quyết định tính khả thi |
| WF2-04 | Service Manager | Lập báo giá theo phiên bản và dự thảo hợp đồng dịch vụ (draft service order) gồm phạm vi đã thống nhất, sản phẩm bàn giao, đơn giá/chi phí ước tính, thời lượng dự kiến và điều khoản thanh toán sau dịch vụ. | Báo giá và dự thảo service order |
| WF2-05 | Client | Xem xét báo giá và dự thảo service order. Phê duyệt hợp đồng và chấp nhận điều khoản thanh toán sau dịch vụ, hoặc yêu cầu điều chỉnh báo giá. | Service order được duyệt hoặc yêu cầu sửa báo giá |
| WF2-06 | Service Manager | Khi service order được duyệt, xác nhận service order và chọn Inspector phù hợp dựa trên năng lực, lịch trống, khối lượng công việc và kiểm tra xung đột lợi ích. | Quyết định phân công Inspector |
| WF2-07 | System | Tạo gói phân công (assignment package) gồm thông tin tài sản, phạm vi đã xác nhận, checklist, thời hạn, hướng dẫn tiếp cận hiện trường và tài liệu hỗ trợ, sau đó gửi thông báo tới Inspector. | Gói phân công được khởi tạo |
| WF2-08 | Inspector | Xem xét gói phân công và chấp nhận hoặc từ chối phân công. Nếu từ chối phải cung cấp lý do. | Phân công được chấp nhận hoặc từ chối |
| WF2-09 | Service Manager | Nếu Inspector từ chối, chọn Inspector đủ điều kiện khác. Nếu Inspector chấp nhận, chuyển trạng thái đợt kiểm tra sang READY_FOR_INSPECTION. | Phân công Inspector được chấp nhận |

### Cancellation flow

Client receives periodic request notification

> ↓

Client sends cancellation request with reason

> ↓

System transitions request to CANCELLED

> ↓

Cycle terminated, schedule awaits next due cycle

### Quotation revision flow

Client requests revision

> ↓

Service Manager creates Quotation v2

> ↓

Client reviews again

> ↓

Approved quotation and service order

### Assignment rejection flow

Inspector rejects assignment

> ↓

Request returns to Service Manager

> ↓

Another qualified Inspector is selected

> ↓

New assignment notification

### Important rules

Client không cần thao tác điền hay bổ sung thông tin yêu cầu kiểm tra tại WF2. Toàn bộ thông số kiểm tra (phạm vi, mức ưu tiên, ràng buộc tiếp cận hiện trường, thông tin liên hệ) đã được thiết lập sẵn từ hồ sơ tài sản (WF1-01) và tự động kế thừa khi hệ thống sinh yêu cầu kiểm tra định kỳ.

Cơ chế tự động chấp nhận và quyền hủy của Client: Khi hệ thống tạo yêu cầu kiểm tra định kỳ, thông báo được gửi ngay cho Client kèm thời hạn phản hồi. Nếu Client không làm gì, hệ thống coi như Client tự động chấp nhận (auto-accepted) và chuyển tiếp quy trình sang Service Manager. Client có thể chủ động gửi yêu cầu hủy (cancellation request) kèm lý do trong thời hạn này để hủy đợt kiểm tra của chu kỳ hiện tại mà không làm ảnh hưởng đến lịch định kỳ dài hạn.

Client chỉ nhận thông báo khi hệ thống tự động khởi tạo yêu cầu kiểm tra định kỳ sắp tới hạn, và chỉ tham gia phê duyệt báo giá/service order (WF2-05) nếu không yêu cầu hủy ở bước WF2-02.

No upfront payment is required.

Before assignment, the Client only needs to approve the service order and post-service payment terms.

An unconfirmed service order cannot proceed to Inspector assignment.

Only an accepted assignment can enter WF3.

### WF2 output

A confirmed service order and accepted Inspector assignment with status READY_FOR_INSPECTION.

## WF3 — Inspection Execution, AI-Assisted Verification and Report Delivery

**Source owner:** Bách

Purpose: Thực hiện inspection, xử lý evidence, xác minh kết quả AI, peer review báo cáo và gửi final report cho khách hàng.

Primary actors: Inspector, Service Manager, Client, System, MinIO, YOLO Service.

### Preconditions

Service order đã được xác nhận trong WF2.

Inspector đã chấp nhận assignment.

Inspection job có trạng thái READY_FOR_INSPECTION.

Inspector có quyền truy cập asset, checklist và assignment package.

| Step | Role / Lane | Detailed Main Activity | Output |
| --- | --- | --- | --- |
| WF3-01 | Inspector | Open the accepted assignment and start a new inspection session. | Active inspection session |
| WF3-02 | System | Change the inspection status from READY_FOR_INSPECTION to IN_PROGRESS and record the session start time and responsible Inspector. | Inspection in progress |
| WF3-03 | Inspector | Conduct the field inspection according to the assigned checklist and confirmed service scope. Manual drone piloting remains outside the platform. | Field inspection results |
| WF3-04 | Inspector | Capture or collect inspection images and transfer them from the drone’s SD card, computer or mobile device to the platform. | Uploaded evidence |
| WF3-05 | System: Upload Service | Accept Web or Mobile uploads through the versioned API; validate file type, size, and content; calculate a server-side checksum; prevent duplicate evidence and retry interrupted uploads without creating duplicate records. | Validated evidence |
| WF3-06 | System: MinIO | Store the evidence and associate it with the inspection, asset, Inspector, capture time, source and available GPS or external mission reference. | Stored inspection evidence |
| WF3-07 | System: YOLO Service | When the configured inference adapter is enabled, analyze eligible images and generate non-official defect candidates containing the predicted label, confidence score, bounding box and model version. AI unavailability does not block evidence access or manual findings. | AI defect candidates or manual fallback |
| WF3-08 | Inspector | Review every AI candidate and select Confirm, Modify or Reject. The Inspector may also manually add a defect missed by the AI model. | Inspector-verified findings |
| WF3-09 | System | Exclude rejected and unverified AI candidates from official defect statistics and report content. | Official verified findings |
| WF3-10 | Inspector | Complete the checklist and add the defect location, severity, technical notes and recommended action for each verified finding. | Completed inspection record |
| WF3-11 | System | Compile a versioned draft report from the checklist, evidence and verified findings. On demand, the Inspector may request an LLM-assisted narrative draft generated from authorized snapshot data; it remains subject to human review and edit via the narrative endpoint. | Versioned draft report |
| WF3-12 | Inspector | Review the draft report, correct its content and submit it for internal peer review. | Report awaiting peer review |
| WF3-13 | Service Manager | Assign another qualified Inspector as the Peer Reviewer. The report author cannot review their own report. | Peer-review assignment |
| WF3-14 | Inspector | Verify that the evidence supports the findings and check defect classification, severity, location, checklist consistency and technical conclusions. The report author cannot review the same report. | Peer-review result |
| WF3-15 | Inspector | Request changes when issues are found, or mark the report as TECHNICALLY_APPROVED when the technical content is acceptable. | Technically approved report |
| WF3-16 | Inspector | If changes are requested, revise the report and resubmit it to the same Peer Reviewer. | Revised report version |
| WF3-17 | Service Manager | Check that the technically approved report is complete and contains all deliverables required by the confirmed service order. | Internally released report |
| WF3-18 | Service Manager | Release the final report to the Client . Internal drafts and peer-review comments remain hidden from the customer. | Final customer report |
| WF3-19 | Client | Review the released report and accept it or request clarification and revision. The Client does not directly edit the technical content. | Accepted report or revision request |
| WF3-20 | System | When the Client accepts the report, record the Client actor; make the version immutable; transition the owning inspection to `COMPLETED`; preserve approval/revision history; and publish one accepted-report handoff. A revision request records its reason and leaves the released version visible to the owning Client organization. | Auditable customer decision and accepted-report event |
| WF3-21 | Billing workflow | Consume the accepted-report handoff and record the inspection billing milestone and invoice/payment status according to the confirmed post-service terms. Invoice persistence belongs to the separately assigned billing work; no online payment gateway is required. | Inspection billing milestone and invoice/payment status |

### Peer-review loop

Inspector submits Draft Report

> ↓

Another Inspector checks technical content

> ↓

Changes required?

- Yes → Inspector creates revised version → Review again

- No → Technically Approved

> ↓

Service Manager releases report

> ↓

Client accepts final report

### Exception cases

A corrupted or unsupported file is rejected and must be uploaded again.

Interrupted uploads are resumed or retried without creating duplicates.

If GPS is unavailable, the evidence remains valid but the missing metadata is recorded.

If YOLO is unavailable, evidence remains stored and can be queued for later inference.

If YOLO detects nothing, the Inspector may still manually add findings.

If report evidence is insufficient, the Peer Reviewer returns the report for correction.

If an accepted report later requires correction, the system creates a new correction version instead of overwriting the accepted version.

### WF3 output

A technically reviewed, customer-released and customer-accepted inspection report.

## WF4 — Maintenance Assessment, Work Execution and Defect Resolution

**Source owner:** Như

Purpose: Chuyển verified defect thành maintenance ticket, đánh giá kỹ thuật, thực hiện sửa chữa và đóng defect hoặc yêu cầu rework/re-inspection.

Primary actors: Client , Service Manager, Maintenance Engineer, System.

### Preconditions

WF3 đã tạo customer-accepted inspection report.

Maintenance ticket phải tham chiếu tới ít nhất một verified defect.

Defect chưa bị đóng hoặc liên kết với một maintenance ticket đang active.

| Step | Role / Lane | Detailed Main Activity | Output |
| --- | --- | --- | --- |
| WF4-01 | Client | Select one or more verified defects from an accepted report and create a maintenance ticket with the required priority, preferred deadline and additional instructions. | Maintenance ticket |
| WF4-02 | System | Link the ticket to the organization, asset, inspection report, verified findings and supporting evidence. | Traceable maintenance ticket |
| WF4-03 | Service Manager | Review the ticket for completeness and determine whether a technical assessment can be performed remotely or requires a site visit. | Assessment plan |
| WF4-04 | Service Manager | Assign a qualified Maintenance Engineer to perform the technical assessment. This is an assessment assignment, not yet an execution assignment. | Assessment assignment |
| WF4-05 | Maintenance Engineer — Assessor | Review the defect evidence and, when necessary, conduct an on-site assessment. | Assessed defect condition |
| WF4-06 | Maintenance Engineer — Assessor | Estimate the required work, materials, labor, expected duration, technical risks, assumptions and estimated cost range. | Technical assessment and estimate |
| WF4-07 | Service Manager | Use the technical assessment and approved pricing rules to prepare a versioned maintenance quotation and draft maintenance order. | Maintenance quotation and draft order |
| WF4-08 | Client | Review the quotation and maintenance order. Approve the scope and post-service payment terms, or request revision. | Approved maintenance order |
| WF4-09 | Service Manager | Confirm the approved maintenance order and assign the same Engineer or another qualified Engineer to perform the work. | Execution assignment |
| WF4-10 | Maintenance Engineer — Executor | Review and accept the execution assignment. If rejected, the Service Manager selects another Engineer. | Accepted execution assignment |
| WF4-11 | Maintenance Engineer — Executor | Perform the maintenance work according to the approved maintenance order and record the work progress. | Maintenance work |
| WF4-12 | Maintenance Engineer — Executor | If additional damage or a significant cost increase is discovered, stop the additional work and submit a change request. | Change request |
| WF4-13 | Service Manager | Prepare a revised maintenance-order version based on the additional technical assessment. | Revised maintenance order |
| WF4-14 | Client | Approve or reject the change request before the Engineer performs the additional work. | Approved or rejected change |
| WF4-15 | Maintenance Engineer — Executor | Complete the approved work and upload before/after evidence, work logs, materials used, actual duration and final cost. | Maintenance completion report |
| WF4-16 | Service Manager | Check that the completion report, evidence and final cost are consistent with the approved maintenance order and approved changes. | Internally verified result |
| WF4-17 | Service Manager | Release the maintenance result to the Client . | Customer-visible maintenance result |
| WF4-18 | Client | Review the result and select Accept Resolution, Request Rework or Request Re-inspection. | Resolution decision |
| WF4-19 | System | If accepted, close the ticket and linked defect. If rework is requested, return the ticket to the execution stage. If re-inspection is requested, create a linked AD_HOC request for WF2. | Closed, rework or re-inspection state |
| WF4-20 | System | Finalize the actual cost, issue the maintenance invoice, record payment status, send notifications and preserve the audit history. | Completed maintenance record |

### Resolution branches

Client reviews maintenance result

> ↓

Accept Resolution

- → Close ticket and defect

- → Issue invoice

Request Rework

- → Return to execution assignment/work

- → Submit new completion evidence

Request Re-inspection

- → Create linked AD_HOC inspection request

- → Enter WF2

### Important rules

The Service Manager does not independently estimate technical work.

A qualified Maintenance Engineer provides the technical estimate.

The estimate is not necessarily the final cost.

No upfront payment is required; the Client approves post-service payment terms in the quotation and service order.

Inspection and maintenance are billed at separate acceptance milestones. The inspection invoice is created after the Client accepts the inspection report. The maintenance invoice is created after the Client accepts the maintenance result. Both use the same invoice status lifecycle; the first release records external or manual payment confirmation and does not integrate an online payment gateway.

A material scope or cost increase requires an approved change-order version.

Before/after evidence is required before the ticket can be closed.

### WF4 output

A closed maintenance ticket and resolved defect, an active rework cycle, or a linked re-inspection request returned to WF2.
