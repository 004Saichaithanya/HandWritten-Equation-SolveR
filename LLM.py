# LLM.py — ask OpenRouter to return strict JSON (preferred)
from dotenv import load_dotenv
import os
import requests
import json
import re

load_dotenv()
apikey = os.getenv("OPENROUTER_API_KEY")

def analyze_image(image_url):
    if not apikey:
        raise ValueError("Missing OPENROUTER_API_KEY in .env")

    payload = {
        "model": "qwen/qwen2.5-vl-72b-instruct",
        "messages": [
            {
                "role": "system",
                "content": "You are a careful math assistant. Answer only in JSON format exactly as: "
                           '{"steps": ["step1", "step2", ...], "final_answer": "value"}. '
                           "Do not add any extra text, no explanation outside the JSON."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Carefully solve the mathematical expression in the image. Return only JSON."},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ],
        "max_tokens": 512,
        "temperature": 0.0
    }

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {apikey}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )

    result = response.json()
    print("DEBUG status:", response.status_code)
    print(json.dumps(result, indent=2))

    # defensive extraction
    content = None
    try:
        content = result["choices"][0]["message"]["content"]
    except Exception:
        raise ValueError("API returned unexpected structure: " + json.dumps(result))

    # If content is list (sometimes returned), join text items
    if isinstance(content, list):
        # extract text fields if present
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
            elif isinstance(item, str):
                parts.append(item)
        content_text = "\n".join(parts).strip()
    else:
        content_text = str(content).strip()

    # Try to parse JSON from the content
    try:
        parsed = json.loads(content_text)
        return parsed  # {"steps": [...], "final_answer": "..."}
    except json.JSONDecodeError:
        # fallback: try to extract content inside <Solution> tags and produce simple structure
        m = re.search(r"<Solution>(.*?)</Solution>", content_text, re.S | re.I)
        if m:
            sol_text = m.group(1).strip()
        else:
            sol_text = content_text

        # naive sentence split to steps as fallback
        sentences = [s.strip() for s in re.split(r'(?<=[\.\n])\s+', sol_text) if s.strip()]
        # Heuristic: last sentence likely contains final answer
        final_answer = sentences[-1] if sentences else sol_text
        steps = sentences[:-1] if len(sentences) > 1 else sentences
        return {"steps": steps, "final_answer": final_answer}
