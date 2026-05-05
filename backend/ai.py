import httpx
import os
import json
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

async def explain_error(logs: list, error_on_chain: dict):
    
    logs_text = "\n".join(logs)
    error_text = json.dumps(error_on_chain)

    prompt = f"""You are a Solana blockchain expert. A developer got this failed transaction.

Transaction logs:
{logs_text}

Error on chain:
{error_text}

Give a response in this exact JSON format:
{{
  "explanation": "plain English explanation of what went wrong (2-3 sentences)",
  "root_cause": "one line: the exact root cause",
  "fix": "exact code or steps to fix this",
  "severity": "one of: funds / config / bug / cpi"
}}

Return ONLY the JSON. No extra text. No markdown. No backticks."""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "SolanaDebugger"
    }

    body = {
        "model": "anthropic/claude-3.5-haiku",
        "max_tokens": 1000,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=body
        )
        data = response.json()

    if "choices" not in data:
        return {
            "explanation": f"AI error: {data}",
            "root_cause": "OpenRouter API issue",
            "fix": "Check API key and credits on openrouter.ai",
            "severity": "config"
        }

    raw = data["choices"][0]["message"]["content"].strip()

    if not raw:
        return {
            "explanation": "AI returned empty response",
            "root_cause": "Empty response from model",
            "fix": "Try again",
            "severity": "config"
        }

    # strip markdown backticks if model added them anyway
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        return {
            "explanation": "AI returned invalid JSON response",
            "root_cause": "Model formatting error",
            "fix": "Try again or check error format",
            "severity": "config"
        }