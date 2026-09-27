# JanSetu — Production Deployment & Authentication Guide

JanSetu is an autonomous, sovereign citizen welfare continuity engine designed for high availability, bank-grade authentication persistence, and unified cross-platform branding.

---

## 1. High-Level Architecture Overview

```
                      ┌──────────────────────────────────────┐
                      │          Citizens / Clients          │
                      │   (Web Browser, PWA, Android, iOS)   │
                      └──────────────────┬───────────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 │                                               │
                 ▼ HTTPS (Port 443)                              ▼ HTTPS (Port 443)
    ┌─────────────────────────┐                     ┌─────────────────────────┐
    │     AWS CloudFront      │                     │     Application Load    │
    │  Global CDN Distribution │                     │      Balancer (ALB)     │
    └────────────┬────────────┘                     └────────────┬────────────┘
                 │ S3 Origin                                     │ Forward (Port 8000)
                 ▼                                               ▼
    ┌─────────────────────────┐                     ┌─────────────────────────┐
    │     AWS S3 Bucket       │                     │    AWS ECS (Fargate)    │
    │   (React 18 + Vite PWA) │                     │     FastAPI Backend     │
    │   Branded Static Assets │                     │  (Gunicorn + Uvicorn)   │
    └─────────────────────────┘                     └────────────┬────────────┘
                                                                 │
                                          ┌──────────────────────┴──────────────────────┐
                                          │                                             │
                                          ▼                                             ▼
                             ┌─────────────────────────┐                   ┌─────────────────────────┐
                             │    AWS RDS PostgreSQL   │                   │   Google Gemini API &   │
                             │ (Authoritative Sessions │                   │    Google OAuth 2.0     │
                             │ & Entitlement Engine)   │                   │     Identity Provider   │
                             └─────────────────────────┘                   └─────────────────────────┘
```

---

## 2. Master Brand Identity & Asset Architecture

The official JanSetu visual identity is established with the master squircle shield logo (golden Setu bridge, citizen figures holding hands, sun radiance, embossed "JanSetu" wordmark, and sovereign tagline *"DISCOVER. VERIFY. ACT. PROTECT."*).

### A. Master Asset Location
- **Web Central Repository**: `frontend/public/brand/jansetu-logo-master.png` (1254 × 1254 RGBA PNG with anti-aliased transparency)
- **Mobile Central Repository**: `mobile/assets/branding/jansetu-logo.png` (1024 × 1024 RGBA PNG)

### B. Derived Assets Generated
To regenerate or inspect derived assets at any time, run:
```bash
python scripts/generate_brand_assets.py
```

| Asset Path | Dimensions | Platform / Usage |
| :--- | :--- | :--- |
| `frontend/public/brand/favicon.ico` | Multi-size (16, 32, 48) | Desktop web browser tab icon |
| `frontend/public/brand/favicon-16x16.png` | 16 × 16 px | Standard browser tab favicon |
| `frontend/public/brand/favicon-32x32.png` | 32 × 32 px | High-DPI browser tab favicon |
| `frontend/public/brand/apple-touch-icon.png` | 180 × 180 px | iOS Safari "Add to Home Screen" |
| `frontend/public/brand/icon-192.png` | 192 × 192 px | PWA install manifest standard icon |
| `frontend/public/brand/icon-512.png` | 512 × 512 px | PWA splash / install banner icon |
| `frontend/public/brand/icon-maskable-512.png` | 512 × 512 px | Android adaptive PWA maskable icon |
| `frontend/public/brand/jansetu-icon.png` | 512 × 512 px | Cropped luminous bridge brand mark |
| `mobile/android/.../mipmap-*` | 48 to 192 px | Android home screen launcher icons |
| `mobile/android/.../drawable/` | 432 × 432 px | Android 8.0+ adaptive icon foreground |
| `mobile/android/.../launch_background.xml`| Vector + PNG | Deep midnight navy (`#060A12`) launch splash |
| `mobile/ios/.../AppIcon.appiconset/` | 20 to 1024 px | Full iOS AppIcon suite (iPhone & iPad) |

