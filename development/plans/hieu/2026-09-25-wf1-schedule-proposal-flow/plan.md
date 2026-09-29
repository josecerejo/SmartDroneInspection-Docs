# WF1 Schedule Proposal Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the revised WF1 flow — Client asset → Manager review → system-generated schedule proposals → Client selects one → active schedule with idempotent due-cycle events — plus catalog/document APIs and the matching web screens, tests, and documentation updates.

**Architecture:** Backend feature module `assets` gains `api/`, `service/`, `events/` layers following the existing `inspections` module pattern (thin controllers, `ApiResponse` envelope, `BusinessException` → RFC 7807, `@PreAuthorize` role checks, organization scope via `UserAccess.ActiveUser`). A new forward migration `V11` adds `category_frequency_suggestions` (Admin policy) and `schedule_proposals` (Manager-reviewed, Client-selected); `inspection_schedules` rows are only created from a `CLIENT_SELECTED` proposal, so the T009/T010 schedule lifecycle is untouched by the proposal state machine. Due-cycle events reuse the Modulith publication registry with unique `(assetId, scheduleId, dueCycle)` identity.

**Tech Stack:** Java 21, Spring Boot 4.1, Spring Modulith, Spring Security (JWT), Spring Data JPA, Flyway, PostgreSQL (Testcontainers), MinIO; React 19 + strict TypeScript + Vite + Material UI + TanStack Query + Vitest.

**Spec:** `development/plans/hieu/2026-09-25-wf1-schedule-proposal-flow/spec.md` (same directory as this plan; the executor reads both).

## Global Constraints

- Backend verification: `.\mvnw.cmd spotless:apply` then `.\mvnw.cmd verify` must pass (formatting, tests, JaCoCo gate, Modulith boundary test).
- Frontend verification: `npm run lint` and `npm run build` (and `npm run test`) must pass.
- Docs verification: `git diff --check` must pass in the docs repository.
- API envelope: every successful JSON response is `ApiResponse.success(...)` → `{"success":true,"message":...,"data":...}`; errors are RFC 7807 ProblemDetail via `GlobalExceptionHandler`.
- Authorization: `@PreAuthorize` role checks on controllers; organization scope resolved from the authenticated principal's user id via `UserAccess.findActiveUser(userId)` — never from an `organizationId` request field.
- Roles are exactly: `ADMIN`, `CLIENT`, `SERVICE_MANAGER`, `INSPECTOR`, `MAINTENANCE_ENGINEER` (JWT authority `ROLE_<name>`).
- Migrations: new forward file only (`V11__...sql`); never edit `V1`–`V10`.
- Generated files (`*.g.dart`, `*.freezed.dart`): never edit manually.
- No new dependencies without a concrete current use case; keep code inside module `assets` / feature `features/assets`.
- Git: one focused commit per task, Conventional Commits, stage explicit files; never push.
- Report 3, `business-flows.md`, `database-design.md`, plan docs, and Report 5 are updated in the final task, in the same change set as the code they describe.

## Review Focus

Inputs and failure modes the spec implies that are most likely to bite a user; each is pinned to a task below.

1. **Cross-organization access on every new endpoint** (Client A reads/manages assets, documents, or proposals of org B by guessing an id) — expected: 404/403, never data. Pinned to Task 3 (assets), Task 4 (proposals), Task 6 (documents), Task 10 (full sweep).
2. **Due-cycle replay** (the due event fires twice for the same schedule/cycle after a retry or registry replay) — expected: exactly one `InspectionScheduleDue` per `(assetId, scheduleId, dueCycle)`. Pinned to Task 8.
3. **Proposal race / double selection** (two Clients select different proposals of the same asset concurrently, or the same proposal twice) — expected: exactly one `inspection_schedules` row; the second select fails with 409. Pinned to Task 4.
4. **Asset state machine bypass** (documents uploaded, or proposals generated, while asset is `PENDING_REVIEW`/`REJECTED`; re-approving duplicates proposals) — expected: rejected by status guard; approval is idempotent. Pinned to Task 5 (review) and Task 6 (documents).
5. **Authority widening via portal sections** (an INSPECTOR or MAINTENANCE_ENGINEER opens the Manager review queue because the operations portal lists it) — expected: route guard denies and the backend still denies independently. Pinned to Task 9 (frontend) and Task 10 (backend negative test).

---

## File Structure

```text
backend/
  src/main/resources/db/migration/V11__schedule_proposals_and_category_policy.sql
  src/main/java/com/smartdroneinspection/assets/
    domain/enums/AssetStatus.java                    (modify: +PENDING_REVIEW, +REJECTED)
    domain/Asset.java                                (modify: clientCreate/review methods)
    domain/CategoryFrequencySuggestion.java          (new)
    domain/ScheduleProposal.java                     (new)
    domain/enums/ScheduleProposalStatus.java         (new)
    repository/CategoryFrequencySuggestionRepository.java (new)
    repository/ScheduleProposalRepository.java       (new)
    api/AssetCatalogController.java                  (new)
    api/AssetController.java                         (new)
    api/AssetDocumentController.java                 (new)
    api/ScheduleProposalController.java              (new)
    api/InspectionScheduleController.java            (new)
    api/dto/request/*.java, api/dto/response/*.java  (new records)
    service/AssetCatalogService.java                 (new)
    service/AssetService.java                        (new)
    service/AssetReviewService.java                  (new)
    service/ScheduleProposalService.java             (new)
    service/AssetDocumentService.java                (new)
    service/InspectionScheduleService.java           (new)
    service/InspectionScheduleDuePublisher.java      (new)
    events/InspectionScheduleDue.java                (new)
  src/test/java/com/smartdroneinspection/assets/
    AssetTestFixture.java                            (new)
    ScheduleProposalModelTest.java                   (new)
    AssetCatalogApiIntegrationTest.java              (new)
    AssetApiIntegrationTest.java                     (new)
    AssetReviewApiIntegrationTest.java               (new)
    ScheduleProposalApiIntegrationTest.java          (new)
    AssetDocumentApiIntegrationTest.java             (new)
    InspectionScheduleServiceTest.java               (new)
    PeriodicRequestHandoffTest.java                  (new)
    AssetWorkflowIntegrationTest.java                (new)
frontend/
  src/features/assets/api/{catalogApi,proposalApi,documentApi}.ts (new)
  src/features/assets/api/assetApi.ts                (modify)
  src/features/assets/hooks/{useCatalog,useProposals,useAssetDocuments}.ts (new)
  src/features/assets/pages/{ScheduleProposalsPage,InspectionSchedulesPage,AssetReviewPage,AssetCatalogPage}.tsx (new)
  src/features/assets/pages/AssetsPage.tsx           (modify)
  src/app/permissions/accessPolicy.ts                (modify)
  src/app/router/router.tsx                          (modify)
docs/
  reports/report-3-software-requirement-specification/03-functional-requirements.md (modify)
  reports/report-3-software-requirement-specification/00-record-of-changes.md (modify)
  project-reference/business-flows.md                (modify)
  project-reference/database-design.md               (modify)
  development/plans/bach/2026-09-22-four-week-mainflow-delivery/{tasks,spec,flow-handoffs}.md (modify)
  development/plans/hieu/plan.md                     (modify)
  reports/report-5-test-report/{01-test-cases,03-features,02-test-statistics,00-cover}/* (modify)
```

---

### Task 1: Migration V11 and domain model

**Files:**
- Create: `backend/src/main/resources/db/migration/V11__schedule_proposals_and_category_policy.sql`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/domain/CategoryFrequencySuggestion.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/domain/ScheduleProposal.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/domain/enums/ScheduleProposalStatus.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/repository/CategoryFrequencySuggestionRepository.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/repository/ScheduleProposalRepository.java`
- Modify: `backend/src/main/java/com/smartdroneinspection/assets/domain/enums/AssetStatus.java`
- Modify: `backend/src/main/java/com/smartdroneinspection/assets/domain/Asset.java`
- Test: `backend/src/test/java/com/smartdroneinspection/assets/ScheduleProposalModelTest.java` (new)

**Interfaces:**
- Consumes: existing tables `asset_categories`, `checklist_templates`, `assets`, `inspection_schedules` (migration `V5`); `AssetStatus` enum; `Asset` constructor.
- Produces (later tasks rely on these exact names):
  - `AssetStatus.PENDING_REVIEW`, `AssetStatus.REJECTED`
  - `ScheduleProposalStatus` values `GENERATED, MANAGER_APPROVED, MANAGER_REJECTED, CLIENT_SELECTED, SUPERSEDED`
  - `ScheduleProposal.generate(UUID assetId, UUID checklistTemplateId, String frequencyUnit, int frequencyInterval)`; lifecycle methods `managerAdjust(String, int)`, `managerApprove(String, UUID)`, `managerReject(String, UUID)`, `clientSelect(UUID)`, `supersede()`; getters `getId/getAssetId/getChecklistTemplateId/getFrequencyUnit/getFrequencyInterval/getStatus/getManagerNote/getReviewedByUserId/getSelectedByUserId`
  - `Asset.clientCreate(...)` (same params as the existing constructor) → asset with `PENDING_REVIEW`; `Asset.approveReview()`; `Asset.rejectReview()`
  - `ScheduleProposalRepository` with `findByAssetIdOrderByCreatedAtAsc(UUID)`, `findByAssetIdAndStatus(UUID, ScheduleProposalStatus)`
  - `CategoryFrequencySuggestionRepository` with `findByAssetCategoryIdOrderBySortOrderAsc(UUID)`

- [ ] **Step 1: Write the failing entity test**

Create `backend/src/test/java/com/smartdroneinspection/assets/ScheduleProposalModelTest.java`:

```java
package com.smartdroneinspection.assets;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.smartdroneinspection.assets.domain.ScheduleProposal;
import com.smartdroneinspection.assets.domain.enums.ScheduleProposalStatus;
import java.util.UUID;
import org.junit.jupiter.api.Test;

class ScheduleProposalModelTest {

  private ScheduleProposal proposal() {
    return ScheduleProposal.generate(
        UUID.randomUUID(), UUID.randomUUID(), "MONTH", 3);
  }

  @Test
  void generatedProposalMustBeManagedBeforeClientSelection() {
    ScheduleProposal p = proposal();
    assertThat(p.getStatus()).isEqualTo(ScheduleProposalStatus.GENERATED);

    assertThatThrownBy(() -> p.clientSelect(UUID.randomUUID()))
        .isInstanceOf(IllegalStateException.class);
  }

  @Test
  void managerApprovalAllowsExactlyOneClientSelection() {
    ScheduleProposal p = proposal();
    UUID client = UUID.randomUUID();
    p.managerApprove("Quarterly fits this asset", UUID.randomUUID());

    p.clientSelect(client);
    assertThat(p.getStatus()).isEqualTo(ScheduleProposalStatus.CLIENT_SELECTED);
    assertThat(p.getSelectedByUserId()).isEqualTo(client);

    assertThatThrownBy(() -> p.clientSelect(UUID.randomUUID()))
        .isInstanceOf(IllegalStateException.class);
  }

  @Test
  void adjustAndRejectAreOnlyValidBeforeClientSelection() {
    ScheduleProposal p = proposal();
    p.managerApprove(null, UUID.randomUUID());
    p.clientSelect(UUID.randomUUID());

    assertThatThrownBy(() -> p.managerAdjust("WEEK", 1))
        .isInstanceOf(IllegalStateException.class);
    assertThatThrownBy(() -> p.managerReject("changed my mind", UUID.randomUUID()))
        .isInstanceOf(IllegalStateException.class);
  }

  @Test
  void supersedeOnlyAppliesToManagerApprovedProposals() {
    ScheduleProposal p = proposal();
    p.managerApprove(null, UUID.randomUUID());
    p.supersede();
    assertThat(p.getStatus()).isEqualTo(ScheduleProposalStatus.SUPERSEDED);

    assertThatThrownBy(() -> p.clientSelect(UUID.randomUUID()))
        .isInstanceOf(IllegalStateException.class);
  }
}
```

- [ ] **Step 2: Run the test to verify it fails**

Run (in `backend/`): `.\mvnw.cmd test -Dtest=ScheduleProposalModelTest`
Expected: COMPILATION ERROR — `ScheduleProposal` and `ScheduleProposalStatus` do not exist.

- [ ] **Step 3: Implement enum, entities, repositories, Asset changes**

`assets/domain/enums/ScheduleProposalStatus.java`:

```java
package com.smartdroneinspection.assets.domain.enums;

public enum ScheduleProposalStatus {
  GENERATED,
  MANAGER_APPROVED,
  MANAGER_REJECTED,
  CLIENT_SELECTED,
  SUPERSEDED
}
```

`assets/domain/enums/AssetStatus.java` — full file:

```java
package com.smartdroneinspection.assets.domain.enums;

public enum AssetStatus {
  PENDING_REVIEW,
  ACTIVE,
  INACTIVE,
  REJECTED,
  RETIRED
}
```

`assets/domain/CategoryFrequencySuggestion.java` (explicit getters, matching `AssetCategory` style — the module does not use Lombok):

```java
package com.smartdroneinspection.assets.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import jakarta.persistence.Version;
import java.util.UUID;

@Entity
@Table(
    name = "category_frequency_suggestions",
    uniqueConstraints =
        @UniqueConstraint(
            name = "uq_category_frequency",
            columnNames = {"asset_category_id", "frequency_unit", "frequency_interval"}))
public class CategoryFrequencySuggestion {

  @Id @GeneratedValue private UUID id;

  @Column(name = "asset_category_id", nullable = false)
  private UUID assetCategoryId;

  @Column(name = "frequency_unit", nullable = false, length = 16)
  private String frequencyUnit;

  @Column(name = "frequency_interval", nullable = false)
  private int frequencyInterval;

  @Column(name = "sort_order", nullable = false)
  private int sortOrder;

  @Version @Column(name = "row_version", nullable = false) private long rowVersion;

  protected CategoryFrequencySuggestion() {}

  public CategoryFrequencySuggestion(
      UUID assetCategoryId, String frequencyUnit, int frequencyInterval, int sortOrder) {
    if (frequencyInterval <= 0) {
      throw new IllegalArgumentException("frequencyInterval must be positive");
    }
    this.assetCategoryId = assetCategoryId;
    this.frequencyUnit = frequencyUnit;
    this.frequencyInterval = frequencyInterval;
    this.sortOrder = sortOrder;
  }

  public UUID getId() { return id; }
  public UUID getAssetCategoryId() { return assetCategoryId; }
  public String getFrequencyUnit() { return frequencyUnit; }
  public int getFrequencyInterval() { return frequencyInterval; }
  public int getSortOrder() { return sortOrder; }
}
```

`assets/domain/ScheduleProposal.java`:

```java
package com.smartdroneinspection.assets.domain;

import com.smartdroneinspection.assets.domain.enums.ScheduleProposalStatus;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import jakarta.persistence.Version;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(
    name = "schedule_proposals",
    uniqueConstraints =
        @UniqueConstraint(
            name = "uq_schedule_proposal_active",
            columnNames = {"asset_id", "frequency_unit", "frequency_interval"}))
public class ScheduleProposal {

  @Id @GeneratedValue private UUID id;

  @Column(name = "asset_id", nullable = false)
  private UUID assetId;

  @Column(name = "checklist_template_id", nullable = false)
  private UUID checklistTemplateId;

  @Column(name = "frequency_unit", nullable = false, length = 16)
  private String frequencyUnit;

  @Column(name = "frequency_interval", nullable = false)
  private int frequencyInterval;

  @Enumerated(EnumType.STRING)
  @Column(nullable = false, length = 24)
  private ScheduleProposalStatus status;

  @Column(name = "manager_note", length = 500)
  private String managerNote;

  @Column(name = "reviewed_by_user_id")
  private UUID reviewedByUserId;

  @Column(name = "selected_by_user_id")
  private UUID selectedByUserId;

  @Column(name = "created_at", nullable = false, updatable = false)
  private Instant createdAt;

  @Column(name = "updated_at", nullable = false)
  private Instant updatedAt;

  @Version @Column(name = "row_version", nullable = false) private long rowVersion;

  protected ScheduleProposal() {}

  private ScheduleProposal(
      UUID assetId, UUID checklistTemplateId, String frequencyUnit, int frequencyInterval) {
    if (frequencyInterval <= 0) {
      throw new IllegalArgumentException("frequencyInterval must be positive");
    }
    this.assetId = assetId;
    this.checklistTemplateId = checklistTemplateId;
    this.frequencyUnit = frequencyUnit;
    this.frequencyInterval = frequencyInterval;
    this.status = ScheduleProposalStatus.GENERATED;
    this.createdAt = Instant.now();
    this.updatedAt = createdAt;
  }

  public static ScheduleProposal generate(
      UUID assetId, UUID checklistTemplateId, String frequencyUnit, int frequencyInterval) {
    return new ScheduleProposal(assetId, checklistTemplateId, frequencyUnit, frequencyInterval);
  }

  public void managerAdjust(String newUnit, int newInterval) {
    requireNotClientSelected();
    if (newInterval <= 0) {
      throw new IllegalArgumentException("frequencyInterval must be positive");
    }
    this.frequencyUnit = newUnit;
    this.frequencyInterval = newInterval;
    touch();
  }

  public void managerApprove(String note, UUID reviewerId) {
    if (status != ScheduleProposalStatus.GENERATED
        && status != ScheduleProposalStatus.MANAGER_REJECTED) {
      throw new IllegalStateException("Only generated proposals can be approved");
    }
    this.managerNote = note;
    this.reviewedByUserId = reviewerId;
    this.status = ScheduleProposalStatus.MANAGER_APPROVED;
    touch();
  }

  public void managerReject(String note, UUID reviewerId) {
    requireNotClientSelected();
    this.managerNote = note;
    this.reviewedByUserId = reviewerId;
    this.status = ScheduleProposalStatus.MANAGER_REJECTED;
    touch();
  }

  public void clientSelect(UUID selectorId) {
    if (status != ScheduleProposalStatus.MANAGER_APPROVED) {
      throw new IllegalStateException("Only manager-approved proposals can be selected");
    }
    this.selectedByUserId = selectorId;
    this.status = ScheduleProposalStatus.CLIENT_SELECTED;
    touch();
  }

  public void supersede() {
    if (status == ScheduleProposalStatus.MANAGER_APPROVED) {
      this.status = ScheduleProposalStatus.SUPERSEDED;
      touch();
    }
  }

  private void requireNotClientSelected() {
    if (status == ScheduleProposalStatus.CLIENT_SELECTED) {
      throw new IllegalStateException("A client-selected proposal cannot be changed");
    }
  }

  private void touch() {
    updatedAt = Instant.now();
  }

  public UUID getId() { return id; }
  public UUID getAssetId() { return assetId; }
  public UUID getChecklistTemplateId() { return checklistTemplateId; }
  public String getFrequencyUnit() { return frequencyUnit; }
  public int getFrequencyInterval() { return frequencyInterval; }
  public ScheduleProposalStatus getStatus() { return status; }
  public String getManagerNote() { return managerNote; }
  public UUID getReviewedByUserId() { return reviewedByUserId; }
  public UUID getSelectedByUserId() { return selectedByUserId; }
  public Instant getCreatedAt() { return createdAt; }
  public Instant getUpdatedAt() { return updatedAt; }
}
```

`assets/repository/CategoryFrequencySuggestionRepository.java`:

```java
package com.smartdroneinspection.assets.repository;

import com.smartdroneinspection.assets.domain.CategoryFrequencySuggestion;
import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CategoryFrequencySuggestionRepository
    extends JpaRepository<CategoryFrequencySuggestion, UUID> {
  List<CategoryFrequencySuggestion> findByAssetCategoryIdOrderBySortOrderAsc(UUID assetCategoryId);
}
```

`assets/repository/ScheduleProposalRepository.java`:

```java
package com.smartdroneinspection.assets.repository;

import com.smartdroneinspection.assets.domain.ScheduleProposal;
import com.smartdroneinspection.assets.domain.enums.ScheduleProposalStatus;
import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ScheduleProposalRepository extends JpaRepository<ScheduleProposal, UUID> {
  List<ScheduleProposal> findByAssetIdOrderByCreatedAtAsc(UUID assetId);

  List<ScheduleProposal> findByAssetIdAndStatus(UUID assetId, ScheduleProposalStatus status);
}
```

`assets/domain/Asset.java` — add these methods after the existing `retire()` (keep the existing constructor unchanged so fixtures still build `ACTIVE` assets):

```java
  public static Asset clientCreate(
      UUID organizationId,
      UUID categoryId,
      String code,
      String name,
      String description,
      String locationText,
      BigDecimal latitude,
      BigDecimal longitude,
      String ownershipInformation,
      UUID createdByUserId) {
    Asset asset =
        new Asset(
            organizationId, categoryId, code, name, description, locationText,
            latitude, longitude, ownershipInformation, createdByUserId);
    asset.status = AssetStatus.PENDING_REVIEW;
    return asset;
  }

  public void approveReview() {
    if (status != AssetStatus.PENDING_REVIEW) {
      throw new IllegalStateException("Only pending assets can be approved");
    }
    status = AssetStatus.ACTIVE;
    updatedAt = Instant.now();
  }

  public void rejectReview() {
    if (status != AssetStatus.PENDING_REVIEW) {
      throw new IllegalStateException("Only pending assets can be rejected");
    }
    status = AssetStatus.REJECTED;
    updatedAt = Instant.now();
  }
```

- [ ] **Step 4: Write the migration**

`backend/src/main/resources/db/migration/V11__schedule_proposals_and_category_policy.sql`:

```sql
CREATE TABLE category_frequency_suggestions (
    id                  UUID PRIMARY KEY,
    asset_category_id   UUID NOT NULL REFERENCES asset_categories (id),
    frequency_unit      VARCHAR(16) NOT NULL,
    frequency_interval  INTEGER NOT NULL,
    sort_order          INTEGER NOT NULL DEFAULT 0,
    row_version         BIGINT NOT NULL DEFAULT 0,
    CONSTRAINT ck_category_frequency_unit
        CHECK (frequency_unit IN ('DAY', 'WEEK', 'MONTH', 'YEAR')),
    CONSTRAINT ck_category_frequency_interval CHECK (frequency_interval > 0),
    CONSTRAINT uq_category_frequency
        UNIQUE (asset_category_id, frequency_unit, frequency_interval)
);

