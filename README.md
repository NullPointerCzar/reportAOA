# Analysis of Prompt Engineering Techniques and Their Algorithmic Effect on LLM Output

IEEE-style research paper (`main.tex`) with a **real, runnable local benchmark**
pipeline for Apple Silicon Macs (16 GB unified memory, Metal via Ollama).

## Benchmark

`run_experiments.py` evaluates four prompt configurations:

| Technique | Operator |
| --- | --- |
| Direct answering | baseline |
| Zero-shot CoT | Ω (trace) |
| Few-shot CoT | Φ + Ω (context + trace) |
| Self-consistency (m = 4, T = 0.7) | Ω + Ψ (trace + decoding) |

against three locally served models (`llama3.2:1b`, `llama3.2:3b`,
`qwen2.5-coder:3b`, Q4_K_M/Q8_0 GGUF) on two tasks:

- **GSM8K** – 100-item seeded sample of the test split (seed 42)
- **HumanEval** – all 164 problems, pass@1 via sandboxed test execution

The grid is a "focused" design: GSM8K gets the full temperature sweep
(T ∈ {0.0, 0.3, 0.7, 1.0}, top-p 0.9) and 4 prompt paraphrases; HumanEval
runs at the reference decoding setting with 2 paraphrases.  Every generation
is logged to `results/records.jsonl` with accuracy, parse success, token
count, and wall-clock latency; aggregated results go to
`results/results.json` and `results/results.csv`.

## Requirements

- Ollama running locally with the three models pulled (the script never
  installs or downloads models):
  ```bash
  ollama pull llama3.2:1b && ollama pull llama3.2:3b && ollama pull qwen2.5-coder:3b
  ```
- Python 3 with `requests`; `matplotlib` only needed for the figure script.
- Benchmark data is fetched automatically from HuggingFace on first run
  (GSM8K test split + HumanEval); or prefetch with `--fetch-data`.

## Run the benchmark

```bash
# download/cache benchmark data (optional - --run does this automatically)
python3 run_experiments.py --fetch-data

# run the full focused grid (all 3 models x 2 tasks, ~25-30 h on a 16 GB Mac)
python3 run_experiments.py --run

# or prioritise / subset:
python3 run_experiments.py --run --models llama3.2:1b          # one model
python3 run_experiments.py --run --tasks gsm8k                 # one task
python3 run_experiments.py --run --quick                       # smoke test
python3 run_experiments.py --run --max-time 540                # ~9-min chunks
```

The run is **resumable**: each generation is appended to
`results/records.jsonl` as it completes, so interrupting (Ctrl+C) or closing
the terminal loses nothing — just re-run the same command to continue.

## Update the paper with measured results

```bash
python3 run_experiments.py --aggregate    # rebuild results.json/csv from records
python3 update_tables.py                  # fill the LaTeX tables (complete cells only)
python3 parts/part-3-results-abstract/make_fig_results.py   # regenerate Fig. 1
pdflatex main.tex && pdflatex main.tex
```

Cells with incomplete data are shown as `--` in the tables, so the paper
never displays a fabricated or partial number.
