# BRUTAL REVIEW — `main.tex`
**"Analysis of Prompt Engineering Techniques and Their Algorithmic Effect on Large Language Model Output"**

Reviewer: hostile, evidence-based. Every number below was recomputed from
`results/records.jsonl` (17,988 real generations) with a paired bootstrap
(10,000 resamples, seed 12345), or read directly from `results/results.json`.

---

## 0. VERDICT: **REJECT** (major revision)

The paper has one real finding, a defensible framing, honest limitations
text, and a reproducible harness — and then it systematically overstates
the strength of nearly everything else. Five of its headline claims do not
survive the paper's own error bars, the flagship "self-consistency gain"
is partially manufactured by an undisclosed, label-peeking tie-break in the
aggregation code, and the AER (the paper's central quantitative
contribution) is computed below its own sampling-noise floor with variance
components clipped to zero. Two statements in the paper are factually
false. This is not resubmittable as-is.

---

## 1. What actually works (so you know this isn't a hatchet job)

- The data are real. 17,988 records with genuine, model-specific responses
  (spot-checked: Qwen emits fenced python, Llama 3.2 1B rambles, etc.).
- `tab:results`, `tab:tempsweep`, `tab:cost`, `tab:aer` are internally
  consistent with `results/results.json`, which I re-derived from the raw
  records.
- All three recent, easy-to-hallucinate citations verify as real:
  b24 (Liu et al., *Front. Comput. Sci.* 2026, doi 10.1007/s11704-025-50058-z),
  b25 (Mei et al., arXiv:2507.13334), b26 (Du/Yang/Welleck, ICML 2025).
- The core magnitude claim — zero-shot CoT at 1B raises GSM8K 12→50%
  (+38 pts, CI [27, 49]) vs. scaling 1B→3B direct 12→53% (+41, CI [29, 53])
  — **is significant and survives**. It's the one headline the paper earned.
- `§VIII Limitations` is unusually candid. Pity the rest of the paper
  doesn't live up to it.
- Compiles clean, 9 pages, IEEE style mostly compliant.

---

## 2. STATISTICAL SINS — the rejection reasons

### 2.1 [BLOCKER] The self-consistency "gains" are inflated by a label-peeking tie-break

`run_experiments.py` `aggregate()` resolves plurality votes with:

```python
winner = max(buckets.items(), key=lambda kv: (len(kv[1]), any(kv[1])))
```

A bucket is a normalised extracted answer; `any(kv[1])` is true only if that
answer matches the gold. **When two answers tie for plurality (2-2 with
m=4), this rule selects the answer that is correct.** That is not a tie-break;
that is reading the label. The paper states self-consistency aggregates
"by plurality vote" (§V-B) and "taking the most frequent answer" (§II) —
neither description discloses this rule.

Measured impact on the headline numbers (paraphrase 1, GSM8K):

| Model | Reported SC | Plurality ties | Resolved *correct* by tie-break | SC if ties count as unresolved |
|---|---|---|---|---|
| 3B | 88% | 14/100 | 11 | **77%** |
| Qwen | 81% | 14/100 | 11 | **70%** |
| 1B | 11% | 31/100 | 8 | **3%** |

Consequences for the paper's claims:

- "Self-consistency adds a further gain over few-shot CoT at the coder
  (71% to 81%)" — with a fair tie-break, Qwen SC ≈ 70% vs. fs-CoT@0.7 =
  69%: **the claimed +12-pt coder gain evaporates to +1.**
- At 3B, SC 88 vs. fs-CoT@0.7 72 → +16 with the biased rule, +5 with ties
  unresolved: barely distinguishable from noise either way at n=100.
- The 1B SC number (11%) is below the fs-CoT@0.7 value (6%) once ties are
  handled fairly — the paper's "SC above fs-CoT at every scale" (§VI-B,
  "the empirical content of H2") is an artifact of the tie-break at two
  of three scales.

Fix: resolve ties by a random or fixed-arbitrary rule (and report the
number of tied items); report SC with and without the rule; disclose it.
Then re-run every SC claim.

### 2.2 [BLOCKER] The temperature narrative is all noise — every comparison is non-significant

The abstract claims: "single-sample accuracy declines with temperature at
the smaller scales and is roughly flat at the 3B scale." §VI-B repeats it
with a "mild peak at T = 0.3." Paired-bootstrap differences (par 1):

