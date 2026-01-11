# Full code: Vamp Tokenizer Trainer, Model Trainer, Model Saver, and Live Code Generation

import os
import math
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from tokenizers import ByteLevelBPETokenizer
from transformers import GPT2TokenizerFast
from tqdm import tqdm

# -------------------------
# Tokenizer Trainer
# -------------------------
def train_tokenizer():
    files = ["python_corpus.txt"]
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
    print("Tokenizer for Vamp trained and saved!")

# -------------------------
# Code Dataset
# -------------------------
class CodeDataset(Dataset):
    def __init__(self, data_dir: str, tokenizer, seq_len: int = 256):
        self.examples = []
        for root, _, files in os.walk(data_dir):
            for fname in files:
                if not fname.endswith('.py'):
                    continue
                path = os.path.join(root, fname)
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()
                tokens = tokenizer(text, add_special_tokens=True).input_ids
                for i in range(0, len(tokens) - seq_len, seq_len):
                    chunk = tokens[i:i + seq_len]
                    self.examples.append(chunk)

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        return torch.tensor(self.examples[idx], dtype=torch.long)

# -------------------------
# Mini Transformer
# -------------------------
class MiniTransformer(nn.Module):
    def __init__(self, vocab_size, d_model=256, nhead=8, num_layers=6, dim_feedforward=1024, max_seq_len=512):
        super().__init__()
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        self.pos_embedding = nn.Embedding(max_seq_len, d_model)
        decoder_layer = nn.TransformerDecoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=0.1,
            activation='gelu',
            batch_first=True
        )
        self.decoder = nn.TransformerDecoder(decoder_layer, num_layers=num_layers)
        self.fc_out = nn.Linear(d_model, vocab_size)
        self.d_model = d_model
        self.max_seq_len = max_seq_len

    def forward(self, input_ids: torch.LongTensor) -> torch.FloatTensor:
        batch_size, seq_len = input_ids.size()
        positions = torch.arange(seq_len, device=input_ids.device).unsqueeze(0).expand(batch_size, -1)
        x = self.token_embedding(input_ids) * math.sqrt(self.d_model)
        x = x + self.pos_embedding(positions)
        tgt_mask = nn.Transformer.generate_square_subsequent_mask(seq_len).to(input_ids.device)
        decoded = self.decoder(tgt=x, memory=x, tgt_mask=tgt_mask)
        return self.fc_out(decoded)

# -------------------------
# Code Generation
# -------------------------
def generate_sample(model, tokenizer, prompt="# Python function", device='cpu', max_gen_len=100):
    model.eval()
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
    for _ in range(max_gen_len):
        with torch.no_grad():
            outputs = model(input_ids)
            next_token_logits = outputs[:, -1, :]
            next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)
            input_ids = torch.cat((input_ids, next_token), dim=1)
            if next_token.item() == tokenizer.eos_token_id:
                break
    return tokenizer.decode(input_ids[0], skip_special_tokens=True)

# -------------------------
# Train Model
# -------------------------
def train_model(data_dir, model, tokenizer, seq_len=256, batch_size=4, num_epochs=100, lr=3e-4, device='cpu', save_path="vamp_model.pth"):
    dataset = CodeDataset(data_dir, tokenizer, seq_len)
    if len(dataset) == 0:
        raise RuntimeError(f"No .py files found in '{data_dir}'")
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss(ignore_index=tokenizer.pad_token_id)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    for epoch in range(1, num_epochs + 1):
        model.train()
        total_loss = 0.0
        loop = tqdm(dataloader, desc=f"Epoch {epoch}/{num_epochs}", leave=False)
        for batch in loop:
            optimizer.zero_grad()
            batch = batch.to(device)
            logits = model(batch)
            shift_logits = logits[:, :-1, :].contiguous()
            shift_labels = batch[:, 1:].contiguous()
            loss = loss_fn(
                shift_logits.view(-1, tokenizer.vocab_size),
                shift_labels.view(-1)
            )
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            loop.set_postfix(loss=loss.item())

        avg_loss = total_loss / len(dataloader)
        print(f"Epoch {epoch}/{num_epochs} — Avg Loss: {avg_loss:.4f}")

        if epoch % 5 == 0 or epoch == num_epochs:
            checkpoint_path = save_path.replace(".pth", f"_epoch{epoch}.pth")
            torch.save(model.state_dict(), checkpoint_path)
            print(f"📦 Saved checkpoint: {checkpoint_path}")
            sample = generate_sample(model, tokenizer, device=device)
            print(f"\n🧠 Vamp generated after Epoch {epoch}:\n{sample}\n")
            # Save the sample to a txt file
            sample_path = save_path.replace(".pth", f"_sample_epoch{epoch}.txt")
            with open(sample_path, "w", encoding="utf-8") as f:
                f.write(sample)
            print(f"📝 Saved generated sample: {sample_path}")

    torch.save(model.state_dict(), save_path)
    print(f"\n✅ Final Vamp model saved to '{save_path}'!")

# -------------------------
# Load Trained Model
# -------------------------
def load_vamp_model(model_class, save_path, vocab_size, device='cpu'):
    model = model_class(vocab_size)
    model.load_state_dict(torch.load(save_path, map_location=device))
    model.to(device)
    model.eval()
    print("✅ Vamp model loaded!")
    return model

# -------------------------
# Example Usage
# -------------------------
if __name__ == "__main__":
    tokenizer = GPT2TokenizerFast(
        vocab_file="vamp-tokenizer/vocab.json",
        merges_file="vamp-tokenizer/merges.txt",
        unk_token="<unk>",
        pad_token="<pad>",
        bos_token="<s>",
        eos_token="</s>",
        mask_token="<mask>"
    )

    model = MiniTransformer(vocab_size=tokenizer.vocab_size)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    train_model(
        data_dir="data",
        model=model,
        tokenizer=tokenizer,
        seq_len=256,
        batch_size=4,
        num_epochs=50,
        lr=3e-4,
        device=device,
        save_path="vamp_checkpoints/vamp_model.pth"
    )

    # Later load model
    # model = load_vamp_model(MiniTransformer, "vamp_checkpoints/vamp_model.pth", tokenizer.vocab_size, device=device)
