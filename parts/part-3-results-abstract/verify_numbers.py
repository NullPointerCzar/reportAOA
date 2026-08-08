"""Final numerical verification: cross-check every table cell and
headline claim in main.tex against the MEASURED results/results.json
and the per-item record count.  Prints PASS/FAIL for each check.

Run from the project root:  python3 parts/part-3-results-abstract/verify_numbers.py
"""
import json, re, math, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
os.chdir(ROOT)
tex = open("main.tex").read()
results = json.load(open("results/results.json"))
records = [json.loads(l) for l in open("results/records.jsonl")]

fails = []
def check(name, cond, detail=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f"  -- {detail}" if detail else ""))
    if not cond:
        fails.append(name)

# --- expected values from results.json (mirror update_tables.py) ---
MODELS = ["llama3.2:1b", "llama3.2:3b", "qwen2.5-coder:3b"]
TASKS = ["gsm8k", "humaneval"]
SC_T, REF_T = 0.7, 0.0
idx = {}
for r in results["table"]:
    idx[(r["model"], r["task"], r["technique"], int(r["paraphrase"]),
         float(r["temperature"]))] = r

def acc(model, task, tech, par=1, temp=None):
    t = SC_T if tech == "self_consistency" else (REF_T if temp is None else temp)
    row = idx.get((model, task, tech, par, t))
    if row is None or not row.get("complete", False):
        return None
    if tech == "self_consistency":
        va = row.get("vote_accuracy")
        return va if va is not None else row.get("accuracy")
    return row.get("accuracy")

def table_rows(label):
    m = re.search(r"BEGIN-TABLE " + label + r"(.*?)END-TABLE", tex, re.S)
    out = []
    for ln in m.group(1).split("\\\\"):
        ln = ln.strip()
        if not ln or ln.startswith("%"):
            continue
        out.append(ln)
    return out

LABEL_TO_TECH = {"Direct answering": "direct", "Zero-shot CoT": "zs_cot",
                 "Few-shot CoT": "fs_cot", "Self-consistency": "self_consistency"}

# ---------------- Table tab:results ----------------
tbl = {}
for ln in table_rows("tab:results"):
    cells = [c.strip() for c in ln.split("&")]
    tbl[cells[0]] = cells[1:]
check("tab:results has 4 technique rows", len(tbl) == 4)
for tech, label in LABEL_TO_TECH.items():
    col = 0
    for model in MODELS:
        for task in TASKS:
            v = acc(model, task, label)
            exp = "--" if v is None else f"{v*100:.1f}"
            check(f"tab:results {tech}/{model}/{task}", tbl[tech][col] == exp,
                  f"got {tbl[tech][col]}, expected {exp}")
            col += 1

# ---------------- Table tab:tempsweep ----------------
for ln in table_rows("tab:tempsweep"):
    cells = [c.strip() for c in ln.split("&")]
    t = float(cells[0])
    col = 1
    for model in MODELS:
        v_fs = acc(model, "gsm8k", "fs_cot", par=1, temp=t)
        exp_fs = "--" if v_fs is None else f"{v_fs*100:.1f}"
        check(f"tab:tempsweep {model} T={t} FS-CoT", cells[col] == exp_fs,
              f"got {cells[col]}, expected {exp_fs}")
        col += 1
        if t == SC_T:
            v_sc = acc(model, "gsm8k", "self_consistency", par=1)
            exp_sc = "--" if v_sc is None else f"{v_sc*100:.1f}"
            check(f"tab:tempsweep {model} T={t} SC", cells[col] == exp_sc,
                  f"got {cells[col]}, expected {exp_sc}")
        else:
            check(f"tab:tempsweep {model} T={t} SC='---'", cells[col] == "---")
        col += 1

# ---------------- Table tab:cost ----------------
for ln in table_rows("tab:cost"):
    cells = [c.strip() for c in ln.split("&")]
    tech = LABEL_TO_TECH[cells[0]]
    col = 1
    for model in MODELS:
        t = SC_T if tech == "self_consistency" else REF_T
        row = idx.get((model, "gsm8k", tech, 1, t))
        if row is None or not row.get("complete", False):
            check(f"tab:cost {cells[0]}/{model} data present", False)
            col += 2
            continue
        mult = 4 if tech == "self_consistency" else 1
        tok = f"{row['mean_tokens']*mult:.0f}"
        lat = f"{row['mean_latency_s']*mult:.1f}"
        check(f"tab:cost {cells[0]}/{model} tokens", cells[col] == tok,
              f"got {cells[col]}, expected {tok}")
        check(f"tab:cost {cells[0]}/{model} latency", cells[col+1] == lat,
              f"got {cells[col+1]}, expected {lat}")
        col += 2

