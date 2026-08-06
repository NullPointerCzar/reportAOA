import re
text = open('main.tex').read()

m = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', text, re.S)
ab = m.group(1)
print('=== chars in set [$\\{}_^] ===')
for i, c in enumerate(ab):
    if c in '$\\{}_^':
        print(repr(ab[max(0,i-25):i+25]))
print()
print('=== context of (1) in body ===')
body = text.split('\\begin{thebibliography}')[0]
for m3 in re.finditer(r'\(1\)', body):
    print('...' + body[max(0,m3.start()-40):m3.end()+20].replace('\n',' ') + '...')
