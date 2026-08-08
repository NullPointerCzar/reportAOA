# Handoff — Part 3: Results, Discussion & Abstract

**Status:** final — **measured data** (17,988 generations, `results/results.json`).
The earlier draft numbers in `results_summary.md` were illustrative
placeholders; they have been replaced by the real benchmark results
(see `results_summary.md` for the provenance of every headline number).
**Page count:** 9 (`pdflatex main.tex`, 2 passes, clean; only two
cosmetic underfull-hbox notes).
**Bibliography:** `\bibitem` entries physically ordered so printed
numbers follow first-citation order (IEEE style); keys b1–b26
unchanged; all 19 entries cited, none uncited.
**Sections touched:** abstract, `IEEEkeywords`, `sec:intro` (comment
banner), `sec:related`, `sec:taxonomy`, `sec:framework` (Eq.
`eq:divergence` compacted), `sec:setup` (research design, models,
hardware), `sec:results` + `tab:results`, `sec:results-main`,
`sec:results-decoding` + `tab:tempsweep`, `sec:results-cost` +
`tab:cost`, `sec:results-aer` + `tab:aer`, `sec:discussion`,
`sec:limitations`, `sec:conclusion`, Acknowledgment.
**New figures/tables:** `figures/fig-results.pdf` / `.png` (label
`fig:results`, regenerated from measured data by
`make_fig_results.py`); tables `tab:results` (table*),
`tab:tempsweep`, `tab:cost`, `tab:aer` filled from
`results/results.json` by `update_tables.py` (marker blocks
`%BEGIN-TABLE` / `%END-TABLE` preserved for re-generation).
**New citations:** none added in Part 3 (b1–b26 unchanged).
**Headline numbers (measured):**
- GSM8K (paraphrase 1, greedy): zero-shot CoT 1B 12.0→50.0 (+38.0);
  few-shot CoT 3B 53.0→70.0 (+17.0), Coder-3B 6.0→71.0 (+65.0),
  1B 12.0→8.0 (−4.0); self-consistency (m=4, T=0.7) 3B 88.0, Coder 81.0.
- Scale comparison: 1B zs-CoT +38.0 ≈ 1B→3B direct +41.0 (12.0→53.0).
- HumanEval: compressed; max gain +2.4 (Coder fs-CoT); zs-CoT
  neutral/negative; SC weakest at every scale.
- AER: GSM8K 0.99 / 0.82 / 1.00 (1B / 3B / Coder); HumanEval 0.98 /
  0.50 (degenerate, both σ² = 0) / 0.25.
- ~18,000 generations (17,988 records).
**Acronyms defined this part:** none new (LLM, CoT, AER reused).
**Open questions for the user:**
- Replace the `<<EMAIL_BRISHAV>>` placeholder in the author block
  before sharing (user chose to keep it for now).
- Confirm the Acknowledgment wording.
- Note: hardware is described as a single consumer gaming laptop
  (Acer Predator) with an NVIDIA RTX 4060 (8 GB VRAM) running Linux,
  using CUDA acceleration through Ollama (llama.cpp) — corrected from
  the earlier 16 GB / Apple Silicon / Metal claims.
**Compile status:** clean (`pdflatex main.tex`, 2 passes), 9 pages,
no LaTeX errors, no undefined references/citations, no overfull hboxes.
**Verification pass (final):** `verify_numbers.py` (updated for the
measured design) — all checks PASS: every table cell cross-checked
against `results/results.json`, headline prose claims verified,
bibliography integrity, abstract word count (234).
**Next-part dependencies:** n/a — this is the final part.  Locked
citation keys b1–b26, labels (`sec:*`, `tab:*`, `fig:*`, `eq:*`), and
the Φ/Ψ/Ω notation are unchanged.
