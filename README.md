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

```text
                         JANSETU (जनसेतु)
                                │
                ┌───────────────┴───────────────┐
                │                               │
             WEB APP                       MOBILE APP
       React 19 + TypeScript             Flutter + Dart
       (Vite + Tailwind CSS)           (Android & iOS)
                │                               │
                └───────────────┬───────────────┘
                                │
                            HTTPS API
                                │
                             FastAPI
                         (Python 3.14)
                                │
                           PostgreSQL
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
           Documents         Schemes            Gemini
       (Sovereign Vault) (Statutory Rules) (Agent Assist)
              │                 │                 │
              └─────────────────┴─────────────────┘
```

---

## 🛠️ Technology Stack

| Component | Technology | Description |
|---|---|---|
| **Web Frontend** | React 19, TypeScript, Vite | Ultra-fast client-side reactive architecture |
| **Mobile App (Android/iOS)** | Flutter 3.47, Dart 3.13 | Native cross-platform application with custom glassmorphism |
| **Styling & Design** | Custom Glass Design System | Custom design tokens, Outfit & Noto Sans typography, Frosted GlassSelect |
| **Backend Framework** | FastAPI (Python 3.14) | Asynchronous REST API with Pydantic validation |
| **Database & ORM** | PostgreSQL 15, SQLAlchemy 2.0 (Asyncpg) | Real relational persistence, user isolation, and audit logging |
| **Database Migrations**| Alembic | Transactional schema migrations |
| **AI & LLM Provider** | Google Gemini (`google-genai`) | Autonomous agent tool-calling with deterministic fallback |
| **Object Storage** | `DocumentStorageProvider` | Local storage with AWS S3 & Google Cloud Storage abstraction |
| **Testing Suite** | Pytest, Asyncpg, Flutter Test | 128 backend tests + 9 mobile Flutter test suites |

---

## 🚀 Quickstart & Installation

### Prerequisites
- Docker and Docker Compose
- Node.js (v18+)
- Python 3.10+ (Python 3.14 supported)
- Flutter SDK 3.47+ (for Mobile App)

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

### 5. Run Web Frontend
```bash
cd ../frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

### 6. Run Mobile Application (Flutter)
```bash
cd ../mobile
flutter pub get
flutter run
```
To run tests:
```bash
flutter test
```
To build release APK:
```bash
flutter build apk --release
```

---

## 🧪 Testing & Verification

JanSetu features an exhaustive test suite verifying real PostgreSQL persistence, user isolation, document byte round-trips, agent tool execution, official handoffs, and native mobile presentation.

### Backend Test Suite (Pytest)
```bash
cd backend
pytest tests -v
```
```text
======================= 128 passed, 28 warnings in 133.45s =======================
✓ test_phase8a_storage_provider (Local, Path Traversal, S3/Cloud Abstraction, Factory)
✓ test_phase8b_gemini_agent (Tool Calling, Error Handling, Graceful Degradation)
✓ test_phase8c_application_journey (Complete Workflow, Pinning, Official Handoff)
✓ test_document_persistence_roundtrip (SHA-256 Byte Verification, Download Authorization)
✓ test_real_authentication & citizen_isolation (Multi-tenant Security, Session TTL)
✓ test_ramesh_agent_end_to_end & test_ramesh_full_welfare_workflow
```

### Mobile Test Suite (Flutter)
```bash
cd mobile
flutter test
```
```text
00:00 +0: JanSetu Tokens & Theme Tests Colors match web tokens exactly
00:00 +1: JanSetu Tokens & Theme Tests Dark theme configuration is valid
00:00 +2: ApiException Mapping Tests Correct mapping for HTTP 401
00:00 +3: ApiException Mapping Tests Correct mapping for HTTP 422
00:00 +4: ApiException Mapping Tests Network and timeout error mapping
00:00 +5: Localization Tests English and Hindi strings have parity
00:00 +6: Data Model Parsing Tests SchemeBenefitModel correctly parses backend payload
00:00 +7: Data Model Parsing Tests WelfareStateModel correctly parses metrics
00:00 +8: GlassCard Widget Test Renders child inside frosted container
00:00 +9: All tests passed!
```

---

---

## 🔐 Production Authentication Architecture

JanSetu implements a hardened, dual-path production authentication system with PostgreSQL as the authoritative source of record:

### Path A — Sovereign Normal Account
- **Registration Fields**: Full Name, Email Address, Mobile Number, Password, Confirm Password.
- **Email Validation**: General RFC-compliant regex supporting all legitimate domains (`@gmail.com`, `@icloud.com`, `@outlook.com`, `@yahoo.com`, `@company.com`, `@university.ac.in`). No hardcoded whitelist.
- **Mobile Number Normalization**: Automatically normalizes Indian mobile numbers from formats like `+91 98765 43210`, `09876543210`, or `9876543210` to canonical E.164 `+91XXXXXXXXXX`.
- **Database Enforced Uniqueness**: Unique constraints on `users.email`, `users.mobile_number`, and `users.phone`.
- **Password Security**: Argon2 password hashing with cryptographically random salts; passwords are never logged, stored in plain text, or exposed to the client.
- **Transactional Consistency**: Atomically creates Citizen, Identity, User, AuthIdentity, and AuthSession in a single atomic database transaction.

### Path B — Real Google OAuth 2.0 / OpenID Connect
- **Real Authorization Code Flow**: Redirects to `accounts.google.com/o/oauth2/v2/auth`.
- **Identity Scopes**: Minimal requested scopes (`openid`, `email`, `profile`).
- **CSRF Protection**: Time-limited cryptographic state nonce validated on callback.
- **Stable Provider Identity**: Uses Google's permanent subject ID (`sub`), stored in `auth_identities(provider, provider_subject)`.
- **Safe Account Linking Flow**: If a user already created a password account with `email@example.com` and later clicks *Continue with Google*, JanSetu detects the collision and requires password authentication to safely link the Google identity without duplicating accounts.
- **Onboarding Route**: Google users are directed to Onboarding to provide their required sovereign mobile number.

---

## 🔑 Google Cloud Console OAuth 2.0 Setup Guide

To configure real Google Sign-In for JanSetu:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing project (e.g., `JanSetu-Production`).
3. Navigate to **APIs & Services** > **OAuth consent screen**:
   - User Type: **External**
   - App Name: `JanSetu`
   - User Support Email: your administrative email
   - Scopes: Add `.../auth/userinfo.email`, `.../auth/userinfo.profile`, `openid`
4. Navigate to **APIs & Services** > **Credentials**:
   - Click **Create Credentials** > **OAuth client ID**
   - Application type: **Web application**
   - Name: `JanSetu Web Client`
   - **Authorized redirect URIs**:
     - Local Development: `http://localhost:8000/api/auth/google/callback` and `http://localhost:8000/auth/google/callback`
     - Production: `https://api.jansetu.in/api/auth/google/callback` and `https://api.jansetu.in/auth/google/callback`
