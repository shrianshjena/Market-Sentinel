import httpx

models = [
    "HuggingFaceH4/zephyr-7b-beta",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "mistralai/Mistral-7B-Instruct-v0.2",
    "meta-llama/Meta-Llama-3-8B-Instruct",
]

prompt = "<s>[INST] Hello [/INST]"

for m in models:
    url = f"https://api-inference.huggingface.co/models/{m}"
    try:
        res = httpx.post(url, json={"inputs": prompt}, timeout=5.0)
        print(f"{m}: HTTP {res.status_code}")
    except Exception as e:
        print(f"{m}: Error {e}")
