# JanSetu - GCP Cloud Run Deployment Script (PowerShell)
# Run after: billing is enabled + gcloud auth login complete
# Usage: .\deploy-gcp.ps1

$ErrorActionPreference = "Stop"

$GCLOUD = "$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
$REGION = "asia-south1"           # Mumbai - closest to India
$PROJECT_ID = "favorable-tree-318603"
$REPO = "jansetu-repo"
$BACKEND_SERVICE = "jansetu-backend"
$FRONTEND_SERVICE = "jansetu-frontend"
$BACKEND_IMAGE = "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/backend:latest"
$FRONTEND_IMAGE = "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/frontend:latest"

# Secrets - loaded from .env.gcp
$envFile = Join-Path $PSScriptRoot ".env.gcp"
if (-not (Test-Path $envFile)) {
    Write-Error ".env.gcp not found at $envFile"
    exit 1
}
$envVars = @{}
Get-Content $envFile | Where-Object { $_ -match "^[^#].*=.*" } | ForEach-Object {
    $parts = $_ -split "=", 2
    $envVars[$parts[0].Trim()] = $parts[1].Trim()
}

$DATABASE_URL = $envVars["DATABASE_URL"]
$SECRET_KEY = $envVars["SECRET_KEY"]
$GEMINI_API_KEY = $envVars["GEMINI_API_KEY"]
$GOOGLE_CLIENT_ID = $envVars["GOOGLE_CLIENT_ID"]
$GOOGLE_CLIENT_SECRET = $envVars["GOOGLE_CLIENT_SECRET"]

Write-Host "=== JanSetu GCP Cloud Run Deployment ===" -ForegroundColor Cyan
Write-Host "Project: $PROJECT_ID | Region: $REGION" -ForegroundColor Cyan

# 1. Set project
Write-Host "`n[1/8] Setting GCP project..." -ForegroundColor Yellow
& $GCLOUD config set project $PROJECT_ID

# 2. Enable APIs
Write-Host "`n[2/8] Enabling Cloud Run + Artifact Registry APIs..." -ForegroundColor Yellow
& $GCLOUD services enable run.googleapis.com artifactregistry.googleapis.com

# 3. Create Artifact Registry repo
Write-Host "`n[3/8] Creating Artifact Registry repo..." -ForegroundColor Yellow
& $GCLOUD artifacts repositories create $REPO `
    --repository-format=docker `
    --location=$REGION `
    --description="JanSetu container images" 2>&1 | Where-Object { $_ -notmatch "already exists" }

# 4. Configure Docker auth
Write-Host "`n[4/8] Configuring Docker for Artifact Registry..." -ForegroundColor Yellow
& $GCLOUD auth configure-docker "${REGION}-docker.pkg.dev" --quiet

# 5. Build & push backend
Write-Host "`n[5/8] Building backend Docker image..." -ForegroundColor Yellow
docker build -t $BACKEND_IMAGE .\backend
Write-Host "Pushing backend image..." -ForegroundColor Yellow
docker push $BACKEND_IMAGE

# 6. Deploy backend to Cloud Run
Write-Host "`n[6/8] Deploying backend to Cloud Run..." -ForegroundColor Yellow
& $GCLOUD run deploy $BACKEND_SERVICE `
    --image $BACKEND_IMAGE `
    --platform managed `
    --region $REGION `
    --port 8080 `
    --allow-unauthenticated `
    --memory 512Mi `
    --cpu 1 `
    --min-instances 0 `
    --max-instances 3 `
    --set-env-vars "DATABASE_URL=$DATABASE_URL,SECRET_KEY=$SECRET_KEY,GEMINI_API_KEY=$GEMINI_API_KEY,GEMINI_MODEL=gemini-1.5-flash,GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID,GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET,DEV_MOCK_ADMIN_AUTH=false,DEV_DEMO_AUTH=false" `
    --timeout 300

# Get backend URL
$BACKEND_URL = & $GCLOUD run services describe $BACKEND_SERVICE `
    --platform managed --region $REGION --format "value(status.url)"
Write-Host "✓ Backend URL: $BACKEND_URL" -ForegroundColor Green

# Update OAuth redirect URI with real backend URL
& $GCLOUD run services update $BACKEND_SERVICE `
    --platform managed --region $REGION `
    --update-env-vars "GOOGLE_REDIRECT_URI=${BACKEND_URL}/api/auth/google/callback"

# 7. Build & push frontend
Write-Host "`n[7/8] Building frontend Docker image (with backend URL baked in)..." -ForegroundColor Yellow
docker build --build-arg VITE_API_BASE_URL=$BACKEND_URL -t $FRONTEND_IMAGE .\frontend
Write-Host "Pushing frontend image..." -ForegroundColor Yellow
docker push $FRONTEND_IMAGE

# Deploy frontend
& $GCLOUD run deploy $FRONTEND_SERVICE `
    --image $FRONTEND_IMAGE `
    --platform managed `
    --region $REGION `
    --port 80 `
    --allow-unauthenticated `
    --memory 256Mi `
    --cpu 1 `
    --min-instances 0 `
    --max-instances 2

$FRONTEND_URL = & $GCLOUD run services describe $FRONTEND_SERVICE `
    --platform managed --region $REGION --format "value(status.url)"
Write-Host "✓ Frontend URL: $FRONTEND_URL" -ForegroundColor Green

# 8. Wire frontend URL back into backend
Write-Host "`n[8/8] Wiring frontend URL into backend..." -ForegroundColor Yellow
& $GCLOUD run services update $BACKEND_SERVICE `
    --platform managed --region $REGION `
    --update-env-vars "FRONTEND_URL=$FRONTEND_URL"

# Health check
Write-Host "`nRunning health check..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
$health = Invoke-RestMethod -Uri "${BACKEND_URL}/api/health" -ErrorAction SilentlyContinue
Write-Host "Health: $($health | ConvertTo-Json)" -ForegroundColor Green

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "  JanSetu Deployed on Google Cloud!  " -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host "Backend:  $BACKEND_URL" -ForegroundColor White
Write-Host "Frontend: $FRONTEND_URL" -ForegroundColor White
Write-Host "Health:   ${BACKEND_URL}/api/health" -ForegroundColor White
Write-Host ""
Write-Host "NEXT STEP - Update Google OAuth Authorized URIs:" -ForegroundColor Yellow
Write-Host "  Authorized JS Origins:  $FRONTEND_URL" -ForegroundColor Yellow
Write-Host "  Authorized Redirect URI: ${BACKEND_URL}/api/auth/google/callback" -ForegroundColor Yellow