| Comparison | Claimed | Δ (pts) | 95% CI | Significant? |
|---|---|---|---|---|
| 1B fs-CoT, T=1.0 vs 0 | "declines 8→6" | −2 | [−8, +4] | **no** |
| Qwen fs-CoT, T=1.0 vs 0 | "declines 71→62" | −9 | [−19, +1] | **no** |
| 3B fs-CoT, T=1.0 vs 0 | "roughly flat 70→66" | −4 | [−13, +5] | **no** |
| 3B fs-CoT, T=0.3 vs 0 | "mild peak" | +4 | [−3, +11] | **no** |
| 1B fs-CoT, T=0.3 vs 0 | (dip to 4) | −4 | [−10, +1] | **no** |

Every single temperature effect the paper reports is inside the ±10-pt band
the paper itself declares as its detection threshold. The "interaction
between temperature and sampling strategy" (§VI-B) is a figure with no
significant structure in it. The 3B "mild peak" is four data points moving
by 4 pts. Either report the CIs on these differences or delete the
temperature story from the abstract.

### 2.3 [MAJOR] "Few-shot CoT hurts the 1B model (12% to 8%)" — not significant

§VI-A asserts fs-CoT "hurts the 1B model." Difference: −4 pts, CI
[−12, +4]. **Not significant.** The abstract doesn't say this (good), but
the body presents a null result as a finding. At n=100, a 4-pt drop is
indistinguishable from chance — which is precisely why the paper's own
table note says only differences "exceeding the interval width" count as
evidence. This difference doesn't, yet it's narrated as a result.

### 2.4 [MAJOR] The Qwen "unusually low" direct-answering baseline is also within noise

§VI-A: "The coder model's direct-answering accuracy on GSM8K is unusually
low (6%)." Qwen direct = 6/100 vs. 1B direct = 12/100 on the same items:
the difference (−6) is not significant at n=100, and across paraphrases
Qwen direct is 6/3/4/11. The entire "algorithmic gain" narrative for Qwen
(+73 pts zs-CoT!) is a ratio whose denominator is statistically
indistinguishable from the 1B baseline it's contrasted against. The
"specialised prior does not by itself make arithmetic tractable" reading
is speculation, not a measured effect.

### 2.5 [BLOCKER] The AER is computed below its own noise floor, with σ² clipped to zero

The AER (§IV-E, §VI-D) is a ratio of variance components estimated by
method-of-moments from the technique × paraphrase cell means — 12 cells
(3×4) on GSM8K, 6 cells (3×2) on HumanEval — with **no accounting for
item-level sampling error**. A single GSM8K cell at n=100, p≈0.5 has
binomial sampling variance p(1−p)/n ≈ **0.0025**. Now look at what the
paper reports as "variance components":

| Cell | σ²_alg | σ²_lex | Sampling-noise floor (≈0.0025) |
|---|---|---|---|
| 1B GSM8K | 0.0281 | 0.0003 | σ²_lex is **8× below the floor** |
| 1B HumanEval | 0.0019 | 0.000043 | both components below the floor |
| 3B GSM8K | 0.0060 | 0.0013 | σ²_lex ~ half the floor |
| Qwen GSM8K | 0.1583 | **0.0000 (clipped)** | σ²_lex = 0 by `max(...,0)` |

The "algorithmic effect ratio is near one (0.82–1.00) on GSM8K" — the
abstract's second quantitative claim — is computed from variance estimates
smaller than, or comparable to, the noise in the cell means feeding them.
The Qwen AER of 1.00 with σ²_lex = 0.0000 is a **clipping artifact**
(`max(σ², 0)`), not a measurement. There is no uncertainty on any AER
value, and on HumanEval (2 paraphrases) the ratio is a single degree of
freedom. This metric as reported is not meaningful, and the Discussion's
"the technique gains largely survive rewording" does not follow from it.

Fix: bootstrap the AER over items (you already have the paired-bootstrap
infrastructure), report CIs, and never present a clipped 0.0000 as a
measured zero.

### 2.6 [MAJOR] The methods promise statistics the results never deliver

