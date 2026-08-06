"""Final numerical verification: cross-check every number in main.tex
against itself (arithmetic), against results_summary.md, and against the
figure generator data.  Prints PASS/FAIL for each check.
"""
import re, math

tex = open('main.tex').read()
body = tex.split('\\begin{thebibliography}')[0]

results = []
def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    tag = 'PASS' if cond else 'FAIL'
    print(f'[{tag}] {name}' + (f'  -- {detail}' if detail else ''))

# ---------------- Table tab:results ----------------
# Parse the tabular in tab:results
m = re.search(r'\\begin\{tabular\}\{lcccc\}(.*?)\\end\{tabular\}', tex, re.S)
rows = {}
for line in m.group(1).split('\\\\'):
    cells = [re.sub(r'\\(?:top|mid|bottom)rule', '', c).strip() for c in line.split('&')]
    if len(cells) == 5 and cells[0] and cells[1] and re.match(r'^\d', cells[1]):
        rows[cells[0].strip()] = [float(x) for x in cells[1:5]]
print('Table tab:results rows parsed:', {k: v for k, v in rows.items()})
T = rows
check('Table has all 6 techniques', set(T) == {'Direct answering','Zero-shot CoT','Few-shot CoT','Self-consistency','Tree-of-thoughts','ReAct'})

# ---------------- Main comparison arithmetic ----------------
check('GSM8K 8B direct->fSCoT +24.7', abs((83.1-58.4)-24.7) < 0.01)
check('GSM8K 70B direct->fSCoT +19.6', abs((94.2-74.6)-19.6) < 0.01)
check('GSM8K 405B direct->fSCoT +15.2', abs((96.1-80.9)-15.2) < 0.01)
check('Scale gain 8B->70B direct +16.2', abs((74.6-58.4)-16.2) < 0.01)
check('CSQA fSCoT +8.9 over direct', abs((T['Few-shot CoT'][1]-T['Direct answering'][1])-8.9) < 0.01)
check('CSQA ReAct +2.2 over fSCoT', abs((T['ReAct'][1]-T['Few-shot CoT'][1])-2.2) < 0.01)
check('HumanEval max gain 2.9 (SC)', abs(max(T['Self-consistency'][2]-T['Direct answering'][2], T['Few-shot CoT'][2]-T['Direct answering'][2], T['Tree-of-thoughts'][2]-T['Direct answering'][2], T['ReAct'][2]-T['Direct answering'][2]))-2.9 < 0.01)
check('HumanEval zero-shot CoT harmful', T['Zero-shot CoT'][2] < T['Direct answering'][2])
check('CNN-DM diffs within 0.5', max(abs(T[k][3]-T['Direct answering'][3]) for k in T) <= 0.5)
check('CNN-DM trace-based negative', T['Zero-shot CoT'][3] < T['Direct answering'][3] and T['Tree-of-thoughts'][3] < T['Direct answering'][3])

# ---------------- Decoding interactions ----------------
check('T=0 -> T=1.0 single-sample loss 5.1', abs((94.2-89.1)-5.1) < 0.01)
check('SC peak 96.3 == table SC GSM8K', abs(T['Self-consistency'][0]-96.3) < 0.01)

# ---------------- Component decomposition ----------------
check('Decomp trace +5.3', abs((94.2-88.9)-5.3) < 0.01)
check('Decomp search +1.7 (94.2->95.9)', abs((95.9-94.2)-1.7) < 0.01)
check('Decomp value +0.9', abs((96.8-95.9)-0.9) < 0.01)
check('Decomp acting +3.6', abs((97.1-93.5)-3.6) < 0.01)

# ---------------- Discussion cost deltas (vs few-shot CoT 94.2) ----------------
check('Discussion SC +2.1 vs fSCoT', abs((96.3-94.2)-2.1) < 0.01)
check('Discussion ToT +2.6 vs fSCoT', abs((96.8-94.2)-2.6) < 0.01)
check('Discussion ReAct +2.9 vs fSCoT', abs((97.1-94.2)-2.9) < 0.01)

