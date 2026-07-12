# Handoff — Part 1: Introduction & Literature Review

**Status:** draft
**Sections touched:** `sec:intro`, `sec:related`, `sec:notation` (plus
placeholder shells for §III–§IX and `Acknowledgment`).
**New figures/tables:** none (figures/tables land in Parts 2 and 3).
**New citations:** `b1`–`b8` (Brown 2020, Min 2022, Wei 2022, Wang
2023, Yao ToT 2023, Yao ReAct 2023, Lewis 2020, Holtzman 2020).
**Headline numbers (Part 3 only):** n/a.
**Acronyms defined this part:** LLM, CoT, ToT, RAG, ICL (in-context
learning) — all spelled out at first use in §I or §II. Part 2 may add
others (e.g., MMLU, GSM8K) and must spell them out too.
**Open questions for the user:**

1. Replace `<<DEPARTMENT>>`, `<<ORGANIZATION>>`, `<<CITY>>`,
   `<<COUNTRY>>`, and the three `<<EMAIL_*>>` placeholders in the
   author block before any compile-and-share.
2. Confirm the author order is **Sarwagya Acharya (1st) → Nitesh Pant
   (2nd) → Brishav Joshi (3rd)**.  This order is permanent for IEEE
   indexing and cannot be changed later without renumbering every
   citation that uses numeric `b*` keys.
3. Decide whether Part 2 should add a second tier of 2024–2025
   references (instruction-tuning surveys, automatic prompt
   optimisation).  Not blocking Part 2.
4. The "Brown et al." abbreviation for b1 is a width concession; the
   final camera-ready should be checked against the IEEE author
   guidelines.

**Compile status:** **not compiled in this environment** — no LaTeX
toolchain present.  The skeleton is byte-identical to the working
template at
`IEEE-conference-template-062824/IEEE-conference-template-062824.tex`
except for the renamed `main.tex` and the new content.  To verify,
the user can run:

```bash
cd "/Users/sarwagyaacharya/6th sem/AOA/research"
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex   # second pass for refs
```

**Next-part dependencies (locked for Part 2):**

- Citation keys `b1`–`b8` are **locked**; Part 2 may add `b9`, `b10`,
  … but must not renumber existing entries.
- Labels `sec:intro`, `sec:related`, `sec:notation` exist and are
  referenced from `main.tex`.  Part 2 may reference them (e.g.,
  "as defined in §II-E") but must not rename or delete them.
- Notation table is sketched in §II-E; Part 2 must keep the symbols
  $P, x, y, r, \theta, T, k, p$ consistent.
- The contribution list in §I names a taxonomy (§III) and a formal
  framework (§IV) — Part 2 must deliver these or the introduction's
  claims become unsupported.
- The acronym set (LLM, CoT, ToT, RAG, ICL) is in scope; Part 2 should
  not redefine them.

**Risks / known issues:**

- The IEEE template's red template-removal line is still present at
  the end of the file.  Per `AGENTS.md` §12 step 7, this must be
  removed before any "final" output.  Kept in Part 1 for now so the
  PDF still compiles to the same reference layout during drafting.
- `\thanks{}` in the title is empty (no funding).  The template
  comment says to delete the funding footnote if none — leaving it as
  an empty `\thanks{}` is safe but should be cleaned up at the end.
