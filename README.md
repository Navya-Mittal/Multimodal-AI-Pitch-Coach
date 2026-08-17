# PitchPolish — Multimodal AI Pitch Coach

Upload a pitch video → Gemini scores it on 5 axes → chat with an AI grounded on your own pitch.

## What's in this repo

```
notebook/   Colab notebook — run this FIRST to validate the Gemini call with your API key
backend/    FastAPI service (Gemini calls, MongoDB, GCS)
frontend/   React + TypeScript + Tailwind UI
```

## Fastest path to a working demo tonight

### 1. Validate the AI piece in Colab (10 min)
Upload `notebook/PitchPolish_Gemini_Prototype.ipynb` to [Google Colab](https://colab.research.google.com),
get a free API key from [Google AI Studio](https://aistudio.google.com/apikey), and run all cells with a
short test video. This confirms the scorecard prompt/schema actually works before you touch the app.

### 2. Run the backend locally
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # paste your GEMINI_API_KEY in here
# MongoDB: easiest is a free MongoDB Atlas cluster — paste its connection string into MONGO_URI
uvicorn main:app --reload --port 8000
```
Visit http://localhost:8000/api/health — should return `{"status": "ok"}`.

### 3. Run the frontend locally
```bash
cd frontend
npm install
npm run dev
```
Visit http://localhost:5173 — upload a video, watch it hit your local backend.

### 4. Deploy (Cloud Run — matches the "100% Google stack" framing on your resume)

**Backend:**
```bash
cd backend
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

gcloud run deploy pitchpolish-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your-key,MONGO_URI=your-atlas-uri,USE_GCS=true,GCS_BUCKET=your-bucket
```

**Frontend:**
```bash
cd frontend
# point it at your deployed backend URL
echo "VITE_API_BASE=https://pitchpolish-backend-xxxxx.a.run.app/api" > .env.production

gcloud run deploy pitchpolish-frontend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

**GCS bucket** (for storing uploaded videos in prod):
```bash
gsutil mb -l us-central1 gs://your-bucket-name
```

**MongoDB:** create a free-tier cluster at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas),
add your Cloud Run service's IP (or `0.0.0.0/0` for quick demo purposes) to network access, and copy the
connection string into `MONGO_URI`.

## Known gaps / what to build next if time allows
- No auth — sessions are unlisted-by-ID, fine for a hackathon demo, not for real users.
- No retry/backoff on the Gemini call — if it times out on a long video, the request just fails.
- Chat re-fetches the Gemini file reference each time; Gemini's file store entries expire after ~48h,
  so old sessions' chat will silently fall back to text-only grounding (see `gemini_service.py`).
- `google-genai` SDK method names shift between versions — if a call errors after `pip install`, check
  the current docs at ai.google.dev; the notebook is the fastest place to confirm the exact call shape.