§V-D: "pairwise comparisons across the algorithmic factor use
Holm–Bonferroni correction." Search the results section: there is **not one
p-value, one corrected comparison, or one interaction test anywhere**.
H2 ("the interaction between the trace and decoding components ... is
significant") is declared *supported* in §VI-B purely by eyeballing that
"SC lies above fs-CoT" — which is (a) not an interaction test and (b) an
artifact per 2.1 at two of three scales. Either run the promised tests and
report them, or remove the promise and downgrade H2 to "exploratory."

### 2.7 [MODERATE] The table note's ±10 pts is optimistic for differences

The note on `tab:results` says paired-bootstrap CIs are "±10 points
(GSM8K, n = 100)." For the *differences* the paper actually compares,
paired CIs are ±11–14 (e.g., zs-CoT 1B: [27, 49] = ±11; fs-CoT 3B:
[5, 29] = ±12). The stated detection threshold understates the true
uncertainty of every claim in §VI-A.

---

## 3. DESIGN AND REPORTING GAPS

### 3.1 [MODERATE] "Varying decoding parameters (T, k, p)" — only T was varied
The intro's contribution bullet and §V-B claim the design varies
`(T, k, p)`. In the data, **top-k = 40 and top-p = 0.9 are fixed
constants**; only temperature varies. `k` and `p` are never varied, never
ablated, and never appear in any table or figure. Cut the claim or run the
ablation.

### 3.2 [MAJOR] HumanEval self-consistency uses a *different* aggregation rule — undisclosed
The code aggregates HumanEval SC by **majority-pass** (≥3 of 4 samples must
pass), because programs can't be plurality-voted — a stricter rule than the
GSM8K plurality. The paper nowhere discloses this. The result: "SC is the
weakest configuration at every scale on HumanEval" (§VI-A) is at least
partly a consequence of applying a stricter rule to SC than to the
single-sample baselines it's compared against. That comparison is
apples-to-oranges and must be disclosed or re-run with a matched rule.

### 3.3 [MAJOR] Headline numbers are single-paraphrase, and paraphrase sensitivity is huge
Every headline number in `tab:results` and the abstract is paraphrase 1
only — yet the paper's own AER analysis shows lexical variance is
non-negligible. Examples of what paraphrase 1 hides (from the records):

- 1B SC GSM8K: par1 = 11%, **par3 = 42%**.
- Qwen direct GSM8K: 6 / 3 / 4 / 11%.
- 3B zs-CoT: par1 75% (not reported in Table 1, but varies similarly).

Any single-paraphrase number in the abstract should be reported with its
paraphrase range, or the abstract should state results are for paraphrase 1
(a deliberately arbitrary choice) with the AER/paraphrase variance
summarised in the body. As written, readers are given one coin flip.

### 3.4 [MODERATE] No error bars anywhere
`fig-results` (both panels) shows lines and bars with no error bars,
despite ±10–14-pt CIs being the paper's own declared uncertainty. The
3B temperature curve (70/74/72/66) renders as a peak when it is flat
within noise. IEEE figures in papers whose entire argument is about
effect sizes require error bars or shaded CIs.

### 3.5 [MODERATE] Parse rates are promised and never reported
The abstract and §V-D promise "parse rates" as part of the protocol. No
table or sentence in the Results reports a single parse-rate value —
because (from `results.json`) **parse rate is 1.0 in every cell**. That
means the Discussion's "parse failures ... are a second source of
systematic loss" is speculation about a phenomenon the data shows never
occurred. Report the (trivially high) parse rates, or stop claiming they're
part of the protocol's output.

### 3.6 [MINOR] "A controlled factorial study"
The design is not a factorial: HumanEval has no temperature factor, SC has
no paraphrase × temperature crossing, and only one lexical level carries
the headline numbers. "Factorial" overstates the design actually executed.
"Partially crossed design" is accurate.

---

## 4. REPRODUCIBILITY & INTEGRITY

### 4.1 [BLOCKER] "random seeds for every model call are recorded in the output logs" — false
§V-E states this verbatim. `records.jsonl` contains **no seed field**
(grep: 0 hits), and `generate()` never passes a seed to the Ollama
`/api/generate` call — the request payload has only `temperature`, `top_p`,
`top_k`, `num_predict`. The runs are therefore **not reproducible
bit-for-bit**, the claimed seed logging does not exist, and the
reproducibility paragraph is inaccurate. Either log a seed (Ollama supports
one) or delete the sentence and state results are single-run estimates.

### 4.2 [MODERATE] Quantisation is uncontrolled
Models are "GGUF quantisations (Q4_K_M or Q8_0 precision)" (§V-C) — i.e.,
different precision levels across the three models, with no sensitivity
analysis. Quantisation shifts the sampled distribution non-trivially and
can interact with the very temperature effects the paper claims. At
minimum, state the exact quantisation per model (it's not in the paper;
only the class is).

### 4.3 [MODERATE] The "18,000 generations" framing hides the real N
There are 17,988 records, but the *effective* N for nearly every claim is
**100 items per cell** (or 164 on HumanEval). "Roughly 18,000 generations"
sounds like a large study; every statistical claim in the paper has the
power of n=100. The paper should lead with the item count, which is what
determines the CIs it then quotes.

### 4.4 [MINOR] The Acknowledgment thanks "the maintainers of the evaluation harness"
This is the authors' own harness (`run_experiments.py`). Thanking yourself
is odd; thanking whoever actually ran the experiments (the friend whose
machine this ran on) would be more honest — the paper currently gives no
credit to the data's actual provenance machine.

### 4.5 [MINOR] Placeholder remains in the author block
`<<EMAIL_BRISHAV>>` is still in the manuscript. Submission-blocking.

---

## 5. FRAMING OVERREACH

- **"Often rivals, and sometimes exceeds, the difference between adjacent
  model scales"** (Introduction): supported in exactly one cell (Qwen
  zs-CoT +73 vs. +41) whose baseline is itself statistically
  indistinguishable from the 1B baseline (2.4), and one "rivals" cell (1B
  zs-CoT +38 vs. +41). Three models, two tasks, four techniques — and the
  generalisation rests on two cells. Qualify it.
