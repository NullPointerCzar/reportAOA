# Literature Matrix — Part 1

Required by `AGENTS.md` §2 (Part 1 deliverables).
Each row summarises one cited paper: how it relates to this paper and
which section of `main.tex` cites it. Citation keys are locked
(`AGENTS.md` §2 cross-part rule) — do not renumber.

| Key | Citation (short) | Technique family | Headline finding | Relation to this paper | Cited in |
| --- | --- | --- | --- | --- | --- |
| b1 | Brown et al., NeurIPS 2020 — *Language Models are Few-Shot Learners* | In-context learning / exemplars | Large LMs solve tasks from a few exemplars in the prompt without weight updates; introduces GPT-3. | Establishes prompting as a first-class interface to LLMs and motivates treating the prompt as a control input. | §I (intro), §II-A |
| b2 | Min et al., EMNLP 2022 — *Rethinking the Role of Demonstrations* | In-context learning / exemplars | Ground-truth labels in exemplars contribute less than the input–output format; prompts act as structural scaffolds. | Evidence that prompts reshape the model's own computation, not just its lexical surface. Justifies our algorithmic framing. | §I (intro), §II-A |
| b3 | Wei et al., NeurIPS 2022 — *Chain-of-Thought Prompting* | Reasoning-trace construction | Appending intermediate reasoning steps to exemplars yields large gains on arithmetic, commonsense, and symbolic tasks. | Canonical example of exposing intermediate computation to the sampling operator; primary motivation for our reasoning-trace axis. | §I (intro), §II-B |
| b4 | Wang et al., ICLR 2023 — *Self-Consistency* | Reasoning-trace construction | Sampling many reasoning chains and taking the majority answer beats greedy CoT, showing the posterior is multimodal. | Demonstrates that marginalising over reasoning traces reallocates probability mass — a directly measurable algorithmic effect. | §I (intro), §II-B |
| b5 | Yao et al., NeurIPS 2023 — *Tree of Thoughts* | Reasoning-trace construction | Generalises CoT to a search over reasoning trees with backtracking. | Extends the reasoning-trace family; provides the most aggressive case of algorithmic intervention via trace construction. | §I (intro), §II-B |
| b6 | Yao et al., ICLR 2023 — *ReAct* | Reasoning-trace + tool use | Interleaves reasoning steps with tool calls, letting the model act on external state. | Shows prompting techniques can reach outside the LM's own computation, broadening what "algorithmic effect" means. | §I (intro), §II-B |
| b7 | Lewis et al., NeurIPS 2020 — *Retrieval-Augmented Generation* | Retrieval / prompt context | Conditioning generation on retrieved documents improves knowledge-intensive tasks without retraining. | We treat RAG as a prompting technique that stochastically rewrites $P$ — bridges the gap between prompt engineering and external memory. | §I (intro), §II-C |
| b8 | Holtzman et al., ICLR 2020 — *The Curious Case of Neural Text Degeneration* | Decoding-time methods | Argues max-decoding produces degenerate text; introduces nucleus (top-$p$) sampling. | Foundational reference for our decoding axis $(T, k, p)$; lets us treat the decoder as a tunable algorithmic parameter. | §II-C |

## Counts

- **Total cited works in Part 1:** 8 (requirement: ≥ 4 — met with margin).
- **By axis:** prompting patterns = 2 (b1, b2), reasoning traces = 4
  (b3, b4, b5, b6), decoding/retrieval = 2 (b7, b8).
- **All entries are real, peer-reviewed papers** (NeurIPS / EMNLP /
  ICLR). No arXiv preprints or non-academic sources in Part 1.

## Open questions for the user

- Should Part 2 add newer (2024–2025) prompt-engineering papers (e.g.,
  instruction-tuning surveys, constitutional AI, automatic prompt
  optimisation)?  The current eight cover the canonical foundations;
  Part 2 may want to add a second tier.
- The first author of b1 is conventionally listed as Brown et al. with
  31 co-authors in GPT-3.  We abbreviate as "T. Brown et al." to fit
  IEEE width.  Confirm the abbreviated form is acceptable for the
  final camera-ready.
