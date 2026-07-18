"""Sequence models (MLP / GRU / Transformer) for next-year separation.

Purpose: test whether a worker's *employment history* (a sequence of yearly
feature vectors) predicts next-year separation better than their current-year
state alone. All three models share the same standardised numeric feature
representation, so:

- MLP (current year only) vs. GRU / Transformer (full history) isolates the
  value of the sequence structure;
- the tree baseline (HistGBM/XGBoost, native categorical handling) is reported
  separately for reference.

With the 2017-2025 panel, per-worker sequences are at most 8 steps long — ample
for a GRU, short for a Transformer (reported honestly).
"""

import numpy as np
import pandas as pd

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import TensorDataset, DataLoader
    _TORCH = True
except Exception:  # pragma: no cover
    _TORCH = False

from sklearn.metrics import roc_auc_score, average_precision_score
from src.config import PKEY


# --------------------------------------------------------------------------
# Sequence construction
# --------------------------------------------------------------------------
def build_sequences(frame: pd.DataFrame, feature_cols, max_len: int = 8):
    """From a transition frame, build left-padded per-sample history sequences.

    For every transition row (person p, year t) the input is p's feature vectors
    for years <= t (chronological, last ``max_len`` kept); the target is
    ``separated`` at t. Returns X [N, max_len, F], mask [N, max_len], y [N],
    years [N] (the transition year, for splitting).
    """
    F = len(feature_cols)
    frame = frame.sort_values([PKEY, "year"])
    feats_by_person = {
        pid: g[feature_cols].to_numpy(dtype=np.float32)
        for pid, g in frame.groupby(PKEY)
    }
    years_by_person = {pid: g["year"].to_numpy() for pid, g in frame.groupby(PKEY)}

    X, mask, y, yrs = [], [], [], []
    for pid, g in frame.groupby(PKEY):
        pf = feats_by_person[pid]
        py = years_by_person[pid]
        sep = g["separated"].to_numpy()
        for i in range(len(g)):
            hist = pf[max(0, i - max_len + 1): i + 1]           # [L, F], L<=max_len
            L = hist.shape[0]
            pad = np.zeros((max_len - L, F), dtype=np.float32)
            X.append(np.concatenate([pad, hist], axis=0))       # left-pad
            m = np.concatenate([np.zeros(max_len - L), np.ones(L)]).astype(np.float32)
            mask.append(m)
            y.append(sep[i])
            yrs.append(py[i])
    return (np.stack(X), np.stack(mask),
            np.asarray(y, dtype=np.float32), np.asarray(yrs))


def standardise(X_train, X_test, mask_train, mask_test):
    """Standardise features using train statistics; NaNs -> 0 after scaling."""
    flat = X_train.reshape(-1, X_train.shape[-1])
    m = mask_train.reshape(-1) > 0
    mu = np.nanmean(np.where(m[:, None], flat, np.nan), axis=0)
    sd = np.nanstd(np.where(m[:, None], flat, np.nan), axis=0)
    sd = np.where(sd < 1e-6, 1.0, sd)

    def apply(X):
        Z = (X - mu) / sd
        Z = np.nan_to_num(Z, nan=0.0, posinf=0.0, neginf=0.0)
        return Z.astype(np.float32)
    return apply(X_train), apply(X_test)


# --------------------------------------------------------------------------
# Models
# --------------------------------------------------------------------------
if _TORCH:
    class _MLP(nn.Module):
        """Current-year-only baseline (uses the last timestep)."""
        def __init__(self, F, hidden=64):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(F, hidden), nn.ReLU(), nn.Dropout(0.2),
                nn.Linear(hidden, hidden), nn.ReLU(), nn.Linear(hidden, 1))

        def forward(self, x, mask):
            return self.net(x[:, -1, :]).squeeze(-1)

    class _GRU(nn.Module):
        def __init__(self, F, hidden=64):
            super().__init__()
            self.gru = nn.GRU(F, hidden, batch_first=True)
            self.head = nn.Linear(hidden, 1)

        def forward(self, x, mask):
            out, h = self.gru(x)
            return self.head(h[-1]).squeeze(-1)

    class _Transformer(nn.Module):
        def __init__(self, F, d_model=64, nhead=4, layers=2, max_len=8):
            super().__init__()
            self.proj = nn.Linear(F, d_model)
            self.pos = nn.Parameter(torch.randn(1, max_len, d_model) * 0.02)
            enc = nn.TransformerEncoderLayer(
                d_model, nhead, dim_feedforward=128, dropout=0.1, batch_first=True)
            self.enc = nn.TransformerEncoder(enc, layers)
            self.head = nn.Linear(d_model, 1)

        def forward(self, x, mask):
            h = self.proj(x) + self.pos[:, -x.shape[1]:, :]
            key_pad = mask < 0.5                                  # True where padding
            h = self.enc(h, src_key_padding_mask=key_pad)
            last = h[:, -1, :]                                    # current-year token
            return self.head(last).squeeze(-1)

    _MODELS = {"mlp": _MLP, "gru": _GRU, "transformer": _Transformer}


def train_eval(kind, Xtr, Mtr, ytr, Xte, Mte, yte, max_len=8,
               epochs=8, batch=512, lr=1e-3, seed=0, device="cpu",
               return_probs=False):
    """Train one sequence model; return test metrics (and probs if requested)."""
    if not _TORCH:
        raise RuntimeError("PyTorch is not installed")
    torch.manual_seed(seed)
    F = Xtr.shape[-1]
    model = (_MODELS[kind](F, max_len=max_len) if kind == "transformer"
             else _MODELS[kind](F)).to(device)
    pos_weight = torch.tensor([(ytr == 0).sum() / max((ytr == 1).sum(), 1)],
                              dtype=torch.float32, device=device)
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    opt = torch.optim.Adam(model.parameters(), lr=lr)

    ds = TensorDataset(torch.from_numpy(Xtr), torch.from_numpy(Mtr),
                       torch.from_numpy(ytr))
    dl = DataLoader(ds, batch_size=batch, shuffle=True)
    model.train()
    for _ in range(epochs):
        for xb, mb, yb in dl:
            xb, mb, yb = xb.to(device), mb.to(device), yb.to(device)
            opt.zero_grad()
            loss = loss_fn(model(xb, mb), yb)
            loss.backward()
            opt.step()

    model.eval()
    with torch.no_grad():
        logits = model(torch.from_numpy(Xte).to(device),
                       torch.from_numpy(Mte).to(device))
        prob = torch.sigmoid(logits).cpu().numpy()
    metrics = {"roc_auc": roc_auc_score(yte, prob),
               "pr_auc": average_precision_score(yte, prob)}
    if return_probs:
        return metrics, prob
    return metrics


def run_comparison(frame, feature_cols, test_year, max_len=8, epochs=8, seed=0):
    """Build sequences, split by year, train MLP/GRU/Transformer.

    Returns ({model: {"roc_auc", "pr_auc"}}, info)."""
    X, mask, y, yrs = build_sequences(frame, feature_cols, max_len=max_len)
    tr, te = yrs < test_year, yrs == test_year
    Xtr, Xte = standardise(X[tr], X[te], mask[tr], mask[te])
    Mtr, Mte = mask[tr], mask[te]
    ytr, yte = y[tr], y[te]
    out = {}
    for kind in ("mlp", "gru", "transformer"):
        out[kind] = train_eval(kind, Xtr, Mtr, ytr, Xte, Mte, yte,
                               max_len=max_len, epochs=epochs, seed=seed)
    return out, {"n_train": int(tr.sum()), "n_test": int(te.sum())}