- **Abstract**: "single-sample accuracy declines with temperature at the
  smaller scales and is roughly flat at the 3B scale" — see 2.2, not
  supported. "the technique gains largely survive rewording" — see 2.5,
  not supported by the reported AER.
- **"An AER near 1 means the benefit survives rewording"** (§IV-E) — with
  the estimator as implemented (clipped, noise-blind), AER ≈ 1 is
  *guaranteed* whenever technique variance dominates a clipped lexical
  term. The paper is explaining a property of the estimator as if it were a
  property of the prompts.

---

## 6. THE ONE REAL RESULT (keep this)

Zero-shot CoT at the 1B scale raises GSM8K exact-match accuracy from 12%
to 50% (CI [27, 49]), statistically indistinguishable from the 41-pt gain
of scaling 1B→3B direct (CI [29, 53]) — i.e., at this size class, a prompt
can buy roughly what a 3× model buys, on reasoning tasks. That is a
publishable observation, but it needs to be the *whole* paper's spine,
with the temperature and AER material demoted or fixed, and every other
claim brought inside the CIs the paper itself prints.

---

## 7. REQUIRED CHANGES BEFORE ANY RESUBMISSION

1. [BLOCKER] Fix the SC tie-break (2.1); disclose the rule; re-report SC.
2. [BLOCKER] Put CIs on every temperature difference, or remove the
   temperature claims from the abstract (2.2).
3. [BLOCKER] Bootstrap the AER over items; report CIs; stop presenting
   clipped zeros (2.5).
4. [BLOCKER] Correct or delete the "seeds are recorded" sentence (4.1).
5. [MAJOR] Report the promised Holm–Bonferroni results or delete the
   promise; downgrade H2 to exploratory (2.6).
6. [MAJOR] Disclose the HumanEval majority-pass rule and match rules
   across techniques (3.2).
7. [MAJOR] Report paraphrase ranges for all headline numbers (3.3).
8. [MAJOR] Add error bars to both figure panels (3.4).
9. [MODERATE] Cut "varying (T, k, p)" to "varying T" (3.1); report parse
   rates or stop promising them (3.5); fix quantisation reporting (4.2);
   lead with n=100 not 18,000 generations (4.3).
10. [MINOR] Remove the placeholder email, fix the Acknowledgment, qualify
    the "rivals/exceeds model scale" claim.

---

## 8. One-line summary for the authors

You have one real, well-measured finding (prompt ≈ 3× scale at 1B, on
reasoning), a genuinely reproducible harness, and an honest limitations
section — and you buried it under five unsupported headline claims, a
label-peeking vote rule, a noise-floor AER, and two false statements about
your own logs. Strip the paper to what the CIs actually support, fix the
aggregation, bootstrap the AER, and this becomes a legitimate small-scale
empirical note. As submitted: **REJECT**.
