# AGENTS.md

## Purpose
This file instructs AI coding/writing agents how to author, edit, and format the IEEE conference-style research paper for the project:

> **"Analysis of Prompt Engineering Techniques and Their Algorithmic Effect on LLM Output"**

The authoritative formatting reference is `format.md` (extracted from `IEEE-conference-template-062824/IEEE-conference-template-062824.tex`). All agents must treat the rules in `format.md` and the LaTeX template as binding. Do **not** invent a new style — mirror the template exactly.

The compilation entry point is `IEEE-conference-template-062824/IEEE-conference-template-062824.tex` using the provided `IEEEtran.cls`. Agents must keep changes inside that template's structure unless the user explicitly asks for a separate manuscript file.

---

## 1. Repository Map

| Path | Role |
| --- | --- |
| `format.md` | Authoritative prose formatting rules (titles, abstract, sections, units, equations, citations, references, common mistakes). Read first. |
| `IEEE-conference-template-062824/IEEE-conference-template-062824.tex` | LaTeX source to be edited as the manuscript. |
| `IEEE-conference-template-062824/IEEEtran.cls` | Class file. Do not modify. |
| `IEEE-conference-template-062824/fig1.png` | Example figure asset. Replace with paper-specific figures. |
| `IEEE-conference-template-062824/IEEE-conference-template-062824.pdf` | Compiled reference for visual verification. |
| `README.md` | Project placeholder. |
| `AGENTS.md` | This file. |
| `parts/` | Suggested working directory for the three-part split (see §2). One sub-folder per deliverable: `part-1-intro-lit/`, `part-2-methodology/`, `part-3-results-abstract/`. Each holds the LaTeX snippets, draft prose, citation keys, and figures that belong to that deliverable. The final paper is assembled into `IEEE-conference-template-062824/IEEE-conference-template-062824.tex` only after all three parts are reviewed. |

---

## 2. Project Deliverables (three-part split)

The paper is delivered in three parts. **An agent must only touch the sections assigned to the part it is currently working on.** Every part must satisfy the formatting rules in `format.md` and be written into the LaTeX template's structure (see §4–§11). Each part also produces a short handoff note (template in §16).

### Part 1 — Introduction & Literature Review
- **LaTeX sections to populate:** `I. Introduction`, `II. Background and Related Work`.
- **Required content:**
  - Motivation and problem statement (algorithmic effect, not just usage tips).
  - Explicit contributions, bulleted.
  - Paper organization paragraph.
  - **Minimum 4 cited papers** in the literature review. Cite seminal prompt-engineering works (e.g., CoT, self-consistency, ToT, ReAct, instruction tuning) plus algorithmic analyses of LLM decoding.
  - A short "how this paper differs" sentence for each cited work.
- **Deliverable artefacts:**
  - Drafted `\section{Introduction}` and `\section{Background and Related Work}` blocks.
  - Bib entries for every cited paper, added to `\begin{thebibliography}` (or `.bib` file).
  - A `literature_matrix.md` table in `parts/part-1-intro-lit/` summarizing each cited paper (citation, technique, finding, how it relates to this paper).
- **Done when:** the introduction has a clear thesis, the literature review cites ≥ 4 papers, every citation resolves to a real reference, and the section compiles cleanly inside the IEEE template.

### Part 2 — Methodology
- **LaTeX sections to populate:** `III. Taxonomy of Prompt Engineering Techniques`, `IV. Algorithmic Framework`, and any methodology sub-blocks inside `V. Experimental Setup` (Research Design, Data Collection, Data Processing and Analysis Tools).
- **Required content:**
  - **Theoretical Framework and Justification** — formalize prompt engineering as transformations on the conditional distribution $p_\theta(y \mid P, x)$: prompt templates $P$, decoding parameters $(T, k, p)$, reasoning chains, and tool use. Justify why these are *algorithmic*, not merely lexical, changes.
  - **Research Design** — comparative empirical study: which techniques, which models, which tasks, controlled variables (prompt template, decoding, model weights).
  - **Data Collection Procedure** (if any) — source datasets (e.g., MMLU, GSM8K, HumanEval, BIG-bench, custom prompts), license, size, sampling.
  - **Data Processing and Analysis Tools** (if any) — evaluation harness, statistical tests, hardware/runtime, libraries.
