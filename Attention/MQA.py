import torch
import torch.nn as nn

class MQA(nn.Module):
    def __init__(self, hidden_dim: int, head_num: int, dropout_rate: float):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.head_num = head_num
        self.head_dim = hidden_dim // head_num
        
        self.query = nn.Linear(hidden_dim, self.head_num*self.head_dim)
        self.key = nn.Linear(hidden_dim, self.head_dim)
        self.value = nn.Linear(hidden_dim, self.head_dim)
        
        self.dropout = nn.Dropout(dropout_rate)
        self.output = nn.Linear(hidden_dim, hidden_dim)
    
    def forward(self, X, attention_mask=None):
        batch_size, seq_len, _ = X.size()
        
        Q = self.query(X)
        K = self.key(X)
        V = self.value(X)
        
        Q = Q.view(batch_size, seq_len, self.head_num, self.head_dim).transpose(1, 2)
        K = K.unsqueeze(1)
        V = V.unsqueeze(1)
        
        attn_scores = torch.matmul(Q, K.transpose(-1, -2)) / torch.sqrt(self.head_dim)
        if attention_mask is not None:
            attn_scores = attn_scores.masked_fill(attention_mask.unsqueeze(1)==0, float("-inf"))
        attn_scores = torch.softmax(attn_scores, dim=-1)
        attn_scores = self.dropout(attn_scores)
    
        attn_output = torch.matmul(attn_scores, V)
        attn_output = attn_output.transpose(1, 2).contiguous().view(batch_size, seq_len, -1)
        
        output = self.output(attn_output)
        return output
        
        
        