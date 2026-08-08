#!/usr/bin/env python3
"""
update_tables.py
================
Fills the experimental table bodies in main.tex from results/results.json.

The tables in main.tex carry marker comments:

    %BEGIN-TABLE <label>
    <rows>
    %END-TABLE

This script regenerates the rows between the markers for tab:results,
tab:tempsweep, tab:cost, and tab:aer.  Cells for which no measured data
exists are rendered as "--" so the paper never shows a fabricated number.

Usage:
    python3 run_experiments.py --aggregate   # recompute results.json first
    python3 update_tables.py                 # rewrite the LaTeX tables
"""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

ROOT = os.path.dirname(os.path.abspath(__file__))
RESULTS_JSON = os.path.join(ROOT, "results", "results.json")
MAIN_TEX = os.path.join(ROOT, "main.tex")

TECHNIQUE_LABELS = {
    "direct": "Direct answering",
    "zs_cot": "Zero-shot CoT",
    "fs_cot": "Few-shot CoT",
    "self_consistency": "Self-consistency",
}
TECHNIQUE_ORDER = ["direct", "zs_cot", "fs_cot", "self_consistency"]
MODELS = ["llama3.2:1b", "llama3.2:3b", "qwen2.5-coder:3b"]
MODEL_LABELS = {"llama3.2:1b": "1B", "llama3.2:3b": "3B", "qwen2.5-coder:3b": "Qwen2.5-Coder-3B"}
TASKS = ["gsm8k", "humaneval"]
REF_T = 0.0
SC_T = 0.7


def pct(x: float, nd: int = 1) -> str:
    return f"{x * 100:.{nd}f}"


def num(x: float, nd: int = 1) -> str:
    return f"{x:.{nd}f}"


def load_results() -> Dict[str, Any]:
    if not os.path.exists(RESULTS_JSON):
        sys.exit(f"[error] {RESULTS_JSON} not found - run the benchmark first.")
    with open(RESULTS_JSON) as f:
        return json.load(f)


def index_table(results: Dict[str, Any]) -> Dict[Tuple[str, str, str, int, float], Dict[str, Any]]:
    """(model, task, technique, paraphrase, temperature) -> row."""
    idx = {}
    for row in results.get("table", []):
        key = (row["model"], row["task"], row["technique"], int(row["paraphrase"]),
               float(row["temperature"]))
        idx[key] = row
    return idx


def acc(idx, model: str, task: str, technique: str, par: int = 1,
        temp: Optional[float] = None) -> Optional[float]:
    """Reference-cell accuracy in [0,1] for COMPLETE cells only; SC uses the
    plurality vote.  Partial cells return None so the paper shows '--'."""
    t = SC_T if technique == "self_consistency" else (REF_T if temp is None else temp)
    row = idx.get((model, task, technique, par, t))
    if row is None or not row.get("complete", False):
        return None
    if technique == "self_consistency":
        va = row.get("vote_accuracy")
        return va if va is not None else row.get("accuracy")
    return row.get("accuracy")


def ref_temp(technique: str) -> float:
    return SC_T if technique == "self_consistency" else REF_T


def fmt_acc(v: Optional[float]) -> str:
    return "--" if v is None else pct(v)


# ---------------------------------------------------------------------------
# Table generators
# ---------------------------------------------------------------------------

def gen_tab_results(idx) -> str:
    rows = []
    for tech in TECHNIQUE_ORDER:
        cells = []
        for model in MODELS:
            for task in TASKS:
                v = acc(idx, model, task, tech)
                cells.append(fmt_acc(v))
        rows.append(f"{TECHNIQUE_LABELS[tech]} & " + " & ".join(cells) + r" \\")
    return "\n".join(rows)


def gen_tab_tempsweep(idx) -> str:
    rows = []
    for t in [0.0, 0.3, 0.7, 1.0]:
        cells = []
        for model in MODELS:
            # few-shot CoT single sample at this temperature
            v_fs = acc(idx, model, "gsm8k", "fs_cot", par=1, temp=t)
            cells.append(fmt_acc(v_fs))
            # self-consistency only at its defined setting
            if t == SC_T:
                v_sc = acc(idx, model, "gsm8k", "self_consistency", par=1, temp=SC_T)
                cells.append(fmt_acc(v_sc))
            else:
                cells.append("---")
        rows.append(f"{t:g} & " + " & ".join(cells) + r" \\")
    return "\n".join(rows)


