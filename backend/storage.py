"""
File storage. Local disk for dev (fast iteration, no GCP setup needed);
Google Cloud Storage for prod (set USE_GCS=true + GCS_BUCKET env var).
"""
import os

LOCAL_UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(LOCAL_UPLOAD_DIR, exist_ok=True)


def save_locally(session_id: str, filename: str, raw_bytes: bytes) -> str:
    path = os.path.join(LOCAL_UPLOAD_DIR, f"{session_id}_{filename}")
    with open(path, "wb") as f:
        f.write(raw_bytes)
    return path


def upload_to_gcs(session_id: str, filename: str, raw_bytes: bytes) -> str:
    from google.cloud import storage  # imported lazily so local dev doesn't need the package

    bucket_name = os.environ["GCS_BUCKET"]
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob_name = f"pitches/{session_id}/{filename}"
    blob = bucket.blob(blob_name)
    blob.upload_from_string(raw_bytes)
    return f"gs://{bucket_name}/{blob_name}"
