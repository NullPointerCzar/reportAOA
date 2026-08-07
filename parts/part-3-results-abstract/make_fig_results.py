#!/usr/bin/env python3
"""Generate Fig. 1 for the paper from the MEASURED benchmark results.

Reads results/results.json (produced by run_experiments.py --aggregate)
and plots:

  (a) GSM8K accuracy vs temperature for single-sample few-shot CoT and
      self-consistency, one line per model.
  (b) GSM8K accuracy by technique and model scale at the reference
      decoding cell.

The figure is a two-column IEEE figure* (full \textwidth).  Cells with no
measured data are skipped; if too little data exists the script exits with
a message instead of drawing an empty plot.
"""

import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
RESULTS_JSON = os.path.join(ROOT, "results", "results.json")
OUT_DIR = os.path.join(ROOT, "figures")

MODELS = ["llama3.2:1b", "llama3.2:3b", "qwen2.5-coder:3b"]
MODEL_LABELS = {"llama3.2:1b": "Llama 3.2 1B", "llama3.2:3b": "Llama 3.2 3B",
                "qwen2.5-coder:3b": "Qwen2.5-Coder 3B"}
MODEL_COLORS = {"llama3.2:1b": "#4c72b0", "llama3.2:3b": "#dd8452",
                "qwen2.5-coder:3b": "#55a868"}
TECHNIQUES = ["direct", "zs_cot", "fs_cot", "self_consistency"]
TECHNIQUE_LABELS = ["Direct", "Zero-shot\nCoT", "Few-shot\nCoT", "Self-\nconsistency"]
TEMPS = [0.0, 0.3, 0.7, 1.0]
REF_T = 0.0
SC_T = 0.7


def main() -> None:
    if not os.path.exists(RESULTS_JSON):
        sys.exit(f"[fig] {RESULTS_JSON} not found - run the benchmark first.")
    with open(RESULTS_JSON) as f:
        results = json.load(f)

    idx = {}
    for row in results.get("table", []):
        key = (row["model"], row["task"], row["technique"], row["paraphrase"],
               row["temperature"])
        idx[key] = row

    def acc(model, task, tech, par, temp):
        row = idx.get((model, task, tech, par, temp))
        if row is None:
            return None
        if tech == "self_consistency":
            va = row.get("vote_accuracy")
            return va if va is not None else row.get("accuracy")
        return row.get("accuracy")

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

    fig = plt.figure(figsize=(7.1, 2.35))

    # ---------------- panel (a): temperature sweep, GSM8K ----------------
    ax = fig.add_axes([0.06, 0.15, 0.40, 0.77])
    plotted_a = False
    for model in MODELS:
        fs = [acc(model, "gsm8k", "fs_cot", 1, t) for t in TEMPS]
        sc_t = acc(model, "gsm8k", "self_consistency", 1, SC_T)
        if any(v is not None for v in fs) or sc_t is not None:
            plotted_a = True
        if any(v is not None for v in fs):
            xs = [t for t, v in zip(TEMPS, fs) if v is not None]
            ys = [v * 100 for v in fs if v is not None]
            ax.plot(xs, ys, "o-", color=MODEL_COLORS[model], lw=1.1, ms=3,
                    label=f"{MODEL_LABELS[model]}, FS-CoT")
        if sc_t is not None:
            ax.plot([SC_T], [sc_t * 100], "s", color=MODEL_COLORS[model], ms=5,
                    mec="k", mew=0.4)
    ax.set_xlabel("Temperature $T$")
    ax.set_ylabel("Accuracy (%)")
    ax.set_xticks(TEMPS)
    ax.set_ylim(0, 100)
    ax.legend(frameon=False, loc="lower left", fontsize=5.5)
    ax.set_title("(a) GSM8K, temperature sweep (nucleus $p=0.9$)")
    if not plotted_a:
        print("[fig] no temperature-sweep data yet; panel (a) empty")

    # ---------------- panel (b): technique x model, GSM8K ----------------
    ax = fig.add_axes([0.55, 0.15, 0.41, 0.77])
    x = np.arange(len(TECHNIQUES))
    w = 0.26
    plotted_b = False
    for i, model in enumerate(MODELS):
        vals = [acc(model, "gsm8k", tech, 1, SC_T if tech == "self_consistency" else REF_T)
                for tech in TECHNIQUES]
        if any(v is not None for v in vals):
            plotted_b = True
        y = [v * 100 if v is not None else 0.0 for v in vals]
        ax.bar(x + (i - 1) * w, y, w, label=MODEL_LABELS[model],
               color=MODEL_COLORS[model], alpha=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels(TECHNIQUE_LABELS)
    ax.set_ylabel("Accuracy (%)")
    ax.set_ylim(0, 100)
    ax.legend(frameon=False, ncol=3, loc="upper left", fontsize=5.5)
    ax.set_title("(b) GSM8K accuracy by technique and model scale")
    if not plotted_b:
        print("[fig] no reference-cell data yet; panel (b) empty")

    fig.savefig(os.path.join(OUT_DIR, "fig-results.pdf"))
    fig.savefig(os.path.join(OUT_DIR, "fig-results.png"), dpi=300)
    print(f"wrote figures/fig-results.pdf and figures/fig-results.png")


if __name__ == "__main__":
    main()
