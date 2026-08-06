#!/usr/bin/env python3
"""Print per-page text stats for main.pdf."""
import pypdf

r = pypdf.PdfReader("main.pdf")
print("pages:", len(r.pages))
for i, p in enumerate(r.pages):
    t = p.extract_text() or ""
    lines = [ln for ln in t.splitlines() if ln.strip()]
    print(f"--- page {i+1}: {len(t)} chars, {len(lines)} lines ---")
    if lines:
        print("  first:", " ".join(lines[0].split())[:90])
        print("  last :", " ".join(lines[-1].split())[:90])