- **Deliverable artefacts:**
  - Drafted taxonomy section with a clear notation table (cf. §10).
  - At least one algorithm pseudocode block (cf. §9) and one equation block.
  - `parts/part-2-methodology/methodology.md` capturing the full prose before LaTeX-ization.
- **Done when:** a reader can replicate the experiment from this section alone — every model, dataset, prompt, metric, and tool is named with version + source.

### Part 3 — Results & Discussion + Abstract
- **LaTeX sections to populate:** `VI. Results and Analysis`, `VII. Discussion`, `VIII. Limitations and Threats to Validity`, `IX. Conclusion`, and the final `\begin{abstract}` / `\begin{IEEEkeywords}` blocks.
- **Required content:**
  - Quantitative results with at least one results table and one figure (per technique × model × task).
  - Ablations isolating the algorithmic effect (e.g., same prompt, different $T$ / $k$ / $p$).
  - Statistical significance or confidence intervals where applicable.
  - Discussion of cost vs. quality trade-offs, failure modes, robustness, bias.
  - Limitations section (mandatory, not a footnote).
  - **Abstract** — write *last*, after results are known. State problem, method, key numerical result, and implication in 150–250 words, no math/symbols.
  - Updated `\begin{IEEEkeywords}` (4–6 terms).
- **Deliverable artefacts:**
  - All figures/tables referenced in earlier parts, with `\label`s and captions following §7/§8.
  - A `parts/part-3-results-abstract/results_summary.md` with the headline numbers to lift into the abstract.
  - A final, fully-assembled `IEEE-conference-template-062824.tex` with template text stripped.
- **Done when:** the full paper compiles, fits the conference page limit, passes the §14 checklist, and the abstract is consistent with the actual reported numbers.

### Cross-part rules
- **Citation keys** (`b1`, `b2`, …) added in Part 1 must not be renumbered in Parts 2/3; renumbering breaks cross-references.
- **Labels** (`\label{...}`) created in Part 1 (e.g., `fig:taxonomy`) may be referenced in Parts 2/3. If a label is added or renamed, mention it in the handoff note.
- **Acronyms** defined in Part 1 (LLM, CoT, RAG, ToT, ReAct, MMLU, etc.) carry forward unchanged.
- **The Abstract is the last thing written** — never draft it in Part 1 or Part 2.

---

## 3. Paper Scope (single source of truth)

**Topic:** *Analysis of prompt engineering techniques and their algorithmic effect on LLM output.*

Agents must keep every contribution aligned with this scope. Acceptable directions include (non-exhaustive):

- Surveys / taxonomies of prompt engineering techniques (zero-shot, few-shot, chain-of-thought, self-consistency, tree-of-thoughts, ReAct, instruction-tuning prompts, role prompts, retrieval-augmented prompts, etc.).
- Empirical comparisons of techniques on standard benchmarks (MMLU, GSM8K, HumanEval, BIG-bench, etc.) and on custom task suites.
- Algorithmic analyses: how a technique changes decoding behavior, attention distribution, logit shaping, sampling variance, calibration, or output determinism.
- Quantitative effects on quality, cost, latency, robustness, bias, and safety.
- Reproducibility artefacts: prompts, evaluation harnesses, datasets.

Out of scope (reject or redirect): generic LLM explainers, non-prompt fine-tuning, hardware/accelerator design, product reviews.

---

## 4. Mandatory LaTeX Skeleton

Always preserve the skeleton in `IEEE-conference-template-062824.tex`. Only edit the *content* slots below.

```latex
\documentclass[conference]{IEEEtran}
\IEEEoverridecommandlockouts
%Template version as of 6/27/2024

\usepackage{cite}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{algorithmic}
\usepackage{graphicx}
\usepackage{textcomp}
\usepackage{xcolor}
\def\BibTeX{{\rm B\kern-.05em{\sc i\kern-.025em b}\kern-.08em
    T\kern-.1667em\lower.7ex\hbox{E}\kern-.125emX}}
```

**Do not** add unneeded packages. If a new package is required, justify it in the commit message and keep it minimal (e.g., `booktabs` for tables, `hyperref` only if explicitly asked).

---

## 5. Required Front-Matter

