import os
import math
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from tokenizers import ByteLevelBPETokenizer
from transformers import GPT2TokenizerFast
from tqdm import tqdm
from model import MiniTransformer, generate_sample

# Tokenizer Trainer
def train_tokenizer():
    files = ["corpus.txt"]
    tokenizer = ByteLevelBPETokenizer()
    tokenizer.train(
        files=files,
        vocab_size=50000,
        min_frequency=2,
        special_tokens=["<s>", "<pad>", "</s>", "<unk>", "<mask>"]
    )
    save_dir = "vamp-tokenizer"
    os.makedirs(save_dir, exist_ok=True)
    tokenizer.save_model(save_dir)
    print("Tokenizer trained and saved to 'vamp-tokenizer/'")

# Dataset for code files
class CodeDataset(Dataset):
    def __init__(self, data_dir, tokenizer, seq_len=256):
        self.examples = []
        for root, _, files in os.walk(data_dir):
            for fname in files:
                if not fname.endswith('.py'):
                    continue
                with open(os.path.join(root, fname), 'r', encoding='utf-8') as f:
                    text = f.read()
                tokens = tokenizer(text, add_special_tokens=True).input_ids
                for i in range(0, len(tokens) - seq_len, seq_len):
                    self.examples.append(tokens[i:i+seq_len])

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        return torch.tensor(self.examples[idx], dtype=torch.long)

# Training loop
def train_model(data_dir, model, tokenizer, epochs=50, batch_size=4, lr=3e-4, device='cpu'):
    dataset = CodeDataset(data_dir, tokenizer)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss(ignore_index=tokenizer.pad_token_id)

    for epoch in range(1, epochs+1):
        model.train()
        total_loss = 0
        for batch in tqdm(dataloader, desc=f"Epoch {epoch}/{epochs}", leave=False):
            optimizer.zero_grad()
            batch = batch.to(device)
            logits = model(batch)
            loss = loss_fn(logits.view(-1, tokenizer.vocab_size), batch.view(-1))
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch} — Avg Loss: {total_loss/len(dataloader):.4f}")

    torch.save(model.state_dict(), "vamp_model.pth")
    print("Model training complete. Saved to 'vamp_model.pth'")

if __name__ == "__main__":
    # Uncomment to train tokenizer
    # train_tokenizer()

    tokenizer = GPT2TokenizerFast(
        vocab_file="vocab.json",
        merges_file="merges.txt",
        unk_token="<unk>", pad_token="<pad>",
        bos_token="<s>", eos_token="</s>",
        mask_token="<mask>"
    )
    model = MiniTransformer(vocab_size=tokenizer.vocab_size)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    train_model(data_dir="data", model=model, tokenizer=tokenizer, epochs=150, device=device)
