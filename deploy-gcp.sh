#!/bin/bash
# JanSetu - Google Cloud Run Deployment Script
# 
# Before running:
#   1. Copy .env.gcp.example to .env.gcp and fill in your values
#   2. Run: gcloud auth login
#   3. Run: bash deploy-gcp.sh
#
# Secrets are loaded from .env.gcp (gitignored) - never hardcoded here.

set -e

# Load secrets from local .env.gcp file
if [ ! -f ".env.gcp" ]; then
  echo "ERROR: .env.gcp not found. Copy .env.gcp.example and fill in your values."
  exit 1
fi
source .env.gcp

# Config (non-secret)
REGION="asia-south1"
REPO="jansetu-repo"
BACKEND_IMAGE="${REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${REPO}/backend:latest"
FRONTEND_IMAGE="${REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${REPO}/frontend:latest"

echo "=== JanSetu GCP Deployment ==="
echo "Project: $GCP_PROJECT_ID | Region: $REGION"

# 1. Set project
gcloud config set project "$GCP_PROJECT_ID"

# 2. Enable required APIs
gcloud services enable run.googleapis.com artifactregistry.googleapis.com

# 3. Create Artifact Registry repo (idempotent)
gcloud artifacts repositories create "$REPO" \
  --repository-format=docker \
  --location="$REGION" \
  --description="JanSetu container images" 2>/dev/null || echo "Repo already exists"

# 4. Configure Docker auth for Artifact Registry
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

# 5. Build & push BACKEND
echo -e "\n--- Building & pushing backend ---"
docker build -t "$BACKEND_IMAGE" ./backend
docker push "$BACKEND_IMAGE"

# 6. Deploy BACKEND to Cloud Run
echo -e "\n--- Deploying backend to Cloud Run ---"
gcloud run deploy jansetu-backend \
  --image "$BACKEND_IMAGE" \
  --platform managed \
  --region "$REGION" \
  --port 8080 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 3 \
  --set-env-vars "DATABASE_URL=${DATABASE_URL}" \
  --set-env-vars "SECRET_KEY=${SECRET_KEY}" \
  --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY}" \
  --set-env-vars "GEMINI_MODEL=gemini-1.5-flash" \
  --set-env-vars "GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}" \
  --set-env-vars "GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}" \
  --set-env-vars "DEV_MOCK_ADMIN_AUTH=false" \
  --set-env-vars "DEV_DEMO_AUTH=false" \
  --timeout 300

# Capture backend URL
BACKEND_URL=$(gcloud run services describe jansetu-backend \
  --platform managed --region "$REGION" --format 'value(status.url)')
echo "✓ Backend URL: $BACKEND_URL"

# Update GOOGLE_REDIRECT_URI now that we have the real URL
gcloud run services update jansetu-backend \
  --platform managed \
  --region "$REGION" \
  --update-env-vars "GOOGLE_REDIRECT_URI=${BACKEND_URL}/api/auth/google/callback"

echo -e "\n--- Building & pushing frontend ---"
docker build \
  --build-arg VITE_API_BASE_URL="$BACKEND_URL" \
  -t "$FRONTEND_IMAGE" ./frontend
docker push "$FRONTEND_IMAGE"

# Deploy FRONTEND
gcloud run deploy jansetu-frontend \
  --image "$FRONTEND_IMAGE" \
  --platform managed \
  --region "$REGION" \
  --port 80 \
  --allow-unauthenticated \
  --memory 256Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 2

FRONTEND_URL=$(gcloud run services describe jansetu-frontend \
  --platform managed --region "$REGION" --format 'value(status.url)')
echo "✓ Frontend URL: $FRONTEND_URL"

# Wire frontend URL back into backend
gcloud run services update jansetu-backend \
  --platform managed \
  --region "$REGION" \
  --update-env-vars "FRONTEND_URL=${FRONTEND_URL}"

echo ""
echo "=============================="
echo "✅ JanSetu Deployed on GCP!"
echo "=============================="
echo "Backend:  $BACKEND_URL"
echo "Frontend: $FRONTEND_URL"
echo "Health:   ${BACKEND_URL}/api/health"
echo ""
echo "Next: Update Google OAuth Authorized URIs in Google Cloud Console:"
echo "  Origins:  $FRONTEND_URL"
echo "  Redirect: ${BACKEND_URL}/api/auth/google/callback"