### 4.1 Title
- One line, no sub-title.
- CRITICAL: no symbols, special characters, footnotes, or math.
- Title-cased, specific, and informative. Bad: "Prompt Engineering for LLMs." Good: "Algorithmic Effects of Prompt Engineering Techniques on Large Language Model Output."
- Delete the `thanks{}` funding footnote or fill it only with a real funder.

### 4.2 Authors
- Keep the existing `\IEEEauthorblockN` / `\IEEEauthorblockA` layout.
- List names left-to-right, then next line (the order is permanent for citations/indexing).
- Affiliations must be succinct: department, organization, city, country, email/ORCID.
- Do **not** group authors by affiliation. Do **not** list in columns.
- Trim unused `\and` blocks if there are fewer than six authors.

### 4.3 Abstract
- Single paragraph inside `\begin{abstract} ... \end{abstract}`.
- No symbols, special characters, footnotes, or math.
- State: (a) the problem, (b) what was investigated, (c) methodology, (d) key quantitative result, (e) implication.
- Typical length: 150–250 words for an IEEE conference paper.

### 4.4 Index Terms (Keywords)
- 4–6 keywords, comma-separated, lowercase, inside `\begin{IEEEkeywords} ... \end{IEEEkeywords}`.
- Examples: `prompt engineering, large language models, chain-of-thought, decoding strategies, evaluation, algorithmic analysis`.

---

## 6. Section Structure (Roman-numeral style)

The template uses `IEEEtran` with `\section{}` / `\subsection{}` — never manually number headings. Use this canonical outline; rename only when scope demands it.

1. **Introduction** — motivate, position vs. prior surveys, contributions bulleted, paper organization.
2. **Background and Related Work** — LLMs, decoding, prior prompt-engineering surveys.
3. **Taxonomy of Prompt Engineering Techniques** — formal definitions and notation.
4. **Algorithmic Framework** — how prompts enter the model, effect on logits/attention/sampling.
5. **Experimental Setup** — models, tasks, metrics, prompts, compute.
6. **Results and Analysis** — tables/figures, statistical significance, ablations.
7. **Discussion** — cost vs. quality trade-offs, failure modes, robustness, bias.
8. **Limitations and Threats to Validity**
9. **Conclusion**
10. **Acknowledgment** (`\section*{Acknowledgment}`)
11. **References** (`\section*{References}` + `\begin{thebibliography}{00}`)

Subsections should be used only when at least two exist. Per `format.md` §II.G: "if there are not at least two sub-topics, then no subheads should be introduced."

---

## 7. Writing Rules (extracted from `format.md`)

These are **non-negotiable** for any agent-generated prose:

- **No abbreviations in the title or heads** unless unavoidable. Define every acronym on first use, even if it appears in the abstract (e.g., LLM, CoT, RAG, ToT, ReAct, MMLU).
- **Units**: SI (MKS) preferred; English units only in parentheses. Never combine SI and CGS. Write units out in prose: "a few henries", not "a few H". Always prepend `0` before decimals: `0.25`, not `.25`. Use `cm³`, not `cc`.
- **Equations**: number consecutively. Use `align` or `IEEEeqnarray`, **never** `eqnarray`. Do not put `\nonumber` inside `array`. Use long dash `---` for minus signs. Italicize Roman symbols for quantities; do not italicize Greek symbols. Define every symbol at first appearance. Cite as `\eqref{eq}`; write "Equation (1) is …" only at sentence start.
- **Cross references**: always soft (`\ref{}`, `\eqref{}`, `\cite{}`); never hard-coded numbers. Place `\label` *after* the caption command it refers to.
- **Common-mistakes list (from `format.md` §II.E)** that the agent must avoid:
  - "data" is plural.
  - $\mu_0$ uses subscript zero, not letter "o".
  - American punctuation inside quotes only for full thoughts/names; parenthetical at sentence end: punctuation outside.
  - "inset", not "insert". "alternatively", not "alternately" (unless truly alternating).
  - "essentially" is not a synonym for "approximately" or "effectively".
  - Title: capitalize "Using" only if "that uses" can replace it.
  - "non" is a prefix, not a word.
  - "et al." has no period after "et".
  - "i.e." = "that is"; "e.g." = "for example".
  - Watch homophones: affect/effect, complement/compliment, discreet/discrete, principal/principle, imply/infer.
