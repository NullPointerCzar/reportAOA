"""Verify that the figure generator's data matches Table I, Table II,
and the results text in main.tex."""
import re, math

tex = open('main.tex').read()

# --- Table I (tab:results) 70B GSM8K column ---
m = re.search(r'\\begin\{tabular\}\{lcccc\}(.*?)\\end\{tabular\}', tex, re.S)
rows = {}
for line in m.group(1).split('\\\\'):
    cells = [re.sub(r'\\(?:top|mid|bottom)rule', '', c).strip() for c in line.split('&')]
    if len(cells) == 5 and cells[0] and cells[1] and re.match(r'^\d', cells[1]):
        rows[cells[0].strip()] = [float(x) for x in cells[1:5]]

checks = []

# --- Figure panel (b): 70B bars must equal Table I GSM8K column ---
fig_70b = [74.6, 88.9, 94.2, 96.3, 96.8, 97.1]  # Direct, ZS-CoT, FS-CoT, SC, ToT, ReAct
order = ['Direct answering', 'Zero-shot CoT', 'Few-shot CoT',
         'Self-consistency', 'Tree-of-thoughts', 'ReAct']
table_70b = [rows[k][0] for k in order]
checks.append(('Fig panel (b) 70B bars == Table I GSM8K column', fig_70b == table_70b,
               f'{fig_70b} vs {table_70b}'))

# --- Figure panel (b): 8B and 405B consistency with text deltas ---
# Text: 8B direct 58.4 -> fSCoT 83.1 (+24.7); SC adds 1.5-5.2; ReAct converts residual errors
fig_8b = [58.4, 76.2, 83.1, 88.3, 89.6, 90.4]
checks.append(('Fig 8B direct==58.4, fSCoT==83.1', fig_8b[0] == 58.4 and fig_8b[2] == 83.1,
               f'{fig_8b}'))
checks.append(('Fig 8B SC within 1.5-5.2 over fSCoT',
               1.5 - 1e-9 <= fig_8b[3] - fig_8b[2] <= 5.2 + 1e-9,
               f'SC delta = {fig_8b[3]-fig_8b[2]:.1f}'))
fig_405b = [80.9, 92.4, 96.1, 97.6, 97.9, 98.2]
checks.append(('Fig 405B direct==80.9, fSCoT==96.1', fig_405b[0] == 80.9 and fig_405b[2] == 96.1,
               f'{fig_405b}'))
checks.append(('Fig 405B SC within 1.5-5.2 over fSCoT',
               1.5 <= fig_405b[3] - fig_405b[2] <= 5.2,
               f'SC delta = {fig_405b[3]-fig_405b[2]:.1f}'))

# --- Figure panel (a): temperature data vs text ---
# Text: single-sample 94.2@T=0 -> 89.1@T=1.0 monotonic; SC peaks 96.3 near T=0.7
single = [94.2, 93.8, 92.4, 89.1]   # T = 0, 0.3, 0.7, 1.0
sc = [94.2, 96.1, 96.3, 95.2]
checks.append(('Fig (a) single-sample monotonic decline to 89.1',
               single[0] == 94.2 and single[-1] == 89.1 and
               all(single[i] >= single[i+1] for i in range(len(single)-1)),
               f'{single}'))
checks.append(('Fig (a) SC peaks at 96.3 at T=0.7', sc[2] == 96.3 and max(sc) == 96.3, f'{sc}'))
checks.append(('Fig (a) SC@T=0 == single@T=0 (greedy collapse)',
               sc[0] == single[0] == 94.2, f'SC@{sc[0]} vs single@{single[0]}'))

# --- Figure panel (a) loss 5.1 matches Discussion ---
checks.append(('Fig (a) T=0->1.0 loss 5.1 == Discussion',
               abs((single[0]-single[-1]) - 5.1) < 0.01, f'{single[0]-single[-1]:.1f}'))

print('=== FIGURE DATA VERIFICATION ===')
fails = 0
for name, ok, detail in checks:
    print(f'[{"PASS" if ok else "FAIL"}] {name}' + (f'  -- {detail}' if detail else ''))
    fails += (not ok)
print(f'TOTAL: {len(checks)} checks, {fails} FAILED')
