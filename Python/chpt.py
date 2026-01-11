from huggingface_hub import hf_hub_download
from llama_cpp import Llama

print("🔻 Loading model...")

MODEL_REPO = "TheBloke/Mistral-7B-Instruct-v0.2-GGUF"
MODEL_FILE = "mistral-7b-instruct-v0.2.Q4_K_M.gguf"

model_path = hf_hub_download(repo_id=MODEL_REPO, filename=MODEL_FILE)

llm = Llama(
    model_path=model_path,
    n_ctx=8192,
    n_batch=256,
    n_threads=6,
    use_mmap=True,
    use_mlock=True,
    verbose=False
)

history = []

print("\n🔥 OFFLINE GPT READY")
print("Type 'exit' to quit.\n")

while True:
    user = input("You > ").strip()
    if user.lower() in ["exit", "quit"]:
        break

    history.append(f"[INST] {user} [/INST]")
    prompt = "\n".join(history[-6:])

    output = llm(prompt, max_tokens=400, stop=["</s>"])
    reply = output["choices"][0]["text"].strip()

    history.append(reply)
    print("\nAI >", reply, "\n")
