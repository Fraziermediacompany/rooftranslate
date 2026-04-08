"""Vercel Python serverless entrypoint.

Vercel Python runtime auto-mounts an ASGI `app` symbol exported from this
file. We re-export the FastAPI app from backend.main so a single
codebase serves both `uvicorn backend.main:app` locally and Vercel in prod.
"""
import sys
from pathlib import Path

# Make `backend` importable when Vercel runs from /var/task
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.main import app  # noqa: E402, F401
