import torch
import torch.nn as nn
import math
import sentencepiece as spm

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len):
        super(PositionalEncoding, self).__init__()
        pe = torch.zeros(max_len, d_model)  # (T, D)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1) # (T, 1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * -(math.log(10000.0) / d_model))  # (D/2, )
        pe[:, 0::2] = torch.cos(position * div_term)    # even idx
        pe[:, 1::2] = torch.sin(position * div_term)    # odd idx
        pe = pe.unsqueeze(0)    # (1, T, D)
        self.register_buffer('pe', pe)

    def forward(self, x):
        seq_len = x.size(1)
        if seq_len > self.pe.size(1):
            raise ValueError(f"[ERROR] Input sequence length {seq_len} exceeds positional encoding max_len {self.pe.size(1)}")
        return x + self.pe[:, :seq_len]


class MiniBART(nn.Module):
    def __init__(self, vocab_size, pad_id, d_model=512, nhead=8, num_layers=3, max_len=512, dropout=0.1):
        super().__init__()
        self.pad_id = pad_id
        self.embed = nn.Embedding(vocab_size, d_model, padding_idx=pad_id)
        self.embed_ln = nn.LayerNorm(d_model)
        self.embed_dropout = nn.Dropout(dropout)
        self.pos_enc = PositionalEncoding(d_model, max_len)

        self.transformer = nn.Transformer(
            d_model=d_model,
            nhead=nhead,
            num_encoder_layers=num_layers,
            num_decoder_layers=num_layers,
            dim_feedforward=1024,
            dropout=dropout,
            batch_first=True
        )

        self.out_ln = nn.LayerNorm(d_model)
        self.out_dropout = nn.Dropout(dropout)
        self.out_proj = nn.Linear(d_model, vocab_size)

    def generate_square_subsequent_mask(self, size):
        # 상삼각 True 마스크 (causal mask)
        mask = torch.triu(torch.ones(size, size, dtype=torch.bool), diagonal=1)
        return mask

    def make_pad_mask(self, seq):
        # 패딩 마스크 생성
        return (seq == self.pad_id)

    def forward(self, src, tgt, src_mask=None):
        """
        src: (B, S), input 문장 (full)
        tgt: (B, T), 요약 문장 (summary)
        """

        if src_mask is None:
            src_pad_mask = self.make_pad_mask(src)  # (B, S)
        else:
            src_pad_mask = src_mask.bool()
        tgt_pad_mask = self.make_pad_mask(tgt)  # (B, T)
        tgt_mask = self.generate_square_subsequent_mask(tgt.size(1)).to(tgt.device)  # (T, T)

        # 임베딩 + 위치 인코딩
        src_emb = self.embed_dropout(self.embed_ln(self.pos_enc(self.embed(src))))  # (B, S, D)
        tgt_emb = self.embed_dropout(self.embed_ln(self.pos_enc(self.embed(tgt))))  # (B, T, D)

        output = self.transformer(
            src=src_emb,
            tgt=tgt_emb,
            tgt_mask=tgt_mask,
            src_key_padding_mask=src_pad_mask,
            tgt_key_padding_mask=tgt_pad_mask,
            memory_key_padding_mask=src_pad_mask
        )  # (B, T, D)

        output = self.out_dropout(self.out_ln(output))
        return self.out_proj(output)  # (B, T, vocab_size)


class FeedForwardWithGating(nn.Module):
    def __init__(self, d_model, hidden_dim, dropout):
        super().__init__()
        self.linear1 = nn.Linear(d_model, hidden_dim)
        self.linear2 = nn.Linear(hidden_dim, d_model)
        self.gate = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(dropout)
        self.activation = nn.GELU()
        self.norm = nn.LayerNorm(d_model)

    def forward(self, x):
        hidden = self.activation(self.linear1(x))
        hidden = self.dropout(self.linear2(hidden))
        gate = torch.sigmoid(self.gate(x))
        out = hidden * gate + x
        return self.norm(out)


class EnhancedMiniBART(nn.Module):
    def __init__(self, vocab_size, pad_id, d_model=512, nhead=8, num_layers=3, max_len=512, dropout=0.1):
        super().__init__()
        self.pad_id = pad_id
        self.embed = nn.Embedding(vocab_size, d_model, padding_idx=pad_id)
        self.embed_ln = nn.LayerNorm(d_model)
        self.embed_dropout = nn.Dropout(dropout)
        self.pos_enc = PositionalEncoding(d_model, max_len)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=1024,
            dropout=dropout,
            batch_first=True,
            activation='gelu'
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        decoder_layer = nn.TransformerDecoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=1024,
            dropout=dropout,
            batch_first=True,
            activation='gelu'
        )
        self.decoder = nn.TransformerDecoder(decoder_layer, num_layers=num_layers)

        self.fusion_ffn = FeedForwardWithGating(d_model, d_model * 4, dropout)


        self.encoder_ln = nn.LayerNorm(d_model)
        self.decoder_ln = nn.LayerNorm(d_model)
        self.out_ln = nn.LayerNorm(d_model)
        self.out_dropout = nn.Dropout(dropout)
        self.out_proj = nn.Linear(d_model, vocab_size)

    def generate_square_subsequent_mask(self, size):
        return torch.triu(torch.ones(size, size, dtype=torch.bool), diagonal=1)

    def make_pad_mask(self, seq):
        return seq == self.pad_id

    def forward(self, src, tgt, src_mask=None):
        if src_mask is None:
            src_pad_mask = self.make_pad_mask(src)
        else:
            src_pad_mask = src_mask.bool()
        tgt_pad_mask = self.make_pad_mask(tgt)
        tgt_mask = self.generate_square_subsequent_mask(tgt.size(1)).to(tgt.device)

        src_emb = self.embed_dropout(self.embed_ln(self.pos_enc(self.embed(src))))
        tgt_emb = self.embed_dropout(self.embed_ln(self.pos_enc(self.embed(tgt))))

        memory = self.encoder(src_emb, src_key_padding_mask=src_pad_mask)
        memory = self.encoder_ln(memory)

        output = self.decoder(
            tgt=tgt_emb,
            memory=memory,
            tgt_mask=tgt_mask,
            tgt_key_padding_mask=tgt_pad_mask,
            memory_key_padding_mask=src_pad_mask
        )
        output = self.decoder_ln(output)

        output = self.fusion_ffn(output)
        output = self.out_ln(self.out_dropout(output))
        return self.out_proj(output)


def get_model(config):
    if config["model_name"] == "MiniBART":
        model = MiniBART(
            vocab_size=config["sp_vocab_size"],
            pad_id=config["pad"],
            d_model=config["d_model"],
            nhead=config["nhead"],
            num_layers=config["num_layers"],
            max_len=config["max_len"],
            dropout=config["dropout"]
        )
        return model.to(config["device"])
    elif config["model_name"] == "EnhancedMiniBART":
        model = EnhancedMiniBART(
            vocab_size=config["sp_vocab_size"],
            pad_id=config["pad"],
            d_model=config["d_model"],
            nhead=config["nhead"],
            num_layers=config["num_layers"],
            max_len=config["max_len"],
            dropout=config["dropout"]
        )
        return model.to(config["device"])
    else:
        raise ValueError(f"Unsupported model: {config['model_name']}")


def get_sp(config):
    sp = spm.SentencePieceProcessor()
    sp.load(config["sp_model_path"])
    return sp