import os
import requests
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

from prompt import AI_PROMPT_TEMPLATE


def get_ai_risk_explanation(document_risk, analysis):
    prompt = AI_PROMPT_TEMPLATE.format(
        document_risk=document_risk,
        analysis=analysis
    )

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a legal risk analysis assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    response = requests.post(DEEPSEEK_URL, headers=headers, json=payload)
    response.raise_for_status()

    ai_text = response.json()["choices"][0]["message"]["content"]

    return ai_text
