"""
Wraps all Gemini calls. The schema/prompt here are copy-identical to the
Colab notebook (../notebook/PitchPolish_Gemini_Prototype.ipynb) — prototype
prompt changes there first since iteration is faster, then sync back here.
"""
import os
import time
import json
import tempfile

from google import genai
from google.genai import types

MODEL = "gemini-2.5-flash"

_client = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable is not set.")
        _client = genai.Client(api_key=api_key)
    return _client


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

    response = client.models.generate_content(
        model=MODEL,
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
    gemini_file_name = scorecard.get("_gemini_file_name")

    grounding_prompt = f"""You have already watched the attached pitch video and produced this scorecard:
{json.dumps({k: v for k, v in scorecard.items() if not k.startswith('_')})}

Answer the user's question ONLY using what you observed in the video and the scorecard above. If asked to predict interviewer questions, ground them in specific, real moments from the pitch (reference timestamps).

User question: {question}"""

    if gemini_file_name:
        gfile = client.files.get(name=gemini_file_name)
        contents = [gfile, grounding_prompt]
    else:
        # Gemini file store entries expire after ~48h — fall back to text-only grounding.
        contents = [grounding_prompt]

    response = client.models.generate_content(model=MODEL, contents=contents)
    return response.text
