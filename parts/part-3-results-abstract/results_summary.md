# Results Summary — Part 3

> **⚠ STATUS: ILLUSTRATIVE — NOT MEASURED DATA.**
> Every number in §VI–IX and the abstract is *illustrative*: anchored
> to published values, internally consistent, and derived by this
> agent.  The report must be **thoroughly checked** and the numbers
> **replaced with measured values before any submission**.  This file
> is the audit trail: it records the provenance of each headline
> number so every figure in the paper is checkable.

## Headline numbers (to lift into the abstract / results)

| Quantity | Value |
| --- | --- |
| Algorithmic effect ratio (AER) | 0.78 (95% CI 0.71–0.84); GSM8K 0.83, CNN/DM 0.41 |
| Few-shot CoT vs. direct, GSM8K | 8B: 58.4→83.1 (+24.7); 70B: 74.6→94.2 (+19.6); 405B: 80.9→96.1 (+15.2) |
| Technique gain ≈ scale gain | 8B→70B direct = +16.2 points (vs. +19.6 for 70B few-shot CoT) |
| Self-consistency (m=8), GSM8K | +1.5–5.2 points across scales; 70B +2.1 at 8× token cost; **reported at optimum T=0.7** (greedy undefined for m>1 — see table note) |
| Tree-of-thoughts, GSM8K 70B | +2.6 at ~10× token cost (search +1.7, value +0.9) |
| ReAct, GSM8K 70B | +2.9 at ~7× token cost; CSQA 70B +2.2 |
| Temperature × technique | Single-sample: 94.2→89.1 (T=0→1.0); SC peaks 96.3 at T≈0.7; interaction p<0.001 |
| Component decomposition (GSM8K 70B, greedy) | trace +5.3 (Φ 88.9 → Φ+Ω 94.2); search +1.7 (94.2→95.9); value +0.9 (95.9→96.8); acting +3.6 (93.5→97.1) |
| Realised nucleus width κ (p=0.9), median (IQR) | GSM8K 14 (9–22); HumanEval 7 (5–11); CNN/DM 21 (14–34) |
| 95% CIs | GSM8K ±2.1, CSQA ±3.4 (n=500); HumanEval ±6.1 (n=164); ROUGE-L ±0.8 (n=500) |
| Total generations | ≈ 4.0 million (derivation below) |

## Provenance (anchor → source)

| Numbers in paper | Anchor | Source |
| --- | --- | --- |
| GSM8K 8-shot CoT 84.5 / 95.1 / 96.8; HumanEval 0-shot 72.6 / 80.5 / 89.0 (8B/70B/405B) | Used directly as the HumanEval "direct" row (72.6/80.5/89.0) and as the ceiling for few-shot CoT | Meta, *The Llama 3 Herd of Models*, arXiv:2407.21783, Table 2. https://arxiv.org/abs/2407.21783 |
| Few-shot CoT (n=4) 83.1 / 94.2 / 96.1 | Derived: 8-shot anchor minus small exemplar-count penalty (−1.4/−0.9/−0.7) | derived |
| Direct answering 58.4 / 74.6 / 80.9 (GSM8K) | Derived from published no-CoT/direct estimates for Llama 3.1 (8B ≈ 55–60, 70B ≈ 70–77, 405B ≈ 79–83 in third-party evals) | derived (range-checked) |
| Zero-shot CoT 76.2 / 88.9 / 92.4 | Derived: direct + 12–18 pts, matching zero-shot-CoT gains | Kojima et al., NeurIPS 2022, arXiv:2205.11916 |
| Self-consistency deltas 1.5–5.2 | Derived: published SC gains 3.9–17.9 pts (GSM8K +17.9 at PaLM-540B), smaller for stronger models | Wang et al., ICLR 2023, arXiv:2203.11171 |
| ToT deltas (search +1.7, value +0.9) | Derived: search structure is the main driver (Game of 24: CoT 4% → ToT 74%) | Yao et al., NeurIPS 2023, arXiv:2305.10601 |
| ReAct deltas (+2.9 GSM8K, +2.2 CSQA) | Derived: acting + retrieval reduces hallucination; calculator removes arithmetic error | Yao et al., ICLR 2023, arXiv:2210.03629 |
| Temperature curve (SC peaks ~0.7; single-sample declines) | Qualitative pattern as reported; optimal T ≈ 0.3–0.7 for multi-sample inference | Du, Yang, Welleck, ICML 2025, arXiv:2502.05234 |
| CSQA 70B 72.4–83.5 | Derived within published instruction-tuned CSQA range: CoT GPT-3 75.2%, PaLM-540B 80.5%; zero-shot CoT InstructGPT 78.6% | Wei et al., NeurIPS 2022, arXiv:2201.11903; Kojima et al., 2022 |
| CNN/DM ROUGE-L 28.0–28.9 | Derived within published instruction-tuned ROUGE-L range (Llama-2-chat ≈ 27–29, GPT-3.5 ≈ 30); technique deltas ≤ 0.5 | derived (range-checked) |
| AER, D_Φ (0.06–1.2 nats/token), κ | Framework-defined quantities (Eq. AER, D_Φ, κ in §IV); illustrative values with no published anchor | derived |
| CIs (±2.1 … ±6.1) | Wald formula ±1.96·√(p(1−p)/n) at the reported accuracies (e.g., GSM8K 94.2%, n=500 → ±2.1; HumanEval 80.5%, n=164 → ±6.1) | mathematically derived |
| p-values, AER CI, REML interaction | Illustrative (paired bootstrap / Holm–Bonferroni / REML as specified in §V-D) | derived |

## Derivation of the ≈4.0M generation estimate

Per (model, task): 6 techniques × 4 paraphrases × 8 decoding cells =
192 cells; mean 1 generation/item, except self-consistency ×8,
tree-of-thoughts ≈9 expansions, ReAct ≈5 tool/trace steps:
≈ 192 + 32·7 + 32·8 + 32·4 = 800 item-equivalents.  Items per task:
500 (GSM8K, CSQA, CNN/DM), 164 (HumanEval) → 800 × 1,664 ≈ 1.33M per
model × 3 models ≈ **4.0M generations**.

## Replace before submission (checklist)

- [ ] Replace **all** numbers in Table I (`tab:results`), Table II
  (`tab:decomposition`), Fig. 1 (`fig:results`), §VI–IX, and the
  abstract with measured values from the actual run.
- [ ] Recompute AER, D_Φ, κ, CIs, p-values, token costs, generation
  count from the real logs.
- [ ] Confirm the claim "8B→70B direct +16.2 ≈ 70B few-shot CoT
  +19.6" still holds with real numbers (it is the paper's headline).
- [ ] Either delete this file before submission or keep it internal
  only — it must not ship with the paper.
