import re

text = open('main.tex').read()

print('=== 1. Abstract ===')
m = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', text, re.S)
ab = m.group(1)
ab_clean = re.sub(r'\\[a-zA-Z]+', ' ', ab)
ab_clean = re.sub(r'[{}%$]', ' ', ab_clean)
words = [w for w in ab_clean.split() if w]
print('word count:', len(words))
# check for math/symbols
math_chars = [c for c in ab if c in '$\\{}_^']
print('math/special chars in abstract:', len(math_chars))

print()
print('=== 2. Keywords ===')
m2 = re.search(r'\\begin\{IEEEkeywords\}(.*?)\\end\{IEEEkeywords\}', text, re.S)
kw = [k.strip().rstrip('.').rstrip(',') for k in m2.group(1).split(',')]
print('count:', len(kw), '->', kw)

print()
print('=== 3. Figures/tables cited before appearing ===')
# order of \label for fig/tab vs \ref usage
labels = [(m.start(), m.group(1)) for m in re.finditer(r'\\label\{(fig:[^}]+|tab:[^}]+)\}', text)]
for pos, lab in labels:
    refs = [r.start() for r in re.finditer(r'\\ref\{' + re.escape(lab) + r'\}', text)]
    cited_before = any(r < pos for r in refs)
    print(f'{lab}: defined at pos {pos}, cited {len(refs)}x, first-cited-before-def: {cited_before}')

print()
print('=== 4. Acronym definitions on first use ===')
body = text.split('\\begin{thebibliography}')[0]
for acro in ['LLM', 'CoT', 'ToT', 'ReAct', 'RAG', 'AER', 'GSM8K', 'CSQA', 'ROUGE', 'REML', 'CI']:
    first = body.find(acro)
    ctx = body[max(0, first-60):first+len(acro)+30].replace('\n', ' ')
    print(f'{acro}: first at {first} -> ...{ctx}...')

print()
print('=== 5. Punctuation after citation brackets ===')
# find "cite{X}.word" or "cite{X}" followed by punctuation rules - spot check
bad = re.findall(r'\\cite\{[^}]*\}[a-zA-Z]', body)
print('cite immediately followed by letter (should be none):', bad[:5] if bad else 'none')

print()
print('=== 6. Title check ===')
mt = re.search(r'\\title\{(.*?)\}', text, re.S)
title = mt.group(1).replace('\n', ' ')
print('title:', title.strip())
bad_syms = [c for c in title if c in '\\$_{}^&']
print('forbidden chars in title:', bad_syms if bad_syms else 'none')

print()
print('=== 7. eqref/ref soft references ===')
hard = re.findall(r'\((?:1|2|3|4|5|6|7|8|9|10)\)', body)
print('hard-coded (n) parens (sample):', hard[:5] if hard else 'none')

print()
print('=== 8. "essentially" / "data is" / "alternately" checks ===')
for pat in ['essentially', 'data is', 'alternately', 'inset', 'prooves']:
    hits = re.findall(pat, body, re.I)
    print(f'{pat}: {len(hits)}')

print()
print('=== 9. Number consistency spot-checks (abstract vs body) ===')
pairs = [('58.4', '58.4'), ('83.1', '83.1'), ('74.6', '74.6'), ('94.2', '94.2'), ('0.78', '0.78')]
for a, b in pairs:
    ca = body.count(a)
    print(f'{a} occurs {ca}x in body')
