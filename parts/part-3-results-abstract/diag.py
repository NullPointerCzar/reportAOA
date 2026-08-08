import re
tex = open('main.tex').read()
m = re.search(r'\\begin\{tabular\}\{lcccc\}(.*?)\\end\{tabular\}', tex, re.S)
if m is None:
    print('NO MATCH for lcccc tabular')
    # find all tabular envs
    for mm in re.finditer(r'\\begin\{tabular\}\{([^}]*)\}', tex):
        print('found tabular with cols:', mm.group(1), 'at', mm.start())
else:
    print('MATCH. Content:')
    print(repr(m.group(1)[:200]))
    rows = {}
    for line in m.group(1).split('\\\\'):
        cells = [re.sub(r'\\\\(?:top|mid|bottom)rule', '', c).strip() for c in line.split('&')]
        if len(cells) == 5 and cells[0] and cells[1] and re.match(r'^\d', cells[1]):
            rows[cells[0].strip()] = [float(x) for x in cells[1:5]]
    print('rows:', rows)
