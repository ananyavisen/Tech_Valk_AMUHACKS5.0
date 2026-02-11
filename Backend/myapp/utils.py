import requests
from django.conf import settings

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"

headers = {
    "Authorization": f"Bearer {settings.HF_API_TOKEN}"
}

def get_ai_response(message):

    payload = {
        "inputs": message,
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    result = response.json()

    if isinstance(result, list):
        return result[0]["generated_text"]
    else:
        return "Mentor is thinking... Try again."
