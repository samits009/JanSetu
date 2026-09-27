# JanSetu (जनसेतु) — Sovereign Welfare Continuity & Portability Platform

> **Built for Bit N Build 2026 State Round Hackathon — Problem Statement 2**  
> *Autonomous, sovereign, and deterministic welfare continuity across India's federal structure.*

---

## 🌟 Overview

Across India, millions of unorganized, migrant, and construction workers lose access to critical welfare benefits—such as the Building and Other Construction Workers (BOCW) welfare pensions, One Nation One Ration Card (ONORC) food subsidies, and healthcare coverages—simply by crossing state boundaries or changing jobs.

**JanSetu (जनसेतु)** is an entitlement portability and welfare continuity platform built to bridge this statutory divide. It pairs a **deterministic statutory policy engine** with **cryptographically verified citizen evidence**, an **interactive sovereign AI navigator powered by Google Gemini**, and an **atmospheric glassmorphic interface** localized in both English and Hindi.

---

## 🛡️ Core Architectural Pillars

### 1. Deterministic Rule Authority (No Hallucinated Benefits)
- **PolicyRuleEngine is authoritative**: Eligibility is mathematically derived by statutory rule matching against verified claims in PostgreSQL.
- **AI Agent Guardrails**: The Google Gemini AI Assistant uses tool calling against registered domain services (`evaluate_welfare_state`, `prepare_application`, `request_consent`, etc.). It never invents policies, benefits, or government responses.

### 2. Sovereign Citizen Evidence Vault
- **Cryptographic Byte Verification**: Every citizen document (BOCW card, Aadhaar, Worker ID, Salary slips) is hashed with SHA-256 and stored via an abstract `DocumentStorageProvider` (supporting local encrypted storage, AWS S3, and Google Cloud Storage).
- **Verified Fact Reuse**: Extracted facts are validated and stored as sovereign evidence rows, automatically satisfying statutory requirements across state and national programs.

### 3. Complete End-to-End Application Workflow
- **Continuous Lifecycle**:
  $$\text{Benefit Discovery} \longrightarrow \text{Why This May Apply} \longrightarrow \text{Evidence Readiness} \longrightarrow \text{Application Preparation} \longrightarrow \text{Citizen Review} \longrightarrow \text{Explicit Sovereign Consent} \longrightarrow \text{Official Government Portal Handoff} \longrightarrow \text{Lifecycle Tracking} \longrightarrow \text{Recovery}$$
- **Authentic Government Integration Rule**: Where direct machine APIs do not exist, JanSetu complies dossiers with sovereign provenance references (e.g., `JS-HANDOFF-XXXX`) and directs citizens to official portals (*e-District Delhi*, *National Food Security Portal Annavitran*, *UP BOCW Portal*).

### 4. Custom JanSetu Glass Design System
- **Cinematic Atmospheric Aesthetics**: Deep midnight navy backdrop (`#060a12`), blurred environmental horizon with Setu bridge silhouette, and warm champagne/gold highlights (`#f5c77c`).
- **Premium GlassSelect Dropdown System**: Fully custom frosted glass dropdowns featuring:
  - All **28 States** and **8 Union Territories** categorized and grouped
  - Dynamic cascading district selection
  - Real-time search with instant filtering
  - Keyboard navigation (Arrow keys, Enter, Escape, Home, End)
  - Intelligent upward/downward collision detection
  - Responsive mobile bottom sheet presentation
  - Zero browser-native select menus

### 5. 100% Bilingual Parity (English ↔ Hindi)
- Instant bidirectional switching with server-persisted user preferences.
- Localized UI strings, forms, validation messages, scheme descriptions, legal consent terms, and agent guidance.

---

## 🏗️ System Architecture

