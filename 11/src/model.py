import torch.nn as nn
import torch.nn.functional as F
import torch

# Encoder 정의
class EncoderRNN(nn.Module):
    def __init__(self, input_size, embedding_dim, hidden_size, num_layers, dropout):
        super(EncoderRNN, self).__init__()
        self.embedding = nn.Embedding(input_size, embedding_dim)
        self.gru = nn.GRU(embedding_dim, hidden_size, num_layers=num_layers, batch_first=True)
        self.dropout = nn.Dropout(dropout)

    def forward(self, input):
        embedded = self.dropout(self.embedding(input))
        output, hidden = self.gru(embedded)
        return output, hidden

# Decoder 정의
class DecoderRNN(nn.Module):
    def __init__(self, output_size, embedding_dim, hidden_size, num_layers, dropout, sos_token, max_len):
        super(DecoderRNN, self).__init__()
        self.embedding = nn.Embedding(output_size, embedding_dim)
        self.gru = nn.GRU(embedding_dim, hidden_size, num_layers=num_layers, batch_first=True)
        self.out = nn.Linear(hidden_size, output_size)
        self.dropout = nn.Dropout(dropout)
        self.sos_token = sos_token
        self.max_len = max_len

    def forward(self, encoder_outputs, encoder_hidden, target_tensor=None):
        batch_size = encoder_outputs.size(0)
        decoder_input = torch.full((batch_size, 1), self.sos_token, dtype=torch.long, device=encoder_outputs.device)
        decoder_hidden = encoder_hidden
        decoder_outputs = []

        decoding_steps = target_tensor.size(1) if target_tensor is not None else self.max_len
        for i in range(decoding_steps):
            decoder_output, decoder_hidden = self.forward_step(decoder_input, decoder_hidden)
            decoder_outputs.append(decoder_output)
            if target_tensor is not None:
                decoder_input = target_tensor[:, i].unsqueeze(1)
            else:
                _, topi = decoder_output.topk(1)
                decoder_input = topi.squeeze(2).detach()

        decoder_outputs = torch.cat(decoder_outputs, dim=1)
        return decoder_outputs, decoder_hidden, None

    def forward_step(self, input, hidden):
        output = self.embedding(input)
        output = F.relu(output)
        output, hidden = self.gru(output, hidden)
        output = self.out(output)
        return output, hidden

import torch.nn as nn
import torch.nn.functional as F

class BahdanauAttention(nn.Module):
    def __init__(self, hidden_size):
        super(BahdanauAttention, self).__init__()
        self.Wa = nn.Linear(hidden_size, hidden_size)
        self.Ua = nn.Linear(hidden_size, hidden_size)
        self.Va = nn.Linear(hidden_size, 1)

    def forward(self, query, keys):
        query = query.expand(-1, keys.size(1), -1)
        scores = self.Va(torch.tanh(self.Wa(query) + self.Ua(keys)))  # [batch, seq_len, 1]
        scores = scores.squeeze(2).unsqueeze(1)                       # [batch, 1, seq_len]
        weights = F.softmax(scores, dim=-1)
        context = torch.bmm(weights, keys)                            # [batch, 1, hidden_size]
        return context, weights

class AttnDecoderRNN(nn.Module):
    def __init__(self, output_size, embedding_dim, hidden_size, num_layers, dropout, sos_token, max_len):
        super(AttnDecoderRNN, self).__init__()
        self.hidden_size = hidden_size
        self.sos_token = sos_token
        self.max_len = max_len

        self.embedding = nn.Embedding(output_size, embedding_dim)
        self.attention = BahdanauAttention(hidden_size)
        self.gru = nn.GRU(
            input_size=hidden_size + embedding_dim,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True
        )
        self.out = nn.Linear(hidden_size + hidden_size, output_size)  # [GRU output + context]
        self.dropout = nn.Dropout(dropout)

    def forward(self, encoder_outputs, encoder_hidden, target_tensor=None):
        batch_size = encoder_outputs.size(0)
        decoder_input = torch.full((batch_size, 1), self.sos_token, dtype=torch.long, device=encoder_outputs.device)
        decoder_hidden = encoder_hidden
        decoder_outputs = []
        attentions = []

        decoding_steps = target_tensor.size(1) if target_tensor is not None else self.max_len
        for i in range(decoding_steps):
            decoder_output, decoder_hidden, attn_weights = self.forward_step(
                decoder_input, decoder_hidden, encoder_outputs
            )
            decoder_outputs.append(decoder_output)
            attentions.append(attn_weights)

            if target_tensor is not None:
                decoder_input = target_tensor[:, i].unsqueeze(1)
            else:
                _, topi = decoder_output.topk(1)
                decoder_input = topi.squeeze(-1).detach()

        decoder_outputs = torch.cat(decoder_outputs, dim=1)  # [B, T, V]
        attentions = torch.cat(attentions, dim=1)            # [B, T, S]
        return decoder_outputs, decoder_hidden, attentions

    def forward_step(self, input, hidden, encoder_outputs):
        embedded = self.dropout(self.embedding(input))  # [batch, 1, emb_dim]
        query = hidden[-1].unsqueeze(1)                 # [1, B, H] → [B, 1, H]
        context, attn_weights = self.attention(query, encoder_outputs)  # context: [B, 1, H]
        input_gru = torch.cat((embedded, context), dim=2)               # [B, 1, H+E]

        output, hidden = self.gru(input_gru, hidden)     # output: [B, 1, H]

        output = torch.cat([output, context], dim=2)     # [B, 1, H+H]
        output = self.out(output)                        # [B, 1, V]

        return output, hidden, attn_weights

