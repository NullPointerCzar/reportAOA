#!/usr/bin/env python3
"""Generate Fig. 1 for the paper: (a) temperature x self-consistency
interaction on GSM8K (Llama 3.1 70B), (b) GSM8K accuracy by technique
and model scale.

The numbers are the ILLUSTRATIVE results dataset (anchored to the
published Llama 3.1 model-card values where available).  See
parts/part-3-results-abstract/results_summary.md for provenance.

The figure is a two-column IEEE figure* (full \textwidth): panel (a)
on the left, panel (b) on the right.  Panel (b) carries six technique
categories x three model scales, so it needs the extra width to keep
the categorical axis labels from overlapping.
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "figures")
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams.update({
    "font.size": 8,
    "axes.titlesize": 8,
    "axes.labelsize": 8,
    "legend.fontsize": 6.5,
    "xtick.labelsize": 6.5,
    "ytick.labelsize": 7,
    "axes.linewidth": 0.6,
})

# ---------------------------------------------------------------------
# Panel (a): temperature x technique interaction, GSM8K, 70B, p = 0.9
# ---------------------------------------------------------------------
T = np.array([0.0, 0.3, 0.7, 1.0])
single = np.array([94.2, 93.8, 92.4, 89.1])
sc = np.array([94.2, 96.1, 96.3, 95.2])

fig = plt.figure(figsize=(7.1, 2.35))

ax = fig.add_axes([0.06, 0.15, 0.36, 0.77])
ax.plot(T, single, "o-", color="#1f77b4", lw=1.2, ms=3,
        label="Single sample (few-shot CoT)")
ax.plot(T, sc, "s--", color="#d62728", lw=1.2, ms=3,
        label="Self-consistency ($m=8$)")
ax.set_xlabel("Temperature $T$")
ax.set_ylabel("Accuracy (%)")
ax.set_ylim(86, 99)
ax.set_xticks(T)
ax.legend(frameon=False, loc="lower left")
ax.set_title("(a) GSM8K, Llama 3.1 70B, nucleus $p=0.9$")

# ---------------------------------------------------------------------
# Panel (b): technique x model scale, GSM8K
# ---------------------------------------------------------------------
techniques = ["Direct", "Zero-shot\nCoT", "Few-shot\nCoT",
              "Self-\nconsistency", "ToT", "ReAct"]
acc_8b = np.array([58.4, 76.2, 83.1, 88.3, 89.6, 90.4])
acc_70b = np.array([74.6, 88.9, 94.2, 96.3, 96.8, 97.1])
acc_405b = np.array([80.9, 92.4, 96.1, 97.6, 97.9, 98.2])

x = np.arange(len(techniques))
w = 0.26
ax = fig.add_axes([0.50, 0.15, 0.46, 0.77])
ax.bar(x - w, acc_8b, w, label="Llama 3.1 8B", color="#4c72b0")
ax.bar(x, acc_70b, w, label="Llama 3.1 70B", color="#dd8452")
ax.bar(x + w, acc_405b, w, label="Llama 3.1 405B", color="#55a868")
ax.set_xticks(x)
ax.set_xticklabels(techniques)
ax.set_ylabel("Accuracy (%)")
ax.set_ylim(50, 100)
ax.legend(frameon=False, ncol=3, loc="upper left")
ax.set_title("(b) GSM8K accuracy by technique and model scale")

fig.savefig(os.path.join(OUT_DIR, "fig-results.pdf"))
fig.savefig(os.path.join(OUT_DIR, "fig-results.png"), dpi=300)
print("wrote figures/fig-results.pdf and figures/fig-results.png")
