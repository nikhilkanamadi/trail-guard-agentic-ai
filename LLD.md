# TrialGuard AI — Low-Level Design

**Version:** 1.0.0  
**Platform:** TrialGuard Clinical Operations  
**Classification:** Internal Technical Reference

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Technology Stack](#2-technology-stack)
3. [Repository Layout](#3-repository-layout)
4. [Infrastructure & Deployment](#4-infrastructure--deployment)
5. [Backend Architecture](#5-backend-architecture)
   - 5.1 [Application Entry Point](#51-application-entry-point)
   - 5.2 [Configuration](#52-configuration)
   - 5.3 [Database Layer](#53-database-layer)
   - 5.4 [Data Models](#54-data-models)
   - 5.5 [Pydantic Schemas](#55-pydantic-schemas)
   - 5.6 [API Layer](#56-api-layer)
   - 5.7 [Authentication & Authorization](#57-authentication--authorization)
6. [Agent Pipeline](#6-agent-pipeline)
   - 6.1 [BaseAgent Contract](#61-baseagent-contract)
   - 6.2 [Pipeline Execution Order](#62-pipeline-execution-order)
   - 6.3 [Agent Specifications](#63-agent-specifications)
   - 6.4 [Quality Scoring Algorithm](#64-quality-scoring-algorithm)
7. [Database Schema](#7-database-schema)
8. [API Reference](#8-api-reference)
9. [Frontend Architecture](#9-frontend-architecture)
   - 9.1 [Page Inventory](#91-page-inventory)
   - 9.2 [Component Inventory](#92-component-inventory)
   - 9.3 [Mock Data Layer](#93-mock-data-layer)
10. [Regulatory Compliance Design](#10-regulatory-compliance-design)
11. [Security Design](#11-security-design)
12. [Error Handling Patterns](#12-error-handling-patterns)
13. [Key Constraints & Limits](#13-key-constraints--limits)

---

## 1. System Overview

TrialGuard AI is an agentic clinical trial document validation platform. It routes uploaded TMF (Trial Master File) documents through a sequential-parallel 7-agent pipeline that checks regulatory compliance, cross-references, data consistency, PHI exposure, and document quality. Results are surfaced via a Next.js dashboard to clinical operations staff.

**Core data flow:**

```
User uploads document
        │
        ▼
  POST /api/v1/documents/upload
        │
        ▼
  ValidationRun created (PENDING)
        │
        ▼
  Celery task dispatched → OrchestratorAgent
        │
        ├─ Stage 1: IngestionAgent  (sequential)
        │
        ├─ Stage 2: ComplianceAgent ─┐
        │           CrossRefAgent   ├─ asyncio.gather (parallel)
        │           ConsistencyAgent│
        │           PHIAgent        ┘
        │
        └─ Stage 3: QualityReviewAgent (sequential)
                │
                ▼
        Findings persisted → ValidationRun updated → AuditTrail written
```

---

## 2. Technology Stack

| Layer | Technology | Version |
|---|---|---|
| Frontend framework | Next.js App Router | 15 |
| UI library | React | 19 |
| Styling | Tailwind CSS | v4 |
| Language (FE) | TypeScript | 5 |
| Backend framework | FastAPI | latest |
| Language (BE) | Python | 3.12 |
| ORM | SQLAlchemy (async) | 2.x |
| Database | PostgreSQL | 16 |
| Task queue | Celery | latest |
| Message broker | Redis | 7 |
| Auth tokens | JWT (python-jose) | HS256 |
| Settings | pydantic-settings | v2 |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | — |
| Vector index | FAISS | — |
| Object storage | S3 / MinIO-compatible | — |
| Container runtime | Docker Compose | 3.9 |

---

## 3. Repository Layout

```
ADLC/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── requirements.txt
│   ├── scripts/
│   │   └── init.sql              # PostgreSQL bootstrap
│   └── app/
│       ├── main.py               # FastAPI app factory
│       ├── config.py             # pydantic-settings
│       ├── database.py           # engine, session, Base, mixins
│       ├── agents/
│       │   ├── base.py           # BaseAgent, AgentFinding, AgentResult
│       │   ├── orchestrator.py   # Pipeline coordinator
│       │   ├── ingestion.py      # Parse + classify + metadata
│       │   ├── compliance.py     # ICH-GCP / FDA / EU CTR checks
│       │   ├── crossref.py       # Internal reference consistency
│       │   ├── consistency.py    # Drug names, doses, dates, units
│       │   ├── phi.py            # PHI / PII detection
│       │   └── quality.py        # Aggregate scoring + escalation
│       ├── models/               # SQLAlchemy ORM models
│       │   ├── user.py
│       │   ├── study.py
│       │   ├── document.py
│       │   ├── validation.py
│       │   ├── finding.py
│       │   └── audit.py
│       ├── schemas/              # Pydantic I/O schemas
│       │   ├── user.py
│       │   ├── study.py
│       │   ├── document.py
│       │   ├── validation.py
│       │   ├── finding.py
│       │   └── audit.py
│       └── api/
│           ├── deps.py           # get_current_user, require_role
│           ├── router.py         # Aggregate router /api/v1
│           └── routes/
│               ├── auth.py
│               ├── studies.py
│               ├── documents.py
│               ├── validation.py
│               ├── findings.py
│               ├── audit.py
│               └── admin.py
└── frontend/
    └── src/
        ├── app/
        │   ├── layout.tsx        # Root layout: Sidebar + main
        │   ├── page.tsx          # Dashboard
        │   ├── globals.css       # TrialGuard theme variables
        │   ├── studies/page.tsx
        │   ├── documents/upload/page.tsx
        │   ├── validation/page.tsx
        │   ├── findings/page.tsx
        │   ├── audit/page.tsx
        │   ├── agents/page.tsx
        │   ├── reports/page.tsx
        │   └── settings/page.tsx
        ├── components/
        │   └── Sidebar.tsx
        └── lib/
            └── mock-data.ts      # Static mock data (pre-API)
```

---

## 4. Infrastructure & Deployment

Five Docker Compose services communicate over the `trialguard-net` bridge network.

| Service | Image / Build | Port | Purpose |
|---|---|---|---|
| `postgres` | `postgres:16-alpine` | 5432 | Primary relational store |
| `redis` | `redis:7-alpine` | 6379 | Celery broker (db 1), result backend (db 2), cache (db 0) |
| `backend` | `./backend` Dockerfile | 8000 | FastAPI HTTP server |
| `celery-worker` | same image | — | Agent task execution, queues: `default`, `validation`, `ingestion`, `agents`, concurrency=4 |
| `celery-beat` | same image | — | Scheduled tasks (periodic cleanup, reports) |
| `frontend` | `./frontend` Dockerfile | 3000 | Next.js SSR server |

**Named volumes:**

| Volume | Mount | Contents |
|---|---|---|
| `postgres_data` | `/var/lib/postgresql/data` | Database files |
| `redis_data` | `/data` | AOF persistence |
| `faiss_data` | `/app/data/faiss_indexes` | FAISS vector index shards |
| `document_storage` | `/app/data/documents` | Uploaded document files |

**Health checks:** All services implement health checks; `backend` and `celery-worker` depend on `postgres` and `redis` being healthy before starting.

---

## 5. Backend Architecture

### 5.1 Application Entry Point

**File:** `backend/app/main.py`

```
FastAPI(title="TrialGuard AI", version="1.0.0")
  ├── CORSMiddleware (origins from settings.CORS_ORIGINS)
  ├── GET /  → health ping {"status": "ok"}
  ├── include_router(api_router, prefix="")  → /api/v1/...
  ├── @app.on_event("startup")  → DB connection pool warm-up
  ├── @app.on_event("shutdown") → engine dispose
  ├── 404 handler → {"detail": "Not Found"}
  └── 500 handler → {"detail": "Internal Server Error"}
```

### 5.2 Configuration

**File:** `backend/app/config.py`

`Settings` extends `pydantic_settings.BaseSettings`. All fields map 1-to-1 to environment variables. The instance is created once via `@lru_cache` on `get_settings()`.

| Group | Key fields |
|---|---|
| App | `APP_NAME`, `APP_VERSION`, `DEBUG`, `ENVIRONMENT`, `LOG_LEVEL` |
| Database | `DATABASE_URL` (asyncpg), pool size=20, max_overflow=10, recycle=3600 |
| Redis | `REDIS_URL`, `CELERY_BROKER_URL` (db 1), `CELERY_RESULT_BACKEND` (db 2) |
| JWT | `JWT_SECRET_KEY`, `JWT_ALGORITHM=HS256`, access=30 min, refresh=7 days |
| Storage | `S3_BUCKET_NAME`, `S3_REGION`, `S3_ENDPOINT_URL` (MinIO override) |
| Embeddings | `FAISS_INDEX_PATH`, `EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2`, `EMBEDDING_DIMENSION=384` |
| Constraints | `MAX_UPLOAD_SIZE_MB=100`, `ALLOWED_MIME_TYPES` (PDF, DOCX, DOC, TXT, CSV) |
| Agents | `AGENT_TIMEOUT_SECONDS=300`, `MAX_CONCURRENT_VALIDATIONS=5` |
| SMTP | `SMTP_HOST/PORT/USER/PASSWORD` (optional notifications) |

### 5.3 Database Layer

**File:** `backend/app/database.py`

```python
# SQLAlchemy async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20, max_overflow=10,
    pool_recycle=3600, pool_pre_ping=True
)

async_session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
```

**Mixins shared by all models:**

| Mixin | Columns added |
|---|---|
| `UUIDPrimaryKeyMixin` | `id: UUID4` (primary key, `default=uuid.uuid4`) |
| `TimestampMixin` | `created_at: timestamptz`, `updated_at: timestamptz` (both `server_default=now()`, `updated_at` has `onupdate`) |

**FastAPI dependency:** `get_db()` yields an `AsyncSession`, commits on clean exit, rolls back on exception, closes always.

**Naming convention** (for Alembic auto-migrations):

```
ix_%(column_0_label)s  |  uq_%(table_name)s_%(column_0_name)s
ck_%(table_name)s_%(constraint_name)s
fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s
pk_%(table_name)s
```

### 5.4 Data Models

#### User (`users`)

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | — |
| email | VARCHAR(320) | unique, indexed |
| full_name | VARCHAR(255) | — |
| hashed_password | VARCHAR(1024) | bcrypt |
| role | VARCHAR(50) | enum: admin / manager / reviewer / uploader / viewer |
| organization | VARCHAR(255) | nullable |
| department | VARCHAR(255) | nullable |
| is_active | BOOLEAN | default true |
| last_login | TIMESTAMPTZ | nullable |
| mfa_enabled | BOOLEAN | default false |
| created_at / updated_at | TIMESTAMPTZ | from mixin |

Indexes: `email` (unique), `role`, `organization`.

#### Study (`studies`)

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | — |
| study_identifier | VARCHAR(100) | unique, indexed |
| sponsor_name | VARCHAR(255) | — |
| protocol_number | VARCHAR(100) | — |
| therapeutic_area | VARCHAR(255) | — |
| phase | VARCHAR(50) | enum: Phase 1/1a/1b/2/2a/2b/3/3a/3b/4/N/A |
| status | VARCHAR(50) | enum: planning/active/enrolling/closed/completed/suspended/terminated/withdrawn |
| countries | JSONB | nullable |
| description | TEXT | nullable |

Indexes: `study_identifier` (unique), `sponsor_name`, `protocol_number`, `therapeutic_area`, `phase`, `status`.

Relationships: `documents` (1→N), `validation_runs` (1→N).

#### Document (`documents`)

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | — |
| study_id | UUID FK → studies | CASCADE delete |
| uploaded_by | UUID FK → users | SET NULL on delete |
| document_type | VARCHAR(100) | e.g. Protocol, ICF, IB |
| tmf_zone | INTEGER | 1–11 (DIA Reference Model) |
| tmf_section | VARCHAR(100) | — |
| tmf_artifact | VARCHAR(255) | nullable |
| title | VARCHAR(500) | — |
| version | VARCHAR(50) | default "1.0" |
| version_date | DATE | nullable |
| language | VARCHAR(10) | default "en" |
| country_code | VARCHAR(3) | nullable |
| site_id | VARCHAR(100) | nullable |
| file_path | VARCHAR(1024) | S3 key or local path |
| file_hash | VARCHAR(128) | SHA-256 hex |
| file_size_bytes | BIGINT | — |
| mime_type | VARCHAR(255) | — |
| page_count | INTEGER | nullable |
| status | VARCHAR(50) | enum: uploaded/processing/validated/failed/superseded/archived/deleted |

Indexes: `study_id`, `document_type`, `tmf_zone`, `tmf_section`, `status`, `file_hash`, `uploaded_by`.

Duplicate detection: upload route checks `(study_id, file_hash, status != DELETED)` and rejects with 409 on match.

Version chain: documents sharing `(study_id, title, document_type)` form a version chain, queryable via `/documents/{id}/versions`.

#### ValidationRun (`validation_runs`)

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | — |
| document_id | UUID FK → documents | CASCADE delete |
| study_id | UUID FK → studies | CASCADE delete |
| run_type | VARCHAR(50) | enum: full/incremental/targeted/revalidation |
| status | VARCHAR(50) | enum: pending/running/completed/failed/cancelled/timed_out |
| started_at | TIMESTAMPTZ | nullable |
| completed_at | TIMESTAMPTZ | nullable |
| total_findings | INTEGER | default 0 |
| critical_findings | INTEGER | default 0 |
| major_findings | INTEGER | default 0 |
| minor_findings | INTEGER | default 0 |
| overall_score | FLOAT | nullable (0–100) |
| triggered_by | VARCHAR(255) | nullable (e.g. "user:email") |
| agent_trace | JSONB | full per-agent execution log |

Indexes: `document_id`, `study_id`, `status`, `run_type`, `started_at`.

Conflict rule: API rejects new run if an existing `PENDING` or `RUNNING` run exists for the same `document_id`.

#### Finding (`findings`)

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | — |
| validation_run_id | UUID FK → validation_runs | CASCADE delete |
| document_id | UUID FK → documents | CASCADE delete |
| agent_name | VARCHAR(100) | which agent emitted this |
| finding_type | VARCHAR(100) | machine-readable classification |
| severity | VARCHAR(50) | critical / major / minor / info |
| category | VARCHAR(100) | human-readable category |
| title | VARCHAR(500) | — |
| description | TEXT | — |
| page_number | INTEGER | nullable |
| section_reference | VARCHAR(255) | nullable |
| regulatory_reference | VARCHAR(500) | nullable |
| suggested_remediation | TEXT | nullable |
| confidence_score | FLOAT | 0.0–1.0 |
| status | VARCHAR(50) | open/in_review/resolved/escalated/false_positive/deferred/wont_fix |
| resolved_by | UUID FK → users | SET NULL |
| resolved_at | TIMESTAMPTZ | nullable |
| resolution_notes | TEXT | nullable |

Indexes: `validation_run_id`, `document_id`, `severity`, `status`, `agent_name`, `category`, `finding_type`.

#### AuditTrail (`audit_trail`)

| Column | Type | Notes |
|---|---|---|
| id | BIGINT PK | auto-increment |
| entity_type | VARCHAR(100) | Document / Validation / Finding / etc. |
| entity_id | VARCHAR(255) | UUID or other ID as string |
| action | VARCHAR(100) | Upload Document / Complete Validation / etc. |
| performed_by | UUID | nullable (system actions have NULL) |
| old_values | JSONB | nullable (before state) |
| new_values | JSONB | nullable (after state) |
| ip_address | VARCHAR(45) | IPv4 or IPv6, nullable |
| user_agent | VARCHAR(512) | nullable |
| reason | TEXT | nullable (21 CFR Part 11 reason-for-change) |
| electronic_signature | JSONB | nullable (Part 11 e-sig metadata) |
| timestamp | TIMESTAMPTZ | `server_default=now()`, immutable |

Indexes: `entity_type`, `entity_id`, `action`, `performed_by`, `timestamp`, composite `(entity_type, entity_id)`.

**Design constraint:** No UPDATE or DELETE should be issued against `audit_trail` in production (append-only, 21 CFR Part 11).

### 5.5 Pydantic Schemas

Each domain has a `schemas/<domain>.py` with:

- `*Create` — fields accepted on POST (excludes server-generated fields)
- `*Read` — fields returned in responses (includes id, timestamps)
- `*Update` — optional fields for PATCH

Special schemas in `validation.py`:
- `ValidationRunCreate` — `document_id`, `study_id`, `run_type`, optional `triggered_by`
- `ValidationRunCancel` — `id`, `status`, `message`
- `FindingList` — `items: list[FindingRead]`, `total`, `page`, `size`

### 5.6 API Layer

**Router:** `api/router.py` mounts sub-routers under `/api/v1`.

| Prefix | Module | Tag |
|---|---|---|
| `/auth` | `routes/auth.py` | Authentication |
| `/studies` | `routes/studies.py` | Studies |
| `/documents` | `routes/documents.py` | Documents |
| `/validation` | `routes/validation.py` | Validation |
| `/findings` | `routes/findings.py` | Findings |
| `/audit` | `routes/audit.py` | Audit Trail |
| `/admin` | `routes/admin.py` | Administration |

### 5.7 Authentication & Authorization

**Flow:**
1. `POST /api/v1/auth/login` → validates credentials → issues JWT (`sub` = user UUID)
2. Every protected route receives `Authorization: Bearer <token>`
3. `get_current_user` dep: decodes JWT → loads `User` from DB → checks `is_active`
4. `require_role(["admin", "manager"])` factory wraps endpoints needing role gating

**JWT claims:** `sub` (user UUID string), `exp`, optional `role`.

**MFA:** `mfa_enabled` flag exists on User; enforcement logic lives in the auth route.

---

## 6. Agent Pipeline

### 6.1 BaseAgent Contract

**File:** `backend/app/agents/base.py`

```python
class BaseAgent(abc.ABC):
    name: str
    version: str
    logger: Logger
    _progress_callbacks: list

    async def execute(document_text, document_metadata, study_metadata, **kwargs) -> AgentResult
        # wraps _execute with timing + exception → AgentResult(status="failed")

    async def _execute(...) -> AgentResult   # abstract — subclasses implement

    def emit_progress(stage, percent)        # fires all registered callbacks
    def on_progress(callback)                # register fn(agent_name, stage, percent)
    def _make_finding(...)  -> AgentFinding  # convenience factory
```

**`AgentFinding` DTO:**

| Field | Type |
|---|---|
| agent_name | str |
| finding_type | str |
| severity | FindingSeverity |
| category | str |
| title | str |
| description | str |
| page_number | int \| None |
| section_reference | str \| None |
| regulatory_reference | str \| None |
| suggested_remediation | str \| None |
| confidence_score | float (default 1.0) |

**`AgentResult` DTO:**

| Field | Type |
|---|---|
| agent_name | str |
| status | str: completed \| failed \| skipped |
| findings | list[AgentFinding] |
| metadata | dict[str, Any] |
| execution_time_ms | float |
| error | str \| None |

### 6.2 Pipeline Execution Order

```
OrchestratorAgent._execute()
│
├─ [10%] IngestionAgent.execute()
│       ↳ if status == "failed" → return early with error AgentResult
│       ↳ merge ingestion metadata into enriched_meta
│
├─ [30%] asyncio.gather(
│           ComplianceAgent.execute(enriched_meta),
│           CrossReferenceAgent.execute(enriched_meta),
│           ConsistencyAgent.execute(enriched_meta),
│           PHIDetectionAgent.execute(enriched_meta),
│           return_exceptions=True
│       )
│       ↳ exceptions from individual agents are logged but don't abort pipeline
│
└─ [80%] QualityReviewAgent.execute(
              ..., findings=all_findings_so_far
         )
         ↳ returns summary AgentFinding + scored metadata
```

`agent_trace` JSONB field in `ValidationRun` stores per-stage timing, finding counts, and errors for full traceability.

### 6.3 Agent Specifications

#### IngestionAgent

**Responsibility:** Parse, classify, extract metadata.  
**Inputs:** raw `document_text`, `document_metadata` (declared type, tmf_zone)  
**Outputs:** enriched metadata dict + findings

| Check | Finding type | Severity |
|---|---|---|
| `word_count < 50` | `low_content` | MAJOR |
| Declared type ≠ classified type | `type_mismatch` | MINOR |
| `tmf_zone` not in 1–11 | `invalid_tmf_zone` | MAJOR |

**Classification:** keyword scoring across 10 document type dictionaries (`DOCUMENT_TYPE_KEYWORDS`). Winner = highest keyword hit count.

**Metadata extracted via regex:**
- `extracted_protocol_number` — `protocol\s*(?:number|no\.?|#)?[:\s]*([\w\-]+)`
- `extracted_version` — `version[:\s]*([\d]+(?:\.[\d]+)*)`
- `extracted_date` — date label + date value
- `extracted_sponsor` — `sponsor[:\s]*([A-Z][\w\s&,]+?)`
- `extracted_phase` — `phase\s*(I{1,3}[ab]?|[1-4][ab]?)`

**TMF Zone Map (DIA Reference Model):**

| Zone | Name |
|---|---|
| 1 | Trial Management |
| 2 | Central Trial Documents |
| 3 | Regulatory |
| 4 | IRB/IEC |
| 5 | Site Management |
| 6 | IP and Trial Supplies |
| 7 | Safety Reporting |
| 8 | Central and Local Testing |
| 9 | Third Parties |
| 10 | Data Management |
| 11 | Statistics |

---

#### ComplianceAgent

**Responsibility:** Check required section presence per document type + FDA Part 11 + date format + version control.

**Required sections by document type:**

| Document Type | Required Sections |
|---|---|
| Protocol | objectives/endpoints/inclusion criteria/statistical/safety monitoring/informed consent |
| ICF | voluntary participation/right to withdraw/risks/benefits/contact/confidentiality |

**Checks performed:**

| Check | Finding type | Severity |
|---|---|---|
| Missing required section | `missing_required_section` | CRITICAL |
| No FDA Part 11 keywords (`electronic record`, `audit trail`, `electronic signature`, `access control`, `21 cfr part 11`) | `missing_part11_controls` | MAJOR |
| Mixed date formats (ISO + US + EU in same doc) | `inconsistent_date_formats` | MINOR |
| No version control evidence (`version`, `revision`, `amendment`) | `missing_version_control` | MINOR |
| No sponsor/PI identification | `missing_sponsor_pi` | MAJOR |

**Regulatory references emitted:** ICH E6(R2) §4.8 (ICF), FDA 21 CFR Part 11, ICH E6(R2) §6 (Protocol).

---

#### CrossReferenceAgent

**Responsibility:** Verify internal reference consistency.

**Checks performed:**

| Check | Finding type | Severity | Logic |
|---|---|---|---|
| Section ref mentioned but not defined as heading | `dangling_section_reference` | MINOR | regex `(?:Section|Appendix|Table|Figure)\s+[\d.]+` vs defined headings `^\d+[\.\d]*\s+\w` |
| Figure/Table ref without matching label | `missing_figure_table` | MINOR | refs `(?:Figure|Table)\s+\d+` vs labels `(?:Figure|Table)\s+\d+[:\.]` |
| Protocol number inconsistency | `protocol_number_inconsistency` | MAJOR | >1 distinct protocol number pattern found |
| Sample size inconsistency | `sample_size_inconsistency` | MAJOR | numeric values near "sample size/subject/patient" vary by >3× |

---

#### ConsistencyAgent

**Responsibility:** Check drug name, dosing, date ordering, and unit consistency.

**Checks performed:**

| Check | Finding type | Severity | Logic |
|---|---|---|---|
| >1 distinct drug name form | `inconsistent_drug_names` | MAJOR | `DRUG_CONTEXT_PATTERN` extracts drug names near dose keywords; normalizes to lower; >1 unique = inconsistency |
| Dose ratio >3× for same unit | `inconsistent_dosing` | MAJOR | extracts `(\d+(?:\.\d+)?)\s*(mg|µg|mcg|g|ml|kg)` per unit group; max/min > 3 |
| Study start date ≥ end date | `date_ordering_error` | MAJOR | `study start date` vs `study end date/completion date` regex patterns |
| mg and mg/kg both present | `mixed_dose_units` | MINOR | both unit patterns found in same document |

---

#### PHIDetectionAgent

**Responsibility:** Detect protected health information (HIPAA Safe Harbor, GDPR).

Eight named patterns with priority order:

| Pattern | Regex | Severity | Regulatory ref |
|---|---|---|---|
| SSN | `\d{3}-\d{2}-\d{4}` | CRITICAL | HIPAA §164.514(b)(2)(i) |
| DOB | date-preceded-by dob/birth/born label | CRITICAL | HIPAA §164.514(b)(2)(i) |
| Patient Name | Mr/Mrs/Ms/Dr + name + patient/subject | MAJOR | HIPAA §164.514(b)(2)(i) |
| MRN | `(?:MRN|Medical Record|Patient ID)[:\s#]*[\w\-]+` | MAJOR | HIPAA §164.514(b)(2)(i) |
| Phone | `(?:\+1\s?)?\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}` | MINOR | HIPAA §164.514(b)(2)(iv) |
| Email | standard email regex | MINOR | GDPR Art. 4(1) |
| Device Serial | `(?:Device|Serial|Lot)\s*(?:Number|No\.?|#)[:\s]*([\w\-]+)` | MINOR | HIPAA §164.514(b)(2)(xi) |
| Geographic Subdivision | state/city/zip/county label + value | MINOR | HIPAA §164.514(b)(2)(iii) |

Each match is de-duplicated. CRITICAL findings prompt immediate escalation; all PHI findings include remediation guidance to redact/de-identify.

---

#### QualityReviewAgent

**Responsibility:** Aggregate upstream findings, compute document quality score, and decide escalation.

**Inputs:** all `AgentFinding` objects passed via `kwargs["findings"]`.

### 6.4 Quality Scoring Algorithm

```
score = 100
       - min(critical_count × 15, 60)   ← CRITICAL_PENALTY, MAX_CRITICAL_DEDUCTION
       - min(major_count   ×  5, 25)    ← MAJOR_PENALTY,    MAX_MAJOR_DEDUCTION
       - min(minor_count   ×  1, 10)    ← MINOR_PENALTY,    MAX_MINOR_DEDUCTION
score = max(0, score)
```

**Escalation triggers (any one):**
- `critical_count ≥ 1`
- `major_count ≥ 5`
- `score < 50`

**Recommendation text logic:**

| Condition | Recommendation |
|---|---|
| critical > 0 | IMMEDIATE ACTION REQUIRED + escalate |
| escalate and major ≥ 5 | ESCALATION RECOMMENDED |
| score < 70 | below acceptable threshold |
| score ≥ 95 | excellent, minor review recommended |
| else | review and resolve outstanding findings |

**Metadata returned by QualityReviewAgent:**

```json
{
  "overall_score": 72.50,
  "critical_count": 0,
  "major_count": 3,
  "minor_count": 5,
  "info_count": 1,
  "total_findings": 9,
  "escalation_required": false,
  "recommendation": "Document quality score: 72.5/100. Review..."
}
```

---

## 7. Database Schema

### Entity Relationship (textual)

```
users (1) ──────────────< documents.uploaded_by
users (1) ──────────────< findings.resolved_by

studies (1) ────────────< documents (N)
studies (1) ────────────< validation_runs (N)

documents (1) ──────────< validation_runs (N)
documents (1) ──────────< findings (N)

validation_runs (1) ────< findings (N)
```

### Cascade Rules

| Parent delete | Child action |
|---|---|
| `studies` | `documents` CASCADE, `validation_runs` CASCADE |
| `documents` | `validation_runs` CASCADE, `findings` CASCADE |
| `validation_runs` | `findings` CASCADE |
| `users` (uploader) | `documents.uploaded_by` SET NULL |
| `users` (resolver) | `findings.resolved_by` SET NULL |

### PostgreSQL Extensions

- `uuid-ossp` — UUID generation functions
- `pgcrypto` — cryptographic functions (password hashing support)

---

## 8. API Reference

All endpoints require `Authorization: Bearer <jwt>` unless noted.

### Authentication `POST /api/v1/auth/login`

Body: `{ email, password }` → returns `{ access_token, refresh_token, token_type }`

### Studies `/api/v1/studies`

| Method | Path | Description |
|---|---|---|
| GET | `/` | List studies (paginated) |
| POST | `/` | Create study |
| GET | `/{study_id}` | Get study by ID |
| PATCH | `/{study_id}` | Update study |
| DELETE | `/{study_id}` | Archive/delete study |

### Documents `/api/v1/documents`

| Method | Path | Description | Notes |
|---|---|---|---|
| POST | `/upload` | Upload document (multipart) | SHA-256 dupe check; 100 MB limit |
| GET | `/{document_id}` | Get document | 404 if DELETED |
| GET | `/{document_id}/versions` | Version chain | same title+type+study |
| DELETE | `/{document_id}` | Soft-delete | sets status=DELETED |

**Upload multipart fields:** `file`, `study_id`, `document_type`, `tmf_zone` (1–11), `tmf_section`, `title`, `version` (opt), `tmf_artifact` (opt), `language` (opt), `country_code` (opt), `site_id` (opt).

### Validation `/api/v1/validation`

| Method | Path | Description | Notes |
|---|---|---|---|
| POST | `/run` | Trigger validation run | 409 if run already in-progress |
| GET | `/runs/{run_id}` | Get run details | — |
| GET | `/runs/{run_id}/findings` | Paginated findings | filter: severity, agent_name |
| POST | `/runs/{run_id}/cancel` | Cancel run | only PENDING or RUNNING |

### Findings `/api/v1/findings`

| Method | Path | Description |
|---|---|---|
| GET | `/` | List findings (paginated, filterable) |
| GET | `/{finding_id}` | Get finding |
| PATCH | `/{finding_id}` | Update status / resolution notes |

### Audit `/api/v1/audit`

| Method | Path | Description |
|---|---|---|
| GET | `/` | List audit entries (paginated) |
| GET | `/{entity_type}/{entity_id}` | Entries for a specific entity |

### Admin `/api/v1/admin`

| Method | Path | Description | Role |
|---|---|---|---|
| GET | `/system/health` | System health + DB ping | public |
| GET | `/users` | List users | admin |
| POST | `/users` | Create user | admin |
| DELETE | `/users/{user_id}` | Deactivate user | admin |

---

## 9. Frontend Architecture

### 9.1 Page Inventory

All pages use `'use client'` and Next.js App Router. Layout wraps all pages in `<Sidebar>` + `<main>`.

| Route | File | Purpose |
|---|---|---|
| `/` | `app/page.tsx` | Dashboard: KPI cards, recent runs, findings summary, TMF zone grid, agent status row |
| `/studies` | `app/studies/page.tsx` | Study grid with `ScoreRing` SVG, search + status filter |
| `/documents/upload` | `app/documents/upload/page.tsx` | Drag-and-drop upload form + documents table |
| `/validation` | `app/validation/page.tsx` | Validation queue table + "Trigger Validation" modal |
| `/findings` | `app/findings/page.tsx` | Finding cards with severity filter, search, collapsible remediation |
| `/audit` | `app/audit/page.tsx` | Audit trail table with action + entity type filters |
| `/agents` | `app/agents/page.tsx` | Agent cards with inline SVG sparklines + circuit breaker badges |
| `/reports` | `app/reports/page.tsx` | Report generation cards (Compliance, TMF Completeness, Findings Export) |
| `/settings` | `app/settings/page.tsx` | API key, agent config, notification toggles, framework checkboxes |

### 9.2 Component Inventory

| Component | File | Props |
|---|---|---|
| `Sidebar` | `components/Sidebar.tsx` | none — reads `usePathname()` for active link |
| `ScoreRing` | inline in `studies/page.tsx` | `score: number` — SVG circle with stroke-dasharray |
| `Sparkline` | inline in `agents/page.tsx` | `data: number[]` — SVG polyline |
| `FindingCard` | inline in `findings/page.tsx` | `finding: Finding` — collapsible card |
| `AgentCard` | inline in `agents/page.tsx` | `agent: AgentStatus` — metric card |

### 9.3 Mock Data Layer

**File:** `frontend/src/lib/mock-data.ts`

Exports static arrays consumed by all pages (no live API calls in current build):

| Export | Type | Used by |
|---|---|---|
| `studies` | `Study[]` | `/studies`, `/documents/upload` |
| `documents` | `Document[]` | `/documents/upload` |
| `validationRuns` | `ValidationRun[]` | `/validation` |
| `findings` | `Finding[]` | `/findings`, `/` |
| `auditEntries` | `AuditEntry[]` | `/audit` |
| `agentStatuses` | `AgentStatus[]` | `/agents`, `/` |

All types are exported as named TypeScript interfaces.

### Theme System

**File:** `frontend/src/app/globals.css`

| CSS class | Usage | Value |
|---|---|---|
| `.glass` | White cards | `background: #FFFFFF; border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.06)` |
| `.glass-strong` | Sidebar | `background: #0057A8; border-right: rgba(255,255,255,0.12)` |
| `.gradient-text` | Page titles | Linear gradient `#0057A8 → #003087` |
| `.gradient-border` | Card borders | Subtle blue gradient border |
| `.dot-grid` | Page background | Radial dot grid, `rgba(0,87,168,0.06)` |
| `.mesh-gradient` | Page background | Radial light mesh |
| `.animate-fade-in` | Page entry | 0→1 opacity, 200ms |
| `.animate-slide-up` | Modal entry | translateY(16px)→0, 250ms |
| `.progress-bar` | Validation progress | Smooth width transition |
| `.sidebar-nav-active` | Active nav item | `rgba(255,255,255,0.15)` background, white text |

**TrialGuard Color Tokens:**

| Token | Hex |
|---|---|
| TrialGuard Blue (primary) | `#0057A8` |
| TrialGuard Navy (hover) | `#003087` |
| Background | `#F4F6F9` |
| Card surface | `#FFFFFF` |
| Border | `#E2E8F0` |
| Text primary | `#0F172A` |
| Text secondary | `#475569` |

---

## 10. Regulatory Compliance Design

| Regulation | Implementation |
|---|---|
| **21 CFR Part 11** | `AuditTrail` table is append-only (no UPDATE/DELETE). Columns: `electronic_signature` (JSONB), `reason`, `performed_by`, `timestamp` (server-side). ComplianceAgent checks documents for Part 11 keyword evidence. |
| **ICH-GCP E6(R2)** | ComplianceAgent validates required Protocol sections per §6 and ICF sections per §4.8. |
| **EU CTR 536/2014** | Referenced in ComplianceAgent regulatory findings. |
| **HIPAA Safe Harbor §164.514(b)(2)** | PHIDetectionAgent patterns cover all 18 Safe Harbor identifiers including SSN, DOB, MRN, phone, email, geographic data, device serial. |
| **GDPR Art. 4(1)** | PHIDetectionAgent email pattern references GDPR. |
| **TMF Reference Model** | All documents classified into 11 DIA zones. `tmf_zone`, `tmf_section`, `tmf_artifact` fields. IngestionAgent validates zone bounds. |

---

## 11. Security Design

| Concern | Mechanism |
|---|---|
| Authentication | JWT HS256, 30-min access token, 7-day refresh |
| Authorization | Role-based via `require_role()` dependency factory (admin/manager/reviewer/uploader/viewer) |
| Password storage | `hashed_password` field — bcrypt in auth routes |
| MFA | `mfa_enabled` flag on User; enforcement in auth route |
| File upload | SHA-256 duplicate detection; MIME type allowlist; 100 MB size cap |
| CORS | Configured via `settings.CORS_ORIGINS`; defaults to localhost:3000/5173/8080 |
| SQL injection | SQLAlchemy parameterized queries throughout; no raw string interpolation |
| Secret management | All secrets via env vars / `.env`; `JWT_SECRET_KEY` placeholder warns to rotate |
| Audit trail | Every state change written to `audit_trail`; IP extracted via `X-Forwarded-For` aware `get_client_ip()` |
| PHI in documents | PHIDetectionAgent runs on every document; findings escalated immediately for CRITICAL severity |

---

## 12. Error Handling Patterns

### Backend

| Layer | Strategy |
|---|---|
| Agent execution | `BaseAgent.execute()` wraps `_execute()` in try/except; returns `AgentResult(status="failed", error=...)` instead of raising |
| Parallel agents | `asyncio.gather(return_exceptions=True)` — one agent failure doesn't abort others |
| Pipeline abort | Only on IngestionAgent failure (nothing to process downstream) |
| API routes | `HTTPException` with appropriate status codes (404, 409, 413, 400, 401, 403) |
| DB session | `get_db()` rolls back on any exception |
| Global handlers | `main.py` 404 → `{"detail": "Not Found"}`, 500 → `{"detail": "Internal Server Error"}` |

### Frontend

| Pattern | Usage |
|---|---|
| Empty state | "No findings match your filters" cards when filtered results are empty |
| Loading state | Spinner SVG during upload/validation trigger simulate (mock) |
| Success state | Checkmark confirmation panels with auto-dismiss timers |
| Error rate coloring | `text-rose-600` when >2%, `text-amber-600` when >1%, `text-emerald-600` otherwise |

---

## 13. Key Constraints & Limits

| Constraint | Value | Source |
|---|---|---|
| Max upload file size | 100 MB | `settings.MAX_UPLOAD_SIZE_MB` |
| Allowed MIME types | PDF, DOCX, DOC, TXT, CSV | `settings.ALLOWED_MIME_TYPES` |
| Agent timeout | 300 s | `settings.AGENT_TIMEOUT_SECONDS` |
| Max concurrent validations | 5 | `settings.MAX_CONCURRENT_VALIDATIONS` |
| Celery worker concurrency | 4 | `docker-compose.yml` command |
| DB connection pool | 20 + 10 overflow | `settings.DATABASE_POOL_SIZE/MAX_OVERFLOW` |
| JWT access token TTL | 30 min | `settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES` |
| JWT refresh token TTL | 7 days | `settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES` |
| Redis max memory | 512 MB | `docker-compose.yml` redis command |
| Section detection cap | 50 sections | `IngestionAgent._parse_document()` |
| Finding list page size | max 200 | `GET /validation/runs/{id}/findings` size param |
| Score floor | 0 | `_compute_score()` |
| Score ceiling | 100 | base value before deductions |
| Max critical deduction | 60 pts | 4+ criticals saturate |
| Max major deduction | 25 pts | 5+ majors saturate |
| Max minor deduction | 10 pts | 10+ minors saturate |
| Escalation: critical threshold | ≥ 1 | `ESCALATION_CRITICAL_THRESHOLD` |
| Escalation: major threshold | ≥ 5 | `ESCALATION_MAJOR_THRESHOLD` |
| Escalation: score threshold | < 50 | `ESCALATION_SCORE_THRESHOLD` |
| Embedding dimension | 384 | all-MiniLM-L6-v2 |
| TMF zones | 1–11 | DIA Reference Model |