### C. Reusable Brand Components
- **Web (React)**: `frontend/src/components/common/JanSetuBrand.tsx`
  - `<JanSetuBrand variant="full" size="lg" showTagline={true} />` (Auth pages, Splash)
  - `<JanSetuBrand variant="compact" size="sm" />` (Topbar, App Shell)
  - `<JanSetuBrand variant="icon" size="sm" />` (Buttons, Compact indicators)
- **Mobile (Flutter)**: `mobile/lib/shared/widgets/jansetu_brand.dart`
  - `JanSetuBrand(variant: JanSetuBrandVariant.full, size: JanSetuBrandSize.lg)`
  - `JanSetuBrand(variant: JanSetuBrandVariant.compact, size: JanSetuBrandSize.sm)`
  - `JanSetuBrand(variant: JanSetuBrandVariant.icon, size: JanSetuBrandSize.sm)`

---

## 3. Production Authentication Architecture

JanSetu implements a dual-path production authentication system with PostgreSQL as the authoritative source of truth:

### Path A: Normal Account Registration & Login
1. **RFC 5322 Compliant Email Validation**: Accepts Gmail, Outlook, iCloud, Yahoo, Proton, corporate, and regional educational TLDs.
2. **E.164 Phone Normalization**: Accepts raw Indian numbers (`9876543210`, `09876543210`, `+91 98765 43210`) and standardizes them to `+91XXXXXXXXXX`.
3. **Argon2id Password Hashing**: Passwords undergo memory-hard, GPU-resistant Argon2id hashing with unique cryptographic salts.
4. **Rate Limiting**: Auth endpoints (`/api/auth/register`, `/api/auth/login`) enforce sliding-window brute-force defense (5 requests / 60 seconds per IP).

### Path B: Continue with Google (OAuth 2.0)
1. **CSRF Nonce Protection**: The backend generates a signed cryptographic `state` token cached for 10 minutes.
2. **Permanent Identity Mapping**: Google identities are mapped via immutable `sub` IDs in the `auth_identities` table.
3. **Safe Account Linking**: If a user previously registered with email+password and subsequently clicks "Continue with Google" using the identical email address, JanSetu securely prompts and links the Google identity without creating duplicate citizen records.
4. **Session Cookie**: Auth issue an HTTP-only, SameSite-protected `jansetu_session` cookie backed by database records in `auth_sessions`.

---

## 4. Google Cloud Console Configuration Guide

To enable Google OAuth in development, staging, or production:

