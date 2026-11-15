import requests
import time

# The models you currently have + the ones we discussed
MODELS = [
    "llama3.2:3b",
    # "llama3.2-vision:11b",
    # "qwen3.5:35b-a3b-coding-nvfp4",
    # "llama3.3:70b",
]
PROMPT = "Write a high-performance Python function to calculate the dot product of two vectors."
PROMPT = "What are your capabilities"


def test_speed(model_name):
    print(f"\n--- Testing Model: {model_name} ---")
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model_name,
        "prompt": PROMPT,
        "stream": False,
        # "options": {"num_predict": 100},  # Keep it short for a quick test
    }

    try:
        response = requests.post(url, json=payload).json()

        generated_text = response.get("response", "").strip()
        print(f"OUTPUT:\n{generated_text}\n")
        print(f"{'-'*50}")

        load_sec = response.get("load_duration", 0) / 1e9
        p_eval_sec = response.get("prompt_eval_duration", 0) / 1e9
        gen_sec = response.get("eval_duration", 0) / 1e9

        tokens = response.get("eval_count", 0)
        tps = tokens / gen_sec if gen_sec > 0 else 0

        print(f"📦 Load Time:   {load_sec:.2f}s")
        print(
            f"⚡ Prompt Eval: {response.get('prompt_eval_count')} tokens in {p_eval_sec:.2f}s"
        )
        print(f"✍️  Generation:  {tokens} tokens in {gen_sec:.2f}s")
        print(f"🚀 SPEED:       {tps:.2f} tokens/sec")

    except Exception as e:
        print(f"❌ Error testing {model_name}: {e}")


if __name__ == "__main__":
    for model in MODELS:
        test_speed(model)
