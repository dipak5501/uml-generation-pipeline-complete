"""Shared HTTP helpers for Streamlit UI."""

from __future__ import annotations

import os
from typing import Any

import httpx

# Server-side Streamlit → FastAPI must stay on loopback. run_local.sh used to set
# API_BASE_URL to the Wi-Fi IP; that address goes stale and the UI shows
# "API error: timed out" / "System offline".
_configured = (os.getenv("API_BASE_URL") or "http://127.0.0.1:8000").rstrip("/")
if "127.0.0.1" in _configured or "localhost" in _configured:
    API_BASE = _configured
else:
    API_BASE = "http://127.0.0.1:8000"
# Browser-facing links (export downloads) may use the LAN host.
PUBLIC_API_BASE = (os.getenv("PUBLIC_API_BASE_URL") or _configured).rstrip("/")


def _auth_headers() -> dict[str, str]:
    token = (os.getenv("API_ACCESS_TOKEN") or "").strip()
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def api_get(path: str, **params) -> Any:
    timeout = float(params.pop("_timeout", 8.0))
    with httpx.Client(base_url=API_BASE, timeout=timeout, headers=_auth_headers()) as client:
        r = client.get(path, params=params or None)
        r.raise_for_status()
        if "application/json" in r.headers.get("content-type", ""):
            return r.json()
        return r.content


def api_post(path: str, payload: dict) -> Any:
    with httpx.Client(base_url=API_BASE, timeout=600.0, headers=_auth_headers()) as client:
        r = client.post(path, json=payload)
        r.raise_for_status()
        return r.json()


def api_get_bytes(path: str) -> bytes:
    with httpx.Client(base_url=API_BASE, timeout=120.0, headers=_auth_headers()) as client:
        r = client.get(path)
        r.raise_for_status()
        return r.content
