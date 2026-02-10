import requests
import streamlit as st
import os

# --------------------
# configs
# --------------------
OLLAMA_URL = "http://localhost:11434/api/generate"
LOCAL_MODEL = "llama3.1:8b"

CLOUD_URL = "https://api.together.xyz/v1/chat/completions"
CLOUD_MODEL = "meta-llama/Meta-Llama-3.1-8B-Instruct"


# --------------------
# secrets loader
# --------------------
def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key)


def get_cloud_key():
    return get_secret("TOGETHER_API_KEY")


# --------------------
# cloud
# --------------------
def summarize_cloud(prompt):

    CLOUD_KEY = get_cloud_key()

    if CLOUD_KEY is None:
        raise Exception("Missing Together API key")

    response = requests.post(
        CLOUD_URL,
        headers={
            "Authorization": f"Bearer {CLOUD_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": CLOUD_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        },
        timeout=60
    )

    if response.status_code != 200:
        raise Exception(f"Cloud LLM error: {response.text}")

    data = response.json()
    return data["choices"][0]["message"]["content"]


# --------------------
# local
# --------------------
def summarize_local(prompt):

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": LOCAL_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
    except requests.exceptions.ConnectionError:
        raise Exception("Ollama não está rodando")

    if response.status_code != 200:
        raise Exception("Local LLM error")

    return response.json()["response"]


# --------------------
# router inteligente
# --------------------
@st.cache_data(ttl=3600)
def summarize_news(text, context=""):

    prompt = f"""
Você é um especialista de mercado financeiro.

Contexto: {context}

Gere um insight estruturado destacando:
- Tendências principais
- Riscos relevantes
- Oportunidades identificadas

Notícias:
{text}
"""

    # texto pequeno → tenta cloud primeiro
    if len(text) < 6000:
        try:
            return summarize_cloud(prompt)
        except Exception as cloud_error:
            print("Cloud error:", cloud_error)

            try:
                return summarize_local(prompt)
            except Exception as local_error:
                print("Local error:", local_error)
                return "⚠️ Não foi possível gerar o insight automaticamente no momento."

    # texto grande → usa local direto
    else:
        try:
            return summarize_local(prompt)
        except Exception as local_error:
            print("Local error:", local_error)
            return "⚠️ Não foi possível gerar o insight automaticamente no momento."


# --------------------
# UI teste standalone
# --------------------
if __name__ == "__main__":

    st.title("News Summarizer (Hybrid LLM)")

    context = st.text_input("Contexto (opcional)")
    text = st.text_area("Texto da notícia")

    if st.button("Resumir"):
        if text.strip() == "":
            st.warning("Digite um texto.")
        else:
            with st.spinner("Gerando resumo..."):
                result = summarize_news(text, context)

            st.success("Resumo gerado")
            st.write(result)