- **Figures and tables**:
  - Place at top/bottom of columns; never in the middle. Large ones may span both columns.
  - Figure captions **below**; table heads **above**.
  - Insert **after** they are cited in the text.
  - Use "Fig. 1" abbreviation, even at sentence start.
  - Axis labels: 8 pt Times New Roman, words not symbols (write "Magnetization (A/m)" not "A/m"), units in parentheses.
  - Table footnotes use letters, not numbers.
- **Citations**: numbered, square brackets, punctuation follows the bracket (`... output [3].`). "Reference [3] was the first …" only at sentence start. No "Ref. [3]". List all authors unless ≥6, then use "et al.". Unpublished → `[4]` style; in-press → `[5]`; arXiv → `[8]` with `arXiv:xxxx.xxxxx`; software → `[9]` GitHub link; dataset → `[10]` DOI; Code Ocean → `[11]`.

---

## 8. Tables and Figures (LaTeX-specific)

### 7.1 Table pattern
```latex
\begin{table}[htbp]
\caption{Table Type Styles}
\begin{center}
\begin{tabular}{|c|c|c|c|}
\hline
\textbf{Head} & \textbf{Col A} & \textbf{Col B} & \textbf{Col C} \\
\hline
row & a & b & c \\
\hline
\multicolumn{4}{l}{$^{\mathrm{a}}$Footnote text.}
\end{tabular}
\label{tab1}
\end{center}
\end{table}
```
- Always `\label` *after* `\caption`.
- Footnotes with superscript letters (`$^{\mathrm{a}}$`).

### 7.2 Figure pattern
```latex
\begin{figure}[htbp]
\centerline{\includegraphics[width=\columnwidth]{fig1.png}}
\caption{Caption text.}
\label{fig}
\end{figure}
```
- Prefer `\columnwidth` for single-column and `\textwidth` for double-column.
- Use vector PDF/SVG when possible; raster figures ≥ 300 dpi.

---

## 9. Algorithms (pseudocode)

Use the `algorithmic` package (already loaded). Style:

```latex
\begin{algorithm}[htbp]
\caption{Algorithmic Effect of Chain-of-Thought Prompting on Decoding}
\label{alg:cot}
\begin{algorithmic}
\STATE Observe input $x$ and CoT prompt $P$.
\STATE Sample reasoning chain $r \sim p_\theta(r \mid P, x)$.
\STATE Sample final answer $y \sim p_\theta(y \mid P, x, r)$.
\RETURN $y$
\end{algorithmic}
\end{algorithm}
```

For a strict IEEE look, wrap in `{IEEEalgorithm}` / `{IEEEalgorithmic}` if loaded — otherwise the default `algorithmic` is acceptable.

---

## 10. Math and Notation

- Define all symbols in a "Notation" subsection or at first use. Example block:

  | Symbol | Meaning |
  | --- | --- |
  | $P$ | prompt template |
  | $x, y$ | input, output |
  | $p_\theta$ | LLM likelihood |
  | $T$ | sampling temperature |
  | $k$ | top-$k$ truncation |
  | $p$ | nucleus threshold |

- Equation (1) example to mirror:

```latex
\begin{equation}
y^* = \arg\max_{y} \; p_\theta(y \mid P, x)
\label{eq:greedy}
\end{equation}
```

---

## 11. References

- The template ships with a manual `thebibliography`. If citation count grows beyond ~20, switch to BibTeX and `\bibliography{refs}` and add the `.bib` file to the repository.
- Number in citation order; renumber when re-ordering.
- Required fields per the template's exemplar entries:
  - Journal article: `Author(s), "Title," Journal, vol. x, pp. xx–xx, Mon. Year.`
  - Book: `Author, Title, xth ed., vol. x. City: Publisher, Year, pp. xx–xx.`
  - Conference paper: `Author(s), "Title," in Proc. Conf., City, Country, Year, pp. xx–xx.`
  - arXiv: `Author(s), "Title," Year, arXiv:xxxx.xxxxx. [Online]. Available: https://arxiv.org/abs/xxxx.xxxxx`
  - GitHub: `Author, "Repo name," Year, gitHub repository. [Online]. Available: URL`
  - Dataset: `Title. Publisher, Mon. Year, DOI:xx.xxxx/xxxxx`
  - Code Ocean: `Author(s), "Capsule title," Code Ocean, Mon. Year. [Online]. Available: URL`
