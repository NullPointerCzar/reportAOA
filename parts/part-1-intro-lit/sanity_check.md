# Part 1 — Sanity Check vs `AGENTS.md` §14 (Pre-Submission Checklist)

This file is the auto-audit for Part 1 of `main.tex`.  Items marked
**✓ pass** are satisfied by the current draft.  Items marked
**⚠ user action** need input from the user before the next pass.

## Title block
- ✓ Title has no symbols, math, footnotes, or sub-title.
- ✓ Title is one logical sentence (broken across two lines by LaTeX,
  which is permitted).
- ⚠ `\thanks{}` is empty — the IEEE template comment says to delete
  the funding footnote if none. Safe for now, but should be removed
  before camera-ready.
- ⚠ Author block contains six `<<…>>` placeholders
  (`<<DEPARTMENT>>`, `<<ORGANIZATION>>`, `<<CITY>>`, `<<COUNTRY>>`,
  and three `<<EMAIL_*>>`).  Must be replaced before any compile
  that is shared externally.

## Abstract
- ✓ Single paragraph inside `\begin{abstract}…\end{abstract}`.
- ✓ No math, no symbols, no footnotes.
- ⚠ Working abstract only — must be **rewritten in Part 3** after
  results are known (per `AGENTS.md` §2 Part 3 rule).

## Index terms
- ✓ Six lowercase, comma-separated keywords inside
  `\begin{IEEEkeywords}…\end{IEEEkeywords}`.

## Headings
- ✓ All headings produced by `\section` / `\subsection`.  No
  hand-numbered `1.`, `2.`, `2.1`.
- ✓ At least two subsections under §II (II-A, II-B, II-C, II-D, II-E).

## Cross-references
- ✓ All citation keys defined in `thebibliography` (b1–b8).
- ✓ Numeric square-bracket citations via `\cite{}` (template default).
- ✓ Section references via `\ref{}` and `\label{}`; no hard-coded
  numbers in prose.
- ✓ `\label{sec:notation}` placed in §II-E (the *primer* subsection)
  so Part 2 can refer to it.

## Common-mistakes list (`format.md` §II.E)
- ✓ No "essentially" used as "approximately".
- ✓ No "alternately" (used "alternative…", "across these works").
- ✓ "et al." used only for ≥2-author citations, no trailing period
  inside the "et".
- ✓ "data" not used (n/a).
- ✓ "non-" joined to host word (n/a in Part 1 prose).
- ✓ "i.e." / "e.g." not used (no false positives).
- ⚠ "insert" not used as a figure caption term (n/a — figures land
  in Part 2/3).  "inset" is not used either.

## Figures / tables
- n/a for Part 1 (no figures or tables yet).  Reminder for Part 2:
  captions go below figures, table heads above; axis labels use
  words + units in parentheses.

## Math / equations
- ✓ Math is inside `$…$`; no `eqnarray` used.
- ✓ Greek symbols (`θ`, `γ` if used later) not italicised; Roman
  symbols (`P`, `x`, `y`, `r`, `T`, `k`, `p`) are in math italic by
  default which is correct.
- n/a for `\eqref` — no numbered equations in Part 1.  Part 2 must
  use `align` or `IEEEeqnarray`, never `eqnarray`.

## References
- ✓ 8 entries in `thebibliography`, in citation order, IEEE format
  (Author, "Title," Venue, vol., pp., Year).
- ⚠ Brown et al. is abbreviated as "T. Brown et al." to fit IEEE
  column width; the GPT-3 paper has 31 authors.  Confirm for
  camera-ready.
- ⚠ "Proc." is abbreviated as "Proc.\ " inside `\emph{}` — the IEEE
  template itself uses this convention, so this is correct.

## Compile
- ⚠ **Not compiled** in this session — the LaTeX toolchain was not
  available.  The skeleton is byte-identical to the working template
  at `IEEE-conference-template-062824/IEEE-conference-template-062824.tex`
  apart from filename and content, so a `pdflatex main.tex` on the
  user's machine should succeed.  Two passes are needed for any
  `\ref`/`\cite` resolution.

## Open / user actions before Part 2 starts
1. **Replace the 6 placeholders** in the author block.
2. **Decide** whether the red template-removal line stays in `main.tex`
   during Part 2 drafting.  Recommendation: keep it until the very
   last edit, then strip it (per `AGENTS.md` §12 step 7).
3. **Confirm** the author order and the "Brown et al." abbreviation.
4. **Compile locally** to confirm the draft produces a clean PDF
   before handing off to Part 2.
