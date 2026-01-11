# codem.py
# pip install transformers torch

from transformers import AutoTokenizer, T5ForConditionalGeneration
import torch

# ---------------------------
# Load CodeT5-small model
# ---------------------------
model_name = "Salesforce/codet5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# ---------------------------
# Helper function to check syntax
# ---------------------------
def is_valid_python(code):
    try:
        compile(code, "<string>", "exec")
        return True
    except SyntaxError:
        return False

# ---------------------------
# Function to fix code
# ---------------------------
def fix_code(code_snippet, instruction="Fix the Python code so it runs correctly"):
    # Build prompt
    prompt = f"# {instruction}:\n{code_snippet}\n# Fixed version:"
    
    # Tokenize and send to model
    inputs = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
    outputs = model.generate(
        inputs,
        max_length=200,
        num_beams=5,
        early_stopping=True
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# ---------------------------
# Main program
# ---------------------------
if __name__ == "__main__":
    print("=== Python Bug Fixer ===")
    print("Type your Python code below. Type 'exit' to quit.\n")
    
    while True:
        # Multi-line input
        print("Enter your code (end with an empty line):")
        lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            if line.lower().strip() == "exit":
                print("Bye!")
                exit()
            lines.append(line)
        code_input = "\n".join(lines)
        
        if not code_input.strip():
            continue  # skip empty input
        
        # Optional: detect syntax errors first
        if not is_valid_python(code_input):
            print("\n[Notice] Your code has a syntax error. Trying to fix...")
        
        # Get fixed version
        fixed_code = fix_code(code_input)
        
        print("\n--- Suggested Fix / Output ---")
        print(fixed_code)
        print("-------------------------------\n")
