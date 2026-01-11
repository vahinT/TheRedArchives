import torch
from transformers import GPT2TokenizerFast
from model import MiniTransformer, generate_sample

def main():
    tokenizer = GPT2TokenizerFast(
        vocab_file="vamp-tokenizer/vocab.json",
        merges_file="vamp-tokenizer/merges.txt",
        unk_token="<unk>",
        pad_token="<pad>",
        bos_token="<s>",
        eos_token="</s>",
        mask_token="<mask>"
    )
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = MiniTransformer(vocab_size=tokenizer.vocab_size)
    model.load_state_dict(torch.load("vamp_model.pth", map_location=device))
    model.to(device)
    model.eval()
    print("VAMP Ready. Enter 'exit' to quit.")
    while True:
        prompt = input("Prompt> ")
        if prompt.lower() == 'exit':
            print("Goodbye!")
            break
        output = generate_sample(model, tokenizer, prompt=prompt, device=device)
        print(output)

if __name__ == '__main__':
    main()
