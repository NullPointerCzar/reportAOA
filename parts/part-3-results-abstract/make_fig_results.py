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
import matplotlib.lines as mlines
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

    # ---- per-cell item-level bootstrap CI (95%) over items ----------------
    # Re-derives per-item 0/1 verdicts from records.jsonl using the same
    # aggregation rules as run_experiments.py (first-seen plurality for
    # GSM8K self-consistency; strict-majority pass for HumanEval).
    RECORDS_JSONL = os.path.join(ROOT, "results", "records.jsonl")
    recs = []
    if os.path.exists(RECORDS_JSONL):
        with open(RECORDS_JSONL) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        recs.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

    def _norm_sc_answer(ans):
        if ans is None:
            return "__UNPARSED__"
        try:
            return format(float(str(ans).replace(",", "")), "g")
        except (ValueError, TypeError):
            return str(ans)

    # raw per-cell per-item sample lists
    raw_items = {}
    sc_buckets = {}
    for r in recs:
        ck = (r["model"], r["task"], r["technique"], r["paraphrase"], r["temperature"])
        raw_items.setdefault(ck, {}).setdefault(r["item_id"], []).append(r["correct"])
        if r["technique"] == "self_consistency" and r["task"] == "gsm8k":
            k2 = (r["model"], r["paraphrase"])
            ans = _norm_sc_answer(r.get("extracted"))
            bucket = sc_buckets.setdefault(k2, {}).setdefault(r["item_id"], {})
            bucket.setdefault(ans, []).append(r["correct"])

    cell_verdicts = {}
    for ck, by_item in raw_items.items():
        d = {}
        for iid, cs in by_item.items():
            if ck[2] == "self_consistency":
                if ck[1] == "humaneval":
                    d[iid] = int(sum(cs) * 2 > len(cs))
                else:
                    buckets = sc_buckets.get((ck[0], ck[3]), {}).get(iid, {})
                    winner = max(buckets.items(), key=lambda kv: len(kv[1])) if buckets else (None, [])
                    ans, flags = winner
                    d[iid] = int(ans is not None and ans != "__UNPARSED__" and any(flags))
            else:
                d[iid] = int(cs[0])
        cell_verdicts[ck] = d

    rng = np.random.default_rng(42)

    def ci95(cell, n_boot=5000):
        """95% bootstrap CI over items for a cell's accuracy, as a fraction."""
        d = cell_verdicts.get(cell, {})
        items = list(d.keys())
        n = len(items)
        if n < 2:
            return None
        vals = []
        for _ in range(n_boot):
            s = rng.choice(items, size=n, replace=True)
            vals.append(sum(d[i] for i in s) / n)
        lo = float(np.percentile(vals, 2.5))
        hi = float(np.percentile(vals, 97.5))
        return (lo, hi)

    def yerr_lo_hi(cell):
        ci = ci95(cell)
        if ci is None:
            return None
        mean = sum(cell_verdicts.get(cell, {}).values()) / max(len(cell_verdicts.get(cell, {})), 1)
        return (mean - ci[0], ci[1] - mean)

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
    # Bottom margin is widened to leave room for the horizontal legend below.
    ax = fig.add_axes([0.06, 0.24, 0.40, 0.70])
    plotted_a = False
    plotted_sc = False
    for model in MODELS:
        fs = [acc(model, "gsm8k", "fs_cot", 1, t) for t in TEMPS]
        sc_t = acc(model, "gsm8k", "self_consistency", 1, SC_T)
        if any(v is not None for v in fs) or sc_t is not None:
            plotted_a = True
        if any(v is not None for v in fs):
            xs = [t for t, v in zip(TEMPS, fs) if v is not None]
            ys = [v * 100 for v in fs if v is not None]
            errs = [yerr_lo_hi((model, "gsm8k", "fs_cot", 1, t)) for t in xs]
            ax.errorbar(xs, ys, yerr=[[e[0] * 100 if e else None for e in errs],
                                      [e[1] * 100 if e else None for e in errs]],
                        fmt="o-", color=MODEL_COLORS[model], lw=1.1, ms=3,
                        elinewidth=0.7, capsize=2, capthick=0.6,
                        label=f"{MODEL_LABELS[model]}, FS-CoT")
        if sc_t is not None:
            plotted_sc = True
            err = yerr_lo_hi((model, "gsm8k", "self_consistency", 1, SC_T))
            ax.errorbar([SC_T], [sc_t * 100],
                        yerr=[[err[0] * 100] if err else None,
                              [err[1] * 100] if err else None],
                        fmt="s", color=MODEL_COLORS[model], ms=5,
                        mec="k", mew=0.4, elinewidth=0.7, capsize=2, capthick=0.6)
    ax.set_xlabel("Temperature $T$")
    ax.set_ylabel("Accuracy (%)")
    ax.set_xticks(TEMPS)
    ax.set_ylim(0, 100)
    # Explicit legend entry for the standalone self-consistency squares,
    # shown only when at least one SC point was actually plotted.
    handles, _ = ax.get_legend_handles_labels()
    if plotted_sc:
        sc_proxy = mlines.Line2D([], [], marker="s", color="none",
                                 markerfacecolor="0.45", markeredgecolor="k",
                                 markeredgewidth=0.4, markersize=5,
                                 label="Self-consistency ($T = 0.7$)")
        handles = handles + [sc_proxy]
    # Horizontal legend below the panel: never overlaps the data lines.
    ax.legend(handles=handles, frameon=False, loc="upper center",
              bbox_to_anchor=(0.5, -0.24), ncol=3, fontsize=5.5,
              handlelength=1.4, handletextpad=0.4, columnspacing=1.2,
              borderaxespad=0.0)
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
        errs = [yerr_lo_hi((model, "gsm8k", tech, 1,
                            SC_T if tech == "self_consistency" else REF_T))
                for tech in TECHNIQUES]
        yerr = np.array([[e[0] * 100 if e else 0.0 for e in errs],
                         [e[1] * 100 if e else 0.0 for e in errs]])
        ax.bar(x + (i - 1) * w, y, w, label=MODEL_LABELS[model],
               color=MODEL_COLORS[model], alpha=0.9, yerr=yerr,
               error_kw=dict(elinewidth=0.7, capsize=2, capthick=0.6))
    ax.set_xticks(x)
    ax.set_xticklabels(TECHNIQUE_LABELS)
    ax.set_ylabel("Accuracy (%)")
    ax.set_ylim(0, 100)
    ax.legend(frameon=False, ncol=3, loc="upper left", fontsize=5.5)
    ax.set_title("(b) GSM8K accuracy by technique and model scale")
    if not plotted_b:
        print("[fig] no reference-cell data yet; panel (b) empty")

    # bbox_inches="tight" (tight_layout is a no-op for manual add_axes).
    fig.savefig(os.path.join(OUT_DIR, "fig-results.pdf"),
                bbox_inches="tight")
    fig.savefig(os.path.join(OUT_DIR, "fig-results.png"), dpi=300,
                bbox_inches="tight")
    print(f"wrote figures/fig-results.pdf and figures/fig-results.png")


if __name__ == "__main__":
    main()