5. Click **Create** and securely copy the generated **Client ID** and **Client Secret**.
6. Store them in AWS Secrets Manager (Production) or `.env` (Local):
   ```env
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret
   GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
   ```

---

## 🚀 AWS Production Deployment Handoff

```text
               INTERNET
                  │
                  ▼
        Amazon CloudFront CDN (HTTPS)
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
  Amazon S3 Bucket    Application Load Balancer (ALB)
  (React PWA Static)        │ (HTTPS Target Group)
                            ▼
                     Amazon ECS Fargate
                    (FastAPI Containers)
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
 Amazon RDS PostgreSQL   Amazon S3 Bucket   AWS Secrets Manager
 (Authoritative DB)     (Encrypted Vault)   (Credentials & Keys)
```

### Production Environment Variables (AWS Secrets Manager)
```env
DATABASE_URL=postgresql+asyncpg://<db_user>:<db_pass>@<rds_endpoint>:5432/jansetu_db
SESSION_SECRET=<cryptographically-random-64-byte-key>
SECRET_KEY=<cryptographically-random-64-byte-key>
GEMINI_API_KEY=<production-google-gemini-key>
GOOGLE_CLIENT_ID=<google-client-id>
GOOGLE_CLIENT_SECRET=<google-client-secret>
GOOGLE_REDIRECT_URI=https://api.jansetu.in/api/auth/google/callback
AWS_REGION=ap-south-1
S3_BUCKET=jansetu-citizen-evidence-ap-south-1
CORS_ORIGINS=https://jansetu.in,https://app.jansetu.in
```

### Step-by-Step Deployment Commands

```bash
# 1. Build and verify frontend production bundle
cd frontend
npm run build

# 2. Authenticate Docker with Amazon ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.ap-south-1.amazonaws.com

# 3. Build & tag Docker backend container
cd ../backend
docker build -t jansetu-backend:latest .
docker tag jansetu-backend:latest <aws_account_id>.dkr.ecr.ap-south-1.amazonaws.com/jansetu-backend:latest
docker push <aws_account_id>.dkr.ecr.ap-south-1.amazonaws.com/jansetu-backend:latest

# 4. Run Alembic migrations against AWS RDS PostgreSQL
alembic upgrade head

# 5. Deploy ECS Task & Service
aws ecs update-service --cluster jansetu-production --service jansetu-backend-service --force-new-deployment

# 6. Deploy React PWA build to S3 & invalidate CloudFront cache
cd ../frontend
aws s3 sync dist/ s3://jansetu-frontend-web/ --delete
aws cloudfront create-invalidation --distribution-id <DISTRIBUTION_ID> --paths "/*"
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