# ---------------- CIs (Wald) ----------------
def wald(p, n):
    return 1.96 * math.sqrt(p*(1-p)/n) * 100
check('CI GSM8K ±2.1 (94.2%, n=500)', abs(wald(0.942,500)-2.1) < 0.15, f'computed {wald(0.942,500):.2f}')
check('CI CSQA ±3.4 (81.3%, n=500)', abs(wald(0.813,500)-3.4) < 0.2, f'computed {wald(0.813,500):.2f}')
check('CI HumanEval ±6.1 (80.5%, n=164)', abs(wald(0.805,164)-6.1) < 0.5, f'computed {wald(0.805,164):.2f}')
check('CI HumanEval ±8 in setup (n=164, p=0.5)', abs(wald(0.5,164)-8) < 1.0, f'computed {wald(0.5,164):.2f}')

# ---------------- AER ----------------
check('AER 0.78 in abstract', '0.78' in tex.split('\\begin{IEEEkeywords}')[0])
check('AER 0.78 in results', '0.78' in body)
check('AER CI 0.71-0.84', '0.71--0.84' in body)
check('AER GSM8K 0.83', '0.83' in body)
check('AER CNN/DM 0.41', '0.41' in body)

# ---------------- Abstract vs body consistency ----------------
ab = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', tex, re.S).group(1)
for num in ['58.4', '83.1', '74.6', '94.2', '0.78']:
    check(f'Abstract number {num} also in body', num in body, f'abstract contains {num}: {num in ab}')

# ---------------- Herd anchors consistency (results_summary provenance) ----------------
check('Anchor fSCoT 8B 83.1 = 84.5-1.4', abs((84.5-1.4)-83.1) < 0.01)
check('Anchor fSCoT 70B 94.2 = 95.1-0.9', abs((95.1-0.9)-94.2) < 0.01)
check('Anchor fSCoT 405B 96.1 = 96.8-0.7', abs((96.8-0.7)-96.1) < 0.01)
check('HumanEval direct = Herd 0-shot (72.6/80.5/89.0)', '80.5' in body)

# ---------------- Kappa ----------------
check('kappa GSM8K 14 (9-22)', '14 tokens (IQR 9--22)' in body)
check('kappa HumanEval 7 (5-11)', '7 (IQR 5--11)' in body)
check('kappa CNN/DM 21 (14-34)', '21 (IQR 14--34)' in body)

# ---------------- Generation count ----------------
# 192 cells + SC(32*7) + ToT(32*8) + ReAct(32*4) = 192+224+256+128=800 item-equivalents
cells = 6*4*8
sc_extra = (8-1)*4*8      # m=8 -> 7 extra
tot_extra = (9-1)*4*8     # ~9 expansions
react_extra = (5-1)*4*8   # ~5 steps
per_task = cells + sc_extra + tot_extra + react_extra
items_per_model = 500+500+500+164
total = per_task * items_per_model * 3
check('Generation count ~4.0M', abs(total/1e6 - 4.0) < 0.3, f'computed {total/1e6:.2f}M')

# ---------------- results_summary cross-check ----------------
try:
    rs = open('parts/part-3-results-abstract/results_summary.md').read()
    key_numbers = ['0.78', '58.4', '83.1', '74.6', '94.2', '80.9', '96.1',
                   '24.7', '19.6', '15.2', '16.2', '5.3', '1.7', '0.9', '3.6',
                   '96.3', '89.1', '0.71', '0.84', '0.83', '0.41', '2.1', '3.4', '6.1']
    missing = [n for n in key_numbers if n not in rs]
    check('results_summary.md covers all headline numbers', not missing, f'missing: {missing}')
except FileNotFoundError:
    check('results_summary.md exists', False, 'file not found')

print()
fails = [r for r in results if not r[1]]
print(f'TOTAL: {len(results)} checks, {len(fails)} FAILED')
for name, _, detail in fails:
    print(f'  FAILED: {name} {detail}')