CREATE INDEX ix_category_frequency_category
    ON category_frequency_suggestions (asset_category_id, sort_order);

CREATE TABLE schedule_proposals (
    id                      UUID PRIMARY KEY,
    asset_id                UUID NOT NULL REFERENCES assets (id),
    checklist_template_id   UUID NOT NULL REFERENCES checklist_templates (id),
    frequency_unit          VARCHAR(16) NOT NULL,
    frequency_interval      INTEGER NOT NULL,
    status                  VARCHAR(24) NOT NULL,
    manager_note            VARCHAR(500),
    reviewed_by_user_id     UUID,
    selected_by_user_id     UUID,
    created_at              TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at              TIMESTAMP WITH TIME ZONE NOT NULL,
    row_version             BIGINT NOT NULL,
    CONSTRAINT ck_schedule_proposal_unit
        CHECK (frequency_unit IN ('DAY', 'WEEK', 'MONTH', 'YEAR')),
    CONSTRAINT ck_schedule_proposal_interval CHECK (frequency_interval > 0),
    CONSTRAINT ck_schedule_proposal_status
        CHECK (status IN ('GENERATED', 'MANAGER_APPROVED', 'MANAGER_REJECTED',
                          'CLIENT_SELECTED', 'SUPERSEDED')),
    CONSTRAINT uq_schedule_proposal_active
        UNIQUE (asset_id, frequency_unit, frequency_interval)
);

CREATE INDEX ix_schedule_proposals_asset_status
    ON schedule_proposals (asset_id, status);
```

Before writing, open `V5__asset_catalog_and_planning.sql` and copy its exact id-generation and timestamp style for `UUID PRIMARY KEY` / `TIMESTAMP WITH TIME ZONE` columns so V11 matches the baseline conventions (if V5 uses `GENERATED ALWAYS AS IDENTITY` sequences or a different id strategy, mirror it).

- [ ] **Step 5: Run model tests and the full backend suite**

Run:
```powershell
.\mvnw.cmd test -Dtest=ScheduleProposalModelTest
.\mvnw.cmd verify
```
Expected: PASS — V11 applies in Testcontainers, existing tests (including `AssetSchemaMigrationTest`, `AssetPersistenceTest`) still green, Modulith boundary test green.

- [ ] **Step 6: Commit**

```powershell
git add src/main/resources/db/migration/V11__schedule_proposals_and_category_policy.sql src/main/java/com/smartdroneinspection/assets src/test/java/com/smartdroneinspection/assets/ScheduleProposalModelTest.java
git commit -m "feat(assets): add schedule proposal domain and category frequency policy"
```

### Task 2: Admin catalog API (T005) + shared test fixture

**Files:**
- Create: `backend/src/test/java/com/smartdroneinspection/assets/AssetTestFixture.java`
- Create: `backend/src/test/java/com/smartdroneinspection/assets/AssetCatalogApiIntegrationTest.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/api/AssetCatalogController.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/service/AssetCatalogService.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/api/dto/request/CreateCategoryRequest.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/api/dto/request/UpdateCategoryRequest.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/api/dto/request/SuggestedFrequencyRequest.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/api/dto/response/CategoryResponse.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/api/dto/response/SuggestedFrequencyResponse.java`

**Interfaces:**
- Consumes: Task 1 (`CategoryFrequencySuggestion`, `CategoryFrequencySuggestionRepository`), existing `AssetCategory`, `AssetCategoryRepository`, `ChecklistTemplate`, `ChecklistTemplateRepository`, `ApiResponse`, `BusinessException`, `UserAccess`.
- Produces:
  - `AssetTestFixture` — constructor `(AssetCategoryRepository, ChecklistTemplateRepository, AssetRepository, UserRepository, JdbcTemplate)`, method `Data create()`; `Data` record: `organizationId, otherOrganizationId, clientId, otherClientId, managerId, adminId, categoryId, checklistTemplateId` (all `UUID`).
  - `AssetCatalogService(UUID adminId)` methods: `List<CategoryResponse> listCategories()`, `CategoryResponse createCategory(CreateCategoryRequest)`, `CategoryResponse updateCategory(UUID, UpdateCategoryRequest)`, `List<SuggestedFrequencyResponse> listFrequencies(UUID categoryId)`, `SuggestedFrequencyResponse addFrequency(UUID categoryId, SuggestedFrequencyRequest)`, `void deleteFrequency(UUID categoryId, UUID frequencyId)`.
  - Routes: `GET/POST /api/v1/asset-categories`, `PUT /api/v1/asset-categories/{id}`, `GET/POST /api/v1/asset-categories/{id}/suggested-frequencies`, `DELETE .../suggested-frequencies/{frequencyId}`.
  - Error codes: `DUPLICATE_CODE` (409), `NOT_FOUND` (404), `VALIDATION_FAILED` (400).

- [ ] **Step 1: Write `AssetTestFixture`**

```java
package com.smartdroneinspection.assets;

import com.smartdroneinspection.assets.domain.AssetCategory;
import com.smartdroneinspection.assets.domain.ChecklistItem;
import com.smartdroneinspection.assets.domain.ChecklistTemplate;
import com.smartdroneinspection.assets.domain.enums.ChecklistResponseType;
import com.smartdroneinspection.assets.repository.AssetCategoryRepository;
import com.smartdroneinspection.assets.repository.AssetRepository;
import com.smartdroneinspection.assets.repository.ChecklistTemplateRepository;
import com.smartdroneinspection.users.domain.User;
import com.smartdroneinspection.users.domain.enums.ActorZone;
import com.smartdroneinspection.users.domain.enums.UserRole;
import com.smartdroneinspection.users.domain.enums.UserStatus;
import com.smartdroneinspection.users.repository.UserRepository;
import java.util.UUID;
import org.springframework.jdbc.core.JdbcTemplate;

/** Users, category, and checklist template shared by the WF1 asset tests. */
public final class AssetTestFixture {

  private final AssetCategoryRepository categories;
  private final ChecklistTemplateRepository templates;
  private final AssetRepository assets;
  private final UserRepository users;
  private final JdbcTemplate jdbcTemplate;

  public AssetTestFixture(
      AssetCategoryRepository categories,
      ChecklistTemplateRepository templates,
      AssetRepository assets,
      UserRepository users,
      JdbcTemplate jdbcTemplate) {
    this.categories = categories;
    this.templates = templates;
    this.assets = assets;
    this.users = users;
    this.jdbcTemplate = jdbcTemplate;
  }

  public Data create() {
    UUID organizationId = createOrganization("Primary");
    UUID otherOrganizationId = createOrganization("Other");

    User client = saveUser("client", UserStatus.ACTIVE, ActorZone.CUSTOMER_ORGANIZATION, organizationId, UserRole.CLIENT);
    User otherClient = saveUser("other-client", UserStatus.ACTIVE, ActorZone.CUSTOMER_ORGANIZATION, otherOrganizationId, UserRole.CLIENT);
    User manager = saveUser("manager", UserStatus.ACTIVE, ActorZone.SERVICE_WORKFORCE, null, UserRole.SERVICE_MANAGER);
    User admin = saveUser("admin", UserStatus.ACTIVE, ActorZone.PLATFORM, null, UserRole.ADMIN);

    AssetCategory category =
        categories.saveAndFlush(
            new AssetCategory("bridge-" + organizationId, "Bridge", "Bridge infrastructure", true));
    ChecklistTemplate template =
        new ChecklistTemplate(
            "bridge-inspection-" + organizationId,
            1,
            category.getId(),
            "Bridge inspection",
            "WF1 fixture checklist",
            manager.getId());
    ChecklistItem item =
        template.addItem(
            "surface-condition", "Surface", "Check the visible surface condition",
            ChecklistResponseType.PASS_FAIL, true, 0, null, null);
    template.publish();
    templates.saveAndFlush(template);

    return new Data(
        organizationId, otherOrganizationId, client.getId(), otherClient.getId(),
        manager.getId(), admin.getId(), category.getId(), template.getId());
  }

  private UUID createOrganization(String label) {
    UUID organizationId = UUID.randomUUID();
    jdbcTemplate.update(
        "INSERT INTO organizations (id, name, code) VALUES (?, ?, ?)",
        organizationId,
        label + " organization " + organizationId,
        "ORG-" + organizationId);
    return organizationId;
  }

  private User saveUser(
      String label, UserStatus status, ActorZone actorZone, UUID organizationId, UserRole role) {
    User user =
        new User(
            label + "-" + UUID.randomUUID() + "@example.test", label, null, status, actorZone,
            organizationId);
    user.addRole(role);
    return users.saveAndFlush(user);
  }

  public record Data(
      UUID organizationId,
      UUID otherOrganizationId,
      UUID clientId,
      UUID otherClientId,
      UUID managerId,
      UUID adminId,
      UUID categoryId,
      UUID checklistTemplateId) {}
}
```

Note: `ChecklistItem item` local variable is unused — drop it if the compiler warns under `-Werror`; otherwise keep `template.addItem(...)` as a statement.

- [ ] **Step 2: Write the failing catalog test**

`AssetCatalogApiIntegrationTest.java` — skeleton with the three acceptance tests:

```java
package com.smartdroneinspection.assets;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.jwt;
import static org.springframework.security.test.web.servlet.setup.SecurityMockMvcConfigurers.springSecurity;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import com.smartdroneinspection.assets.repository.AssetCategoryRepository;
import com.smartdroneinspection.assets.repository.AssetRepository;
import com.smartdroneinspection.assets.repository.ChecklistTemplateRepository;
import com.smartdroneinspection.users.repository.UserRepository;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.annotation.Import(TestcontainersConfiguration.class);
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.context.WebApplicationContext;

@SpringBootTest
@Import(TestcontainersConfiguration.class)
@Transactional
class AssetCatalogApiIntegrationTest {

  @Autowired WebApplicationContext webApplicationContext;
  @Autowired AssetCategoryRepository categories;
  @Autowired ChecklistTemplateRepository templates;
  @Autowired AssetRepository assets;
  @Autowired UserRepository users;
  @Autowired JdbcTemplate jdbcTemplate;

  private AssetTestFixture.Data fixture;
  private MockMvc mockMvc;

  @BeforeEach
  void setUp() {
    mockMvc = MockMvcBuilders.webAppContextSetup(webApplicationContext).apply(springSecurity()).build();
    fixture =
        new AssetTestFixture(categories, templates, assets, users, jdbcTemplate).create();
  }

  @Test
  void adminCreatesCategoryAndClientIsDenied() throws Exception {
    mockMvc
        .perform(
            post("/api/v1/asset-categories")
                .with(admin(fixture.adminId()))
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"code\":\"tower\",\"name\":\"Tower\",\"description\":\"Comms tower\"}"))
        .andExpect(status().isCreated())
        .andExpect(jsonPath("$.success").value(true))
        .andExpect(jsonPath("$.data.code").value("TOWER"));

    mockMvc
        .perform(
            post("/api/v1/asset-categories")
                .with(client(fixture.clientId()))
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"code\":\"denied\",\"name\":\"Denied\"}"))
        .andExpect(status().isForbidden());
  }

  @Test
  void duplicateCategoryCodeConflicts() throws Exception {
    mockMvc
        .perform(
            post("/api/v1/asset-categories")
                .with(admin(fixture.adminId()))
                .contentType(MediaType.APPLICATION_JSON)
                .content(
                    "{\"code\":\""
                        + categories.findById(fixture.categoryId()).orElseThrow().getCode()
                        + "\",\"name\":\"Bridge 2\"}"))
        .andExpect(status().isConflict())
        .andExpect(jsonPath("$.code").value("DUPLICATE_CODE"));
  }

  @Test
  void adminManagesSuggestedFrequencies() throws Exception {
    mockMvc
        .perform(
            post("/api/v1/asset-categories/{id}/suggested-frequencies", fixture.categoryId())
                .with(admin(fixture.adminId()))
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"frequencyUnit\":\"MONTH\",\"frequencyInterval\":3}"))
        .andExpect(status().isCreated())
        .andExpect(jsonPath("$.data.frequencyUnit").value("MONTH"));

    mockMvc
        .perform(
            post("/api/v1/asset-categories/{id}/suggested-frequencies", fixture.categoryId())
                .with(admin(fixture.adminId()))
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"frequencyUnit\":\"MONTH\",\"frequencyInterval\":0}"))
        .andExpect(status().isBadRequest());

    MvcResult list =
        mockMvc
            .perform(
                get("/api/v1/asset-categories/{id}/suggested-frequencies", fixture.categoryId())
                    .with(admin(fixture.adminId())))
            .andExpect(status().isOk())
            .andReturn();
    org.assertj.core.api.Assertions
        .assertThat(list.getResponse().getContentAsString())
        .contains("\"frequencyUnit\":\"MONTH\"");
  }

  private org.springframework.test.web.servlet.request.RequestPostProcessor admin(UUID id) {
    return jwt().jwt(t -> t.subject(id.toString()))
        .authorities(new org.springframework.security.core.authority.SimpleGrantedAuthority("ROLE_ADMIN"));
  }

  private org.springframework.test.web.servlet.request.RequestPostProcessor client(UUID id) {
    return jwt().jwt(t -> t.subject(id.toString()))
        .authorities(new org.springframework.security.core.authority.SimpleGrantedAuthority("ROLE_CLIENT"));
  }
}
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `.\mvnw.cmd test -Dtest=AssetCatalogApiIntegrationTest`
Expected: FAIL — 404 on `/api/v1/asset-categories` (controller does not exist).

- [ ] **Step 4: Implement DTOs, service, controller**

DTO records (in `api/dto/request` / `api/dto/response`; all public records with jakarta validation):

```java
// request/CreateCategoryRequest.java
package com.smartdroneinspection.assets.api.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record CreateCategoryRequest(
    @NotBlank @Size(max = 64) String code,
    @NotBlank @Size(max = 200) String name,
    @Size(max = 2000) String description) {}
```

```java
// request/UpdateCategoryRequest.java — same fields as CreateCategoryRequest (code, name, description)
// request/SuggestedFrequencyRequest.java
package com.smartdroneinspection.assets.api.dto.request;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;

public record SuggestedFrequencyRequest(
    @NotBlank @Pattern(regexp = "DAY|WEEK|MONTH|YEAR") String frequencyUnit,
    @Min(1) int frequencyInterval) {}
```

```java
// response/CategoryResponse.java
package com.smartdroneinspection.assets.api.dto.response;

import java.util.UUID;

public record CategoryResponse(UUID id, String code, String name, String description, boolean active) {}
```

```java
// response/SuggestedFrequencyResponse.java
package com.smartdroneinspection.assets.api.dto.response;

import java.util.UUID;

public record SuggestedFrequencyResponse(
    UUID id, String frequencyUnit, int frequencyInterval, int sortOrder) {}
```

`service/AssetCatalogService.java`:

```java
package com.smartdroneinspection.assets.service;

import com.smartdroneinspection.assets.api.dto.request.CreateCategoryRequest;
import com.smartdroneinspection.assets.api.dto.request.SuggestedFrequencyRequest;
import com.smartdroneinspection.assets.api.dto.request.UpdateCategoryRequest;
import com.smartdroneinspection.assets.api.dto.response.CategoryResponse;
import com.smartdroneinspection.assets.api.dto.response.SuggestedFrequencyResponse;
import com.smartdroneinspection.assets.domain.AssetCategory;
import com.smartdroneinspection.assets.domain.CategoryFrequencySuggestion;
import com.smartdroneinspection.assets.repository.AssetCategoryRepository;
import com.smartdroneinspection.assets.repository.CategoryFrequencySuggestionRepository;
import com.smartdroneinspection.shared.exception.BusinessException;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AssetCatalogService {

  private final AssetCategoryRepository categories;
  private final CategoryFrequencySuggestionRepository frequencies;

  public AssetCatalogService(
      AssetCategoryRepository categories, CategoryFrequencySuggestionRepository frequencies) {
    this.categories = categories;
    this.frequencies = frequencies;
  }

  @Transactional(readOnly = true)
  public List<CategoryResponse> listCategories() {
    return categories.findAll().stream().map(this::toResponse).toList();
  }

  @Transactional
  public CategoryResponse createCategory(CreateCategoryRequest request) {
    if (categories.existsByCode(request.code().trim().toUpperCase(java.util.Locale.ROOT))) {
      throw new BusinessException(HttpStatus.CONFLICT, "DUPLICATE_CODE", "Category code already exists");
    }
    AssetCategory category =
        new AssetCategory(request.code(), request.name(), request.description(), true);
    return toResponse(categories.saveAndFlush(category));
  }

  @Transactional
  public CategoryResponse updateCategory(UUID categoryId, UpdateCategoryRequest request) {
    AssetCategory category =
        categories.findById(categoryId).orElseThrow(() -> notFound(categoryId));
    category.update(request.name(), request.description());
    return toResponse(categories.saveAndFlush(category));
  }

  @Transactional(readOnly = true)
  public List<SuggestedFrequencyResponse> listFrequencies(UUID categoryId) {
    requireCategory(categoryId);
    return frequencies.findByAssetCategoryIdOrderBySortOrderAsc(categoryId).stream()
        .map(
            f ->
                new SuggestedFrequencyResponse(
                    f.getId(), f.getFrequencyUnit(), f.getFrequencyInterval(), f.getSortOrder()))
        .toList();
  }

  @Transactional
  public SuggestedFrequencyResponse addFrequency(UUID categoryId, SuggestedFrequencyRequest request) {
    requireCategory(categoryId);
    CategoryFrequencySuggestion suggestion =
        new CategoryFrequencySuggestion(
            categoryId,
            request.frequencyUnit(),
            request.frequencyInterval(),
            frequencies.findByAssetCategoryIdOrderBySortOrderAsc(categoryId).size());
    try {
      suggestion = frequencies.saveAndFlush(suggestion);
    } catch (org.springframework.dao.DataIntegrityViolationException ex) {
      throw new BusinessException(
          HttpStatus.CONFLICT, "DUPLICATE_FREQUENCY", "Suggested frequency already exists");
    }
    return new SuggestedFrequencyResponse(
        suggestion.getId(),
        suggestion.getFrequencyUnit(),
        suggestion.getFrequencyInterval(),
        suggestion.getSortOrder());
  }

  @Transactional
  public void deleteFrequency(UUID categoryId, UUID frequencyId) {
    requireCategory(categoryId);
    CategoryFrequencySuggestion suggestion =
        frequencies.findById(frequencyId)
            .filter(f -> f.getAssetCategoryId().equals(categoryId))
            .orElseThrow(() -> notFound(frequencyId));
    frequencies.delete(suggestion);
  }

  private void requireCategory(UUID categoryId) {
    categories.findById(categoryId).orElseThrow(() -> notFound(categoryId));
  }

  private BusinessException notFound(UUID id) {
    return new BusinessException(HttpStatus.NOT_FOUND, "NOT_FOUND", "Catalog entry not found: " + id);
  }

  private CategoryResponse toResponse(AssetCategory category) {
    return new CategoryResponse(
        category.getId(),
        category.getCode(),
        category.getName(),
        category.getDescription(),
        category.isActive());
  }
}
```

`AssetCategory` gains the mutator used above — add it in `assets/domain/AssetCategory.java` during this task (code is immutable after creation, so the duplicate-code guard stays meaningful):

```java
// in assets/domain/AssetCategory.java
public void update(String newName, String newDescription) {
  this.name = newName;
  this.description = newDescription;
}
```

`api/AssetCatalogController.java`:

```java
package com.smartdroneinspection.assets.api;

import com.smartdroneinspection.assets.api.dto.request.CreateCategoryRequest;
import com.smartdroneinspection.assets.api.dto.request.SuggestedFrequencyRequest;
import com.smartdroneinspection.assets.api.dto.request.UpdateCategoryRequest;
import com.smartdroneinspection.assets.api.dto.response.CategoryResponse;
import com.smartdroneinspection.assets.api.dto.response.SuggestedFrequencyResponse;
import com.smartdroneinspection.assets.service.AssetCatalogService;
import com.smartdroneinspection.shared.api.ApiResponse;
import jakarta.validation.Valid;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/asset-categories")
public class AssetCatalogController {

  private final AssetCatalogService catalog;

  public AssetCatalogController(AssetCatalogService catalog) {
    this.catalog = catalog;
  }

  @GetMapping
  @PreAuthorize("isAuthenticated()")
  public ApiResponse<List<CategoryResponse>> list() {
    return ApiResponse.success(catalog.listCategories());
  }

  @PostMapping
  @PreAuthorize("hasRole('ADMIN')")
  @ResponseStatus(HttpStatus.CREATED)
  public ApiResponse<CategoryResponse> create(@Valid @RequestBody CreateCategoryRequest request) {
    return ApiResponse.success(catalog.createCategory(request));
  }

  @PutMapping("/{categoryId}")
  @PreAuthorize("hasRole('ADMIN')")
  public ApiResponse<CategoryResponse> update(
      @PathVariable UUID categoryId, @Valid @RequestBody UpdateCategoryRequest request) {
    return ApiResponse.success(catalog.updateCategory(categoryId, request));
  }

  @GetMapping("/{categoryId}/suggested-frequencies")
  @PreAuthorize("isAuthenticated()")
  public ApiResponse<List<SuggestedFrequencyResponse>> listFrequencies(@PathVariable UUID categoryId) {
    return ApiResponse.success(catalog.listFrequencies(categoryId));
  }

  @PostMapping("/{categoryId}/suggested-frequencies")
  @PreAuthorize("hasRole('ADMIN')")
  @ResponseStatus(HttpStatus.CREATED)
  public ApiResponse<SuggestedFrequencyResponse> addFrequency(
      @PathVariable UUID categoryId, @Valid @RequestBody SuggestedFrequencyRequest request) {
    return ApiResponse.success(catalog.addFrequency(categoryId, request));
  }

  @DeleteMapping("/{categoryId}/suggested-frequencies/{frequencyId}")
  @PreAuthorize("hasRole('ADMIN')")
  public ApiResponse<Void> deleteFrequency(
      @PathVariable UUID categoryId, @PathVariable UUID frequencyId) {
    catalog.deleteFrequency(categoryId, frequencyId);
    return ApiResponse.success(null);
  }
}
```

