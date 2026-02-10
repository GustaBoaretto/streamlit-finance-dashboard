import requests
import os

API_KEY = os.getenv("TOGETHER_API_KEY")  # ou coloque direto para teste

url = "https://api.together.xyz/v1/chat/completions"

response = requests.post(
    url,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "messages": [
            {"role": "user", "content": "Explique o que é inflação em 2 linhas"}
        ],
        "temperature": 0.3
    }
)

print(response.status_code)
print(response.text)
