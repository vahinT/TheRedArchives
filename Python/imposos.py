import os
import subprocess
import sys
import torch
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM

# Auto-install required packages
def ensure_package(pkg):
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

for pkg in ["torch", "transformers"]:
    ensure_package(pkg)

# Model setup
model_name = "Salesforce/codegen-350M-multi"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", torch_dtype=torch.float32)

def ask_codegen_to_fix(code):
    prompt = f"""### Buggy Python Code
{code}

### Fix the code and output only the fixed code:"""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_length=512, temperature=0.5, do_sample=False)
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    fixed_code = decoded.split("### Fix the code and output only the fixed code:")[-1].strip()
    return fixed_code

def main():
    path = input("Enter path to the Python script: ").strip('"')
    if not os.path.exists(path):
        print("[!] File not found.")
        return

    with open(path, "r") as f:
        original_code = f.read()

    temp_dir = os.path.join(os.getenv("TEMP"), "auto_debugger_codegen")
    os.makedirs(temp_dir, exist_ok=True)

    attempt = 1
    while True:
        print(f"\n[INFO] Attempt {attempt} — Running {path}...")
        result = subprocess.run(["python", path], capture_output=True, text=True)
        if result.returncode == 0:
            print("[✓] Code ran successfully!")
            print(result.stdout)
            break

        print("[!] Error detected:")
        print(result.stderr)
        fixed_code = ask_codegen_to_fix(original_code)

        temp_path = os.path.join(temp_dir, f"fixed_attempt_{attempt}.py")
        with open(temp_path, "w") as f:
            f.write(fixed_code)

        print(f"[INFO] Trying fixed code in: {temp_path}")
        path = temp_path
        original_code = fixed_code
        attempt += 1

if __name__ == "__main__":
    main()
