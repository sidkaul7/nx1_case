import subprocess
import os

def run_llama3(prompt, model=None):
    """
    Run a prompt through the local Ollama LLM.
    Returns the model's output as a string.
    """
    # Only use model from .env file
    model = os.getenv("OLLAMA_MODEL")
    if not model:
        raise ValueError("OLLAMA_MODEL environment variable not set")
        
    # If this hangs, check that Ollama is running and the model is available.
    result = subprocess.run([
        "ollama", "run", model, prompt
    ], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Ollama returned an error: {result.stderr.strip()} (model: {model})")
    return result.stdout.strip()

if __name__ == "__main__":
    # Quick test: classify a sample acquisition event
    prompt = "You are an expert in SEC filings. Classify this event: Apple acquired a startup."
    print(run_llama3(prompt))
