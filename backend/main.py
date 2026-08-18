"""
Pitch Perfect backend — FastAPI service.

Flow:
  POST /api/analyze   -> upload video/slides, run Gemini scorecard, persist session
  GET  /api/session/{id} -> fetch a session's scorecard
  POST /api/chat/{id} -> grounded Q&A chat about a specific pitch
  GET  /api/share/{id}-> public, read-only view of a session (for the shareable link)

Run locally:
  uvicorn main:app --reload --port 8000

Deploy: see ../README.md for the Cloud Run steps.
"""
from dotenv import load_dotenv
load_dotenv()

import os
import uuid
import json
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from gemini_service import analyze_pitch, ask_pitch_question
from storage import upload_to_gcs, save_locally
from db import get_db

app = FastAPI(title="Pitch Perfect API")

# Loosen for local dev; tighten allow_origins to your deployed frontend URL in prod.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

USE_GCS = os.getenv("USE_GCS", "false").lower() == "true"


class ChatRequest(BaseModel):
    question: str


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    # Accepts a video file (mp4/mov/webm) or a slide PDF. Returns session_id + scorecard.
    session_id = str(uuid.uuid4())
    raw_bytes = await file.read()

    if len(raw_bytes) > 200 * 1024 * 1024:  # 200MB guardrail
        raise HTTPException(status_code=413, detail="File too large. Keep uploads under 200MB (~3min video).")

    # Persist the raw file (GCS in prod, local disk in dev) so /api/chat can re-ground later.
    if USE_GCS:
        file_uri = upload_to_gcs(session_id, file.filename, raw_bytes)
    else:
        file_uri = save_locally(session_id, file.filename, raw_bytes)

    try:
        scorecard = analyze_pitch(raw_bytes, file.filename, file.content_type)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini analysis failed: {e}")

    db = get_db()
    db.sessions.insert_one({
        "_id": session_id,
        "filename": file.filename,
        "file_uri": file_uri,
        "scorecard": scorecard,
        "chat_history": [],
    })

    return {"session_id": session_id, "scorecard": scorecard}


@app.get("/api/session/{session_id}")
def get_session(session_id: str):
    db = get_db()
    session = db.sessions.find_one({"_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": session_id,
        "filename": session["filename"],
        "scorecard": session["scorecard"],
    }


@app.post("/api/chat/{session_id}")
def chat(session_id: str, req: ChatRequest):
    db = get_db()
    session = db.sessions.find_one({"_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    answer = ask_pitch_question(
        file_uri=session["file_uri"],
        scorecard=session["scorecard"],
        question=req.question,
    )

    db.sessions.update_one(
        {"_id": session_id},
        {"$push": {"chat_history": {"question": req.question, "answer": answer}}},
    )
    return {"answer": answer}


@app.get("/api/share/{session_id}")
def share(session_id: str):
    """Public, read-only view — no auth, this is what the shareable link hits."""
    db = get_db()
    session = db.sessions.find_one({"_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "filename": session["filename"],
        "scorecard": session["scorecard"],
    }
