# pip install transformers torch
from transformers import AutoTokenizer, T5ForConditionalGeneration
import torch

# ---------------------------
# Load CodeT5-small model
# ---------------------------
model_name = "Salesforce/codet5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

# Use GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# ---------------------------
# Function to fix or suggest code
# ---------------------------
def fix_code(code_snippet):
    # Prepare prompt for CodeT5
    prompt = f"fix the python code:\n{code_snippet}"
    
    # Tokenize input
    inputs = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
    
    # Generate output
    outputs = model.generate(
        inputs, 
        max_length=200,       # max tokens in output
        num_beams=5,          # beam search for better results
        early_stopping=True
    )
    
    # Decode and return text
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# ---------------------------
# Main program
# ---------------------------
if __name__ == "__main__":
    print("=== Python Bug Fixer ===")
    print("Type your Python code below. Type 'exit' to quit.\n")
    
    while True:
        # Take multi-line input
        print("Enter your code (end with an empty line):")
        lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            lines.append(line)
        code_input = "\n".join(lines)
        
        if code_input.lower() == "exit":
            print("Bye!")
            break
        
        # Generate fix
        result = fix_code(code_input)
        print("\n--- Suggested Fix / Output ---")
        print(result)
        print("-------------------------------\n")