def gen_tab_cost(idx) -> str:
    rows = []
    for tech in TECHNIQUE_ORDER:
        cells = []
        for model in MODELS:
            row = idx.get((model, "gsm8k", tech, 1, ref_temp(tech)))
            if row is None or not row.get("complete", False):
                cells += ["--", "--"]
                continue
            mult = 4 if tech == "self_consistency" else 1
            tok = row["mean_tokens"] * mult
            lat = row["mean_latency_s"] * mult
            cells += [f"{tok:.0f}", num(lat, 1)]
        rows.append(f"{TECHNIQUE_LABELS[tech]} & " + " & ".join(cells) + r" \\")
    return "\n".join(rows)


TASK_LABELS = {"gsm8k": "GSM8K", "humaneval": "HumanEval"}


def gen_tab_aer(results) -> str:
    aer = results.get("aer", {})
    rows = []
    for model in MODELS:
        for task in TASKS:
            entry = aer.get(model, {}).get(task)
            label = TASK_LABELS.get(task, task)
            if entry is None:
                rows.append(f"{MODEL_LABELS[model]} & {label} & -- & -- & -- \\\\")
                continue
            rows.append(f"{MODEL_LABELS[model]} & {label} & "
                        f"{entry['aer']:.2f} & {entry['sigma_alg']:.4f} & "
                        f"{entry['sigma_lex']:.4f} \\\\")
    return "\n".join(rows)


# ---------------------------------------------------------------------------
# main.tex patching
# ---------------------------------------------------------------------------

BEGIN_RE = re.compile(r"^%BEGIN-TABLE\s+([\w:]+)\s*$", re.M)
END_RE = re.compile(r"^%END-TABLE\s*$", re.M)


def patch_tex(generators: Dict[str, str]) -> int:
    """Replace each table body between its %BEGIN-TABLE/%END-TABLE markers.

    All replacement positions are collected from the ORIGINAL text first and
    the file is rebuilt in one pass, so length changes in earlier bodies never
    shift the offsets of later blocks.
    """
    with open(MAIN_TEX) as f:
        tex = f.read()
    blocks = []  # (start_after_begin, end_before_end, body)
    for m in BEGIN_RE.finditer(tex):
        label = m.group(1)
        end = END_RE.search(tex, m.end())
        if end is None:
            continue
        body = generators.get(label)
        if body is None:
            continue
        blocks.append((m.end(), end.start(), body))
    if not blocks:
        return 0
    out: List[str] = []
    pos = 0
    for start, end, body in blocks:
        out.append(tex[pos:start])
        out.append("\n" + body + "\n")
        pos = end
    out.append(tex[pos:])
    with open(MAIN_TEX, "w") as f:
        f.write("".join(out))
    return len(blocks)


def main() -> None:
    results = load_results()
    idx = index_table(results)

    generators = {
        "tab:results": gen_tab_results(idx),
        "tab:tempsweep": gen_tab_tempsweep(idx),
        "tab:cost": gen_tab_cost(idx),
        "tab:aer": gen_tab_aer(results),
    }
    n = patch_tex(generators)
    print(f"[update] patched {n} tables in {MAIN_TEX}")

    # Echo the headline numbers for prose/abstract use.
    print("\n-- headline numbers --")
    for model in MODELS:
        g = acc(idx, model, "gsm8k", "direct")
        f = acc(idx, model, "gsm8k", "fs_cot")
        sc = acc(idx, model, "gsm8k", "self_consistency")
        print(f"{MODEL_LABELS[model]:>3} GSM8K  direct={fmt_acc(g)}  fs_cot={fmt_acc(f)}"
              f"  sc={fmt_acc(sc)}", end="")
        if g and f:
            print(f"  (fs-direct gain={(f - g) * 100:+.1f} pts)", end="")
        print()
    for model in MODELS:
        g = acc(idx, model, "humaneval", "direct")
        f = acc(idx, model, "humaneval", "fs_cot")
        sc = acc(idx, model, "humaneval", "self_consistency")
        print(f"{MODEL_LABELS[model]:>3} HumanEval direct={fmt_acc(g)}  fs_cot={fmt_acc(f)}"
              f"  sc={fmt_acc(sc)}")
    if results.get("aer"):
        for model, tasks in results["aer"].items():
            for task, e in tasks.items():
                print(f"AER {MODEL_LABELS.get(model, model)}/{task} = {e['aer']:.2f}")


if __name__ == "__main__":
    main()
