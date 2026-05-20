# TrialGuard AI

**Agentic Clinical Trial Document Validation Platform**

> Built using the Agentic Development Life Cycle (ADLC) methodology.

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)

---

## Overview

TrialGuard AI is an **agentic, AI-powered clinical trial document validation platform** that automates the validation, compliance checking, cross-referencing, and quality review of clinical trial documents against ICH-GCP E6(R2), FDA 21 CFR Part 11, EU CTR 536/2014, and country-specific regulatory requirements.

### The 7-Agent Architecture

| Agent | Role |
|---|---|
| 🔄 **Orchestrator** | Workflow coordination, routing, escalation |
| 📥 **Ingestion** | Document parsing, OCR, classification, embedding |
| ✅ **Compliance Validator** | ICH-GCP, Part 11, EU CTR rule checking |
| 🔗 **Cross-Reference** | Inter/intra-document reference validation |
| 🔍 **Consistency Checker** | Terminology, dosing, date, multi-site consistency |
| 🔒 **PHI/PII Redaction** | HIPAA/GDPR compliance, de-identification |
| 📊 **Quality Review** | Scoring, reporting, human-in-the-loop escalation |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15 + Tailwind CSS v4 + TypeScript |
| Backend API | Python 3.12 + FastAPI |
| Database | PostgreSQL 16 (relational) + FAISS (vector) |
| Task Queue | Celery + Redis |
| Embeddings | PubMedBERT / sentence-transformers |
| Auth | JWT + RBAC (SSO-ready via Keycloak) |
| Infrastructure | Docker + Docker Compose |

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.12+ (for local backend development)

### 1. Clone & Start

```bash
# Clone the repository
git clone <repo-url> trialguard-ai
cd trialguard-ai

# Start all services
docker-compose up -d

# Verify
docker-compose ps
```

### 2. Access the Application

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (ReDoc) | http://localhost:8000/redoc |

### 3. Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## Project Structure

```
ADLC/
├── backend/
│   ├── app/
│   │   ├── agents/           # 7 AI validation agents
│   │   │   ├── base.py       # Base agent class
│   │   │   ├── orchestrator.py
│   │   │   ├── ingestion.py
│   │   │   ├── compliance.py
│   │   │   ├── crossref.py
│   │   │   ├── consistency.py
│   │   │   ├── phi.py
│   │   │   └── quality.py
│   │   ├── api/              # FastAPI routes
│   │   │   └── routes/
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic services
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database setup
│   │   └── main.py           # FastAPI app entry
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js App Router pages
│   │   ├── components/       # Reusable UI components
│   │   └── lib/              # Utilities, mock data
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Regulatory Compliance

TrialGuard AI is designed to meet the requirements of:

- **ICH E6(R2) GCP** — Good Clinical Practice guidelines
- **FDA 21 CFR Part 11** — Electronic records and signatures
- **EU CTR 536/2014** — European Clinical Trials Regulation
- **HIPAA** — Protected health information safeguards
- **GDPR** — Data protection and privacy
- **ALCOA+** — Data integrity principles (Attributable, Legible, Contemporaneous, Original, Accurate + Complete, Consistent, Enduring, Available)

---

## Document Types Supported

- Clinical Study Protocols & Amendments
- Informed Consent Forms (ICF)
- Investigator's Brochures (IB)
- Clinical Study Reports (CSR)
- Case Report Forms (CRF)
- Serious Adverse Event (SAE) Reports
- IRB/IEC Approval Letters
- Trial Master File (TMF) — all 11 DIA Reference Model zones
- Monitoring Visit Reports
- Delegation Logs
- Investigator CVs & GCP Certificates
- Regulatory Correspondence

---

## License

Proprietary — Clinical Operations
