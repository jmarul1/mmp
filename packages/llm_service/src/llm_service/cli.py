import rich_click as click
from rich import print as rprint


@click.command()
def run_llm_service():
    """Launch LLM Hosting"""
    from os import environ
    from subprocess import Popen, DEVNULL, run
    from time import sleep

    quantization = "8_0"
    env = environ.copy()
    env["OLLAMA_FLASH_ATTENTION"] = "1"
    env["OLLAMA_KV_CACHE_TYPE"] = f"q{quantization}"
    server_cmd = ["/opt/homebrew/opt/ollama/bin/ollama", "serve"]
    rprint("🚀 Starting Ollama Server ...")
    rprint(f"🧠 Optimizations: Flash Attention [ON], KV Cache [Q{quantization}]")
    server_process = Popen(server_cmd, env=env, stdout=DEVNULL, stderr=DEVNULL)
    while not is_service_ready():
        sleep(0.5)
        if server_process.poll() is not None:
            rprint("❌ Server failed to start.")
            return
    rprint("✅ OLlama is LIVE @ http://localhost:11434")
    rprint("⌨️  Press Ctrl+C to shut down and free your RAM.")
    try:
        server_process.wait()
    except KeyboardInterrupt:
        rprint("\n🛑 Shutdown signal received...")
    finally:
        server_process.terminate()
        run(["killall", "ollama"], stderr=DEVNULL)
        rprint("✨ RAM cleared. Server closed.")


def is_service_ready() -> None:
    from http.client import HTTPConnection

    try:
        conn = HTTPConnection("localhost", 11434, timeout=1)
        conn.request("GET", "/")
        response = conn.getresponse()
        return response.status == 200
    except:
        return False


if __name__ == "__main__":
    run_llm_service()
