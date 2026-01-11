import math
import torch
import torch.nn as nn

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

    def forward(self, input_ids: torch.LongTensor) -> torch.FloatTensor:
        batch_size, seq_len = input_ids.size()
        positions = torch.arange(seq_len, device=input_ids.device).unsqueeze(0).expand(batch_size, -1)
        x = self.token_embedding(input_ids) * math.sqrt(self.d_model)
        x = x + self.pos_embedding(positions)
        tgt_mask = nn.Transformer.generate_square_subsequent_mask(seq_len).to(input_ids.device)
        decoded = self.decoder(tgt=x, memory=x, tgt_mask=tgt_mask)
        return self.fc_out(decoded)

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
