#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${1:-project-95a57dd6-b093-4c73-919}"
REGION="asia-southeast2"
SERVICE_NAME="aqruntime-workdoc"

echo "=================================================================="
echo " Deploying AQRuntime WorkDoc to Google Cloud Run"
echo " Project : ${PROJECT_ID}"
echo " Region  : ${REGION}"
echo " Service : ${SERVICE_NAME}"
echo "=================================================================="

gcloud config set project "${PROJECT_ID}"

echo "[1/3] Enabling required Google Cloud APIs (Cloud Run, Cloud Build, Artifact Registry)..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  storage.googleapis.com

PROJECT_NUMBER="$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')"
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
echo "Granting Cloud Build permissions to ${COMPUTE_SA}..."
for ROLE in roles/storage.admin roles/artifactregistry.writer roles/logging.logWriter roles/cloudbuild.builds.builder; do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${COMPUTE_SA}" \
    --role="${ROLE}" \
    --condition=None \
    --quiet >/dev/null
done

EXTRA_ENV=""
if [ -n "${GEMINI_API_KEY:-}" ]; then
  echo "Detected GEMINI_API_KEY in environment; enabling Gemini Cloud + Gemma GGUF hybrid mode..."
  EXTRA_ENV="--set-env-vars=GEMINI_API_KEY=${GEMINI_API_KEY}"
fi

echo "[2/3] Building container image & deploying to Cloud Run (this takes ~5-8 minutes on first build while downloading Gemma 2 2B GGUF)..."
gcloud run deploy "${SERVICE_NAME}" \
  --source . \
  --region "${PROJECT_ID:+${REGION}}" \
  --allow-unauthenticated \
  --cpu 4 \
  --memory 8Gi \
  --concurrency 1 \
  --min-instances 0 \
  --max-instances 1 \
  --timeout 300 \
  --port 8080 \
  --quiet \
  ${EXTRA_ENV}

echo "[3/3] Fetching live Cloud Run URL..."
SERVICE_URL="$(gcloud run services describe "${SERVICE_NAME}" --region "${REGION}" --format='value(status.url)')"

echo "=================================================================="
echo " DEPLOYMENT SUCCESSFUL!"
echo " Live Control Center : ${SERVICE_URL}/ui"
echo " Live WorkDoc Demo   : ${SERVICE_URL}/workdoc"
echo " Health Check        : ${SERVICE_URL}/health"
echo "=================================================================="
