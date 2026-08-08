import pypdf
r = pypdf.PdfReader('main.pdf')
for i, p in enumerate(r.pages):
    # measure bottom-most text y in right column and left column
    words = p.extract_text().split('\n')
    print(f'page {i+1}: {len(words)} text lines')
