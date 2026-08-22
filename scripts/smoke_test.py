#!/usr/bin/env python3
"""End-to-end smoke test: paper diagram types + source code mode.

Matches GenerateRequest: diagram_type is class|object|component|package
(flowchart is not in the API schema). Sync generate requires async_mode=false
so the artifact is in the HTTP response. skip_vlm=true keeps this a render
smoke, not a full 3-VLM scoring run.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

import requests

API = "http://127.0.0.1:8000"
ROOT = Path(__file__).resolve().parent.parent
SAMPLE_REQ_FILE = ROOT / "sample_data" / "requirements.txt"
SAMPLE_CODE_FILE = ROOT / "sample_data" / "sample_code.py"

# Paper types only — same Literal as app.schemas.DiagramType
DIAGRAM_TYPES = ["class", "object", "component", "package"]

SAMPLE_CODE = '''class User:
    def authenticate(self, password: str) -> bool:
        return True

class Order:
    def total(self) -> float:
        return 0.0
'''


def _requirement() -> str:
    if SAMPLE_REQ_FILE.is_file():
        for line in SAMPLE_REQ_FILE.read_text(encoding="utf-8").splitlines():
            if line.strip():
                return line.strip()
    return "Design a hospital appointment system for patients, doctors, and clinic schedules."


def _sample_code() -> str:
    if SAMPLE_CODE_FILE.is_file():
        text = SAMPLE_CODE_FILE.read_text(encoding="utf-8").strip()
        if text:
            return text
    return SAMPLE_CODE


def main() -> int:
    health = requests.get(f"{API}/api/settings/health", timeout=10)
    health.raise_for_status()
    print("Health:", health.json().get("provider_summary") or health.json().get("provider"))

    requirement = _requirement()
    print(f"Requirement: {requirement}")

    failures = 0
    for dtype in DIAGRAM_TYPES:
        r = requests.post(
            f"{API}/api/generate",
            json={
                "requirement": requirement,
                "diagram_type": dtype,
                "input_mode": "requirement",
                "async_mode": False,
                "skip_vlm": True,
            },
            timeout=180,
        )
        if r.status_code != 200:
            print(f"FAIL {dtype}: HTTP {r.status_code} {r.text[:200]}")
            failures += 1
            continue
        art = r.json()["artifact"]
        ok = art["render_status"] == "success" and "@startuml" in art["plantuml_code"].lower()
        print(
            f"{'OK' if ok else 'FAIL'} {dtype}: render={art['render_status']} "
            f"score={art['composite_score']:.2f} lang={art.get('source_language')}"
        )
        if not ok:
            failures += 1
            print("  validation:", art.get("validation_messages"))

    r = requests.post(
        f"{API}/api/generate",
        json={
            "requirement": _sample_code(),
            "diagram_type": "class",
            "input_mode": "source_code",
            "async_mode": False,
            "skip_vlm": True,
        },
        timeout=180,
    )
    if r.status_code != 200:
        print(f"FAIL source_code: HTTP {r.status_code}")
        failures += 1
    else:
        art = r.json()["artifact"]
        ok = (
            art["render_status"] == "success"
            and art.get("input_mode") == "source_code"
            and art.get("source_language") == "python"
        )
        print(f"{'OK' if ok else 'FAIL'} source_code: render={art['render_status']} lang={art.get('source_language')}")
        if not ok:
            failures += 1

    if failures:
        print(f"\nSmoke test FAILED ({failures} cases)")
        return 1
    print("\nSmoke test PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
