import httpx

url = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct/v1/chat/completions"
# Needs a valid HF token usually, but even without it we should get 401 Unauthorized instead of 410 Gone to prove the route exists.
try:
    res = httpx.post(url, json={"model": "meta-llama/Meta-Llama-3-8B-Instruct", "messages": [{"role": "user", "content": "Hello"}]}, timeout=5.0)
    print(f"Llama 3 Chat Completions: {res.status_code}")
except Exception as e:
    print(f"Llama 3 Error {e}")