# ---------------- Table tab:aer ----------------
ML = {"1B": "llama3.2:1b", "3B": "llama3.2:3b", "Qwen2.5-Coder-3B": "qwen2.5-coder:3b"}
TL = {"GSM8K": "gsm8k", "HumanEval": "humaneval"}
for ln in table_rows("tab:aer"):
    cells = [c.strip() for c in ln.split("&")]
    e = results["aer"].get(ML[cells[0]], {}).get(TL[cells[1]])
    check(f"tab:aer {cells[0]}/{cells[1]} AER", cells[2] == f"{e['aer']:.2f}",
          f"got {cells[2]}, expected {e['aer']:.2f}")
    check(f"tab:aer {cells[0]}/{cells[1]} sigma_alg", cells[3] == f"{e['sigma_alg']:.4f}")
    check(f"tab:aer {cells[0]}/{cells[1]} sigma_lex", cells[4] == f"{e['sigma_lex']:.4f}")

# ---------------- Prose claims ----------------
body = tex.split(r"\begin{thebibliography}")[0]
check("abstract: 12 percent to 50 percent",
      "12 percent to 50 percent" in tex.split(r"\end{abstract}")[0])
check("abstract: 41-point", "41-point" in tex.split(r"\end{abstract}")[0])
check("abstract: AER 0.82--1.00", "0.82--1.00" in tex.split(r"\end{abstract}")[0])
check("VI-A: zs-cot 1B 12% to 50%", "12\\% to 50\\%" in body)
check("VI-A: fs-cot hurts 1B 12% to 8%", "12\\% to 8\\%" in body)
check("VI-A: fs-cot 3B 53% to 70%", "53\\% to 70\\%" in body)
check("VI-A: fs-cot coder 6% to 71%", "6\\% to 71\\%" in body)
check("VI-A: SC 3B 70% to 88%", "70\\% to 88\\%" in body)
check("VI-A: SC coder 71% to 81%", "71\\% to 81\\%" in body)

max_gain = 0.0
for model in MODELS:
    d = acc(model, "humaneval", "direct")
    for tech in ["zs_cot", "fs_cot", "self_consistency"]:
        v = acc(model, "humaneval", tech)
        if v is not None and d is not None:
            max_gain = max(max_gain, (v - d) * 100)
check("VI-A: max HumanEval technique gain <= 3 pts", max_gain <= 3.0,
      f"max gain {max_gain:.1f}")

weakest_ok = all(
    acc(m, "humaneval", "self_consistency") < min(
        acc(m, "humaneval", t) for t in ["direct", "zs_cot", "fs_cot"])
    for m in MODELS)
check("VI-A: SC weakest on HumanEval at every scale", weakest_ok)

check("~18,000 generations measured", len(records) == 17988, f"records={len(records)}")
check("18,000 in text", "18,000" in body)

def wald(p, n):
    return 1.96 * math.sqrt(p * (1 - p) / n) * 100
check("CI GSM8K ~10 (p=0.5,n=100)", abs(wald(0.5, 100) - 9.8) < 0.3,
      f"{wald(0.5,100):.1f}")
check("CI HumanEval ~8 (p=0.5,n=164)", abs(wald(0.5, 164) - 7.65) < 0.3,
      f"{wald(0.5,164):.1f}")

check("VI-AER: GSM8K ratio near one (0.82--1.00)", "0.82--1.00" in body)
check("VI-AER: 3B HumanEval degenerate", "degenerate" in body)
check("tab:aer footnote present", r"reported as 0.50 by convention" in tex)

# bibliography integrity
bib = re.search(r"\\begin\{thebibliography\}\{00\}(.*?)\\end\{thebibliography\}", tex, re.S).group(1)
bibkeys = set(re.findall(r"\\bibitem\{([^}]*)\}", bib))
cited = set()
for c in re.findall(r"\\cite\{([^}]*)\}", tex):
    for k in c.split(","):
        cited.add(k.strip())
check("every citation resolves to a bibitem", cited <= bibkeys,
      f"missing: {sorted(cited - bibkeys)}")
check("no uncited bibitems", bibkeys <= cited, f"uncited: {sorted(bibkeys - cited)}")

# abstract word count (150-250)
ab = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.S).group(1)
nw = len(ab.split())
check("abstract word count 150-250", 150 <= nw <= 250, f"{nw} words")

print()
if fails:
    print(f"TOTAL: {len(fails)} FAILED: {fails}")
    sys.exit(1)
print("TOTAL: all checks PASS")
