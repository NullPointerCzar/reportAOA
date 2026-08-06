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
| b23 | Sahoo et al., arXiv 2024 (v2 2025) — *A Systematic Survey of Prompt Engineering in LLMs* | Survey / taxonomy by application | Catalogues techniques by application area with methodology, models, datasets; names open challenges. | Closest prior survey; organises by application, not by the algorithmic object modified — the foil for our operator-based taxonomy. | §II-E (synthesis) |
| b24 | Liu et al., Front. Comput. Sci. 2026 — *A Comprehensive Taxonomy of Prompt Engineering Techniques* | Survey / taxonomy by function | Taxonomy across profile/instruction, knowledge, reasoning/planning, reliability dimensions. | Its functional dimensions become derived categories under our $\Phi/\Psi/\Omega$ operator taxonomy. | §II-E (synthesis) |
| b25 | Mei et al., arXiv 2025 — *A Survey of Context Engineering for LLMs* | Survey / context engineering | Formalises context engineering; identifies an asymmetry between consuming and generating long context; calls for principled measurement. | Justifies our demand for distribution-level measures ($D_{\Phi}$, $\kappa$) in the evaluation protocol. | §II-E (synthesis) |
| b26 | Du, Yang, Welleck, ICML 2025 — *Optimizing Temperature for Multi-Sample Inference* | Decoding / temperature selection | Temperature is usually left at a fixed default or tuned on scarce labels; optimal value varies with model, task, and sampling strategy. | Empirical support for our decoding axis and for H2 (trace--decoding interaction). | §II-E (synthesis) |

## Counts

- **Total cited works:** 12 (8 foundational + 4 recent, added in the
  lit-review synthesis revision; requirement: ≥ 4 — met with margin).
- **By axis:** prompting patterns = 2 (b1, b2), reasoning traces = 4
  (b3, b4, b5, b6), decoding/retrieval = 2 (b7, b8), recent
  surveys/synthesis = 4 (b23, b24, b25, b26).
- **Foundational entries are real, peer-reviewed papers** (NeurIPS /
  EMNLP / ICLR / ACL / ICML).  The synthesis tier adds two arXiv
  preprints (b23, b25) and one journal taxonomy (b24) — flagged as
  preprints in the bibliography per IEEE arXiv convention.

## Open questions for the user

- ~~Should Part 2 add newer (2024–2025) prompt-engineering papers?~~
  **Resolved:** four recent works (b23–b26) added to close the
  lit-review synthesis; keys appended after b22, none renumbered.
- The first author of b1 is conventionally listed as Brown et al. with
  31 co-authors in GPT-3.  We abbreviate as "T. Brown et al." to fit
  IEEE width.  Confirm the abbreviated form is acceptable for the
  final camera-ready.
