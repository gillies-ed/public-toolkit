"""
Extract structured job fields from plain text using a local OpenAI-compatible LLM endpoint.

Works with Ollama, OpenAI, or any other server that speaks the OpenAI
chat completions API.

Configure via environment:
  LLM_BASE_URL  — base URL of the inference server  (default: http://localhost:11434/v1)
  LLM_MODEL     — model name to request             (default: default)
"""
import json
import re
import httpx

from config import settings
from schemas import ExtractedFields

_SYSTEM_PROMPT = """\
You are a job-application data extractor. Given raw text from a job posting, extract key details
and return them as a single JSON object — no markdown, no explanation, just the JSON object.

Fields to extract:
- company: the hiring company name (string or null)
- position: the job title (string or null)
- wage_max: the MAXIMUM annual salary in GBP as an integer, or null if not stated or if given
  only as a daily/hourly rate that you cannot reliably annualise
- location: the primary city or location (string or null)
- office_days: number of days per week required in office as an integer (0 = fully remote), or null
  if not specified
- agency_name: the recruiting agency name if the role is agency-posted, otherwise null
- agency_or_direct: "Agency" if posted by a recruiter/agency, "Direct" if posted by the company
  itself, or null if unclear

If a field cannot be determined, use null. Do not guess. Return only the JSON object.
"""


def extract_fields(text: str) -> ExtractedFields:
    """Call the local LLM to extract structured fields from *text*."""
    base_url = settings.llm_base_url.rstrip("/")
    payload = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": f"Job posting text:\n\n{text}"},
        ],
        "temperature": 0.1,
        "max_tokens": 512,
    }

    headers = {}
    if settings.llm_api_key:
        headers["Authorization"] = f"Bearer {settings.llm_api_key}"

    with httpx.Client(timeout=60) as client:
        response = client.post(f"{base_url}/chat/completions", json=payload, headers=headers)
        response.raise_for_status()

    raw = response.json()["choices"][0]["message"]["content"].strip()

    # Strip <think>...</think> reasoning blocks (e.g. MiniMax-M2.7)
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

    # Strip markdown code fences if the model adds them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    data = json.loads(raw)
    return ExtractedFields(**data)
