# Results Summary — Part 3

> ✅ **Status: MEASURED DATA.** All headline numbers below come from the
> completed local benchmark run (17,988 generations; three models × two
> tasks × the focused grid of `run_experiments.py`).  They are lifted
> directly from `results/results.json` (see `update_tables.py` and
> `parts/part-3-results-abstract/verify_numbers.py`).

## Headline numbers (measured)

| Quantity | Value |
| --- | --- |
| Total generations | 17,988 (GSM8K 11,100 + HumanEval 6,888) |
| Zero-shot CoT vs. direct, GSM8K (paraphrase 1, greedy) | 1B: 12.0→50.0 (+38.0); 3B: 53.0→75.0 (+22.0); Coder-3B: 6.0→79.0 (+73.0) |
| Few-shot CoT vs. direct, GSM8K | 1B: 12.0→8.0 (−4.0); 3B: 53.0→70.0 (+17.0); Coder-3B: 6.0→71.0 (+65.0) |
| Technique gain ≈ scale gain | 1B zs-CoT +38.0 vs. 1B→3B direct +41.0 (12.0→53.0) — nearly identical |
| Self-consistency (m=4, T=0.7), GSM8K | 1B: 11.0; 3B: 88.0 (+18.0 over fs-CoT 70.0); Coder-3B: 81.0 (+10.0 over fs-CoT 71.0); reported at defined T=0.7 |
| HumanEval, all techniques | Compressed: max gain +2.4 (Coder-3B fs-CoT 82.9 vs 80.5 direct); zs-CoT neutral/negative; SC weakest at every scale |
| Temperature × technique (GSM8K, fs-CoT single-sample) | 1B: 8.0→4.0→6.0→6.0; 3B: 70.0→74.0→72.0→66.0 (peak T=0.3); Coder: 71.0→67.0→69.0→62.0 (T=0, 0.3, 0.7, 1.0) |
| AER (technique × paraphrase, reference cell) | 1B: GSM8K 0.99 / HE 0.98; 3B: 0.82 / 0.50 (degenerate: both σ² = 0); Coder-3B: 1.00 / 0.25 |
| 95% CIs (paired bootstrap / Wald) | GSM8K ±10 pts (n=100, p≈0.5); HumanEval ±8 pts (n=164, p≈0.5) |
| Token cost (mean tokens/item, GSM8K, par 1) | direct 33–79; zs-CoT 178–244; fs-CoT 126–173; SC ×4: 503–730 |

## Headline claims in the paper (and the numbers that support them)

- **Algorithmic effect ≈ model scale.** On GSM8K, zero-shot CoT lifts
  the 1B model 12.0→50.0, while scaling 1B→3B under direct answering
  lifts 12.0→53.0 (+38 vs +41 points).  Few-shot CoT and
  self-consistency add further substantial gains at the 3B and coder
  scales.
- **AER near one on GSM8K** (0.82–1.00): the technique gains survive
  rewording of the prompt.  On HumanEval the ratio is mixed
  (0.25–0.98) and degenerate for the 3B model where technique effects
  vanish.
- **Temperature interacts with sampling.**  Single-sample few-shot
  CoT declines with temperature at the 1B and coder scales and is
  roughly flat (mild peak at T=0.3) at the 3B scale; self-consistency
  requires T > 0 and is evaluated at its defined setting T = 0.7.
- **Task dependence.**  Trace- and ensemble-based techniques help on
  GSM8K and are roughly neutral or negative on HumanEval, where
  self-consistency is the weakest configuration at every scale.

## Replace before submission (checklist)

- [x] Tables `tab:results`, `tab:tempsweep`, `tab:cost`, `tab:aer`
      filled from measured data (`update_tables.py`, re-run via
      `python3 update_tables.py`).
- [x] Fig. `fig:results` regenerated from measured data
      (`parts/part-3-results-abstract/make_fig_results.py`).
- [x] Abstract and §VI–IX prose checked against the measured numbers
      (script: `parts/part-3-results-abstract/verify_numbers.py`).
- [ ] Replace `<<EMAIL_BRISHAV>>` in the author block (open question
      for the user).
- [ ] Keep this file internal only — it must not ship with the paper.

## Provenance

Every cell in `tab:results`, `tab:tempsweep`, and `tab:cost` is
computed from `results/results.json` by `update_tables.py`; the AER
and its variance components are computed by `run_experiments.py
--aggregate` from the per-item records in `results/records.jsonl`.
The verification script `verify_numbers.py` cross-checks every table
cell and headline claim against `results/results.json` and the record
count.