- Capitalize only the first word of a paper title (plus proper nouns and element symbols).

---

## 12. Tone and Style

- Formal, third-person, evidence-driven. No marketing language. No "we believe" without results.
- Present tense for established facts, past tense for what the paper did/observed.
- Hedge appropriately: "suggests", "appears to", "is consistent with". Avoid "proves" without a theorem.
- Numbers under 10 spelled out; ≥10 as numerals. Always numerals with units (`5 ms`, not `five ms`).
- No emoji, no colored prose (the template uses red only for the removal reminder; strip it before submission).

---

## 13. Editing Workflow for Agents

1. **Read first**: open `format.md` and the current `IEEE-conference-template-062824.tex` before any edit.
2. **Plan**: enumerate every section that will be created/rewritten and the figures/tables it needs.
3. **Edit in place**: keep the LaTeX skeleton, replace content slots only. Do not delete `\maketitle`, `\begin{abstract}`, `\begin{IEEEkeywords}`, or `thebibliography`.
4. **Preserve labels**: never rename an existing `\label`; add new ones in kebab-/snake-case and place after `\caption`.
5. **Compile** with `pdflatex` (and `bibtex` if applicable). Inspect the PDF for page-limit, margin, and font issues. Re-run until clean.
6. **Self-audit** with the checklist in §14.
7. **Strip the red template-reminder sentence** before any "final" output. The line is:
   > *IEEE conference templates contain guidance text for composing and formatting conference papers. Please ensure that all template text is removed …*

---

## 14. Pre-Submission Checklist (run before declaring done)

- [ ] Title has no symbols, math, or footnotes; sub-title removed.
- [ ] Abstract is one paragraph, no math, no symbols, ≤ 250 words.
- [ ] 4–6 IEEEkeywords; each well-known acronym defined on first use.
- [ ] All headings produced by LaTeX, not hand-numbered.
- [ ] At least two subsections where used; none where only one would exist.
- [ ] Every figure/table cited in text before it appears; caption on figures is below; table head is above.
- [ ] Figure axis labels use words + units in parentheses.
- [ ] Equations numbered consecutively; no `eqnarray`; `\label` after `\caption`; `\eqref` used in prose.
- [ ] All `\cite{}` are numeric and square-bracketed; punctuation after the bracket; "Reference [n] was …" only at sentence start.
- [ ] References in citation order, IEEE format, arXiv/GitHub/DOI URLs valid.
- [ ] No template instructions, placeholder text, or red removal notice left in the file.
- [ ] No "essentially" used as "approximately"; "data" treated as plural; "non-" joined to host word; "et al." has no trailing period inside the "et".
- [ ] Page count within the conference's limit; font/margins untouched.

---

## 15. Anti-Patterns (auto-reject if seen)

- Hallucinated citations, fake DOIs, or URLs that 404.
- Bullet lists where IEEE sectioning would be cleaner.
- Colored prose for emphasis (the template's red is template-only).
- Screenshots of code or tables instead of native LaTeX.
- Manual numbering of sections (`1.`, `2.`, `2.1`).
- Mixing SI and CGS without explicit per-quantity unit declaration.
- Defining acronyms only in the abstract and not in body.
- A "References" section that uses author-year style — IEEE is strictly numeric `[n]`.
- Adding a new package that conflicts with `IEEEtran` (e.g., `geometry`, `titlesec`).

---

## 16. Hand-off Contract

When an agent finishes a pass it must report:
1. Sections touched (by `\label`).
2. New figures/tables added (file paths + `\label`s).
3. New citations added (keys).
4. Open questions / missing data for the user.
5. Compilation status (clean / warnings).

### Per-part handoff template

Save as `parts/part-N-<name>/handoff.md` at the end of each part.

```markdown
# Handoff — Part N: <name>

**Status:** draft | review | final
**Sections touched:** <list of \label values>
**New figures/tables:** <paths + \label>
**New citations:** <bib keys, e.g. b12, b13>
**Headline numbers (Part 3 only):** <n>%
**Acronyms defined this part:** <list>
**Open questions for the user:**
- ...
**Compile status:** clean | <warnings>
**Next-part dependencies:** <what the next agent must respect — locked citation keys, label names, notation>
```
