#!/usr/bin/env python3
"""Run the Atlas voice-stack bake-off against one real course benchmark.

Configured by environment variables. The script deliberately records observed
wall-clock timings and HTTP outcomes only. It does not invent quality scores.

VoiceStudio:
  VOICESTUDIO_URL=http://127.0.0.1:PORT
  VOICESTUDIO_MODEL=omnivoice
  VOICESTUDIO_VOICE=default

Voicebox:
  VOICEBOX_URL=http://127.0.0.1:17493
  VOICEBOX_PROFILE=<profile-name-or-id>
  VOICEBOX_ENGINE=<optional-engine>

Pipecat / PhoneLLM OpenAI-compatible endpoint:
  PIPECAT_CHAT_URL=https://.../v1/chat/completions
  PIPECAT_API_KEY=...
  PIPECAT_MODEL=pipecat-ai/phonellm-alpha-1

The Pipecat leg tests the conversational brain/tool-call path. It does not
claim end-to-end audio latency unless the configured endpoint exposes the
actual real-time audio pipeline.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CORPUS = json.loads((ROOT / "benchmark_corpus.json").read_text())


def http_json(url: str, payload: dict, headers: dict | None = None, timeout: int = 120):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
            elapsed = time.perf_counter() - started
            return r.status, data, elapsed, None
    except Exception as exc:
        elapsed = time.perf_counter() - started
        return None, b"", elapsed, str(exc)


def run_voicestudio():
    base = os.getenv("VOICESTUDIO_URL")
    if not base:
        return {"status": "BLOCKED", "reason": "VOICESTUDIO_URL not configured"}
    model = os.getenv("VOICESTUDIO_MODEL", "omnivoice")
    voice = os.getenv("VOICESTUDIO_VOICE", "default")
    rows = []
    for p in CORPUS["passages"]:
        status, audio, elapsed, err = http_json(
            base.rstrip("/") + "/v1/audio/speech",
            {"model": model, "input": p["text"], "voice": voice, "response_format": "wav"},
            timeout=300,
        )
        rows.append({
            "id": p["id"], "http_status": status, "wall_seconds": round(elapsed, 3),
            "bytes": len(audio), "error": err,
        })
    return {"status": "REAL" if all(r["http_status"] == 200 for r in rows) else "PARTIAL", "rows": rows}


def poll_voicebox(base: str, generation_id: str, timeout: int = 300):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(base.rstrip("/") + f"/generate/{generation_id}/status", timeout=30) as r:
                data = json.loads(r.read())
            state = data.get("status") or data.get("state")
            if state in {"completed", "complete", "failed", "error"}:
                return data
        except Exception as exc:
            return {"status": "error", "error": str(exc)}
        time.sleep(0.5)
    return {"status": "timeout"}


def run_voicebox():
    base = os.getenv("VOICEBOX_URL")
    profile = os.getenv("VOICEBOX_PROFILE")
    if not base or not profile:
        return {"status": "BLOCKED", "reason": "VOICEBOX_URL and VOICEBOX_PROFILE required"}
    engine = os.getenv("VOICEBOX_ENGINE")
    rows = []
    for p in CORPUS["passages"]:
        payload = {"text": p["text"], "profile": profile, "language": "en"}
        if engine:
            payload["engine"] = engine
        status, body, elapsed, err = http_json(base.rstrip("/") + "/speak", payload, timeout=60)
        row = {"id": p["id"], "http_status": status, "submit_seconds": round(elapsed, 3), "error": err}
        if status == 200:
            try:
                response = json.loads(body)
                gid = response.get("id")
                if gid:
                    done_started = time.perf_counter()
                    final = poll_voicebox(base, gid)
                    row["generation_seconds"] = round(time.perf_counter() - done_started + elapsed, 3)
                    row["generation"] = final
            except Exception as exc:
                row["parse_error"] = str(exc)
        rows.append(row)
    return {"status": "REAL" if all(r["http_status"] == 200 for r in rows) else "PARTIAL", "rows": rows}


def run_phone_llm():
    url = os.getenv("PIPECAT_CHAT_URL")
    if not url:
        return {"status": "BLOCKED", "reason": "PIPECAT_CHAT_URL not configured"}
    model = os.getenv("PIPECAT_MODEL", "pipecat-ai/phonellm-alpha-1")
    key = os.getenv("PIPECAT_API_KEY", "")
    headers = {"Authorization": f"Bearer {key}"} if key else {}

    tool = {
        "type": "function",
        "function": {
            "name": "course_lookup",
            "description": "Look up authoritative Atlas course facts.",
            "parameters": {"type": "object", "properties": {"topic": {"type": "string"}}, "required": ["topic"]},
        },
    }
    prompts = [
        "Explain identity proofing in plain English.",
        "What evidence would be needed to test the working hypothesis?",
        "Quiz me on the evidence lab and do not give me the answer before I respond.",
        "Look up the authoritative course facts for identity proofing.",
    ]
    rows = []
    for prompt in prompts:
        status, body, elapsed, err = http_json(
            url,
            {"model": model, "messages": [{"role": "user", "content": prompt}], "tools": [tool], "tool_choice": "auto"},
            headers=headers,
            timeout=180,
        )
        row = {"prompt": prompt, "http_status": status, "wall_seconds": round(elapsed, 3), "error": err}
        if body:
            try:
                data = json.loads(body)
                msg = (data.get("choices") or [{}])[0].get("message") or {}
                row["tool_calls"] = msg.get("tool_calls") or []
                row["text"] = msg.get("content") or ""
            except Exception as exc:
                row["parse_error"] = str(exc)
        rows.append(row)
    return {"status": "REAL" if all(r["http_status"] == 200 for r in rows) else "PARTIAL", "rows": rows}


def main():
    run_id = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    result = {
        "run_id": run_id,
        "course_id": CORPUS["course_id"],
        "started_at": run_id,
        "candidates": {
            "voicestudio": run_voicestudio(),
            "voicebox": run_voicebox(),
            "pipecat_phonellm": run_phone_llm(),
        },
    }
    out = ROOT / f"results-{run_id}.json"
    out.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"\nRESULT_FILE={out}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