### Step 1: Open Google Cloud Console
1. Navigate to: [https://console.cloud.google.com/](https://console.cloud.google.com/)
2. Select or create your Google Cloud Project: `JanSetu-Production`.

### Step 2: Configure OAuth Consent Screen
1. In the left navigation menu, go to **APIs & Services** > **OAuth consent screen** (or **Audience** / **Branding** in newer interfaces).
2. Choose **User Type**:
   - Select **External** (allows any Google account holder to authenticate).
   - Click **Create**.
3. **App Information**:
   - **App name**: `JanSetu`
   - **User support email**: Your support or admin email.
   - **App logo**: Upload `frontend/public/brand/jansetu-logo-master.png`.
   - **Application home page**: `https://jansetu.gov.in` (or your domain).
   - **Application privacy policy link**: `https://jansetu.gov.in/privacy`
   - **Application terms of service link**: `https://jansetu.gov.in/terms`
   - **Authorized domains**: Add `jansetu.gov.in` (and your cloud domain).
   - **Developer contact information**: Your email address.
   - Click **Save and Continue**.
4. **Scopes**:
   - Click **Add or Remove Scopes**.
   - Select the 3 standard userinfo scopes:
     - `.../auth/userinfo.email`
     - `.../auth/userinfo.profile`
     - `openid`
   - Click **Update** > **Save and Continue**.
5. **Publishing Status**:
   - In development/testing, you can add test emails.
   - For live launch, click **Publish App** to move from *Testing* to *Production*.

### Step 3: Create OAuth 2.0 Client Credentials
1. In the left navigation menu, click **Credentials**.
2. Click **+ Create Credentials** at the top > select **OAuth client ID**.
3. **Application type**: Select **Web application**.
4. **Name**: `JanSetu Production Web Client`
5. **Authorized JavaScript origins**:
   - Development: `http://localhost:5173`, `http://localhost:3000`
   - Production: `https://jansetu.gov.in`, `https://app.jansetu.gov.in`
6. **Authorized redirect URIs**:
   - Development: `http://localhost:8000/api/auth/google/callback`
   - Production: `https://api.jansetu.gov.in/api/auth/google/callback`
7. Click **Create**.
8. A modal appears displaying your **Client ID** and **Client Secret**. Copy both immediately.

---

## 5. Environment Variables Configuration

### Backend (`backend/.env`)
```bash
# Environment Mode
ENVIRONMENT=production
DEBUG=false

# Authoritative Database (AWS RDS PostgreSQL with SSL)
DATABASE_URL=postgresql+asyncpg://jansetu_admin:SUPER_SECRET_PASSWORD@jansetu-db.cr12345.ap-south-1.rds.amazonaws.com:5432/jansetu_prod?ssl=require

# Cookie Security & Domain
COOKIE_SECURE=true
COOKIE_SAMESITE=lax
COOKIE_DOMAIN=.jansetu.gov.in

# Cryptographic Session Secrets
JWT_SECRET=generate_using_openssl_rand_hex_64
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Google OAuth 2.0 Credentials
GOOGLE_CLIENT_ID=YOUR_CLIENT_ID.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-YOUR_CLIENT_SECRET
GOOGLE_REDIRECT_URI=https://api.jansetu.gov.in/api/auth/google/callback
FRONTEND_URL=https://jansetu.gov.in

# AI Entitlement Continuity Engine
GEMINI_API_KEY=AIzaSy_YOUR_PRODUCTION_GEMINI_KEY
```

### Frontend (`frontend/.env`)
```bash
VITE_API_URL=https://api.jansetu.gov.in
```

---

## 6. Database Migration (PostgreSQL / Alembic)

Run database migrations on the target RDS instance prior to starting container tasks:

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Verify current revision
alembic current

# Run migrations to latest head
alembic upgrade head

# Verify deployment readiness via Python check
python -c "
import asyncio
from app.db.session import engine
from sqlalchemy import text

async def check():
    async with engine.connect() as conn:
        res = await conn.execute(text('SELECT count(*) FROM users'))
        print('PostgreSQL DB connection verified! User count:', res.scalar())

asyncio.run(check())
"
```

---

## 7. Containerization & Production Build

### A. Frontend Dockerfile (`frontend/Dockerfile`)
```dockerfile
# Stage 1: Build Vite React bundle
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Serve via Nginx with SPA routing & high-performance caching
FROM nginx:1.25-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### B. Frontend Nginx Configuration (`frontend/nginx.conf`)
```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Static assets caching
    location ~* \.(ico|css|js|gif|jpeg|jpg|png|woff2|woff|ttf|svg|eot)$ {
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
        access_log off;
    }

    # SPA routing fallback
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### C. Backend Dockerfile (`backend/Dockerfile`)
```dockerfile
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Run non-root user for security
RUN useradd -m jansetu && chown -R jansetu:jansetu /app
USER jansetu

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--proxy-headers"]
```

---

## 8. AWS Production Deployment Steps

### Step 1: AWS RDS PostgreSQL Setup
1. Create a VPC with 2 public subnets and 2 private subnets across availability zones (e.g. `ap-south-1a`, `ap-south-1b`).
2. Provision **Amazon RDS for PostgreSQL** (Version 15 or 16):
   - Instance Class: `db.t4g.medium` (or larger for production).
   - Storage: 50GB gp3 with Auto-scaling enabled.
   - Multi-AZ: Enabled for high availability failover.
   - Subnet Group: Private DB Subnets.
   - Security Group: Inbound Port 5432 allowed *only* from the ECS Backend Security Group.
   - Enable encryption at rest using AWS KMS.

### Step 2: Build & Push Images to Amazon ECR
```bash
# Authenticate Docker to AWS ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com

# Build & Push Backend
docker build -t jansetu-backend:latest ./backend
docker tag jansetu-backend:latest <AWS_ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/jansetu-backend:latest
docker push <AWS_ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/jansetu-backend:latest

# Build & Push Frontend
docker build -t jansetu-frontend:latest ./frontend
docker tag jansetu-frontend:latest <AWS_ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/jansetu-frontend:latest
docker push <AWS_ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/jansetu-frontend:latest
```

### Step 3: Configure AWS Secrets Manager
Store sensitive credentials in AWS Secrets Manager:
- Secret Name: `prod/jansetu/backend`
- Keys:
  - `DATABASE_URL`
  - `JWT_SECRET`
  - `GOOGLE_CLIENT_ID`
  - `GOOGLE_CLIENT_SECRET`
  - `GEMINI_API_KEY`

### Step 4: Provision ECS Fargate Service
1. Create an ECS Cluster: `jansetu-production-cluster`.
2. Define Task Definition `jansetu-backend-task`:
   - Launch type: `FARGATE`
   - CPU: 1 vCPU (1024), Memory: 2 GB (2048)
   - Map container port `8000`.
   - Inject environment variables from AWS Secrets Manager.
3. Attach to **Application Load Balancer (ALB)**:
   - HTTPS Listener on port 443 with ACM SSL Certificate for `api.jansetu.gov.in`.
   - Target Group Health Check path: `/api/health`.

### Step 5: Provision S3 & CloudFront for Frontend Web App
1. Create S3 Bucket `jansetu-web-production` (Private, Block all public access).
2. Configure AWS CloudFront Distribution:
   - Origin: `jansetu-web-production` via Origin Access Control (OAC).
   - Custom SSL Certificate via ACM (`us-east-1` for CloudFront): `jansetu.gov.in`.
   - Default Root Object: `index.html`.
   - Custom Error Response: HTTP 403 & 404 redirected to `/index.html` with response code 200 (SPA client routing).
3. Deploy build output:
   ```bash
   cd frontend
   npm run build
   aws s3 sync dist/ s3://jansetu-web-production/ --delete
   aws cloudfront create-invalidation --distribution-id <DISTRIBUTION_ID> --paths "/*"
   ```

---

## 9. Verification & Health Monitoring

### A. Deployment Readiness Check
JanSetu includes an automated pre-flight readiness endpoint that validates database connectivity, schema integrity, and authentication identity tables:

```bash
curl -X GET https://api.jansetu.gov.in/api/deployment/readiness
```

**Expected Response**:
```json
{
  "ready": true,
  "environment": "production",
  "database": "connected",
  "auth_schema": {
    "users_table": true,
    "identities_table": true,
    "sessions_table": true
  },
  "readiness_score": 100
}
```

### B. Healthcheck Endpoint
```bash
curl -I https://api.jansetu.gov.in/api/health
# HTTP/1.1 200 OK
```

### C. Live Brand & Favicon Audit
Verify in your browser:
- `https://jansetu.gov.in/brand/favicon.ico`
- `https://jansetu.gov.in/brand/jansetu-logo-master.png`
- `https://jansetu.gov.in/manifest.json`

---

## 10. Summary Checklist for Release

- [x] Official JanSetu master logo integrated without distortion across Web, PWA, Android, and iOS.
- [x] High-resolution derived assets generated (`favicon.ico`, `favicon-16x16`, `favicon-32x32`, `apple-touch-icon`, `icon-192`, `icon-512`, `icon-maskable-512`).
- [x] PWA manifest updated with proper title `JanSetu` and official brand icons.
- [x] Web root `index.html` updated with official favicons, OpenGraph metadata, and title `JanSetu`.
- [x] Reusable `<JanSetuBrand />` and `JanSetuBrand()` components created for Web and Flutter.
- [x] Login, Register, Forgot Password, and App Shell headers upgraded to use the official logo with atmospheric glow.
- [x] Android launcher mipmap icons and adaptive icon XMLs generated.
- [x] iOS AppIcon and LaunchImage suites configured.
- [x] Production authentication verified with 20/20 passing tests (Normal account + Google OAuth 2.0).
- [x] Zero build errors on frontend (`npm run build` completed cleanly).