Checklist-template write endpoints are **not** part of this task beyond what exists; T005's acceptance ("only Admin can activate valid catalog versions") is covered by category create/update + frequency management here; template authoring already exists via domain and is exercised by fixtures.

- [ ] **Step 5: Run the test to verify it passes**

Run: `.\mvnw.cmd test -Dtest=AssetCatalogApiIntegrationTest`
Expected: PASS (3 tests).

- [ ] **Step 6: Format, full verify, commit**

```powershell
.\mvnw.cmd spotless:apply
.\mvnw.cmd verify
git add src/main/java/com/smartdroneinspection/assets src/test/java/com/smartdroneinspection/assets src/main/resources/db/migration
git commit -m "feat(assets): add admin catalog api with suggested frequencies"
```

### Task 3: Organization-scoped asset API (T006)

**Files:**
- Create: `backend/src/main/java/com/smartdroneinspection/assets/api/AssetController.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/service/AssetService.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/api/dto/request/CreateAssetRequest.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/api/dto/request/UpdateAssetRequest.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/api/dto/response/AssetResponse.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/api/dto/response/AssetPageResponse.java`
- Test: `backend/src/test/java/com/smartdroneinspection/assets/AssetApiIntegrationTest.java`

**Interfaces:**
- Consumes: Task 1 (`Asset.clientCreate`, `AssetStatus.PENDING_REVIEW`), Task 2 (`AssetTestFixture`), `UserAccess` (`users` module public boundary), `AssetRepository` (`existsByOrganizationIdAndCode`, `findByOrganizationId`, `findByIdAndOrganizationId`).
- Produces:
  - `AssetService` methods: `AssetResponse create(UUID actorId, CreateAssetRequest)`, `AssetPageResponse list(UUID actorId, int page, int pageSize, String search)`, `AssetResponse get(UUID actorId, UUID assetId)`, `AssetResponse update(UUID actorId, UUID assetId, UpdateAssetRequest)`.
  - Routes: `POST/GET /api/v1/assets` (CLIENT only for create; CLIENT+ADMIN for list), `GET/PUT /api/v1/assets/{assetId}`.
  - `AssetResponse(id, code, name, description, locationText, latitude, longitude, status, categoryId, createdAt)`; `AssetPageResponse(items, page, pageSize, totalCount, totalPages)` (matches the frontend `PagedResult<T>` shape).
  - Errors: `DUPLICATE_CODE` (409), `NOT_FOUND` (404), `VALIDATION_FAILED` (400 — e.g. Client without organization, unknown/inactive category).

- [ ] **Step 1: Write the failing test**

`AssetApiIntegrationTest.java` (same `@SpringBootTest/@Import(TestcontainersConfiguration.class)/@Transactional` header and JWT helpers as `AssetCatalogApiIntegrationTest` — `admin()`, `client()` post-processors; add `manager()` with `ROLE_SERVICE_MANAGER`):

```java
  @Test
  void clientCreatesAssetInPendingReviewState() throws Exception {
    mockMvc
        .perform(
            post("/api/v1/assets")
                .with(client(fixture.clientId()))
                .contentType(MediaType.APPLICATION_JSON)
                .content(
                    "{\"code\":\"BR-01\",\"name\":\"North bridge\",\"description\":\"Main span\","
                        + "\"categoryId\":\"" + fixture.categoryId() + "\","
                        + "\"locationText\":\"District 1\"}"))
        .andExpect(status().isCreated())
        .andExpect(jsonPath("$.success").value(true))
        .andExpect(jsonPath("$.data.status").value("PENDING_REVIEW"));
  }

  @Test
  void duplicateCodeInSameOrganizationConflictsAndCrossOrgSeesNothing() throws Exception {
    String body =
        "{\"code\":\"BR-DUP\",\"name\":\"Bridge\",\"categoryId\":\""
            + fixture.categoryId() + "\",\"locationText\":\"District 1\"}";
    mockMvc
        .perform(post("/api/v1/assets").with(client(fixture.clientId()))
            .contentType(MediaType.APPLICATION_JSON).content(body))
        .andExpect(status().isCreated());
    mockMvc
        .perform(post("/api/v1/assets").with(client(fixture.clientId()))
            .contentType(MediaType.APPLICATION_JSON).content(body))
        .andExpect(status().isConflict())
        .andExpect(jsonPath("$.code").value("DUPLICATE_CODE"));

    // other-org client lists only its own assets
    mockMvc
        .perform(get("/api/v1/assets").with(client(fixture.otherClientId())))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.totalCount").value(0));
  }

  @Test
  void crossOrganizationReadAndUpdateAreDenied() throws Exception {
    MvcResult created =
        mockMvc
            .perform(post("/api/v1/assets").with(client(fixture.clientId()))
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"code\":\"BR-X\",\"name\":\"Bridge\",\"categoryId\":\""
                    + fixture.categoryId() + "\",\"locationText\":\"District 1\"}"))
            .andExpect(status().isCreated())
            .andReturn();
    UUID assetId =
        UUID.fromString(
            com.jayway.jsonpath.JsonPath.read(created.getResponse().getContentAsString(), "$.data.id"));

    mockMvc
        .perform(get("/api/v1/assets/{id}", assetId).with(client(fixture.otherClientId())))
        .andExpect(status().isNotFound());

    mockMvc
        .perform(
            put("/api/v1/assets/{id}", assetId).with(client(fixture.otherClientId()))
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"name\":\"Hijacked\",\"locationText\":\"Elsewhere\"}"))
        .andExpect(status().isNotFound());

    mockMvc
        .perform(
            put("/api/v1/assets/{id}", assetId).with(client(fixture.clientId()))
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"name\":\"Renamed\",\"locationText\":\"District 2\"}"))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.data.name").value("Renamed"));
  }

  @Test
  void managerCannotCreateAssetsAndCategoryMustBeActive() throws Exception {
    mockMvc
        .perform(post("/api/v1/assets").with(manager(fixture.managerId()))
            .contentType(MediaType.APPLICATION_JSON)
            .content("{\"code\":\"NO\",\"name\":\"Nope\",\"categoryId\":\""
                + fixture.categoryId() + "\",\"locationText\":\"X\"}"))
        .andExpect(status().isForbidden());
  }
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `.\mvnw.cmd test -Dtest=AssetApiIntegrationTest`
Expected: FAIL — 404 (no controller).

- [ ] **Step 3: Implement DTOs, service, controller**

```java
// request/CreateAssetRequest.java
package com.smartdroneinspection.assets.api.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.math.BigDecimal;
import java.util.UUID;

public record CreateAssetRequest(
    @NotBlank @Size(max = 64) String code,
    @NotBlank @Size(max = 200) String name,
    @Size(max = 2000) String description,
    @NotNull UUID categoryId,
    @NotBlank @Size(max = 500) String locationText,
    BigDecimal latitude,
    BigDecimal longitude,
    @Size(max = 1000) String ownershipInformation) {}
```

```java
// request/UpdateAssetRequest.java — optional fields; null = unchanged
package com.smartdroneinspection.assets.api.dto.request;

import jakarta.validation.constraints.Size;
import java.math.BigDecimal;

public record UpdateAssetRequest(
    @Size(max = 200) String name,
    @Size(max = 2000) String description,
    @Size(max = 500) String locationText,
    BigDecimal latitude,
    BigDecimal longitude,
    @Size(max = 1000) String ownershipInformation) {}
```

```java
// response/AssetResponse.java
package com.smartdroneinspection.assets.api.dto.response;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

public record AssetResponse(
    UUID id,
    String code,
    String name,
    String description,
    String locationText,
    BigDecimal latitude,
    BigDecimal longitude,
    String status,
    UUID categoryId,
    Instant createdAt) {}
```

```java
// response/AssetPageResponse.java
package com.smartdroneinspection.assets.api.dto.response;

import java.util.List;

public record AssetPageResponse(
    List<AssetResponse> items, int page, int pageSize, long totalCount, int totalPages) {}
```

`service/AssetService.java`:

```java
package com.smartdroneinspection.assets.service;

import com.smartdroneinspection.assets.api.dto.request.CreateAssetRequest;
import com.smartdroneinspection.assets.api.dto.request.UpdateAssetRequest;
import com.smartdroneinspection.assets.api.dto.response.AssetPageResponse;
import com.smartdroneinspection.assets.api.dto.response.AssetResponse;
import com.smartdroneinspection.assets.domain.Asset;
import com.smartdroneinspection.assets.domain.AssetCategory;
import com.smartdroneinspection.assets.domain.enums.AssetStatus;
import com.smartdroneinspection.assets.repository.AssetCategoryRepository;
import com.smartdroneinspection.assets.repository.AssetRepository;
import com.smartdroneinspection.shared.exception.BusinessException;
import com.smartdroneinspection.users.UserAccess;
import java.util.Locale;
import java.util.UUID;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AssetService {

  private final AssetRepository assets;
  private final AssetCategoryRepository categories;
  private final UserAccess userAccess;

  public AssetService(
      AssetRepository assets, AssetCategoryRepository categories, UserAccess userAccess) {
    this.assets = assets;
    this.categories = categories;
    this.userAccess = userAccess;
  }

  @Transactional
  public AssetResponse create(UUID actorId, CreateAssetRequest request) {
    UUID organizationId = requireClientOrganization(actorId);
    AssetCategory category =
        categories
            .findById(request.categoryId())
            .filter(AssetCategory::isActive)
            .orElseThrow(
                () ->
                    new BusinessException(
                        HttpStatus.BAD_REQUEST, "VALIDATION_FAILED", "Unknown or inactive category"));
    if (assets.existsByOrganizationIdAndCode(organizationId, normalize(request.code()))) {
      throw new BusinessException(HttpStatus.CONFLICT, "DUPLICATE_CODE", "Asset code already exists");
    }
    Asset asset =
        Asset.clientCreate(
            organizationId,
            category.getId(),
            request.code(),
            request.name(),
            request.description(),
            request.locationText(),
            request.latitude(),
            request.longitude(),
            request.ownershipInformation(),
            actorId);
    return toResponse(assets.saveAndFlush(asset));
  }

  @Transactional(readOnly = true)
  public AssetPageResponse list(UUID actorId, int page, int pageSize, String search) {
    UserAccess.ActiveUser actor = requireActive(actorId);
    UUID organizationId = requireOrganization(actor);
    Page<Asset> result =
        assets.findByOrganizationId(
            organizationId,
            PageRequest.of(Math.max(page - 1, 0), Math.min(Math.max(pageSize, 1), 100),
                Sort.by("name")));
    return new AssetPageResponse(
        result.getContent().stream().map(this::toResponse).toList(),
        page,
        pageSize,
        result.getTotalElements(),
        result.getTotalPages());
  }

  @Transactional(readOnly = true)
  public AssetResponse get(UUID actorId, UUID assetId) {
    return toResponse(requireOwnedAsset(actorId, assetId));
  }

  @Transactional
  public AssetResponse update(UUID actorId, UUID assetId, UpdateAssetRequest request) {
    Asset asset = requireOwnedAsset(actorId, assetId);
    if (asset.getStatus() != AssetStatus.PENDING_REVIEW
        && asset.getStatus() != AssetStatus.INACTIVE) {
      throw new BusinessException(
          HttpStatus.CONFLICT, "INVALID_STATE", "Only pending or inactive assets can be edited");
    }
    asset.update(
        request.name(), request.description(), request.locationText(),
        request.latitude(), request.longitude(), request.ownershipInformation());
    return toResponse(assets.saveAndFlush(asset));
  }

  private Asset requireOwnedAsset(UUID actorId, UUID assetId) {
    UserAccess.ActiveUser actor = requireActive(actorId);
    UUID organizationId = requireOrganization(actor);
    return assets
        .findByIdAndOrganizationId(assetId, organizationId)
        .orElseThrow(
            () -> new BusinessException(HttpStatus.NOT_FOUND, "NOT_FOUND", "Asset not found"));
  }

  private UUID requireClientOrganization(UUID actorId) {
    return requireOrganization(requireActive(actorId));
  }

  private UUID requireOrganization(UserAccess.ActiveUser actor) {
    if (actor.organizationId() == null) {
      throw new BusinessException(
          HttpStatus.BAD_REQUEST, "VALIDATION_FAILED", "Actor has no organization scope");
    }
    return actor.organizationId();
  }

  private UserAccess.ActiveUser requireActive(UUID actorId) {
    return userAccess
        .findActiveUser(actorId)
        .orElseThrow(
            () -> new BusinessException(HttpStatus.FORBIDDEN, "FORBIDDEN", "User is not active"));
  }

  private static String normalize(String code) {
    return code.trim().toUpperCase(Locale.ROOT);
  }

  private AssetResponse toResponse(Asset asset) {
    return new AssetResponse(
        asset.getId(), asset.getCode(), asset.getName(), asset.getDescription(),
        asset.getLocationText(), asset.getLatitude(), asset.getLongitude(),
        asset.getStatus().name(), asset.getCategoryId(), asset.getCreatedAt());
  }
}
```

`Asset` gains the `update(...)` mutator used above — add to `assets/domain/Asset.java` (guard is already enforced by the service status check):

```java
  public void update(
      String name,
      String description,
      String locationText,
      BigDecimal latitude,
      BigDecimal longitude,
      String ownershipInformation) {
    validateCoordinates(latitude, longitude);
    if (name != null) this.name = name;
    if (description != null) this.description = description;
    if (locationText != null) this.locationText = locationText;
    if (latitude != null) this.latitude = latitude;
    if (longitude != null) this.longitude = longitude;
    if (ownershipInformation != null) this.ownershipInformation = ownershipInformation;
    updatedAt = Instant.now();
  }
```

(If `Asset` lacks `getLatitude/getLongitude/getDescription/getLocationText/getCategoryId/getCreatedAt` getters, add them in the same style as the existing getters.)

`api/AssetController.java`:

```java
package com.smartdroneinspection.assets.api;

import com.smartdroneinspection.assets.api.dto.request.CreateAssetRequest;
import com.smartdroneinspection.assets.api.dto.request.UpdateAssetRequest;
import com.smartdroneinspection.assets.api.dto.response.AssetPageResponse;
import com.smartdroneinspection.assets.api.dto.response.AssetResponse;
import com.smartdroneinspection.assets.service.AssetService;
import com.smartdroneinspection.shared.api.ApiResponse;
import jakarta.validation.Valid;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/assets")
public class AssetController {

  private final AssetService assets;

  public AssetController(AssetService assets) {
    this.assets = assets;
  }

  @PostMapping
  @PreAuthorize("hasRole('CLIENT')")
  @ResponseStatus(HttpStatus.CREATED)
  public ApiResponse<AssetResponse> create(
      @AuthenticationPrincipal Jwt jwt, @Valid @RequestBody CreateAssetRequest request) {
    return ApiResponse.success(assets.create(UUID.fromString(jwt.getSubject()), request));
  }

  @GetMapping
  @PreAuthorize("hasAnyRole('CLIENT', 'ADMIN', 'SERVICE_MANAGER')")
  public ApiResponse<AssetPageResponse> list(
      @AuthenticationPrincipal Jwt jwt,
      @RequestParam(defaultValue = "1") int page,
      @RequestParam(defaultValue = "20") int pageSize,
      @RequestParam(required = false) String search) {
    return ApiResponse.success(assets.list(UUID.fromString(jwt.getSubject()), page, pageSize, search));
  }

  @GetMapping("/{assetId}")
  @PreAuthorize("hasAnyRole('CLIENT', 'ADMIN', 'SERVICE_MANAGER')")
  public ApiResponse<AssetResponse> get(
      @AuthenticationPrincipal Jwt jwt, @PathVariable UUID assetId) {
    return ApiResponse.success(assets.get(UUID.fromString(jwt.getSubject()), assetId));
  }

