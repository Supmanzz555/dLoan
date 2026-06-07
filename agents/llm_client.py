import os
import re
import time
import json
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")

if LLM_PROVIDER == "openai":
    from openai import OpenAI, RateLimitError
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found. Set it in .env or export it. "
            "Get a key at https://platform.openai.com/api-keys"
        )
    client = OpenAI(api_key=api_key)
    MODEL = "gpt-4o-mini"
else:
    from groq import Groq, RateLimitError
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. Set it in .env or export it. "
            "Get a free key at https://console.groq.com"
        )
    client = Groq(api_key=api_key)
    MODEL = "llama-3.3-70b-versatile"


def _parse_retry_after(error_body: dict) -> int:
    msg = error_body.get("error", {}).get("message", "")
    match = re.search(r"in (\d+)m(\d+)", msg)
    if match:
        return int(match.group(1)) * 60 + int(match.group(2))
    match = re.search(r"in (\d+)s", msg)
    if match:
        return int(match.group(1)) + 5
    return 65


def call_llm(messages: list[dict]) -> dict:
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                messages=messages,
                model=MODEL,
                temperature=0,
                response_format={"type": "json_object"},
            )
            return json.loads(response.choices[0].message.content)
        except RateLimitError as e:
            err_body = getattr(e, "body", {}) or {}
            msg = err_body.get("error", {}).get("message", str(e))
            print(f"  {LLM_PROVIDER} rate limit (attempt {attempt+1}/3): {msg[:100]}...")
            if attempt == 2:
                raise
            wait = _parse_retry_after(err_body)
            print(f"  Waiting {wait}s...")
            time.sleep(wait)
