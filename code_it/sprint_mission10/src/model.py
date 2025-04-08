import torch.nn as nn
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class EmbeddingLSTM(nn.Module):
    def __init__(self, embedding_matrix, hidden_dim, output_dim, num_layers=2, dropout=0.5):
        super(EmbeddingLSTM, self).__init__()
        num_embeddings, embedding_dim = embedding_matrix.shape
        self.embedding = nn.Embedding.from_pretrained(torch.tensor(embedding_matrix, dtype=torch.float).to(device), freeze=False)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers=num_layers, batch_first=True, dropout=dropout, bidirectional=True)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        embedded = self.embedding(x)
        _, (hidden, _) = self.lstm(embedded)
        output = self.fc(hidden[-1])
        return output


class AttnBiLSTM(nn.Module):
    def __init__(self, embedding_matrix, hidden_dim, output_dim, num_layers=2, dropout=0.5):
        super(AttnBiLSTM, self).__init__()
        num_embeddings, embedding_dim = embedding_matrix.shape
        self.embedding = nn.Embedding.from_pretrained(
            torch.tensor(embedding_matrix, dtype=torch.float).to(device), freeze=False
        )

        self.lstm = nn.LSTM(
            embedding_dim, hidden_dim, num_layers=num_layers,
            batch_first=True, dropout=dropout, bidirectional=True
        )

        self.attn_fc = nn.Linear(hidden_dim * 2, 1)  # attention score 계산용
        self.layer_norm = nn.LayerNorm(hidden_dim * 2)
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_dim * 2, output_dim)

    def forward(self, x):
        embedded = self.embedding(x)  # [B, T, E]
        lstm_out, _ = self.lstm(embedded)  # [B, T, 2H]

        # Attention weights
        attn_scores = self.attn_fc(lstm_out).squeeze(-1)  # [B, T]
        attn_weights = torch.softmax(attn_scores, dim=1).unsqueeze(-1)  # [B, T, 1]

        # Attention-weighted sum
        context = torch.sum(lstm_out * attn_weights, dim=1)  # [B, 2H]
        context = self.layer_norm(context)
        context = self.dropout(context)

        output = self.fc(context)
        return output

class FinalBiLSTM(nn.Module):
    def __init__(self, embedding_matrix, hidden_dim, output_dim, num_layers=2, dropout=0.5):
        super(FinalBiLSTM, self).__init__()
        num_embeddings, embedding_dim = embedding_matrix.shape
        self.embedding = nn.Embedding.from_pretrained(
            torch.tensor(embedding_matrix, dtype=torch.float).to(device), freeze=False
        )

        self.embedding_dropout = nn.Dropout(dropout)  # (1) Embedding 이후 Dropout

        self.lstm = nn.LSTM(
            embedding_dim, hidden_dim, num_layers=num_layers,
            batch_first=True, dropout=dropout, bidirectional=True
        )

        self.attn_fc = nn.Linear(hidden_dim * 2, 1)
        self.layer_norm = nn.LayerNorm(hidden_dim * 2)
        self.dropout = nn.Dropout(dropout)
        self.relu = nn.ReLU()  # (2) 비선형성 추가
        self.fc = nn.Linear(hidden_dim * 2, output_dim)

    def forward(self, x):
        embedded = self.embedding(x)  # [B, T, E]
        embedded = self.embedding_dropout(embedded)  # (1)

        lstm_out, _ = self.lstm(embedded)  # [B, T, 2H]

        attn_scores = self.attn_fc(lstm_out).squeeze(-1)  # [B, T]
        attn_weights = torch.softmax(attn_scores, dim=1).unsqueeze(-1)  # [B, T, 1]

        context = torch.sum(lstm_out * attn_weights, dim=1)  # [B, 2H]
        context = self.layer_norm(context)
        context = self.dropout(context)

        output = self.fc(self.relu(context))  # (2)
        return output


def get_model(config, embedding_matrix):
    if config["model"] == "EmbeddingLSTM":
        return EmbeddingLSTM(
            embedding_matrix=embedding_matrix,
            hidden_dim=config["hidden_dim"],
            output_dim=config["output_dim"],
            num_layers=config["num_layers"],
            dropout=config["dropout"]
        ).to(device)

    elif config["model"] == "AttnBiLSTM":
        return AttnBiLSTM(
            embedding_matrix=embedding_matrix,
            hidden_dim=config["hidden_dim"],
            output_dim=config["output_dim"],
            num_layers=config["num_layers"],
            dropout=config["dropout"]
        ).to(device)

    elif config["model"] == "FinalBiLSTM":
        return FinalBiLSTM(
            embedding_matrix=embedding_matrix,
            hidden_dim=config["hidden_dim"],
            output_dim=config["output_dim"],
            num_layers=config["num_layers"],
            dropout=config["dropout"]
            ).to(device)

    else:
        raise ValueError(f"Unknown model type: {config['model']}")