```mermaid
graph TD
    subgraph Frontend ["Frontend (React 19 + TypeScript + Vite)"]
        UI[JanSetu Glassmorphic UI]
        GS[Custom GlassSelect System]
        LANG[Bilingual Context EN / HI]
        AGENT_UI[Gemini Welfare Drawer]
    end

    subgraph Backend ["Backend (FastAPI + Async Python 3.14)"]
        API[FastAPI Gateway]
        AUTH[Real Session & Cookie Auth]
        POLICY[Deterministic Policy Rule Engine]
        DOC_SVC[Document & Storage Service]
        APP_SVC[Application State Machine]
        GEMINI_AGENT[Welfare Agent Engine]
        HANDOFF[Official Portal Handoff Provider]
    end

    subgraph Storage ["Persistence & Storage Tier"]
        PG[(PostgreSQL 15)]
        DOC_STORE[Document Storage Local / S3 / GCS]
    end

    UI --> API
    GS --> UI
    LANG --> UI
    AGENT_UI --> API
    API --> AUTH
    API --> POLICY
    API --> DOC_SVC
    API --> APP_SVC
    API --> GEMINI_AGENT
    APP_SVC --> HANDOFF
    AUTH --> PG
    POLICY --> PG
    DOC_SVC --> PG
    DOC_SVC --> DOC_STORE
    APP_SVC --> PG
```

---

## 🛠️ Technology Stack

| Component | Technology | Description |
|---|---|---|
| **Frontend Framework** | React 19, TypeScript, Vite | Ultra-fast client-side reactive architecture |
| **Styling & Design** | Vanilla Glassmorphism CSS | Custom design tokens, Outfit & Noto Sans typography |
| **Backend Framework** | FastAPI (Python 3.14) | Asynchronous REST API with Pydantic validation |
| **Database & ORM** | PostgreSQL 15, SQLAlchemy 2.0 (Asyncpg) | Real relational persistence, user isolation, and audit logging |
| **Database Migrations**| Alembic | Transactional schema migrations |
| **AI & LLM Provider** | Google Gemini (`google-genai`) | Autonomous agent tool-calling with deterministic fallback |
| **Object Storage** | `DocumentStorageProvider` | Local storage with AWS S3 & Google Cloud Storage abstraction |
| **Testing Suite** | Pytest, AnyIO, Asyncpg | 128 comprehensive automated integration and unit tests |

---

## 🚀 Quickstart & Installation

### Prerequisites
- Docker and Docker Compose
- Node.js (v18+)
- Python 3.10+ (Python 3.14 supported)

### 1. Clone the Repository
```bash
git clone https://github.com/samits009/JanSetu.git
cd JanSetu
```

### 2. Environment Configuration
Copy the example environment file:
```bash
cp .env.example .env
```
Key variables:
```env
DATABASE_URL=postgresql+asyncpg://jansetu_user:jansetu_password@127.0.0.1:5433/jansetu_db
DOCUMENT_STORAGE_PROVIDER=local
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Run with Docker Compose
```bash
docker compose up -d db
```

### 4. Run Backend
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
alembic upgrade head
python setup_db.py
uvicorn app.main:app --reload --port 8000
```

### 5. Run Frontend
```bash
cd ../frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🧪 Testing & Verification

JanSetu features an exhaustive test suite verifying real PostgreSQL persistence, user isolation, document byte round-trips, agent tool execution, and official handoffs.

```bash
cd backend
pytest tests -v
```

### Test Suite Results:
```text
======================= 128 passed, 28 warnings in 133.45s =======================
✓ test_phase8a_storage_provider (Local, Path Traversal, S3/Cloud Abstraction, Factory)
✓ test_phase8b_gemini_agent (Tool Calling, Error Handling, Graceful Degradation)
✓ test_phase8c_application_journey (Complete Workflow, Pinning, Official Handoff)
✓ test_document_persistence_roundtrip (SHA-256 Byte Verification, Download Authorization)
✓ test_real_authentication & citizen_isolation (Multi-tenant Security, Session TTL)
✓ test_ramesh_agent_end_to_end & test_ramesh_full_welfare_workflow
```

---

## 👥 Hackathon Team & Author

- **Author**: Samit Shukla
- **Email**: [samit.ss.shukla@gmail.com](mailto:samit.ss.shukla@gmail.com)
- **GitHub**: [@samits009](https://github.com/samits009)
- **Project Repository**: [https://github.com/samits009/JanSetu](https://github.com/samits009/JanSetu)

---

## 📜 License
This project is developed for the **Bit N Build 2026 State Round Hackathon**.
