"""
Wraps all Gemini calls. The schema/prompt here are copy-identical to the
Colab notebook (../notebook/Pitch_Perfect_Gemini_Prototype.ipynb) — prototype
prompt changes there first since iteration is faster, then sync back here.
"""
import os
import time
import json
import tempfile

from google import genai
from google.genai import types
from google.genai.errors import ServerError

MODEL = "gemini-2.5-flash"
FALLBACK_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash"]  # tried in order

_client = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable is not set.")
        _client = genai.Client(api_key=api_key)
    return _client


def _generate_with_retry(client, **kwargs):
    """Gemini's free tier occasionally returns 503 UNAVAILABLE under load.
    For each model in FALLBACK_MODELS, retry a few times with backoff; if a model
    is still down after its retries, fall through to the next model in the list
    rather than failing the whole request outright."""
    last_error = None
    for model in FALLBACK_MODELS:
        call_kwargs = {**kwargs, "model": model}
        for attempt in range(3):
            try:
                response = client.models.generate_content(**call_kwargs)
                if model != FALLBACK_MODELS[0]:
                    print(f"Succeeded using fallback model: {model}")
                return response
            except ServerError as e:
                last_error = e
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    wait = 5 * (attempt + 1)  # 5s, 10s, 15s
                    print(f"{model} 503 (attempt {attempt + 1}/3), retrying in {wait}s...")
                    time.sleep(wait)
                    continue
                raise
        print(f"{model} exhausted retries, falling back to next model...")
    raise last_error


SCORECARD_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "axes": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "name": {
                        "type": "STRING",
                        "enum": ["Clarity", "Pacing", "Technical Depth", "Storytelling", "Slide Quality"],
                    },
                    "score": {"type": "INTEGER", "description": "Score from 1-10"},
                    "critiques": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "note": {"type": "STRING"},
                                "timestamp_seconds": {"type": "INTEGER"},
                            },
                            "required": ["note", "timestamp_seconds"],
                        },
                    },
                    "rewrite_suggestion": {"type": "STRING"},
                },
                "required": ["name", "score", "critiques", "rewrite_suggestion"],
            },
        },
        "overall_summary": {"type": "STRING"},
    },
    "required": ["axes", "overall_summary"],
}

SCORECARD_PROMPT = """You are an expert hackathon/pitch coach reviewing a student's pitch video.

Watch and listen to the full video. Score it on exactly these 5 axes: Clarity, Pacing, Technical Depth, Storytelling, Slide Quality.

For each axis:
- Give a score from 1-10
- Give exactly 2 specific critiques, each grounded to a real timestamp in the video (timestamp_seconds must be an actual moment you observed, not a guess)
- Give 1 concrete rewrite suggestion

Be specific and honest — reference what was actually said or shown, not generic pitch advice. Then write a 2-3 sentence overall_summary.
"""


def _upload_and_wait(raw_bytes: bytes, filename: str, content_type: str):
    """Gemini requires files to go through its file store before use in a call."""
    client = get_client()
    suffix = os.path.splitext(filename)[1] or ""
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(raw_bytes)
        tmp_path = tmp.name

    gfile = client.files.upload(file=tmp_path)
    while gfile.state.name == "PROCESSING":
        time.sleep(3)
        gfile = client.files.get(name=gfile.name)

    os.unlink(tmp_path)

    if gfile.state.name == "FAILED":
        raise RuntimeError("Gemini file processing failed.")
    return gfile


def analyze_pitch(raw_bytes: bytes, filename: str, content_type: str) -> dict:
    client = get_client()
    gfile = _upload_and_wait(raw_bytes, filename, content_type)

    response = _generate_with_retry(
        client,
        contents=[gfile, SCORECARD_PROMPT],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SCORECARD_SCHEMA,
        ),
    )
    scorecard = json.loads(response.text)
    # Stash the Gemini file reference name so /api/chat can reuse it without re-uploading.
    scorecard["_gemini_file_name"] = gfile.name
    return scorecard


def ask_pitch_question(file_uri: str, scorecard: dict, question: str) -> str:
    client = get_client()

    # Ground on the saved scorecard (already has timestamped citations) instead of
    # re-sending the full video — video re-processing took 30-60s+ per question,
    # this takes a few seconds since it's text-only.
    grounding_prompt = f"""You already watched this person's pitch video and produced this scorecard:
{json.dumps({k: v for k, v in scorecard.items() if not k.startswith('_')})}

Answer the user's question using ONLY the scorecard above — its scores, critiques, and timestamps. If asked to predict interviewer questions, ground them in the specific critiques and timestamps already noted in the scorecard.

User question: {question}"""

    contents = [grounding_prompt]

    response = _generate_with_retry(client, contents=contents)
    return response.text
