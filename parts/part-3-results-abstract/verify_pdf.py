import pypdf, re

r = pypdf.PdfReader('main.pdf')
print('PAGES:', len(r.pages))
t = r.pages[-1].extract_text()
print('--- last page first 500 chars ---')
print(t[:500])
print()
# Reference numbering spot check
alltext = '\n'.join(p.extract_text() or '' for p in r.pages)
for n in ['[1]', '[7]', '[8]', '[10]', '[22]']:
    idx = alltext.find(n)
    ctx = alltext[idx:idx+70].replace('\n', ' ') if idx >= 0 else 'NOT FOUND'
    print(f'{n}: {ctx}')