  @PutMapping("/{assetId}")
  @PreAuthorize("hasRole('CLIENT')")
  public ApiResponse<AssetResponse> update(
      @AuthenticationPrincipal Jwt jwt,
      @PathVariable UUID assetId,
      @Valid @RequestBody UpdateAssetRequest request) {
    return ApiResponse.success(assets.update(UUID.fromString(jwt.getSubject()), assetId, request));
  }
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `.\mvnw.cmd test -Dtest=AssetApiIntegrationTest`
Expected: PASS (4 tests).

- [ ] **Step 5: Full verify and commit**

```powershell
.\mvnw.cmd spotless:apply
.\mvnw.cmd verify
git add src/main/java/com/smartdroneinspection/assets src/test/java/com/smartdroneinspection/assets/AssetApiIntegrationTest.java
git commit -m "feat(assets): add organization-scoped asset api"
```

### Task 4: Schedule proposal API — Manager review + Client select (creates schedule)

**Files:**
- Create: `backend/src/main/java/com/smartdroneinspection/assets/api/ScheduleProposalController.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/service/ScheduleProposalService.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/api/dto/request/ReviewProposalRequest.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/api/dto/request/SelectProposalRequest.java` (empty body not needed — select takes no body)
- Create: `backend/src/main/java/com/smartdroneinspection/assets/api/dto/response/ScheduleProposalResponse.java`
- Modify: `backend/src/main/java/com/smartdroneinspection/assets/repository/ScheduleProposalRepository.java` (add locked fetch)
- Modify: `backend/src/main/java/com/smartdroneinspection/assets/domain/InspectionSchedule.java` (add `static create(...)`, getter `getStatus` exists)
- Test: `backend/src/test/java/com/smartdroneinspection/assets/ScheduleProposalApiIntegrationTest.java`

**Interfaces:**
- Consumes: Task 1 (`ScheduleProposal`, `ScheduleProposalRepository`), Task 2 fixture, Task 3 asset scoping pattern (`UserAccess`), existing `InspectionSchedule` (`activate(AssetStatus, ChecklistTemplateStatus)`, `pause()`, `markGenerated(...)`), `InspectionScheduleRepository`.
- Produces:
  - Routes: `GET /api/v1/schedule-proposals` (CLIENT: own-org `MANAGER_APPROVED`; MANAGER/ADMIN: all statuses, `assetId` query required for MANAGER/ADMIN), `POST /api/v1/schedule-proposals/{proposalId}/review` (MANAGER), `POST /api/v1/schedule-proposals/{proposalId}/select` (CLIENT).
  - `ScheduleProposalService`: `List<ScheduleProposalResponse> listForClient(UUID actorId, UUID assetIdOrNull)`, `List<ScheduleProposalResponse> listForManager(UUID actorId, UUID assetId)`, `ScheduleProposalResponse review(UUID managerId, UUID proposalId, ReviewProposalRequest)`, `ScheduleProposalResponse select(UUID clientId, UUID proposalId)`.
  - `ReviewProposalRequest(action: "APPROVE"|"REJECT", note: String|null, frequencyUnit: String|null, frequencyInterval: Integer|null)` — unit/interval optional, applied via `managerAdjust` before approve/reject.
  - Errors: `NOT_FOUND` (404 cross-org/unknown), `INVALID_STATE` (409 double-select, already scheduled, edit-after-select), `VALIDATION_FAILED` (400 bad action).
  - Locked repository method: `Optional<ScheduleProposal> findWithLockById(UUID id)` using `@Lock(LockModeType.PESSIMISTIC_WRITE)`.

- [ ] **Step 1: Write the failing test**

`ScheduleProposalApiIntegrationTest.java` — header/helpers identical to Task 2's test. Seed helper inside the class:

```java
  private UUID seedProposal(UUID assetId, ScheduleProposalStatus status) {
    ScheduleProposal p =
        ScheduleProposal.generate(assetId, fixture.checklistTemplateId(), "MONTH", 3);
    if (status == ScheduleProposalStatus.MANAGER_APPROVED) {
      p.managerApprove(null, fixture.managerId());
    }
    return proposals.saveAndFlush(p).getId();
  }

  private UUID seedPendingAsset() {
    return assets
        .saveAndFlush(
            Asset.clientCreate(
                fixture.organizationId(), fixture.categoryId(), "PA-" + UUID.randomUUID(),
                "Pending asset", null, "District 1", null, null, null, fixture.clientId()))
        .getId();
  }
```

(Autowired: `ScheduleProposalRepository proposals`, `InspectionScheduleRepository schedules`, plus the fixture repos.)

Tests:

```java
  @Test
  void managerReviewsProposalAndClientOnlySeesApprovedOwnOrg() throws Exception {
    UUID assetId = seedPendingAsset();
    UUID proposalId = seedProposal(assetId, ScheduleProposalStatus.GENERATED);

    // CLIENT cannot see GENERATED
    mockMvc
        .perform(
            get("/api/v1/schedule-proposals").param("assetId", assetId.toString())
                .with(client(fixture.clientId())))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.length()").value(0));

    // MANAGER approves (with adjustment)
    mockMvc
        .perform(
            post("/api/v1/schedule-proposals/{id}/review", proposalId)
                .with(manager(fixture.managerId()))
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"action\":\"APPROVE\",\"frequencyUnit\":\"WEEK\",\"frequencyInterval\":2}"))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.data.status").value("MANAGER_APPROVED"))
        .andExpect(jsonPath("$.data.frequencyInterval").value(2));

    // CLIENT now sees it
    mockMvc
        .perform(
            get("/api/v1/schedule-proposals").param("assetId", assetId.toString())
                .with(client(fixture.clientId())))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$[0].id").value(proposalId.toString()));

    // cross-org client sees nothing
    mockMvc
        .perform(
            get("/api/v1/schedule-proposals").param("assetId", assetId.toString())
                .with(client(fixture.otherClientId())))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.length()").value(0));
  }

  @Test
  void selectingCreatesOneScheduleSupersedesSiblingsAndIsNotRepeatable() throws Exception {
    UUID assetId = seedPendingAsset();
    UUID first = seedProposal(assetId, ScheduleProposalStatus.MANAGER_APPROVED);
    UUID second = seedProposal(assetId, ScheduleProposalStatus.MANAGER_APPROVED);
    assets.saveAndFlush(approved(assetId)); // asset must be ACTIVE for activate()

    mockMvc
        .perform(post("/api/v1/schedule-proposals/{id}/select", first).with(client(fixture.clientId())))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.data.status").value("CLIENT_SELECTED"));

    // sibling superseded
    assertThat(proposals.findById(second).orElseThrow().getStatus())
        .isEqualTo(ScheduleProposalStatus.SUPERSEDED);

    // exactly one schedule, ACTIVE
    List<InspectionSchedule> forAsset = schedules.findByAssetIdOrderByNextDueAt(assetId);
    assertThat(forAsset).hasSize(1);
    assertThat(forAsset.get(0).getStatus()).isEqualTo(InspectionScheduleStatus.ACTIVE);

    // double select → 409
    mockMvc
        .perform(post("/api/v1/schedule-proposals/{id}/select", first).with(client(fixture.clientId())))
        .andExpect(status().isConflict());
    // second proposal is SUPERSEDED → 409 as well
    mockMvc
        .perform(post("/api/v1/schedule-proposals/{id}/select", second).with(client(fixture.clientId())))
        .andExpect(status().isConflict());

    // a second schedule cannot be created for an already scheduled asset
    UUID third = seedProposal(assetId, ScheduleProposalStatus.MANAGER_APPROVED);
    // re-approve path: seedProposal already approved; manager re-approves siblings? third is
    // GENERATED-level conflict — seed as MANAGER_APPROVED directly:
    mockMvc
        .perform(post("/api/v1/schedule-proposals/{id}/select", third).with(client(fixture.clientId())))
        .andExpect(status().isConflict());
  }

  @Test
  void crossOrgSelectAndNonManagerReviewAreDenied() throws Exception {
    UUID assetId = seedPendingAsset();
    UUID proposalId = seedProposal(assetId, ScheduleProposalStatus.MANAGER_APPROVED);

    mockMvc
        .perform(post("/api/v1/schedule-proposals/{id}/select", proposalId)
            .with(client(fixture.otherClientId())))
        .andExpect(status().isNotFound());

    mockMvc
        .perform(post("/api/v1/schedule-proposals/{id}/review", proposalId)
            .with(client(fixture.clientId()))
            .contentType(MediaType.APPLICATION_JSON)
            .content("{\"action\":\"APPROVE\"}"))
        .andExpect(status().isForbidden());

    mockMvc
        .perform(post("/api/v1/schedule-proposals/{id}/review", proposalId)
            .with(manager(fixture.managerId()))
            .contentType(MediaType.APPLICATION_JSON)
            .content("{\"action\":\"MAYBE\"}"))
        .andExpect(status().isBadRequest());
  }
```

Where `approved(assetId)` is a small helper that loads the asset, calls `asset.approveReview()` (the seeded asset starts `PENDING_REVIEW`), and saves it — needed because `InspectionSchedule.activate` validates `AssetStatus.ACTIVE`.

- [ ] **Step 2: Run the test to verify it fails**

Run: `.\mvnw.cmd test -Dtest=ScheduleProposalApiIntegrationTest`
Expected: FAIL — 404 (no controller).

- [ ] **Step 3: Implement locked fetch, schedule factory, service, controller**

Repository addition in `ScheduleProposalRepository`:

```java
  @Lock(LockModeType.PESSIMISTIC_WRITE)
  @Query("select p from ScheduleProposal p where p.id = :id")
  Optional<ScheduleProposal> findWithLockById(@Param("id") UUID id);
```
(import `jakarta.persistence.LockModeType`, `org.springframework.data.jpa.repository.Lock`, `@Query`, `@Param`, `java.util.Optional`.)

`InspectionSchedule` factory — add to the existing entity:

```java
  public static InspectionSchedule fromSelectedProposal(
      UUID assetId,
      UUID checklistTemplateId,
      String frequencyUnit,
      int frequencyInterval,
      UUID createdByUserId) {
    InspectionSchedule schedule =
        new InspectionSchedule(
            assetId,
            checklistTemplateId,
            InspectionFrequencyUnit.valueOf(frequencyUnit),
            frequencyInterval,
            Instant.now(),
            createdByUserId);
    schedule.activate(AssetStatus.ACTIVE, ChecklistTemplateStatus.ACTIVE);
    return schedule;
  }
```

(The constructor's `nextDueAt` argument is overwritten below by the first `markGenerated`/recompute in T010; for creation, recompute a correct first due date before saving — see `ScheduleProposalService.select`: it computes `nextDueAt = plusFrequency(Instant.now(), unit, interval)` and passes it. Adjust the factory signature to take `Instant nextDueAt` instead of `Instant.now()` internally if the constructor requires a future date.)

`ReviewProposalRequest`:

```java
package com.smartdroneinspection.assets.api.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;

public record ReviewProposalRequest(
    @NotBlank @Pattern(regexp = "APPROVE|REJECT") String action,
    @jakarta.validation.constraints.Size(max = 500) String note,
    @Pattern(regexp = "DAY|WEEK|MONTH|YEAR") String frequencyUnit,
    @jakarta.validation.constraints.Min(1) Integer frequencyInterval) {}
```

`ScheduleProposalResponse`:

```java
package com.smartdroneinspection.assets.api.dto.response;

import java.util.UUID;

public record ScheduleProposalResponse(
    UUID id,
    UUID assetId,
    UUID checklistTemplateId,
    String frequencyUnit,
    int frequencyInterval,
    String status,
    String managerNote) {}
```

`service/ScheduleProposalService.java`:

```java
package com.smartdroneinspection.assets.service;

import com.smartdroneinspection.assets.api.dto.request.ReviewProposalRequest;
import com.smartdroneinspection.assets.api.dto.response.ScheduleProposalResponse;
import com.smartdroneinspection.assets.domain.Asset;
import com.smartdroneinspection.assets.domain.InspectionSchedule;
import com.smartdroneinspection.assets.domain.ScheduleProposal;
import com.smartdroneinspection.assets.domain.enums.InspectionScheduleStatus;
import com.smartdroneinspection.assets.domain.enums.ScheduleProposalStatus;
import com.smartdroneinspection.assets.repository.AssetRepository;
import com.smartdroneinspection.assets.repository.InspectionScheduleRepository;
import com.smartdroneinspection.assets.repository.ScheduleProposalRepository;
import com.smartdroneinspection.shared.exception.BusinessException;
import com.smartdroneinspection.users.UserAccess;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Locale;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ScheduleProposalService {

  private final ScheduleProposalRepository proposals;
  private final AssetRepository assets;
  private final InspectionScheduleRepository schedules;
  private final UserAccess userAccess;

  public ScheduleProposalService(
      ScheduleProposalRepository proposals,
      AssetRepository assets,
      InspectionScheduleRepository schedules,
      UserAccess userAccess) {
    this.proposals = proposals;
    this.assets = assets;
    this.schedules = schedules;
    this.userAccess = userAccess;
  }

  @Transactional(readOnly = true)
  public List<ScheduleProposalResponse> listForClient(UUID actorId, UUID assetId) {
    Asset asset = requireOwnedAsset(actorId, assetId);
    return proposals.findByAssetIdAndStatus(asset.getId(), ScheduleProposalStatus.MANAGER_APPROVED)
        .stream().map(this::toResponse).toList();
  }

  @Transactional(readOnly = true)
  public List<ScheduleProposalResponse> listForManager(UUID assetId) {
    requireAssetExists(assetId);
    return proposals.findByAssetIdOrderByCreatedAtAsc(assetId).stream()
        .map(this::toResponse)
        .toList();
  }

  @Transactional
  public ScheduleProposalResponse review(UUID managerId, UUID proposalId, ReviewProposalRequest request) {
    ScheduleProposal proposal =
        proposals.findWithLockById(proposalId)
            .orElseThrow(() -> notFound(proposalId));
    if ("APPROVE".equals(request.action())) {
      if (request.frequencyUnit() != null && request.frequencyInterval() != null) {
        proposal.managerAdjust(request.frequencyUnit(), request.frequencyInterval());
      }
      proposal.managerApprove(request.note(), managerId);
    } else if ("REJECT".equals(request.action())) {
      proposal.managerReject(request.note(), managerId);
    } else {
      throw new BusinessException(
          HttpStatus.BAD_REQUEST, "VALIDATION_FAILED", "Unknown review action");
    }
    return toResponse(proposals.saveAndFlush(proposal));
  }

  @Transactional
  public ScheduleProposalResponse select(UUID clientId, UUID proposalId) {
    ScheduleProposal proposal =
        proposals.findWithLockById(proposalId).orElseThrow(() -> notFound(proposalId));
    Asset asset = requireOwnedAsset(clientId, proposal.getAssetId());

    boolean alreadyScheduled =
        schedules.findByAssetIdOrderByNextDueAt(asset.getId()).stream()
            .anyMatch(s -> s.getStatus() == InspectionScheduleStatus.ACTIVE);
    if (alreadyScheduled) {
      throw new BusinessException(
          HttpStatus.CONFLICT, "INVALID_STATE", "Asset already has an active schedule");
    }

    proposal.clientSelect(clientId);
    proposals.saveAndFlush(proposal);
    for (ScheduleProposal sibling :
        proposals.findByAssetIdAndStatus(proposal.getAssetId(), ScheduleProposalStatus.MANAGER_APPROVED)) {
      sibling.supersede();
      proposals.save(sibling);
    }

    InspectionSchedule schedule =
        InspectionSchedule.fromSelectedProposal(
            proposal.getAssetId(),
            proposal.getChecklistTemplateId(),
            proposal.getFrequencyUnit(),
            proposal.getFrequencyInterval(),
            plusFrequency(Instant.now(), proposal.getFrequencyUnit(), proposal.getFrequencyInterval()),
            clientId);
    schedules.saveAndFlush(schedule);
    return toResponse(proposal);
  }

  public static Instant plusFrequency(Instant from, String unit, int interval) {
    return switch (unit) {
      case "DAY" -> from.plus(interval, ChronoUnit.DAYS);
      case "WEEK" -> from.plus(interval * 7L, ChronoUnit.DAYS);
      case "MONTH" -> from.plus(interval * 30L, ChronoUnit.DAYS);
      case "YEAR" -> from.plus(interval * 365L, ChronoUnit.DAYS);
      default -> throw new IllegalArgumentException("Unsupported frequency unit: " + unit);
    };
  }

  private Asset requireOwnedAsset(UUID actorId, UUID assetId) {
    UserAccess.ActiveUser actor =
        userAccess.findActiveUser(actorId)
            .orElseThrow(() -> new BusinessException(HttpStatus.FORBIDDEN, "FORBIDDEN", "User is not active"));
    if (actor.organizationId() == null) {
      throw new BusinessException(HttpStatus.FORBIDDEN, "FORBIDDEN", "No organization scope");
    }
    return assets.findByIdAndOrganizationId(assetId, actor.organizationId())
        .orElseThrow(() -> notFound(assetId));
  }

  private void requireAssetExists(UUID assetId) {
    assets.findById(assetId).orElseThrow(() -> notFound(assetId));
  }

  private BusinessException notFound(UUID id) {
    return new BusinessException(HttpStatus.NOT_FOUND, "NOT_FOUND", "Proposal not found: " + id);
  }

  private ScheduleProposalResponse toResponse(ScheduleProposal p) {
    return new ScheduleProposalResponse(
        p.getId(), p.getAssetId(), p.getChecklistTemplateId(), p.getFrequencyUnit(),
        p.getFrequencyInterval(), p.getStatus().name(), p.getManagerNote());
  }
}
```

Note: `fromSelectedProposal` factory signature takes `(assetId, checklistTemplateId, unit, interval, Instant nextDueAt, UUID createdByUserId)` — adjust the factory added in this step to accept `nextDueAt` as its 5th parameter (the test block above shows the call shape).

`api/ScheduleProposalController.java` (role branching uses `UserAccess`, not JWT claims — inject both dependencies):

```java
package com.smartdroneinspection.assets.api;

import com.smartdroneinspection.assets.api.dto.request.ReviewProposalRequest;
import com.smartdroneinspection.assets.api.dto.response.ScheduleProposalResponse;
import com.smartdroneinspection.assets.service.ScheduleProposalService;
import com.smartdroneinspection.shared.api.ApiResponse;
import com.smartdroneinspection.shared.exception.BusinessException;
import com.smartdroneinspection.users.UserAccess;
import jakarta.validation.Valid;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/schedule-proposals")
public class ScheduleProposalController {

  private final ScheduleProposalService proposals;
  private final UserAccess userAccess;

  public ScheduleProposalController(ScheduleProposalService proposals, UserAccess userAccess) {
    this.proposals = proposals;
    this.userAccess = userAccess;
  }

  @GetMapping
  @PreAuthorize("hasAnyRole('CLIENT', 'SERVICE_MANAGER', 'ADMIN')")
  public ApiResponse<List<ScheduleProposalResponse>> list(
      @AuthenticationPrincipal Jwt jwt, @RequestParam UUID assetId) {
    UUID actorId = UUID.fromString(jwt.getSubject());
    UserAccess.ActiveUser actor =
        userAccess
            .findActiveUser(actorId)
            .orElseThrow(() -> new BusinessException(HttpStatus.FORBIDDEN, "FORBIDDEN", "User is not active"));
    if (actor.hasRole("SERVICE_MANAGER") || actor.hasRole("ADMIN")) {
      return ApiResponse.success(proposals.listForManager(assetId));
    }
    return ApiResponse.success(proposals.listForClient(actorId, assetId));
  }

  @PostMapping("/{proposalId}/review")
  @PreAuthorize("hasRole('SERVICE_MANAGER')")
  public ApiResponse<ScheduleProposalResponse> review(
      @AuthenticationPrincipal Jwt jwt,
      @PathVariable UUID proposalId,
      @Valid @RequestBody ReviewProposalRequest request) {
    return ApiResponse.success(
        proposals.review(UUID.fromString(jwt.getSubject()), proposalId, request));
  }

  @PostMapping("/{proposalId}/select")
  @PreAuthorize("hasRole('CLIENT')")
  public ApiResponse<ScheduleProposalResponse> select(
      @AuthenticationPrincipal Jwt jwt, @PathVariable UUID proposalId) {
    return ApiResponse.success(
        proposals.select(UUID.fromString(jwt.getSubject()), proposalId));
  }
}
```

(`assetId` is a required query parameter for both roles — the CLIENT list is per-asset on the proposal screen.)

- [ ] **Step 4: Run the test to verify it passes**

Run: `.\mvnw.cmd test -Dtest=ScheduleProposalApiIntegrationTest`
Expected: PASS (3 tests).

- [ ] **Step 5: Full verify and commit**

```powershell
.\mvnw.cmd spotless:apply
.\mvnw.cmd verify
git add src/main/java/com/smartdroneinspection/assets src/test/java/com/smartdroneinspection/assets/ScheduleProposalApiIntegrationTest.java
git commit -m "feat(assets): add schedule proposal review and selection api"
```

### Task 5: Asset review — approve generates proposals (spec lifecycle)

**Files:**
- Create: `backend/src/main/java/com/smartdroneinspection/assets/service/AssetReviewService.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/api/dto/request/ReviewAssetRequest.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/api/dto/response/AssetReviewResponse.java`
- Modify: `backend/src/main/java/com/smartdroneinspection/assets/api/AssetController.java` (add review route)
- Modify: `backend/src/main/java/com/smartdroneinspection/assets/repository/ChecklistTemplateRepository.java` (add active-by-category finder)
- Test: `backend/src/test/java/com/smartdroneinspection/assets/AssetReviewApiIntegrationTest.java`

**Interfaces:**
- Consumes: Task 1 (`Asset.approveReview/rejectReview`, `ScheduleProposal.generate`), Task 2 fixture, `CategoryFrequencySuggestionRepository`, `ScheduleProposalRepository`.
- Produces:
  - `AssetReviewService(UUID managerId)` methods: `AssetReviewResponse review(UUID managerId, UUID assetId, ReviewAssetRequest)`.
  - Route: `POST /api/v1/assets/{assetId}/review` (`SERVICE_MANAGER`).
  - `ReviewAssetRequest(action: "APPROVE"|"REJECT", note: String|null)` — matches the API table's `APPROVE`/`REJECTED` mapping (`REJECT` action = `AssetStatus.REJECTED`).
  - `AssetReviewResponse(assetId, status, proposalCount)`.
  - Checklist finder: `ChecklistTemplateRepository.findFirstByAssetCategoryIdAndStatusOrderByVersionNumberDesc(UUID categoryId, ChecklistTemplateStatus status)`.
  - Behavior: APPROVE on `PENDING_REVIEW` → `ACTIVE` + one `GENERATED` proposal per category suggestion (checklist template = active template of the asset's category); APPROVE when already `ACTIVE` with proposals → idempotent no-op (same response); category without suggestions → 409 `NO_SUGGESTED_FREQUENCIES`; APPROVE on `REJECTED` → 409 `INVALID_STATE`; REJECT only from `PENDING_REVIEW`.

- [ ] **Step 1: Write the failing test**

`AssetReviewApiIntegrationTest.java` (same header/helpers as Task 2; autowire `ScheduleProposalRepository proposals`, `CategoryFrequencySuggestionRepository frequencies`, `AssetRepository assets` plus fixture deps):

```java
  @Test
  void managerApprovalActivatesAssetAndGeneratesOneProposalPerSuggestion() throws Exception {
    frequencies.saveAndFlush(new CategoryFrequencySuggestion(fixture.categoryId(), "MONTH", 3, 0));
    frequencies.saveAndFlush(new CategoryFrequencySuggestion(fixture.categoryId(), "YEAR", 1, 1));
    UUID assetId = seedPendingAsset();

    mockMvc
        .perform(
            post("/api/v1/assets/{id}/review", assetId)
                .with(manager(fixture.managerId()))
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"action\":\"APPROVE\",\"note\":\"Standard cadence\"}"))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.data.status").value("ACTIVE"))
        .andExpect(jsonPath("$.data.proposalCount").value(2));

    assertThat(proposals.findByAssetIdOrderByCreatedAtAsc(assetId))
        .hasSize(2)
        .allSatisfy(p -> assertThat(p.getStatus()).isEqualTo(ScheduleProposalStatus.GENERATED));

    // idempotent re-approve does not duplicate
    mockMvc
        .perform(
            post("/api/v1/assets/{id}/review", assetId)
                .with(manager(fixture.managerId()))
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"action\":\"APPROVE\"}"))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.data.proposalCount").value(2));
    assertThat(proposals.findByAssetIdOrderByCreatedAtAsc(assetId)).hasSize(2);
  }

  @Test
  void approvalRequiresSuggestedFrequenciesAndRejectionLeavesNoProposals() throws Exception {
    UUID assetNoSuggestions = seedPendingAsset();
    mockMvc
        .perform(
            post("/api/v1/assets/{id}/review", assetNoSuggestions)
                .with(manager(fixture.managerId()))
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"action\":\"APPROVE\"}"))
        .andExpect(status().isConflict())
        .andExpect(jsonPath("$.code").value("NO_SUGGESTED_FREQUENCIES"));

    UUID assetId = seedPendingAsset();
    mockMvc
        .perform(
            post("/api/v1/assets/{id}/review", assetId)
                .with(manager(fixture.managerId()))
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"action\":\"REJECT\",\"note\":\"Unlocatable\"}"))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.data.status").value("REJECTED"))
        .andExpect(jsonPath("$.data.proposalCount").value(0));
    assertThat(proposals.findByAssetIdOrderByCreatedAtAsc(assetId)).isEmpty();
  }

  @Test
  void onlyServiceManagerCanReview() throws Exception {
    UUID assetId = seedPendingAsset();
    mockMvc
        .perform(
            post("/api/v1/assets/{id}/review", assetId)
                .with(client(fixture.clientId()))
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"action\":\"APPROVE\"}"))
        .andExpect(status().isForbidden());
    mockMvc
        .perform(
            post("/api/v1/assets/{id}/review", assetId)
                .with(admin(fixture.adminId()))
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"action\":\"APPROVE\"}"))
        .andExpect(status().isForbidden());
  }
```

(`seedPendingAsset()` is copied from Task 4's test helper. The category-frequencies test class must save suggestions before approving; if the previous test class's transaction rolled back — each test is `@Transactional`, so state is isolated.)

- [ ] **Step 2: Run the test to verify it fails**

Run: `.\mvnw.cmd test -Dtest=AssetReviewApiIntegrationTest`
Expected: FAIL — 404 (no review route on `AssetController`).

- [ ] **Step 3: Implement DTOs, repository finder, service, route**

DTOs:

```java
// request/ReviewAssetRequest.java
package com.smartdroneinspection.assets.api.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public record ReviewAssetRequest(
    @NotBlank @Pattern(regexp = "APPROVE|REJECT") String action,
    @Size(max = 500) String note) {}
```

```java
// response/AssetReviewResponse.java
package com.smartdroneinspection.assets.api.dto.response;

import java.util.UUID;

public record AssetReviewResponse(UUID assetId, String status, int proposalCount) {}
```

Finder addition in `ChecklistTemplateRepository`:

```java
  Optional<ChecklistTemplate> findFirstByAssetCategoryIdAndStatusOrderByVersionNumberDesc(
      UUID assetCategoryId, ChecklistTemplateStatus status);
```
(import `ChecklistTemplateStatus`.)

`service/AssetReviewService.java`:

```java
package com.smartdroneinspection.assets.service;

import com.smartdroneinspection.assets.api.dto.request.ReviewAssetRequest;
import com.smartdroneinspection.assets.api.dto.response.AssetReviewResponse;
import com.smartdroneinspection.assets.domain.Asset;
import com.smartdroneinspection.assets.domain.AssetCategory;
import com.smartdroneinspection.assets.domain.ChecklistTemplate;
import com.smartdroneinspection.assets.domain.ScheduleProposal;
import com.smartdroneinspection.assets.domain.enums.AssetStatus;
import com.smartdroneinspection.assets.domain.enums.ChecklistTemplateStatus;
import com.smartdroneinspection.assets.domain.enums.ScheduleProposalStatus;
import com.smartdroneinspection.assets.repository.AssetCategoryRepository;
import com.smartdroneinspection.assets.repository.AssetRepository;
import com.smartdroneinspection.assets.repository.CategoryFrequencySuggestionRepository;
import com.smartdroneinspection.assets.repository.ChecklistTemplateRepository;
import com.smartdroneinspection.assets.repository.ScheduleProposalRepository;
import com.smartdroneinspection.shared.exception.BusinessException;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AssetReviewService {

  private final AssetRepository assets;
  private final AssetCategoryRepository categories;
  private final CategoryFrequencySuggestionRepository suggestions;
  private final ChecklistTemplateRepository templates;
  private final ScheduleProposalRepository proposals;

  public AssetReviewService(
      AssetRepository assets,
      AssetCategoryRepository categories,
      CategoryFrequencySuggestionRepository suggestions,
      ChecklistTemplateRepository templates,
      ScheduleProposalRepository proposals) {
    this.assets = assets;
    this.categories = categories;
    this.suggestions = suggestions;
    this.templates = templates;
    this.proposals = proposals;
  }

  @Transactional
  public AssetReviewResponse review(UUID managerId, UUID assetId, ReviewAssetRequest request) {
    Asset asset =
        assets.findById(assetId)
            .orElseThrow(
                () -> new BusinessException(HttpStatus.NOT_FOUND, "NOT_FOUND", "Asset not found"));

    if ("REJECT".equals(request.action())) {
      asset.rejectReview();
      assets.saveAndFlush(asset);
      return new AssetReviewResponse(assetId, asset.getStatus().name(), 0);
    }
    if (!"APPROVE".equals(request.action())) {
      throw new BusinessException(
          HttpStatus.BAD_REQUEST, "VALIDATION_FAILED", "Unknown review action");
    }

    if (asset.getStatus() == AssetStatus.ACTIVE) {
      // idempotent re-approve: return current proposal count, generate nothing new
      return new AssetReviewResponse(
          assetId,
          asset.getStatus().name(),
          proposals.findByAssetIdAndStatus(assetId, ScheduleProposalStatus.GENERATED).size()
              + proposals.findByAssetIdAndStatus(assetId, ScheduleProposalStatus.MANAGER_APPROVED).size()
              + proposals.findByAssetIdAndStatus(assetId, ScheduleProposalStatus.CLIENT_SELECTED).size());
    }
    if (asset.getStatus() != AssetStatus.PENDING_REVIEW) {
      throw new BusinessException(
          HttpStatus.CONFLICT, "INVALID_STATE", "Asset is not awaiting review");
    }

    var categorySuggestions =
        suggestions.findByAssetCategoryIdOrderBySortOrderAsc(asset.getCategoryId());
    if (categorySuggestions.isEmpty()) {
      throw new BusinessException(
          HttpStatus.CONFLICT, "NO_SUGGESTED_FREQUENCIES",
          "Category has no suggested frequencies; ask an Admin to configure them first");
    }
    ChecklistTemplate template =
        templates
            .findFirstByAssetCategoryIdAndStatusOrderByVersionNumberDesc(
                asset.getCategoryId(), ChecklistTemplateStatus.ACTIVE)
            .orElseThrow(
                () ->
                    new BusinessException(
                        HttpStatus.CONFLICT, "NO_ACTIVE_CHECKLIST",
                        "Category has no active checklist template"));

    asset.approveReview();
    assets.saveAndFlush(asset);
    for (var suggestion : categorySuggestions) {
      proposals.saveAndFlush(
          ScheduleProposal.generate(
              assetId,
              template.getId(),
              suggestion.getFrequencyUnit(),
              suggestion.getFrequencyInterval()));
    }
    return new AssetReviewResponse(assetId, asset.getStatus().name(), categorySuggestions.size());
  }
}
```

Route addition in `AssetController` (inject `AssetReviewService` alongside `AssetService`):

```java
  @PostMapping("/{assetId}/review")
  @PreAuthorize("hasRole('SERVICE_MANAGER')")
  public ApiResponse<AssetReviewResponse> review(
      @AuthenticationPrincipal Jwt jwt,
      @PathVariable UUID assetId,
      @Valid @RequestBody ReviewAssetRequest request) {
    return ApiResponse.success(
        assetReview.review(UUID.fromString(jwt.getSubject()), assetId, request));
  }
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `.\mvnw.cmd test -Dtest=AssetReviewApiIntegrationTest`
Expected: PASS (3 tests).

- [ ] **Step 5: Full verify and commit**

```powershell
.\mvnw.cmd spotless:apply
.\mvnw.cmd verify
git add src/main/java/com/smartdroneinspection/assets src/test/java/com/smartdroneinspection/assets/AssetReviewApiIntegrationTest.java
git commit -m "feat(assets): add manager asset review with proposal generation"
```

### Task 6: Authorized asset-document upload (T008)

**Files:**
- Create: `backend/src/main/java/com/smartdroneinspection/assets/api/AssetDocumentController.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/service/AssetDocumentService.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/api/dto/response/AssetDocumentResponse.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/api/dto/request/AssetDocumentMetadataRequest.java`
- Modify: `backend/src/main/java/com/smartdroneinspection/assets/domain/Asset.java` (document accessors if missing)
- Test: `backend/src/test/java/com/smartdroneinspection/assets/AssetDocumentApiIntegrationTest.java`

**Interfaces:**
- Consumes: `Asset.addDocument(...)` (exists), `AssetRepository.findDetailedByIdAndOrganizationId` (exists), `com.smartdroneinspection.inspections.spi.EvidenceObjectStore` (published Modulith named interface: `put(String objectKey, String contentType, long sizeBytes, InputStream)`, `open(String)`, `delete(String)`), `ApiResponse`, `BusinessException`.
- Produces:
  - Routes: `POST /api/v1/assets/{assetId}/documents` (multipart `file` + `documentType`, `documentDate` fields; CLIENT own org — also allowed for ADMIN), `GET /api/v1/assets/{assetId}/documents`, `GET /api/v1/assets/{assetId}/documents/{documentId}/content`.
  - `AssetDocumentService`: `AssetDocumentResponse upload(UUID actorId, UUID assetId, MultipartFile file, String documentType, LocalDate documentDate)`, `List<AssetDocumentResponse> list(UUID actorId, UUID assetId)`, `DocumentContent open(UUID actorId, UUID assetId, UUID documentId)` (record `DocumentContent(String contentType, String fileName, InputStream stream)`).
  - Rules: allowed types `image/png`, `image/jpeg`, `image/webp`, `application/pdf` (else 415 `UNSUPPORTED_MEDIA_TYPE`); max 10 MB (else 413 `PAYLOAD_TOO_LARGE`); asset must exist in actor's org (`NOT_FOUND` otherwise); asset status must be `ACTIVE`, `INACTIVE`, or `PENDING_REVIEW`… **spec rule: `PENDING_REVIEW` upload denied** → allow only `ACTIVE`/`INACTIVE` (else 409 `INVALID_STATE`); object key `assets/{assetId}/documents/{uuid}`; checksum sha-256 hex of content.
  - `AssetDocumentResponse(id, documentType, fileName, contentType, sizeBytes, checksumSha256, documentDate, createdAt)`.

- [ ] **Step 1: Write the failing test**

`AssetDocumentApiIntegrationTest.java` (same header as Task 2; `@MockitoBean EvidenceObjectStore objectStore` with an in-memory `Map<String, byte[]>` like `InspectionReportApiIntegrationTest`; helper `client()/admin()`):

```java
  private static final byte[] PNG =
      java.util.Base64.getDecoder().decode(
          "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/o2cAAAAASUVORK5CYII=");
  private static final byte[] NOT_AN_IMAGE = new byte[] {1, 2, 3};

  @Test
  void activeAssetDocumentUploadsAndListsForOwnOrgOnly() throws Exception {
    UUID assetId = seedActiveAsset(); // Asset via constructor (ACTIVE), own org

    mockMvc
        .perform(
            multipart("/api/v1/assets/{id}/documents", assetId)
                .file(new MockMultipartFile("file", "permit.png", "image/png", PNG))
                .param("documentType", "PERMIT")
                .param("documentDate", "2026-09-01")
                .with(client(fixture.clientId())))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.data.fileName").value("permit.png"))
        .andExpect(jsonPath("$.data.contentType").value("image/png"));

    mockMvc
        .perform(get("/api/v1/assets/{id}/documents", assetId).with(client(fixture.clientId())))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.length()").value(1));

    mockMvc
        .perform(get("/api/v1/assets/{id}/documents", assetId).with(client(fixture.otherClientId())))
        .andExpect(status().isNotFound());
  }

  @Test
  void unsupportedTypeOversizeAndPendingAssetsAreRejected() throws Exception {
    UUID assetId = seedActiveAsset();
    mockMvc
        .perform(
            multipart("/api/v1/assets/{id}/documents", assetId)
                .file(new MockMultipartFile("file", "odd.bin", "application/octet-stream", NOT_AN_IMAGE))
                .param("documentType", "OTHER")
                .with(client(fixture.clientId())))
        .andExpect(status().isUnsupportedMediaType());

    byte[] big = new byte[11 * 1024 * 1024];
    mockMvc
        .perform(
            multipart("/api/v1/assets/{id}/documents", assetId)
                .file(new MockMultipartFile("file", "big.png", "image/png", big))
                .param("documentType", "PERMIT")
                .with(client(fixture.clientId())))
        .andExpect(status().isPayloadTooLarge());

    UUID pendingId = seedPendingAsset();
    mockMvc
        .perform(
            multipart("/api/v1/assets/{id}/documents", pendingId)
                .file(new MockMultipartFile("file", "ok.png", "image/png", PNG))
                .param("documentType", "PERMIT")
                .with(client(fixture.clientId())))
        .andExpect(status().isConflict());
  }
```

(`seedActiveAsset()` mirrors `seedPendingAsset()` but uses `new Asset(...)` — the existing constructor leaves status `ACTIVE`.)

- [ ] **Step 2: Run the test to verify it fails**

Run: `.\mvnw.cmd test -Dtest=AssetDocumentApiIntegrationTest`
Expected: FAIL — 404.

- [ ] **Step 3: Implement metadata request, response, service, controller**

```java
// request/AssetDocumentMetadataRequest.java
package com.smartdroneinspection.assets.api.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.PastOrPresent;
import jakarta.validation.constraints.Size;
import java.time.LocalDate;

public record AssetDocumentMetadataRequest(
    @NotBlank @Size(max = 64) String documentType,
    @PastOrPresent LocalDate documentDate) {}
```

```java
// response/AssetDocumentResponse.java
package com.smartdroneinspection.assets.api.dto.response;

import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;

public record AssetDocumentResponse(
    UUID id,
    String documentType,
    String fileName,
    String contentType,
    long sizeBytes,
    String checksumSha256,
    LocalDate documentDate,
    Instant createdAt) {}
```

`service/AssetDocumentService.java`:

```java
package com.smartdroneinspection.assets.service;

import com.smartdroneinspection.assets.api.dto.response.AssetDocumentResponse;
import com.smartdroneinspection.assets.domain.Asset;
import com.smartdroneinspection.assets.domain.AssetDocument;
import com.smartdroneinspection.assets.domain.enums.AssetStatus;
import com.smartdroneinspection.assets.repository.AssetRepository;
import com.smartdroneinspection.inspections.spi.EvidenceObjectStore;
import com.smartdroneinspection.shared.exception.BusinessException;
import com.smartdroneinspection.users.UserAccess;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.LocalDate;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

@Service
public class AssetDocumentService {

  static final long MAX_SIZE_BYTES = 10L * 1024 * 1024;
  private static final Set<String> ALLOWED_TYPES =
      Set.of("image/png", "image/jpeg", "image/webp", "application/pdf");

  private final AssetRepository assets;
  private final EvidenceObjectStore objectStore;
  private final UserAccess userAccess;

  public AssetDocumentService(
      AssetRepository assets, EvidenceObjectStore objectStore, UserAccess userAccess) {
    this.assets = assets;
    this.objectStore = objectStore;
    this.userAccess = userAccess;
  }

  @Transactional
  public AssetDocumentResponse upload(
      UUID actorId, UUID assetId, MultipartFile file, String documentType, LocalDate documentDate) {
    Asset asset = requireOwnedAsset(actorId, assetId);
    if (asset.getStatus() != AssetStatus.ACTIVE && asset.getStatus() != AssetStatus.INACTIVE) {
      throw new BusinessException(
          HttpStatus.CONFLICT, "INVALID_STATE", "Documents can only be added to active assets");
    }
    String contentType = file.getContentType() == null ? "" : file.getContentType();
    if (!ALLOWED_TYPES.contains(contentType)) {
      throw new BusinessException(
          HttpStatus.UNSUPPORTED_MEDIA_TYPE, "UNSUPPORTED_MEDIA_TYPE",
          "Allowed types: png, jpeg, webp, pdf");
    }
    byte[] content;
    try {
      content = file.getBytes();
    } catch (IOException ex) {
      throw new BusinessException(HttpStatus.BAD_REQUEST, "VALIDATION_FAILED", "Unreadable file");
    }
    if (content.length > MAX_SIZE_BYTES) {
      throw new BusinessException(
          HttpStatus.PAYLOAD_TOO_LARGE, "PAYLOAD_TOO_LARGE", "Maximum document size is 10 MB");
    }

    String objectKey = "assets/" + assetId + "/documents/" + UUID.randomUUID();
    try {
      objectStore.put(
          objectKey, contentType, content.length, new ByteArrayInputStream(content));
    } catch (IOException ex) {
      throw new BusinessException(
          HttpStatus.BAD_GATEWAY, "STORAGE_UNAVAILABLE", "Object storage is unavailable");
    }

    AssetDocument document =
        asset.addDocument(
            actorId,
            documentType,
            sanitizeFileName(file.getOriginalFilename()),
            contentType,
            content.length,
            sha256(content),
            objectKey,
            documentDate);
    assets.saveAndFlush(asset);
    return toResponse(document);
  }

  @Transactional(readOnly = true)
  public List<AssetDocumentResponse> list(UUID actorId, UUID assetId) {
    Asset asset = requireOwnedAsset(actorId, assetId);
    return asset.getDocuments().stream().map(this::toResponse).toList();
  }

  @Transactional(readOnly = true)
  public DocumentContent open(UUID actorId, UUID assetId, UUID documentId) {
    Asset asset = requireOwnedAsset(actorId, assetId);
    AssetDocument document =
        asset.getDocuments().stream()
            .filter(d -> d.getId().equals(documentId))
            .findFirst()
            .orElseThrow(
                () ->
                    new BusinessException(HttpStatus.NOT_FOUND, "NOT_FOUND", "Document not found"));
    try {
      return new DocumentContent(
          document.getContentType(), document.getFileName(), objectStore.open(document.getObjectKey()));
    } catch (IOException ex) {
      throw new BusinessException(
          HttpStatus.BAD_GATEWAY, "STORAGE_UNAVAILABLE", "Object storage is unavailable");
    }
  }

  private Asset requireOwnedAsset(UUID actorId, UUID assetId) {
    UserAccess.ActiveUser actor =
        userAccess.findActiveUser(actorId)
            .orElseThrow(() -> new BusinessException(HttpStatus.FORBIDDEN, "FORBIDDEN", "User is not active"));
    if (actor.organizationId() == null) {
      throw new BusinessException(HttpStatus.FORBIDDEN, "FORBIDDEN", "No organization scope");
    }
    return assets
        .findDetailedByIdAndOrganizationId(assetId, actor.organizationId())
        .orElseThrow(
            () -> new BusinessException(HttpStatus.NOT_FOUND, "NOT_FOUND", "Asset not found"));
  }

  private static String sanitizeFileName(String name) {
    if (name == null || name.isBlank()) {
      return "document";
    }
    String cleaned = name.replaceAll("[\\\\/\\r\\n]", "_");
    return cleaned.length() > 500 ? cleaned.substring(0, 500) : cleaned;
  }

  private static String sha256(byte[] content) {
    try {
      return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(content));
    } catch (NoSuchAlgorithmException ex) {
      throw new IllegalStateException(ex);
    }
  }

  private AssetDocumentResponse toResponse(AssetDocument d) {
    return new AssetDocumentResponse(
        d.getId(), d.getDocumentType(), d.getFileName(), d.getContentType(), d.getSizeBytes(),
        d.getChecksumSha256(), d.getDocumentDate(), d.getCreatedAt());
  }

  public record DocumentContent(String contentType, String fileName, InputStream stream) {}
}
```

(If `AssetDocument` lacks getters `getId/getDocumentType/getFileName/getContentType/getSizeBytes/getChecksumSha256/getDocumentDate/getCreatedAt/getObjectKey`, add them in the entity's existing style; check `AssetDocumentMappingTest` for the actual property names first.)

`api/AssetDocumentController.java`:

```java
package com.smartdroneinspection.assets.api;

import com.smartdroneinspection.assets.api.dto.response.AssetDocumentResponse;
import com.smartdroneinspection.assets.service.AssetDocumentService;
import com.smartdroneinspection.shared.api.ApiResponse;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;
import org.springframework.core.io.InputStreamResource;
import org.springframework.http.ContentDisposition;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/v1/assets/{assetId}/documents")
public class AssetDocumentController {

  private final AssetDocumentService documents;

  public AssetDocumentController(AssetDocumentService documents) {
    this.documents = documents;
  }

  @PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
  @PreAuthorize("hasAnyRole('CLIENT', 'ADMIN')")
  public ApiResponse<AssetDocumentResponse> upload(
      @AuthenticationPrincipal Jwt jwt,
      @PathVariable UUID assetId,
      @RequestParam("file") MultipartFile file,
      @RequestParam String documentType,
      @RequestParam(required = false) @org.springframework.format.annotation.DateTimeFormat(iso = org.springframework.format.annotation.DateTimeFormat.ISO.DATE) LocalDate documentDate) {
    return ApiResponse.success(
        documents.upload(UUID.fromString(jwt.getSubject()), assetId, file, documentType, documentDate));
  }

  @GetMapping
  @PreAuthorize("hasAnyRole('CLIENT', 'ADMIN', 'SERVICE_MANAGER')")
  public ApiResponse<List<AssetDocumentResponse>> list(
      @AuthenticationPrincipal Jwt jwt, @PathVariable UUID assetId) {
    return ApiResponse.success(documents.list(UUID.fromString(jwt.getSubject()), assetId));
  }

  @GetMapping("/{documentId}/content")
  @PreAuthorize("hasAnyRole('CLIENT', 'ADMIN', 'SERVICE_MANAGER')")
  public ResponseEntity<InputStreamResource> content(
      @AuthenticationPrincipal Jwt jwt,
      @PathVariable UUID assetId,
      @PathVariable UUID documentId) {
    AssetDocumentService.DocumentContent content =
        documents.open(UUID.fromString(jwt.getSubject()), assetId, documentId);
    return ResponseEntity.ok()
        .contentType(MediaType.parseMediaType(content.contentType()))
        .header(
            HttpHeaders.CONTENT_DISPOSITION,
            ContentDisposition.attachment().filename(content.fileName()).build().toString())
        .body(new InputStreamResource(content.stream()));
  }
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `.\mvnw.cmd test -Dtest=AssetDocumentApiIntegrationTest`
Expected: PASS (2 tests).

- [ ] **Step 5: Full verify and commit**

```powershell
.\mvnw.cmd spotless:apply
.\mvnw.cmd verify
git add src/main/java/com/smartdroneinspection/assets src/test/java/com/smartdroneinspection/assets/AssetDocumentApiIntegrationTest.java
git commit -m "feat(assets): add authorized asset document upload"
```

### Task 7: Schedule lifecycle API (T009)

**Files:**
- Create: `backend/src/main/java/com/smartdroneinspection/assets/service/InspectionScheduleService.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/api/InspectionScheduleController.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/api/dto/response/InspectionScheduleResponse.java`
- Test: `backend/src/test/java/com/smartdroneinspection/assets/InspectionScheduleServiceTest.java`

**Interfaces:**
- Consumes: `InspectionScheduleRepository.findByAssetIdOrderByNextDueAt`, `InspectionSchedule.pause()/activate(AssetStatus, ChecklistTemplateStatus)`, Task 3 asset scoping (`UserAccess`), Task 4 `fromSelectedProposal`.
- Produces:
  - Routes: `GET /api/v1/inspection-schedules?assetId=` (CLIENT own org / ADMIN), `POST /api/v1/inspection-schedules/{scheduleId}/pause`, `POST /api/v1/inspection-schedules/{scheduleId}/activate` (CLIENT own org).
  - `InspectionScheduleService`: `List<InspectionScheduleResponse> listForClient(UUID actorId, UUID assetId)`, `InspectionScheduleResponse pause(UUID actorId, UUID scheduleId)`, `InspectionScheduleResponse activate(UUID actorId, UUID scheduleId)`.
  - `InspectionScheduleResponse(id, assetId, checklistTemplateId, frequencyUnit, frequencyInterval, nextDueAt, status)`.
  - Guards: schedule must belong to an asset in actor's org (`NOT_FOUND`); `pause` on `DISABLED` or `activate` on already-`ACTIVE` → 409 `INVALID_STATE`; `activate` validates current `AssetStatus.ACTIVE` and checklist `ACTIVE` via domain `activate(...)` — a `BusinessException(INVALID_STATE)` is thrown when the domain throws `IllegalStateException`.
  - Acceptance (T009): inactive asset or unavailable checklist **cannot become an active schedule** — covered by domain `activate` validation, asserted in Step 1 test.

- [ ] **Step 1: Write the failing test**

`InspectionScheduleServiceTest.java` — a `@SpringBootTest` slice with fixture (same header; autowire `InspectionScheduleRepository schedules`, `AssetRepository assets`, `ChecklistTemplateRepository templates`, `ScheduleProposalRepository proposals`):

```java
  @Test
  void onlyScheduledAssetsAreListedAndPauseActivateRoundTrip() {
    UUID assetId = seedActiveAsset();
    InspectionSchedule schedule =
        schedules.saveAndFlush(
            InspectionSchedule.fromSelectedProposal(
                assetId, fixture.checklistTemplateId(), "MONTH", 3,
                ScheduleProposalService.plusFrequency(
                    java.time.Instant.now(), "MONTH", 3),
                fixture.clientId()));

    assertThat(service.listForClient(fixture.clientId(), assetId)).hasSize(1);

    service.pause(fixture.clientId(), schedule.getId());
    assertThat(schedules.findById(schedule.getId()).orElseThrow().getStatus())
        .isEqualTo(InspectionScheduleStatus.PAUSED);

    service.activate(fixture.clientId(), schedule.getId());
    assertThat(schedules.findById(schedule.getId()).orElseThrow().getStatus())
        .isEqualTo(InspectionScheduleStatus.ACTIVE);
  }

  @Test
  void inactiveAssetCannotProduceAnActiveSchedule() {
    UUID assetId = seedPendingAsset(); // PENDING_REVIEW — not ACTIVE
    Asset asset = assets.findById(assetId).orElseThrow();
    ChecklistTemplate template =
        templates.findById(fixture.checklistTemplateId()).orElseThrow();

    assertThatThrownBy(
            () ->
                InspectionSchedule.fromSelectedProposal(
                    assetId,
                    fixture.checklistTemplateId(),
                    "MONTH",
                    3,
                    ScheduleProposalService.plusFrequency(java.time.Instant.now(), "MONTH", 3),
                    fixture.clientId())
                    .activate(asset.getStatus(), template.getStatus()))
        .isInstanceOf(IllegalStateException.class);
  }

  @Test
  void crossOrgScheduleOperationsAreDenied() {
    UUID assetId = seedActiveAsset();
    InspectionSchedule schedule =
        schedules.saveAndFlush(
            InspectionSchedule.fromSelectedProposal(
                assetId, fixture.checklistTemplateId(), "MONTH", 3,
                ScheduleProposalService.plusFrequency(java.time.Instant.now(), "MONTH", 3),
                fixture.clientId()));

    assertThatThrownBy(() -> service.pause(fixture.otherClientId(), schedule.getId()))
        .isInstanceOf(BusinessException.class);
  }
```

(If `ChecklistTemplate.getStatus()` does not exist, read status through `template.getStatus()` as exposed by the entity or use `ChecklistTemplateStatus.ACTIVE` after `publish()` — the fixture template is already published.)

- [ ] **Step 2: Run the test to verify it fails**

Run: `.\mvnw.cmd test -Dtest=InspectionScheduleServiceTest`
Expected: COMPILATION ERROR — `InspectionScheduleService` does not exist.

- [ ] **Step 3: Implement service and controller**

```java
// service/InspectionScheduleService.java
package com.smartdroneinspection.assets.service;

import com.smartdroneinspection.assets.api.dto.response.InspectionScheduleResponse;
import com.smartdroneinspection.assets.domain.Asset;
import com.smartdroneinspection.assets.domain.ChecklistTemplate;
import com.smartdroneinspection.assets.domain.InspectionSchedule;
import com.smartdroneinspection.assets.domain.enums.InspectionScheduleStatus;
import com.smartdroneinspection.assets.repository.AssetRepository;
import com.smartdroneinspection.assets.repository.ChecklistTemplateRepository;
import com.smartdroneinspection.assets.repository.InspectionScheduleRepository;
import com.smartdroneinspection.shared.exception.BusinessException;
import com.smartdroneinspection.users.UserAccess;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class InspectionScheduleService {

  private final InspectionScheduleRepository schedules;
  private final AssetRepository assets;
  private final ChecklistTemplateRepository templates;
  private final UserAccess userAccess;

  public InspectionScheduleService(
      InspectionScheduleRepository schedules,
      AssetRepository assets,
      ChecklistTemplateRepository templates,
      UserAccess userAccess) {
    this.schedules = schedules;
    this.assets = assets;
    this.templates = templates;
    this.userAccess = userAccess;
  }

  @Transactional(readOnly = true)
  public List<InspectionScheduleResponse> listForClient(UUID actorId, UUID assetId) {
    requireOwnedAsset(actorId, assetId);
    return schedules.findByAssetIdOrderByNextDueAt(assetId).stream().map(this::toResponse).toList();
  }

  @Transactional
  public InspectionScheduleResponse pause(UUID actorId, UUID scheduleId) {
    InspectionSchedule schedule = requireOwnedSchedule(actorId, scheduleId);
    if (schedule.getStatus() != InspectionScheduleStatus.ACTIVE) {
      throw new BusinessException(HttpStatus.CONFLICT, "INVALID_STATE", "Only active schedules can be paused");
    }
    schedule.pause();
    return toResponse(schedules.saveAndFlush(schedule));
  }

  @Transactional
  public InspectionScheduleResponse activate(UUID actorId, UUID scheduleId) {
    InspectionSchedule schedule = requireOwnedSchedule(actorId, scheduleId);
    if (schedule.getStatus() == InspectionScheduleStatus.ACTIVE) {
      throw new BusinessException(HttpStatus.CONFLICT, "INVALID_STATE", "Schedule is already active");
    }
    Asset asset =
        assets.findById(schedule.getAssetId())
            .orElseThrow(() -> new BusinessException(HttpStatus.NOT_FOUND, "NOT_FOUND", "Asset not found"));
    ChecklistTemplate template =
        templates
            .findById(schedule.getChecklistTemplateId())
            .orElseThrow(() -> new BusinessException(HttpStatus.NOT_FOUND, "NOT_FOUND", "Checklist not found"));
    try {
      schedule.activate(asset.getStatus(), template.getStatus());
    } catch (IllegalStateException ex) {
      throw new BusinessException(HttpStatus.CONFLICT, "INVALID_STATE", ex.getMessage());
    }
    return toResponse(schedules.saveAndFlush(schedule));
  }

  private InspectionSchedule requireOwnedSchedule(UUID actorId, UUID scheduleId) {
    InspectionSchedule schedule =
        schedules.findById(scheduleId)
            .orElseThrow(() -> new BusinessException(HttpStatus.NOT_FOUND, "NOT_FOUND", "Schedule not found"));
    requireOwnedAsset(actorId, schedule.getAssetId());
    return schedule;
  }

  private void requireOwnedAsset(UUID actorId, UUID assetId) {
    UserAccess.ActiveUser actor =
        userAccess.findActiveUser(actorId)
            .orElseThrow(() -> new BusinessException(HttpStatus.FORBIDDEN, "FORBIDDEN", "User is not active"));
    if (actor.organizationId() == null) {
      throw new BusinessException(HttpStatus.FORBIDDEN, "FORBIDDEN", "No organization scope");
    }
    assets.findByIdAndOrganizationId(assetId, actor.organizationId())
        .orElseThrow(() -> new BusinessException(HttpStatus.NOT_FOUND, "NOT_FOUND", "Asset not found"));
  }

  private InspectionScheduleResponse toResponse(InspectionSchedule s) {
    return new InspectionScheduleResponse(
        s.getId(), s.getAssetId(), s.getChecklistTemplateId(),
        s.getFrequencyUnit().name(), s.getFrequencyInterval(), s.getNextDueAt(),
        s.getStatus().name());
  }
}
```

(If `InspectionSchedule` lacks `getFrequencyUnit/getFrequencyInterval/getStatus` getters, add them; `getAssetId/getChecklistTemplateId/getNextDueAt` already exist.)

Response record + controller:

```java
// api/dto/response/InspectionScheduleResponse.java
package com.smartdroneinspection.assets.api.dto.response;

import java.time.Instant;
import java.util.UUID;

public record InspectionScheduleResponse(
    UUID id,
    UUID assetId,
    UUID checklistTemplateId,
    String frequencyUnit,
    int frequencyInterval,
    Instant nextDueAt,
    String status) {}
```

```java
// api/InspectionScheduleController.java
package com.smartdroneinspection.assets.api;

import com.smartdroneinspection.assets.api.dto.response.InspectionScheduleResponse;
import com.smartdroneinspection.assets.service.InspectionScheduleService;
import com.smartdroneinspection.shared.api.ApiResponse;
import java.util.List;
import java.util.UUID;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/inspection-schedules")
public class InspectionScheduleController {

  private final InspectionScheduleService schedules;

  public InspectionScheduleController(InspectionScheduleService schedules) {
    this.schedules = schedules;
  }

  @GetMapping
  @PreAuthorize("hasAnyRole('CLIENT', 'ADMIN')")
  public ApiResponse<List<InspectionScheduleResponse>> list(
      @AuthenticationPrincipal Jwt jwt, @RequestParam UUID assetId) {
    return ApiResponse.success(
        schedules.listForClient(UUID.fromString(jwt.getSubject()), assetId));
  }

  @PostMapping("/{scheduleId}/pause")
  @PreAuthorize("hasRole('CLIENT')")
  public ApiResponse<InspectionScheduleResponse> pause(
      @AuthenticationPrincipal Jwt jwt, @PathVariable UUID scheduleId) {
    return ApiResponse.success(schedules.pause(UUID.fromString(jwt.getSubject()), scheduleId));
  }

  @PostMapping("/{scheduleId}/activate")
  @PreAuthorize("hasRole('CLIENT')")
  public ApiResponse<InspectionScheduleResponse> activate(
      @AuthenticationPrincipal Jwt jwt, @PathVariable UUID scheduleId) {
    return ApiResponse.success(schedules.activate(UUID.fromString(jwt.getSubject()), scheduleId));
  }
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `.\mvnw.cmd test -Dtest=InspectionScheduleServiceTest`
Expected: PASS (3 tests).

- [ ] **Step 5: Full verify and commit**

```powershell
.\mvnw.cmd spotless:apply
.\mvnw.cmd verify
git add src/main/java/com/smartdroneinspection/assets src/test/java/com/smartdroneinspection/assets/InspectionScheduleServiceTest.java
git commit -m "feat(assets): add inspection schedule lifecycle api"
```

### Task 8: Durable due-cycle event + producer-side handoff test (T010 + T012)

**Files:**
- Create: `backend/src/main/java/com/smartdroneinspection/assets/events/InspectionScheduleDue.java`
- Create: `backend/src/main/java/com/smartdroneinspection/assets/service/InspectionScheduleDuePublisher.java`
- Modify: `backend/src/main/java/com/smartdroneinspection/shared/config/` — add `SchedulingConfig.java` with `@EnableScheduling` (no `@Scheduled`/`@EnableScheduling` exists yet in `src/main`)
- Test: `backend/src/test/java/com/smartdroneinspection/assets/PeriodicRequestHandoffTest.java`

**Interfaces:**
- Consumes: `InspectionScheduleRepository.findDueForUpdate(InspectionScheduleStatus.ACTIVE, now, Pageable)` (PESSIMISTIC_WRITE — exists), `InspectionSchedule.markGenerated(LocalDate dueCycle, Instant nextDueAt)` (exists), `ScheduleProposalService.plusFrequency(Instant, String, int)` (Task 4), `ApplicationEventPublisher` (pattern: `InspectionReportService`).
- Produces:
  - `record InspectionScheduleDue(UUID organizationId, UUID assetId, UUID scheduleId, UUID checklistTemplateVersionId, LocalDate dueCycle)` in `assets.events` — **frozen contract**, consumed later by WF2 (`flow-handoffs.md`).
  - `InspectionScheduleDuePublisher.publishDueSchedules()` → `int` count published; wired to `@Scheduled(fixedDelayString = "PT1M")`.
  - Behavior: for each due ACTIVE schedule, `dueCycle = nextDueAt` converted to `LocalDate` in `Asia/Ho_Chi_Minh`; publish event; then `markGenerated(dueCycle, plusFrequency(now, unit, interval))` — **mark before considering the cycle done** (same `@Transactional`, flush after both). `lastGeneratedDueCycle` + advancing `nextDueAt` make a second run produce no event for the same cycle (unique identity per contract).

- [ ] **Step 1: Write the failing test**

`PeriodicRequestHandoffTest.java` (`@SpringBootTest`, `@Import(TestcontainersConfiguration.class)`, `@Transactional`, `@RecordApplicationEvents`; autowire `ApplicationEvents applicationEvents`, `InspectionScheduleDuePublisher publisher`, `InspectionScheduleRepository schedules`, `AssetRepository assets`, fixture deps; register a local counter listener instead of ApplicationEvents if `@RecordApplicationEvents` does not capture `ApplicationEventPublisher` events — use this form which works either way):

```java
package com.smartdroneinspection.assets;

import static org.assertj.core.api.Assertions.assertThat;

import com.smartdroneinspection.assets.domain.Asset;
import com.smartdroneinspection.assets.domain.InspectionSchedule;
import com.smartdroneinspection.assets.domain.enums.InspectionScheduleStatus;
import com.smartdroneinspection.assets.events.InspectionScheduleDue;
import com.smartdroneinspection.assets.repository.AssetCategoryRepository;
import com.smartdroneinspection.assets.repository.AssetRepository;
import com.smartdroneinspection.assets.repository.ChecklistTemplateRepository;
import com.smartdroneinspection.assets.repository.InspectionScheduleRepository;
import com.smartdroneinspection.assets.service.InspectionScheduleDuePublisher;
import com.smartdroneinspection.assets.service.ScheduleProposalService;
import com.smartdroneinspection.users.repository.UserRepository;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;
import org.springframework.context.event.EventListener;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.annotation.Import(TestcontainersConfiguration.class);
import org.springframework.transaction.annotation.Transactional;

@SpringBootTest
@Import(TestcontainersConfiguration.class)
@Transactional
class PeriodicRequestHandoffTest {

  @Autowired AssetCategoryRepository categories;
  @Autowired ChecklistTemplateRepository templates;
  @Autowired AssetRepository assets;
  @Autowired UserRepository users;
  @Autowired JdbcTemplate jdbcTemplate;
  @Autowired InspectionScheduleRepository schedules;
  @Autowired InspectionScheduleDuePublisher publisher;

  private final List<InspectionScheduleDue> received = new ArrayList<>();
  private AssetTestFixture.Data fixture;

  @EventListener
  void capture(InspectionScheduleDue event) {
    received.add(event);
  }

  @BeforeEach
  void setUp() {
    received.clear();
    fixture = new AssetTestFixture(categories, templates, assets, users, jdbcTemplate).create();
  }

  private InspectionSchedule dueSchedule() {
    Asset asset =
        assets.saveAndFlush(
            new Asset(
                fixture.organizationId(), fixture.categoryId(), "DUE-" + UUID.randomUUID(),
                "Due asset", null, "District 1", null, null, null, fixture.clientId()));
    return schedules.saveAndFlush(
        InspectionSchedule.fromSelectedProposal(
            asset.getId(),
            fixture.checklistTemplateId(),
            "DAY",
            1,
            Instant.now().minusSeconds(3600), // already due
            fixture.clientId()));
  }

  @Test
  void publishesExactlyOneEventPerDueScheduleCycleAndReplayIsSilent() {
    InspectionSchedule schedule = dueSchedule();
    LocalDate dueCycle =
        schedule.getNextDueAt().atZone(ZoneId.of("Asia/Ho_Chi_Minh")).toLocalDate();

    int firstRun = publisher.publishDueSchedules();
    assertThat(firstRun).isEqualTo(1);
    assertThat(received).hasSize(1);

    InspectionScheduleDue event = received.get(0);
    assertThat(event.assetId()).isEqualTo(schedule.getAssetId());
    assertThat(event.scheduleId()).isEqualTo(schedule.getId());
    assertThat(event.organizationId()).isEqualTo(fixture.organizationId());
    assertThat(event.checklistTemplateVersionId()).isEqualTo(fixture.checklistTemplateId());
    assertThat(event.dueCycle()).isEqualTo(dueCycle);

    // second run: schedule advanced, nothing due — replay publishes nothing
    int secondRun = publisher.publishDueSchedules();
    assertThat(secondRun).isZero();
    assertThat(received).hasSize(1);

    // identity guard on the domain: an older cycle cannot regenerate
    InspectionSchedule reloaded = schedules.findById(schedule.getId()).orElseThrow();
    assertThat(reloaded.getLastGeneratedDueCycle()).isEqualTo(dueCycle);
  }

  @Test
  void pausedAndInactiveSchedulesNeverPublish() {
    InspectionSchedule schedule = dueSchedule();
    schedule.pause();
    schedules.saveAndFlush(schedule);

    assertThat(publisher.publishDueSchedules()).isZero();
    assertThat(received).isEmpty();
  }
}
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `.\mvnw.cmd test -Dtest=PeriodicRequestHandoffTest`
Expected: COMPILATION ERROR — `InspectionScheduleDue`, `InspectionScheduleDuePublisher` do not exist.

- [ ] **Step 3: Implement event, publisher, scheduling config**

```java
// assets/events/InspectionScheduleDue.java
package com.smartdroneinspection.assets.events;

import java.time.LocalDate;
import java.util.UUID;

/**
 * Frozen WF1→WF2 handoff contract (see
 * development/plans/bach/2026-09-22-four-week-mainflow-delivery/flow-handoffs.md).
 * Identity: unique (assetId, scheduleId, dueCycle).
 */
public record InspectionScheduleDue(
    UUID organizationId,
    UUID assetId,
    UUID scheduleId,
    UUID checklistTemplateVersionId,
    LocalDate dueCycle) {}
```

```java
// assets/service/InspectionScheduleDuePublisher.java
package com.smartdroneinspection.assets.service;

import com.smartdroneinspection.assets.domain.Asset;
import com.smartdroneinspection.assets.domain.InspectionSchedule;
import com.smartdroneinspection.assets.domain.enums.InspectionScheduleStatus;
import com.smartdroneinspection.assets.events.InspectionScheduleDue;
import com.smartdroneinspection.assets.repository.AssetRepository;
import com.smartdroneinspection.assets.repository.InspectionScheduleRepository;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.data.domain.PageRequest;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

@Component
public class InspectionScheduleDuePublisher {

  private static final Logger LOG = LoggerFactory.getLogger(InspectionScheduleDuePublisher.class);
  private static final ZoneId BUSINESS_ZONE = ZoneId.of("Asia/Ho_Chi_Minh");
  private static final int BATCH_SIZE = 50;

  private final InspectionScheduleRepository schedules;
  private final AssetRepository assets;
  private final ApplicationEventPublisher events;

  public InspectionScheduleDuePublisher(
      InspectionScheduleRepository schedules,
      AssetRepository assets,
      ApplicationEventPublisher events) {
    this.schedules = schedules;
    this.assets = assets;
    this.events = events;
  }

  @Scheduled(fixedDelayString = "PT1M")
  public void scheduledPublish() {
    int published = publishDueSchedules();
    if (published > 0) {
      LOG.info("Published {} inspection schedule due events", published);
    }
  }

  @Transactional
  public int publishDueSchedules() {
    Instant now = Instant.now();
    List<InspectionSchedule> due =
        schedules.findDueForUpdate(InspectionScheduleStatus.ACTIVE, now, PageRequest.of(0, BATCH_SIZE));
    int published = 0;
    for (InspectionSchedule schedule : due) {
      Asset asset =
          assets.findById(schedule.getAssetId()).orElse(null);
      if (asset == null) {
        continue;
      }
      LocalDate dueCycle = schedule.getNextDueAt().atZone(BUSINESS_ZONE).toLocalDate();
      events.publishEvent(
          new InspectionScheduleDue(
              asset.getOrganizationId(),
              asset.getId(),
              schedule.getId(),
              schedule.getChecklistTemplateId(),
              dueCycle));
      schedule.markGenerated(
          dueCycle,
          ScheduleProposalService.plusFrequency(
              now, schedule.getFrequencyUnit().name(), schedule.getFrequencyInterval()));
      schedules.saveAndFlush(schedule);
      published++;
    }
    return published;
  }
}
```

`shared/config/SchedulingConfig.java`:

```java
package com.smartdroneinspection.shared.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableScheduling;

@Configuration
@EnableScheduling
public class SchedulingConfig {}
```

Idempotency note for the executor: the `@Transactional` publisher publishes via `ApplicationEventPublisher` (synchronous listeners in-process; durable outbox via the existing Modulith publication registry applies to asynchronous/repository-backed listeners — the WF2 consumer side enforces contract-level idempotency as recorded in the T012 deviation). The producer guarantee tested here: **the same schedule never publishes twice for the same `dueCycle`**, because `markGenerated` advances `nextDueAt` in the same transaction.

- [ ] **Step 4: Run the test to verify it passes**

Run: `.\mvnw.cmd test -Dtest=PeriodicRequestHandoffTest`
Expected: PASS (2 tests). If `@EventListener` in a test class does not receive events published by a bean, replace the capture with a registered `ApplicationListener<InspectionScheduleDue>` bean defined via `@TestConfiguration` and autowire it.

- [ ] **Step 5: Full verify and commit**

```powershell
.\mvnw.cmd spotless:apply
.\mvnw.cmd verify
git add src/main/java/com/smartdroneinspection src/test/java/com/smartdroneinspection/assets/PeriodicRequestHandoffTest.java
git commit -m "feat(assets): publish idempotent due-cycle events for wf2 handoff"
```

T012 deviation to record in Report 5 (Task 11): this test is **producer-side** — it asserts event identity/payload/idempotency with an in-process listener standing in for the WF2 consumer; the real consumer integration (one `PERIODIC` request per replayed event) belongs to Quốc's T014/T021.

### Task 9: Frontend screens (T007 + T011 + proposal/review/catalog)

Split into 9a (API/hooks/AssetsPage/routing) and 9b (four new pages).

#### Task 9a: Frontend API layer, hooks, AssetsPage, routing

**Files:**
- Modify: `frontend/src/features/assets/api/assetApi.ts`
- Create: `frontend/src/features/assets/api/catalogApi.ts`
- Create: `frontend/src/features/assets/api/proposalApi.ts`
- Create: `frontend/src/features/assets/api/documentApi.ts`
- Create: `frontend/src/features/assets/hooks/useCatalog.ts`
- Create: `frontend/src/features/assets/hooks/useProposals.ts`
- Create: `frontend/src/features/assets/hooks/useAssetDocuments.ts`
- Modify: `frontend/src/features/assets/pages/AssetsPage.tsx`
- Modify: `frontend/src/app/permissions/accessPolicy.ts`
- Modify: `frontend/src/app/router/router.tsx`
- Test: `frontend/src/features/assets/api/assetsApi.test.ts`

**Interfaces:**
- Consumes: backend routes from Tasks 3–7 (envelope already unwrapped by `shared/api/client.ts` interceptor — see `src/shared/api/apiResponse.ts`), `useToastStore`, existing `useAssets` hook pattern.
- Produces (used by Task 9b):
  - `assetApi`: `list(filters) → {items, page, pageSize, totalCount, totalPages}`, `getById(id) → Asset`, `create(input) → Asset`, `update(id, input) → Asset`, `review(id, {action, note?}) → AssetReviewResponse` (Manager; add even though role gate hides it for Client).
  - `Asset` interface: `id, code, name, description, locationText, latitude, longitude, status, categoryId, createdAt` (replace `address`/`region` with `locationText` to match the backend).
  - `catalogApi`: `listCategories()`, `createCategory(input)`, `updateCategory(id, input)`, `listFrequencies(categoryId)`, `addFrequency(categoryId, input)`, `deleteFrequency(categoryId, frequencyId)`.
  - `proposalApi`: `listForAsset(assetId) → Proposal[]`, `review(proposalId, input)`, `select(proposalId) → Proposal`, `listForManager(assetId) → Proposal[]`.
  - `Proposal` interface: `id, assetId, checklistTemplateId, frequencyUnit, frequencyInterval, status, managerNote`.
  - `documentApi`: `list(assetId)`, `upload(assetId, file, documentType, documentDate)` (FormData), `contentUrl(assetId, documentId)` → string path for `<a href>` download.
  - Query keys: `assetKeys` (existing) + `catalogKeys = ['catalog']`, `proposalKeys(assetId) = ['proposals', assetId]`, `documentKeys(assetId) = ['asset-documents', assetId]`.
  - `accessPolicy.ts`: `SECTION_ROLE_ACCESS.operations.assets` → `['SERVICE_MANAGER']`.
  - Router wiring is done in Task 9b after the four page files exist, so the build never references missing modules.

- [ ] **Step 1: Write the failing API test**

`frontend/src/features/assets/api/assetsApi.test.ts` (Vitest; mock `@/shared/api/client` module — follow `src/shared/api/apiResponse.test.ts` style):

```typescript
import { describe, expect, it, vi, beforeEach } from 'vitest';

vi.mock('@/shared/api/client', () => ({
  api: { get: vi.fn(), post: vi.fn(), put: vi.fn() },
}));

import { api } from '@/shared/api/client';
import { assetApi } from './assetApi';

describe('assetApi', () => {
  beforeEach(() => vi.clearAllMocks());

  it('lists assets and returns the paged payload', async () => {
    const page = {
      items: [],
      page: 1,
      pageSize: 20,
      totalCount: 0,
      totalPages: 0,
    };
    vi.mocked(api.get).mockResolvedValue({ data: page });

    await expect(assetApi.list({ page: 1, pageSize: 20 })).resolves.toEqual(page);
    expect(api.get).toHaveBeenCalledWith('/assets', {
      params: { page: 1, pageSize: 20 },
    });
  });

  it('creates an asset without sending organizationId', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: { id: 'a1', status: 'PENDING_REVIEW' } });

    await assetApi.create({
      code: 'BR-1',
      name: 'Bridge',
      categoryId: 'c1',
      locationText: 'District 1',
    });

    const body = vi.mocked(api.post).mock.calls[0][1] as Record<string, unknown>;
    expect(body).not.toHaveProperty('organizationId');
    expect(api.post).toHaveBeenCalledWith('/assets', body);
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run (in `frontend/`): `npm run test -- src/features/assets/api/assetsApi.test.ts`
Expected: FAIL — `create` has no `locationText` / test module shape differs.

- [ ] **Step 3: Implement the API modules**

`assetApi.ts` — replace the file (aligns `Asset` with the backend `AssetResponse`, adds update/review):

```typescript
import { api } from '@/shared/api/client';

export interface Asset {
  id: string;
  code: string;
  name: string;
  description: string | null;
  locationText: string;
  latitude: number | null;
  longitude: number | null;
  status: 'PENDING_REVIEW' | 'ACTIVE' | 'INACTIVE' | 'REJECTED' | 'RETIRED';
  categoryId: string;
  createdAt: string;
}

export interface AssetListFilters {
  page?: number;
  pageSize?: number;
  search?: string | undefined;
}

export interface CreateAssetInput {
  name: string;
  code: string;
  description?: string | null;
  categoryId: string;
  locationText: string;
  latitude?: number | null;
  longitude?: number | null;
  ownershipInformation?: string | null;
}

export interface UpdateAssetInput {
  name?: string;
  description?: string | null;
  locationText?: string;
  latitude?: number | null;
  longitude?: number | null;
  ownershipInformation?: string | null;
}

export interface AssetPage {
  items: Asset[];
  page: number;
  pageSize: number;
  totalCount: number;
  totalPages: number;
}

export interface AssetReviewResponse {
  assetId: string;
  status: string;
  proposalCount: number;
}

export const assetKeys = {
  all: ['assets'] as const,
  lists: () => [...assetKeys.all, 'list'] as const,
  list: (filters: AssetListFilters) => [...assetKeys.lists(), filters] as const,
  detail: (id: string) => [...assetKeys.all, 'detail', id] as const,
};

export const assetApi = {
  list: (filters: AssetListFilters) =>
    api.get<AssetPage>('/assets', { params: filters }).then((r) => r.data),

  getById: (id: string) => api.get<Asset>(`/assets/${id}`).then((r) => r.data),

  create: (input: CreateAssetInput) =>
    api.post<Asset>('/assets', input).then((r) => r.data),

  update: (id: string, input: UpdateAssetInput) =>
    api.put<Asset>(`/assets/${id}`, input).then((r) => r.data),

  review: (id: string, input: { action: 'APPROVE' | 'REJECT'; note?: string }) =>
    api.post<AssetReviewResponse>(`/assets/${id}/review`, input).then((r) => r.data),
};
```

`catalogApi.ts`:

```typescript
import { api } from '@/shared/api/client';

export interface Category {
  id: string;
  code: string;
  name: string;
  description: string | null;
  active: boolean;
}

export interface SuggestedFrequency {
  id: string;
  frequencyUnit: 'DAY' | 'WEEK' | 'MONTH' | 'YEAR';
  frequencyInterval: number;
  sortOrder: number;
}

export const catalogKeys = {
  all: ['catalog'] as const,
  categories: () => [...catalogKeys.all, 'categories'] as const,
  frequencies: (categoryId: string) =>
    [...catalogKeys.all, 'frequencies', categoryId] as const,
};

export const catalogApi = {
  listCategories: () => api.get<Category[]>('/asset-categories').then((r) => r.data),
  createCategory: (input: { code: string; name: string; description?: string }) =>
    api.post<Category>('/asset-categories', input).then((r) => r.data),
  updateCategory: (
    id: string,
    input: { code: string; name: string; description?: string },
  ) => api.put<Category>(`/asset-categories/${id}`, input).then((r) => r.data),
  listFrequencies: (categoryId: string) =>
    api
      .get<SuggestedFrequency[]>(`/asset-categories/${categoryId}/suggested-frequencies`)
      .then((r) => r.data),
  addFrequency: (
    categoryId: string,
    input: { frequencyUnit: string; frequencyInterval: number },
  ) =>
    api
      .post<SuggestedFrequency>(
        `/asset-categories/${categoryId}/suggested-frequencies`,
        input,
      )
      .then((r) => r.data),
  deleteFrequency: (categoryId: string, frequencyId: string) =>
    api
      .delete<void>(
        `/asset-categories/${categoryId}/suggested-frequencies/${frequencyId}`,
      )
      .then((r) => r.data),
};
```

`proposalApi.ts`:

```typescript
import { api } from '@/shared/api/client';

export interface Proposal {
  id: string;
  assetId: string;
  checklistTemplateId: string;
  frequencyUnit: 'DAY' | 'WEEK' | 'MONTH' | 'YEAR';
  frequencyInterval: number;
  status:
    | 'GENERATED'
    | 'MANAGER_APPROVED'
    | 'MANAGER_REJECTED'
    | 'CLIENT_SELECTED'
    | 'SUPERSEDED';
  managerNote: string | null;
}

export const proposalKeys = {
  all: ['proposals'] as const,
  forAsset: (assetId: string) => [...proposalKeys.all, assetId] as const,
};

export const proposalApi = {
  listForAsset: (assetId: string) =>
    api
      .get<Proposal[]>('/schedule-proposals', { params: { assetId } })
      .then((r) => r.data),
  review: (
    proposalId: string,
    input: {
      action: 'APPROVE' | 'REJECT';
      note?: string;
      frequencyUnit?: string;
      frequencyInterval?: number;
    },
  ) =>
    api
      .post<Proposal>(`/schedule-proposals/${proposalId}/review`, input)
      .then((r) => r.data),
  select: (proposalId: string) =>
    api.post<Proposal>(`/schedule-proposals/${proposalId}/select`).then((r) => r.data),
};
```

`documentApi.ts`:

```typescript
import { api } from '@/shared/api/client';

export interface AssetDocument {
  id: string;
  documentType: string;
  fileName: string;
  contentType: string;
  sizeBytes: number;
  checksumSha256: string;
  documentDate: string | null;
  createdAt: string;
}

export const documentKeys = {
  all: ['asset-documents'] as const,
  forAsset: (assetId: string) => [...documentKeys.all, assetId] as const,
};

export const documentApi = {
  list: (assetId: string) =>
    api.get<AssetDocument[]>(`/assets/${assetId}/documents`).then((r) => r.data),
  upload: (assetId: string, file: File, documentType: string, documentDate?: string) => {
    const form = new FormData();
    form.append('file', file);
    form.append('documentType', documentType);
    if (documentDate) form.append('documentDate', documentDate);
    return api
      .post<AssetDocument>(`/assets/${assetId}/documents`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((r) => r.data);
  },
  contentPath: (assetId: string, documentId: string) =>
    `/api/v1/assets/${assetId}/documents/${documentId}/content`,
};
```

- [ ] **Step 4: Hooks + AssetsPage updates**

`useCatalog.ts` / `useProposals.ts` / `useAssetDocuments.ts` follow the `useAssets.ts` pattern exactly (`useQuery` with the keys above, `useMutation` + `queryClient.invalidateQueries` + `showToast`). Example `useProposals.ts`:

```typescript
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useToastStore } from '@/shared/ui/Toast';
import { proposalApi, proposalKeys, type Proposal } from '../api/proposalApi';

export function useProposals(assetId: string) {
  return useQuery({
    queryKey: proposalKeys.forAsset(assetId),
    queryFn: () => proposalApi.listForAsset(assetId),
  });
}

export function useSelectProposal(assetId: string) {
  const queryClient = useQueryClient();
  const showToast = useToastStore((s) => s.showToast);

  return useMutation({
    mutationFn: (proposalId: string) => proposalApi.select(proposalId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: proposalKeys.forAsset(assetId) });
      void queryClient.invalidateQueries({ queryKey: ['assets'] });
      showToast('Schedule selected');
    },
  });
}
```

(`useCatalog.ts` exposes `useCategories`, `useFrequencies(categoryId)`, `useAddFrequency`, `useDeleteFrequency`, `useCreateCategory`; `useAssetDocuments.ts` exposes `useAssetDocuments(assetId)`, `useUploadDocument(assetId)` — same shape.)

`AssetsPage.tsx` modifications (T007):
- Replace removed `address`/`region` references with `locationText` (the `Asset` type changed); the create form field label becomes "Location" bound to `locationText`.
- Status chip per `Asset.status`: `PENDING_REVIEW` → "Awaiting review" (color `warning`), `ACTIVE` → `success`, `REJECTED` → `error`, `INACTIVE`/`RETIRED` → `default`.
- Create form success toast text: "Asset submitted for review".
- Detail drawer: document list + upload form via `useAssetDocuments`/`useUploadDocument` (shown when status is `ACTIVE` or `INACTIVE`; hide upload otherwise with helper text "Available after review").
- For `PENDING_REVIEW` assets owned by the Client, add buttons "View proposed schedules" → navigate to `/client/schedule-proposals/{id}` and "Schedules" → `/client/inspection-schedules/{id}` (only for `ACTIVE`).

- [ ] **Step 5: accessPolicy role change**

`accessPolicy.ts` — one change:

```typescript
  operations: {
    dashboard: ['SERVICE_MANAGER', 'INSPECTOR', 'MAINTENANCE_ENGINEER'],
    assets: ['SERVICE_MANAGER'],
    ...
```

Router wiring (lazy imports, new section ids, `SECTION_LABELS`/`SECTION_ROLE_ACCESS` entries) happens in **Task 9b, after the four page files exist**, so the build never references missing modules.

- [ ] **Step 6: Run tests**

Run: `npm run test -- src/features/assets/api/assetsApi.test.ts` → PASS.
(`npm run lint && npm run build` are run at the end of 9b, when the router additions land.)

- [ ] **Step 7: Commit**

```powershell
git add src/features/assets src/app/permissions/accessPolicy.ts src/app/router/router.tsx
git commit -m "feat(assets): wire client asset screens to live apis"
```

#### Task 9b: Four new pages + router wiring

**Files:**
- Create: `frontend/src/features/assets/pages/ScheduleProposalsPage.tsx`
- Create: `frontend/src/features/assets/pages/InspectionSchedulesPage.tsx`
- Create: `frontend/src/features/assets/pages/AssetReviewPage.tsx`
- Create: `frontend/src/features/assets/pages/AssetCatalogPage.tsx`
- Modify: `frontend/src/app/router/router.tsx` (lazy imports + routes)
- Modify: `frontend/src/app/permissions/accessPolicy.ts` (new section ids)
- Test: `frontend/src/features/assets/pages/ScheduleProposalsPage.test.tsx`
- Test: `frontend/src/features/assets/pages/AssetReviewPage.test.tsx`

**Interfaces:**
- Consumes: Task 9a (`proposalApi/useProposals/useSelectProposal`, `assetApi/useAssets/review`, `catalogApi/useCatalog`, `documentApi`), `useToastStore`, MUI components, `react-router-dom` `useParams/useNavigate` (follow `AssetsPage` imports).
- Produces: routes `/client/schedule-proposals/:assetId`, `/client/inspection-schedules/:assetId`, `/operations/asset-review`, `/admin/asset-catalog`.

- [ ] **Step 1: Write the failing page tests**

`ScheduleProposalsPage.test.tsx` (Vitest + RTL; mock `../api/proposalApi` and `react-router-dom` `useParams`):

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const select = vi.fn();
const listForAsset = vi.fn();

vi.mock('../api/proposalApi', () => ({
  proposalApi: { listForAsset: (...a: unknown[]) => listForAsset(...a), select: (...a: unknown[]) => select(...a) },
  proposalKeys: { forAsset: (id: string) => ['proposals', id] },
}));

vi.mock('../hooks/useProposals', () => ({
  useProposals: () => ({
    data: [
      { id: 'p1', assetId: 'a1', checklistTemplateId: 'c1', frequencyUnit: 'MONTH', frequencyInterval: 3, status: 'MANAGER_APPROVED', managerNote: 'Standard' },
      { id: 'p2', assetId: 'a1', checklistTemplateId: 'c1', frequencyUnit: 'YEAR', frequencyInterval: 1, status: 'MANAGER_APPROVED', managerNote: null },
    ],
    isLoading: false,
  }),
  useSelectProposal: () => ({ mutate: select, isPending: false }),
}));

import ScheduleProposalsPage from './ScheduleProposalsPage';

describe('ScheduleProposalsPage', () => {
  beforeEach(() => vi.clearAllMocks());

  it('renders both approved options and selects one', async () => {
    render(<ScheduleProposalsPage />);
    expect(screen.getByText('Every 3 month(s)')).toBeInTheDocument();
    expect(screen.getByText('Every 1 year(s)')).toBeInTheDocument();

    await userEvent.click(screen.getAllByRole('button', { name: /select/i })[0]);
    expect(select).toHaveBeenCalledWith('p1');
  });
});
```

`AssetReviewPage.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const review = vi.fn();

vi.mock('../api/assetApi', () => ({
  assetApi: { review: (...a: unknown[]) => review(...a), list: vi.fn() },
  assetKeys: { all: ['assets'], lists: () => ['assets', 'list'], list: (f: unknown) => ['assets', 'list', f], detail: (id: string) => ['assets', 'detail', id] },
}));

vi.mock('../hooks/useAssets', () => ({
  useAssets: () => ({
    data: {
      items: [
        { id: 'a1', code: 'BR-1', name: 'North bridge', description: null, locationText: 'District 1', latitude: null, longitude: null, status: 'PENDING_REVIEW', categoryId: 'c1', createdAt: '2026-09-25T00:00:00Z' },
      ],
      page: 1, pageSize: 20, totalCount: 1, totalPages: 1,
    },
    isLoading: false,
  }),
  useReviewAsset: () => ({ mutate: review, isPending: false }),
}));

import AssetReviewPage from './AssetReviewPage';

describe('AssetReviewPage', () => {
  beforeEach(() => vi.clearAllMocks());

  it('lists pending assets and approves one', async () => {
    render(<AssetReviewPage />);
    expect(screen.getByText('North bridge')).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: /approve/i }));
    expect(review).toHaveBeenCalledWith({ id: 'a1', input: { action: 'APPROVE' } });
  });
});
```

(If the hooks you wrote in 9a expose different mutation argument shapes, align the **implementation** to these tests — `useReviewAsset().mutate({ id, input })` is the contract; add that hook to `useAssets.ts` in this task.)

- [ ] **Step 2: Run tests to verify they fail**

Run: `npm run test -- src/features/assets/pages`
Expected: FAIL — page modules do not exist.

- [ ] **Step 3: Implement `ScheduleProposalsPage`**

```tsx
import { Button, Card, CardContent, CircularProgress, Container, Typography } from '@mui/material';
import { useParams } from 'react-router-dom';
import { useProposals, useSelectProposal } from '../hooks/useProposals';

const UNIT_LABEL: Record<string, string> = { DAY: 'day', WEEK: 'week', MONTH: 'month', YEAR: 'year' };

export default function ScheduleProposalsPage() {
  const { assetId = '' } = useParams();
  const { data: proposals, isLoading } = useProposals(assetId);
  const select = useSelectProposal(assetId);

  if (isLoading) return <CircularProgress />;
  if (!proposals?.length) {
    return (
      <Container maxWidth="md">
        <Typography variant="h5">Proposed schedules</Typography>
        <Typography color="text.secondary">
          No approved schedule proposals yet. Your Service Manager reviews the platform
          suggestions first.
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="md">
      <Typography variant="h5" gutterBottom>
        Proposed schedules — choose one
      </Typography>
      {proposals.map((p) => (
        <Card key={p.id} sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6">
              Every {p.frequencyInterval} {UNIT_LABEL[p.frequencyUnit]}
              {p.frequencyInterval > 1 ? 's' : ''}
            </Typography>
            {p.managerNote && <Typography color="text.secondary">{p.managerNote}</Typography>}
            <Button
              variant="contained"
              sx={{ mt: 1 }}
              disabled={select.isPending}
              onClick={() => select.mutate(p.id)}
            >
              Select
            </Button>
          </CardContent>
        </Card>
      ))}
    </Container>
  );
}
```

- [ ] **Step 4: Implement `InspectionSchedulesPage`**

Reads `useAssets` detail + a `useSchedules(assetId)` hook (add to `useAssets.ts`: wraps `assetApi`-adjacent call — first add `scheduleApi` methods `list(assetId)`, `pause(id)`, `activate(id)` in `assetApi.ts` hitting `/inspection-schedules`):

```tsx
import { Button, Card, CardContent, CircularProgress, Container, Typography } from '@mui/material';
import { useParams } from 'react-router-dom';
import { useSchedules, useToggleSchedule } from '../hooks/useSchedules';

export default function InspectionSchedulesPage() {
  const { assetId = '' } = useParams();
  const { data: schedules, isLoading } = useSchedules(assetId);
  const toggle = useToggleSchedule(assetId);

  if (isLoading) return <CircularProgress />;

  return (
    <Container maxWidth="md">
      <Typography variant="h5" gutterBottom>
        Inspection schedules
      </Typography>
      {!schedules?.length && (
        <Typography color="text.secondary">No schedule selected for this asset yet.</Typography>
      )}
      {schedules?.map((s) => (
        <Card key={s.id} sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6">{s.status}</Typography>
            <Typography color="text.secondary">
              Every {s.frequencyInterval} {s.frequencyUnit}(s) · next due{' '}
              {new Date(s.nextDueAt).toLocaleDateString()}
            </Typography>
            <Button
              variant="outlined"
              sx={{ mt: 1 }}
              disabled={toggle.isPending}
              onClick={() => toggle.mutate(s)}
            >
              {s.status === 'ACTIVE' ? 'Pause' : 'Activate'}
            </Button>
          </CardContent>
        </Card>
      ))}
    </Container>
  );
}
```

(`useSchedules`/`useToggleSchedule` live in a new `hooks/useSchedules.ts` with the same mutation/invalidate/toast pattern; `toggle.mutate(s)` calls `pause` when `s.status === 'ACTIVE'` else `activate`.)

- [ ] **Step 5: Implement `AssetReviewPage` (Manager)**

```tsx
import { Alert, Button, Card, CardContent, CircularProgress, Container, Stack, TextField, Typography } from '@mui/material';
import { useState } from 'react';
import { useAssets, useReviewAsset } from '../hooks/useAssets';

export default function AssetReviewPage() {
  const { data: page, isLoading } = useAssets({ page: 1, pageSize: 50 });
  const review = useReviewAsset();
  const [notes, setNotes] = useState<Record<string, string>>({});
  const pending = (page?.items ?? []).filter((a) => a.status === 'PENDING_REVIEW');

  if (isLoading) return <CircularProgress />;

  return (
    <Container maxWidth="md">
      <Typography variant="h5" gutterBottom>
        Asset review queue
      </Typography>
      {!pending.length && <Alert severity="info">Nothing awaiting review.</Alert>}
      {pending.map((asset) => (
        <Card key={asset.id} sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6">
              {asset.name} ({asset.code})
            </Typography>
            <Typography color="text.secondary">{asset.locationText}</Typography>
            <TextField
              fullWidth
              size="small"
              label="Manager note"
              sx={{ mt: 1 }}
              value={notes[asset.id] ?? ''}
              onChange={(e) => setNotes({ ...notes, [asset.id]: e.target.value })}
            />
            <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
              <Button
                variant="contained"
                disabled={review.isPending}
                onClick={() => review.mutate({ id: asset.id, input: { action: 'APPROVE', note: notes[asset.id] } })}
              >
                Approve
              </Button>
              <Button
                color="error"
                variant="outlined"
                disabled={review.isPending}
                onClick={() => review.mutate({ id: asset.id, input: { action: 'REJECT', note: notes[asset.id] } })}
              >
                Reject
              </Button>
            </Stack>
          </CardContent>
        </Card>
      ))}
    </Container>
  );
}
```

(After `APPROVE` succeeds, show the proposal count from the `AssetReviewResponse` in the success toast: extend `useReviewAsset` `onSuccess` to `showToast(\`Approved — \${data.proposalCount} proposal(s) generated\`)`, and list approved assets below the queue with a "Review proposals" link to a manager proposal list — reuse `ScheduleProposalsPage` with a manager mode **only if trivial**; otherwise link to the existing per-asset proposal review through `AssetReviewPage`'s own list calling `proposalApi.listForAsset`. Ship the approve/reject queue first; proposal fine-review UI can be the `proposalApi.review` call wired to buttons next to each `GENERATED` proposal loaded for approved assets via `useProposals` with the manager list. Keep this section minimal: Manager sees proposals for a selected approved asset and can approve/reject/edit-interval them.)

- [ ] **Step 6: Implement `AssetCatalogPage` (Admin)**

Two panels: category table (`catalogApi.listCategories` + inline create form code/name/description) and, for the selected category, the suggested-frequency chips (`useFrequencies`) with add (`unit` select + interval number input) and delete buttons. Follow `AssetsPage` table/form style; wire `useCreateCategory`, `useAddFrequency`, `useDeleteFrequency` from `useCatalog.ts`. Validation: interval min 1 (MUI `inputProps={{ min: 1 }}`), unit from the four enum values.

- [ ] **Step 7: Router + section ids**

Add to `accessPolicy.ts`:

```typescript
export const SECTION_IDS = [
  'dashboard', 'assets', 'asset-catalog', 'asset-review',
  'schedule-proposals', 'inspection-schedules',
  'inspections', 'reports', 'maintenance',
] as const;

export const SECTION_LABELS: Record<SectionId, string> = {
  // ...existing...
  'asset-catalog': 'Asset catalog',
  'asset-review': 'Asset review',
  'schedule-proposals': 'Proposed schedules',
  'inspection-schedules': 'Schedules',
};
```

and matching `SECTION_ROLE_ACCESS` entries: `admin['asset-catalog'] = ['ADMIN']`, `operations['asset-review'] = ['SERVICE_MANAGER']`, `client['schedule-proposals'] = ['CLIENT']`, `client['inspection-schedules'] = ['CLIENT']`; all other portals' new sections `[]`.

`router.tsx`: four `lazy()` imports (shown in 9a's removed draft) + register each section route in its portal map following the `assets` entry shape. `ScheduleProposalsPage`/`InspectionSchedulesPage` read `assetId` from route params — register them as `schedule-proposals/:assetId` (and adjust `SECTION_LABELS` link generation: links to these pages are produced by `AssetsPage` buttons with explicit `navigate(...)` paths, not by the section nav; keep them out of the visible portal nav lists if the nav builder only lists `SECTION_IDS` — filter the four new ids from the sidebar the same way any non-nav sections are handled).

- [ ] **Step 8: Run tests, lint, build**

```powershell
npm run test
npm run lint
npm run build
```
Expected: all PASS.

- [ ] **Step 9: Commit**

```powershell
git add src/features/assets src/app
git commit -m "feat(assets): add proposal, review, schedule, and catalog screens"
```

### Task 10: Full WF1 workflow integration + negative-scope sweep (T013)

**Files:**
- Create: `backend/src/test/java/com/smartdroneinspection/assets/AssetWorkflowIntegrationTest.java`

**Interfaces:**
- Consumes: every route and behavior from Tasks 2–8; `AssetTestFixture`; JWT helpers `admin/client/manager`.
- Produces: the T013 evidence run — full happy path + negative scope at every endpoint; this is the test cited in Report 5 `03-features/feature-1.md`.

- [ ] **Step 1: Write the integration test**

Same `@SpringBootTest/@Import(TestcontainersConfiguration.class)/@Transactional` header; `@RecordApplicationEvents` + `@Autowired ApplicationEvents applicationEvents` for the due-event assertion; autowire `InspectionScheduleDuePublisher publisher`, `ScheduleProposalRepository proposals`, `InspectionScheduleRepository schedules` plus fixture deps. JWT helpers: `admin`, `client`, `manager` (as in Task 2).

```java
  @Test
  void fullWf1FlowFromAssetCreationToDueEvent() throws Exception {
    frequencies.saveAndFlush(new CategoryFrequencySuggestion(fixture.categoryId(), "MONTH", 3, 0));
    frequencies.saveAndFlush(new CategoryFrequencySuggestion(fixture.categoryId(), "YEAR", 1, 1));

    // 1. Client creates asset → PENDING_REVIEW
    MvcResult created =
        mockMvc
            .perform(post("/api/v1/assets").with(client(fixture.clientId()))
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"code\":\"WF1-FULL\",\"name\":\"Full flow bridge\","
                    + "\"categoryId\":\"" + fixture.categoryId() + "\",\"locationText\":\"District 1\"}"))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.data.status").value("PENDING_REVIEW"))
            .andReturn();
    UUID assetId = uuid(created, "$.data.id");

    // 2. Manager approves → ACTIVE + 2 proposals
    mockMvc
        .perform(post("/api/v1/assets/{id}/review", assetId).with(manager(fixture.managerId()))
            .contentType(MediaType.APPLICATION_JSON).content("{\"action\":\"APPROVE\"}"))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.data.proposalCount").value(2));

    // 3. Manager approves both proposals
    for (ScheduleProposal p : proposals.findByAssetIdOrderByCreatedAtAsc(assetId)) {
      mockMvc
          .perform(post("/api/v1/schedule-proposals/{id}/review", p.getId())
              .with(manager(fixture.managerId()))
              .contentType(MediaType.APPLICATION_JSON).content("{\"action\":\"APPROVE\"}"))
          .andExpect(status().isOk());
    }

    // 4. Client selects one → ACTIVE schedule, sibling SUPERSEDED
    List<ScheduleProposal> approved = proposals.findByAssetIdOrderByCreatedAtAsc(assetId);
    mockMvc
        .perform(post("/api/v1/schedule-proposals/{id}/select", approved.get(0).getId())
            .with(client(fixture.clientId())))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.data.status").value("CLIENT_SELECTED"));

    assertThat(schedules.findByAssetIdOrderByNextDueAt(assetId)).hasSize(1);

    // 5. Due event publishes once with contract payload
    long eventsBefore = applicationEvents.stream(InspectionScheduleDue.class).count();
    // force due: set next_due_at into the past
    jdbcTemplate.update(
        "UPDATE inspection_schedules SET next_due_at = now() - interval '1 hour' WHERE asset_id = ?",
        assetId);
    schedules.flush();
    assertThat(publisher.publishDueSchedules()).isEqualTo(1);
    assertThat(publisher.publishDueSchedules()).isZero();
    long eventsAfter = applicationEvents.stream(InspectionScheduleDue.class).count();
    assertThat(eventsAfter - eventsBefore).isEqualTo(1);

    InspectionScheduleDue due =
        applicationEvents.stream(InspectionScheduleDue.class)
            .reduce((first, second) -> second) // latest
            .orElseThrow();
    assertThat(due.organizationId()).isEqualTo(fixture.organizationId());
    assertThat(due.assetId()).isEqualTo(assetId);
    assertThat(due.checklistTemplateVersionId()).isEqualTo(fixture.checklistTemplateId());
  }

  @Test
  void negativeScopeSweepAcrossEveryWf1Endpoint() throws Exception {
    // seed: own pending asset, other-org approved asset with one approved proposal
    UUID ownPending = seedPendingAsset();
    UUID otherAssetId =
        assets.saveAndFlush(
            new Asset(fixture.otherOrganizationId, fixture.categoryId(), "OTH-" + UUID.randomUUID(),
                "Other org asset", null, "District 9", null, null, null, fixture.otherClientId()))
            .getId();
    ScheduleProposal otherProposal =
        ScheduleProposal.generate(otherAssetId, fixture.checklistTemplateId(), "MONTH", 3);
    otherProposal.managerApprove(null, fixture.managerId());
    otherProposal = proposals.saveAndFlush(otherProposal);

    // CLIENT cannot review assets
    mockMvc.perform(post("/api/v1/assets/{id}/review", ownPending).with(client(fixture.clientId()))
        .contentType(MediaType.APPLICATION_JSON).content("{\"action\":\"APPROVE\"}"))
        .andExpect(status().isForbidden());

    // MANAGER cannot create assets or manage catalog
    mockMvc.perform(post("/api/v1/assets").with(manager(fixture.managerId()))
        .contentType(MediaType.APPLICATION_JSON).content(
            "{\"code\":\"M1\",\"name\":\"x\",\"categoryId\":\"" + fixture.categoryId() + "\",\"locationText\":\"x\"}"))
        .andExpect(status().isForbidden());
    mockMvc.perform(post("/api/v1/asset-categories").with(manager(fixture.managerId()))
        .contentType(MediaType.APPLICATION_JSON).content("{\"code\":\"c\",\"name\":\"c\"}"))
        .andExpect(status().isForbidden());

    // ADMIN cannot select proposals (Client-only action)
    mockMvc.perform(post("/api/v1/schedule-proposals/{id}/select", otherProposal.getId())
        .with(admin(fixture.adminId())))
        .andExpect(status().isForbidden());

    // cross-org: other-org asset invisible to our client everywhere
    mockMvc.perform(get("/api/v1/assets/{id}", otherAssetId).with(client(fixture.clientId())))
        .andExpect(status().isNotFound());
    mockMvc.perform(get("/api/v1/assets/{id}/documents", otherAssetId).with(client(fixture.clientId())))
        .andExpect(status().isNotFound());
    mockMvc.perform(post("/api/v1/schedule-proposals/{id}/select", otherProposal.getId())
        .with(client(fixture.clientId())))
        .andExpect(status().isNotFound());
    mockMvc.perform(post("/api/v1/assets/{id}/review", otherAssetId).with(manager(fixture.managerId()))
        .contentType(MediaType.APPLICATION_JSON).content("{\"action\":\"APPROVE\"}"))
        .andExpect(status().isOk()); // manager review is platform-scoped, not org-scoped —
    // NOTE: this last expectation documents the intended rule. If the product decision is that
    // SERVICE_MANAGER reviews are platform-wide, keep isOk(); if they must be organization-
    // scoped, change AssetReviewService to resolve manager organization and return 404 for
    // foreign assets, and flip this assertion to isNotFound(). Resolve deliberately and record
    // the choice in Report 3 — the spec states Manager is a platform role (org = null in
    // fixtures), so isOk() is correct for the current model.

    // unauthenticated → 401 problem detail
    mockMvc.perform(get("/api/v1/assets"))
        .andExpect(status().isUnauthorized())
        .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_PROBLEM_JSON));
  }

  private UUID uuid(MvcResult result, String expression) {
    return UUID.fromString(
        com.jayway.jsonpath.JsonPath.read(result.getResponse().getContentAsString(), expression)
            .toString());
  }
```

(Add `@Autowired JdbcTemplate jdbcTemplate` and `@Autowired CategoryFrequencySuggestionRepository frequencies` to the class.)

- [ ] **Step 2: Run the test to verify it passes**

Run: `.\mvnw.cmd test -Dtest=AssetWorkflowIntegrationTest`
Expected: PASS (2 tests). If the platform-vs-org manager scope assertion fails, resolve per the inline note and keep Report 3 aligned (documented in Task 11).

- [ ] **Step 3: Full verification**

```powershell
.\mvnw.cmd spotless:apply
.\mvnw.cmd verify
```
Expected: PASS — includes Modulith boundary test (assets → `inspections.spi` named interface is allowed) and JaCoCo gate.

- [ ] **Step 4: Commit**

```powershell
git add src/test/java/com/smartdroneinspection/assets/AssetWorkflowIntegrationTest.java
git commit -m "test(assets): cover full wf1 workflow and negative scope"
```

### Task 11: Documentation sync (Report 3, flows, data model, plans, Report 5)

All edits are in the **SmartDroneInspection-Docs** repository. Read each target file first and preserve its existing table/heading structure.

**Files (modify):**
- `reports/report-3-software-requirement-specification/03-functional-requirements.md`
- `reports/report-3-software-requirement-specification/00-record-of-changes.md`
- `project-reference/business-flows.md`
- `project-reference/database-design.md`
- `development/plans/bach/2026-09-22-four-week-mainflow-delivery/tasks.md`
- `development/plans/bach/2026-09-22-four-week-mainflow-delivery/spec.md`
- `development/plans/bach/2026-09-22-four-week-mainflow-delivery/flow-handoffs.md`
- `development/plans/hieu/plan.md`
- `reports/report-5-test-report/01-test-cases/test-case-list.md`
- `reports/report-5-test-report/03-features/feature-1.md`
- `reports/report-5-test-report/02-test-statistics/test-statistics.md`
- `reports/report-5-test-report/00-cover/cover.md`
- `reports/report-5-test-report/00-cover/record-of-changes.md`
- Create: `backend/flows/assets-and-scheduling.md` (the flow doc T013 requires) + link it from `backend/_index.md`

**Interfaces:**
- Consumes: all behaviors implemented in Tasks 1–10 and the spec (`spec.md`, same directory).
- Produces: the handoff's `Documentation impact` evidence; Report 5 case IDs referenced by the statistics recount.

- [ ] **Step 1: Report 3 functional requirements**

In `03-functional-requirements.md`, locate the WF1 / asset & scheduling sections (§3.x covering FE-02/FE-03 — use the section that currently says Clients create inspection schedules). Rewrite that subsection's flow to:

> A Client registers an asset in `PENDING_REVIEW`. A Service Manager approves or rejects the review. On approval the platform generates one schedule proposal per suggested frequency configured on the asset's category (Admin catalog policy); the Manager reviews, adjusts, or rejects each proposal. The Client compares the `MANAGER_APPROVED` proposals and selects exactly one, which creates the active inspection schedule; the remaining proposals are superseded. The Client cannot create schedules directly. The due-cycle publisher then emits one idempotent `InspectionScheduleDue` event per asset/schedule/cycle for WF2.

Also update: (a) the asset-status list to include `PENDING_REVIEW` and `REJECTED`; (b) document-upload rules (types png/jpeg/webp/pdf, max 10 MB, active/inactive assets only); (c) the note that Manager review is **platform-scoped** (Manager accounts have no organization) — the deliberate choice from Task 10.

In `00-record-of-changes.md`, append a row: date `2026-09-25`, section(s) `3.x asset/scheduling`, description "Replaced Client-created schedules with Manager-reviewed platform proposals (asset PENDING_REVIEW → proposal generation → Client selection); added asset document upload and due-cycle event contract", author `Hiếu`.

- [ ] **Step 2: Business flows**

In `project-reference/business-flows.md`, update the **WF1** swimlane/sequence: add the Manager actor to the Client-asset path with the two review decisions (asset review, proposal review), the N-proposal comparison step, and the selection step that precedes schedule activation. Keep the existing WF1→WF2 handoff event line unchanged (event name/fields).

- [ ] **Step 3: Database design**

In `project-reference/database-design.md`: add the `category_frequency_suggestions` and `schedule_proposals` tables (columns from spec §Domain and migration, V11), update the `assets.status` enum list with `PENDING_REVIEW`/`REJECTED`, and note `inspection_schedules` is written only from a `CLIENT_SELECTED` proposal.

- [ ] **Step 4: Plan documents**

- `bach/2026-09-22-four-week-mainflow-delivery/tasks.md`: update T005 (add suggested-frequencies), T006 (create → `PENDING_REVIEW` + Manager review endpoint), T009 (schedule created only from selected proposal), T012 (add "**producer-side** per deviation: real WF2 consumer test in T021"), T013 (add new test class name `AssetWorkflowIntegrationTest`).
- `bach/.../spec.md`: add a short "Amended 2026-09-25: schedule proposals" note pointing at `development/plans/hieu/2026-09-25-wf1-schedule-proposal-flow/spec.md`.
- `bach/.../flow-handoffs.md`: in the WF1→WF2 row, keep the 5 contract fields; append to the note: "Upstream flow amended 2026-09-25 — schedules originate from Manager-reviewed proposals; the event contract is unchanged."
- `development/plans/hieu/plan.md`: add links to the new spec and plan; update owner tasks to mention proposal flow; add a Deviations section: "T012 executed producer-side (consumer test = T021)".

- [ ] **Step 5: Backend flow doc**

Create `backend/flows/assets-and-scheduling.md` describing: module layout (`assets` api/service/events), the API route table from the spec, the proposal lifecycle state diagram (text), the due-cycle event contract, and the authorization rules (role + org scope, Manager platform-scoped). Link it from `backend/_index.md`.

- [ ] **Step 6: Report 5 test records**

1. `01-test-cases/test-case-list.md` — append cases with **stable new IDs** (do not rename existing rows; WF1 cases belong to the `Feature 1` workbook sheet, FE-02/WF1 codes per AGENTS.md):

| ID | FE | WF | Sheet | Description | Pre-condition |
|---|---|---|---|---|---|
| `WF1-011` | FE-02 | WF1 | Feature 1 | Client creates asset → `PENDING_REVIEW` | Client org + active category exists |
| `WF1-012` | FE-02 | WF1 | Feature 1 | Manager approves asset → N proposals generated | Asset `PENDING_REVIEW`, category has suggested frequencies |
| `WF1-013` | FE-02 | WF1 | Feature 1 | Manager rejects asset → no proposals | Asset `PENDING_REVIEW` |
| `WF1-014` | FE-02 | WF1 | Feature 1 | Manager approves/rejects/adjusts proposals | Asset `ACTIVE`, proposals `GENERATED` |
| `WF1-015` | FE-02 | WF1 | Feature 1 | Client selects one proposal → active schedule, siblings superseded | ≥1 `MANAGER_APPROVED` proposal |
| `WF1-016` | FE-02 | WF1 | Feature 1 | Double-select and cross-org select denied | Active schedule exists / foreign org |
| `WF1-017` | FE-03 | WF1 | Feature 1 | Due-cycle event publishes once per cycle; replay silent | Active schedule with `next_due_at` in the past |
| `WF1-018` | FE-03 | WF1 | Feature 1 | Asset document upload type/size/scope rules | Active asset; png/pdf fixtures |
| `WF1-019` | FE-03 | WF1 | Feature 1 | Negative scope sweep across all WF1 endpoints | Two organizations, five roles |

2. `03-features/feature-1.md` — add the same IDs with full procedure, expected result, pre-conditions, and **status**: mark `Passed` only for the cases executed by Task 10's automated tests in this run (list the exact test method names as evidence), mark the T012-driven `WF1-017` with a note "producer-side; consumer half pending T021" and status `Passed` only for the producer assertions.
3. `02-test-statistics/test-statistics.md` — recount `Passed/Failed/Pending/N/A` so totals match `feature-1.md`; update subtotals/formulas.
4. `00-cover/cover.md` + `00-cover/record-of-changes.md` — bump report version/date/scope; append change-history row "WF1 proposal flow cases added".

- [ ] **Step 7: Verify docs repo**

```powershell
git diff --check
```
Expected: no output. Then link-check: confirm every new relative link in the edited files resolves (open each target path).

- [ ] **Step 8: Commit**

```powershell
git add reports project-reference development backend
git commit -m "docs(wf1): sync srs, flows, data model, and test report for schedule proposals"
```

---

## Final verification (all three repositories)

```powershell
cd SmartDroneInspection-Backend; .\mvnw.cmd spotless:apply; .\mvnw.cmd verify
cd ..\SmartDroneInspection-Frontend; npm run lint; npm run test; npm run build
cd ..\SmartDroneInspection-Docs; git diff --check
```

All three must pass. Report the exact commands run and their results in the handoff — never claim an unexecuted check.
