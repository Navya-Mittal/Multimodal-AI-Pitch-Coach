# Pitch Perfect

I built this because I kept running into the same problem: you can practice a pitch or a presentation as many times as you want, but it's genuinely hard to know how it actually lands. You're too close to your own material to catch what's unclear, and reading it off a page doesn't tell you anything about pacing, tone, or whether your slides are pulling their weight.

Pitch Perfect is an AI coach for that. Upload a short video of yourself pitching — a project, a startup idea, a thesis defense, whatever — and it uses Gemini's multimodal API to score you across five axes: clarity, pacing, technical depth, storytelling, and slide quality. Every piece of feedback is tied to a specific timestamp, so instead of "be more confident," you get "at 0:23 you lost the thread explaining your architecture, here's a tighter way to say it." There's also an "Ask my pitch" chat, where you can ask things like *"what would someone ask me after this?"* and get an answer grounded in what you actually said, not generic advice.

## Why Gemini

The core idea only works if one model can watch the video, listen to the audio, and read the slides together — otherwise you're stitching together separate speech-to-text, vision, and language models and losing context between them every time. Gemini 2.5's native multimodal input handles all of that in a single call, which is the real reason I built this on Google's stack rather than piecing together a GPT + Whisper + OCR pipeline.

## What's actually working right now

I'd rather be upfront about where this stands than oversell it:

- **The core AI pipeline is built and validated** — I've run real pitch video through it in Google Colab (see `notebook/Pitch_Perfect_Gemini_Prototype.ipynb`) and gotten back real, grounded, timestamped scorecards. This was the part I was least sure would work well, and it does.
- **The full app is written** — FastAPI backend, React frontend, MongoDB for session storage, all in this repo — but it's running locally, not yet deployed. I prioritized getting the AI pipeline right before spending time on deployment.
- **Next up:** deploy to Cloud Run, add persistent public share links, and keep tuning the prompt against more real pitches.

## Try the AI pipeline yourself (no setup needed)

The fastest way to see this work is the Colab notebook — it doesn't need the rest of the app running:

1. Open `notebook/Pitch_Perfect_Gemini_Prototype.ipynb` in [Google Colab](https://colab.research.google.com)
2. Get a free API key from [Google AI Studio](https://aistudio.google.com/apikey)
3. Upload any short pitch video and run the cells

## Running the full app locally

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your GEMINI_API_KEY
uvicorn main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Visit `localhost:5173`, upload a video, and it'll hit the local backend end-to-end.

## Stack

Gemini 2.5 (multimodal) · FastAPI · React + TypeScript + Tailwind · MongoDB · built for Google Cloud Run

## About me

I'm Navya, a Computer Engineering student at Trinity College Dublin. I like building things where the interesting part is a real judgment call — here, that was betting on native multimodal input instead of a stitched pipeline, and designing the scorecard to cite evidence instead of just outputting a number. Happy to walk through any part of the code or the reasoning behind it.
