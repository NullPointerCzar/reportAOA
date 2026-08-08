#!/usr/bin/env python3
"""
run_experiments.py
==================
Local benchmark runner for "Analysis of Prompt Engineering Techniques and
Their Algorithmic Effect on LLM Output".

Runs a fully crossed grid of prompt configurations against locally hosted
Ollama models (llama3.2:1b, llama3.2:3b, qwen2.5-coder:3b) on two tasks:

    * GSM8K    - 100-item seeded sample of the test split (N = 100)
    * HumanEval- all 164 problems, pass@1 via sandboxed unit-test execution

Technique configurations (the algorithmic factor):
    * direct           - answer-only prompting (baseline)
    * zs_cot           - zero-shot chain-of-thought trigger
    * fs_cot           - few-shot chain-of-thought (2 exemplars)
    * self_consistency - few-shot CoT, m = 4 samples at T = 0.7, plurality vote

Lexical factor: 4 paraphrases of every template (same exemplar count, same
trace shape, same output format), used to estimate the algorithmic effect
ratio (AER) at the reference decoding setting.

Decoding factor: temperature sweep T in {0.0, 0.3, 0.7, 1.0}; top-p = 0.9,
top-k = 40 for stochastic sampling (T > 0).  Greedy (T = 0) is the reference
cell.  Self-consistency is evaluated at its defined setting T = 0.7.

Per generation the runner records: raw response, extracted answer, exact-match
correctness, parse success, generated token count (eval_count), and wall-clock
latency (s).  All records append to results/records.jsonl (resumable); the
aggregated results are exported to results/results.json and results/results.csv.

Usage
-----
    python3 run_experiments.py --fetch-data        # download/cache benchmark data
    python3 run_experiments.py --run               # balanced grid, all models
    python3 run_experiments.py --run --models llama3.2:1b --tasks gsm8k
    python3 run_experiments.py --run --quick       # 3-item smoke test
    python3 run_experiments.py --aggregate         # recompute results.json from records

The models must already be pulled into Ollama (e.g. `ollama pull llama3.2:1b`);
this script never installs or downloads models.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import time
import urllib.parse
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
API_GENERATE = f"{OLLAMA_HOST}/api/generate"
API_TAGS = f"{OLLAMA_HOST}/api/tags"

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "data")
RESULTS_DIR = os.environ.get("RESULTS_DIR", os.path.join(ROOT, "results"))

GSM8K_DATASET = "openai/gsm8k"
GSM8K_CONFIG = "main"
HUMANEVAL_DATASET = "openai/openai_humaneval"
HUMANEVAL_CONFIG = "openai_humaneval"
HF_ROWS_URL = "https://datasets-server.huggingface.co/rows"

DEFAULT_MODELS = ["llama3.2:1b", "llama3.2:3b", "qwen2.5-coder:3b"]
DEFAULT_TASKS = ["gsm8k", "humaneval"]
TECHNIQUES = ["direct", "zs_cot", "fs_cot", "self_consistency"]
TEMPS = [0.0, 0.3, 0.7, 1.0]
N_PARAPHRASES = 4
GSM8K_SAMPLE_N = 100
GSM8K_SEED = 42
SC_M = 4          # self-consistency samples
SC_T = 0.7        # self-consistency temperature (defined setting)
REF_T = 0.0       # reference temperature for single-sample techniques
TOP_P = 0.9
TOP_K = 40
NUM_PREDICT = 1024
REQ_TIMEOUT = 900          # generous: first call may load the model into RAM
RETRY_BACKOFF = [2, 5, 15, 30, 60]

# Expected record count per complete cell: (task, technique) -> n records
# (n items x m samples; m = SC_M for self-consistency, else 1).
CELL_N = {
    ("gsm8k", "self_consistency"): GSM8K_SAMPLE_N * SC_M,
    ("gsm8k", "*"): GSM8K_SAMPLE_N,
    ("humaneval", "self_consistency"): 164 * SC_M,
    ("humaneval", "*"): 164,
}


def cell_complete(task: str, technique: str, n: int) -> bool:
    expected = CELL_N.get((task, "self_consistency") if technique == "self_consistency"
                          else (task, "*"))
    return expected is not None and n >= expected

# ---------------------------------------------------------------------------
# Prompt templates (4 paraphrases x technique x task)
# ---------------------------------------------------------------------------

GSM8K_FEWSHOT_EXEMPLARS = (
    "Q: There are 15 trees in the grove. Grove workers will plant trees in the "
    "grove today. After they are done, there will be 21 trees. How many trees "
    "did the grove workers plant today?\n"
    "A: There are 15 trees originally. Then there were 21 trees after some more "
    "were planted. So there must have been 21 - 15 = 6 trees planted. #### 6\n"
    "\n"
    "Q: If there are 3 cars in the parking lot and 2 more cars arrive, how many "
    "cars are in the parking lot?\n"
    "A: There are originally 3 cars. 2 more arrive. 3 + 2 = 5. #### 5\n"
)

HUMANEVAL_FEWSHOT_EXEMPLARS = (
    "Example 1\n"
    "Prompt:\n"
    "def sum_two(a: int, b: int) -> int:\n"
    "    \"\"\"Return the sum of a and b.\n"
    "    >>> sum_two(2, 3)\n"
    "    5\n"
    "    \"\"\"\n"
    "Reasoning: this function simply adds its two arguments together.\n"
    "Implementation:\n"
    "```python\n"
    "def sum_two(a: int, b: int) -> int:\n"
    "    return a + b\n"
    "```\n"
    "\n"
    "Example 2\n"
    "Prompt:\n"
    "def is_even(n: int) -> bool:\n"
    "    \"\"\"Return True if n is even.\n"
    "    >>> is_even(4)\n"
    "    True\n"
    "    >>> is_even(7)\n"
    "    False\n"
    "    \"\"\"\n"
    "Reasoning: a number is even when it is divisible by two.\n"
    "Implementation:\n"
    "```python\n"
    "def is_even(n: int) -> bool:\n"
    "    return n % 2 == 0\n"
    "```\n"
)


def _gsm8k_prompts(paraphrase: int) -> Dict[str, str]:
    """Return the four technique templates for GSM8K under a paraphrase."""
    q = "{question}"
    if paraphrase == 1:
        direct = f"Problem: {q}\nWhat is the answer? Give only the final number."
        zs = f"Problem: {q}\nLet's think step by step, and end your response with '#### <final number>'."
        fs = (f"Solve the following math problems step by step. End each answer "
              f"with '#### <final number>'.\n\n{GSM8K_FEWSHOT_EXEMPLARS}"
              f"Q: {q}\nA:")
    elif paraphrase == 2:
        direct = f"Question: {q}\nAnswer with just the final numeric result."
        zs = f"Question: {q}\nReason through this carefully step by step, then close with '#### <final number>'."
        fs = (f"Work through each word problem in steps. Conclude each response "
              f"with '#### <final number>'.\n\n{GSM8K_FEWSHOT_EXEMPLARS}"
              f"Q: {q}\nA:")
    elif paraphrase == 3:
        direct = f"Math problem: {q}\nRespond with only the final answer as a number."
        zs = f"Math problem: {q}\nTake it one step at a time and finish with '#### <final number>'."
        fs = (f"Below are worked examples. Solve the final problem step by step "
              f"and finish with '#### <final number>'.\n\n{GSM8K_FEWSHOT_EXEMPLARS}"
              f"Q: {q}\nA:")
    else:  # paraphrase 4
        direct = f"Task: {q}\nOutput the final answer as a bare number."
        zs = f"Task: {q}\nThink through the solution step by step, ending with '#### <final number>'."
        fs = (f"Study the examples, then solve the question below with a step-by-step "
              f"trace ending in '#### <final number>'.\n\n{GSM8K_FEWSHOT_EXEMPLARS}"
              f"Q: {q}\nA:")
    return {"direct": direct, "zs_cot": zs, "fs_cot": fs}


def _humaneval_prompts(paraphrase: int) -> Dict[str, str]:
    """Return the four technique templates for HumanEval under a paraphrase."""
    p = "{prompt}"
    if paraphrase == 1:
        direct = f"Complete the following Python function. Return only the code.\n\n{p}"
        zs = f"{p}\nLet's think step by step about how to implement this function, then write the code.\n```python\n"
        fs = (f"{HUMANEVAL_FEWSHOT_EXEMPLARS}\n"
              f"Now complete the function below. Write the implementation only.\n{p}")
    elif paraphrase == 2:
        direct = f"Fill in the implementation of the Python function below. Output just the code.\n\n{p}"
        zs = f"{p}\nReason step by step about the implementation, then emit the code in a fenced block.\n```python\n"
        fs = (f"{HUMANEVAL_FEWSHOT_EXEMPLARS}\n"
              f"Implement the function below; provide only the code this time.\n{p}")
    elif paraphrase == 3:
        direct = f"Implement the function. Your answer must be plain Python code.\n\n{p}"
        zs = f"{p}\nPlan the solution step by step, then finish with the code.\n```python\n"
        fs = (f"{HUMANEVAL_FEWSHOT_EXEMPLARS}\n"
              f"Solve the following function; give only the implementation.\n{p}")
    else:  # paraphrase 4
        direct = f"Write the body of the function so it satisfies its docstring. Code only.\n\n{p}"
        zs = f"{p}\nWalk through the logic step by step, then output the completed function.\n```python\n"
        fs = (f"{HUMANEVAL_FEWSHOT_EXEMPLARS}\n"
              f"Complete the function below; respond with the code alone.\n{p}")
    return {"direct": direct, "zs_cot": zs, "fs_cot": fs}


PROMPT_BUILDERS = {
    "gsm8k": _gsm8k_prompts,
    "humaneval": _humaneval_prompts,
}


# ---------------------------------------------------------------------------
# Data acquisition (dataset downloads are benchmark data, not models)
# ---------------------------------------------------------------------------

def _hf_rows(dataset: str, config: str, split: str, offset: int, length: int) -> List[Dict[str, Any]]:
    params = urllib.parse.urlencode(
        {"dataset": dataset, "config": config, "split": split,
         "offset": offset, "length": length}
    )
    resp = requests.get(f"{HF_ROWS_URL}?{params}", timeout=120)
    resp.raise_for_status()
    payload = resp.json()
    if "rows" not in payload:
        raise RuntimeError(f"HF rows error for {dataset}: {payload}")
    return [r["row"] for r in payload["rows"]]


def fetch_data(force: bool = False) -> None:
    """Download and cache the two benchmark datasets into data/."""
    os.makedirs(DATA_DIR, exist_ok=True)
    gsm8k_path = os.path.join(DATA_DIR, "gsm8k_test.jsonl")
    humaneval_path = os.path.join(DATA_DIR, "humaneval_test.jsonl")

    if not os.path.exists(gsm8k_path) or force:
        print("[data] downloading GSM8K test split ...", flush=True)
        rows: List[Dict[str, Any]] = []
        offset = 0
        while True:
            batch = _hf_rows(GSM8K_DATASET, GSM8K_CONFIG, "test", offset, 100)
            if not batch:
                break
            rows.extend(batch)
            offset += len(batch)
            if len(batch) < 100:
                break
        with open(gsm8k_path, "w") as f:
            for r in rows:
                f.write(json.dumps({"question": r["question"], "answer": r["answer"]}) + "\n")
        print(f"[data] GSM8K: {len(rows)} test items cached", flush=True)

    if not os.path.exists(humaneval_path) or force:
        print("[data] downloading HumanEval ...", flush=True)
        rows = []
        offset = 0
        while True:
            batch = _hf_rows(HUMANEVAL_DATASET, HUMANEVAL_CONFIG, "test", offset, 100)
            if not batch:
                break
            rows.extend(batch)
            offset += len(batch)
            if len(batch) < 100:
                break
        with open(humaneval_path, "w") as f:
            for r in rows:
                f.write(json.dumps({
                    "task_id": r["task_id"], "prompt": r["prompt"],
                    "test": r["test"], "entry_point": r["entry_point"],
                }) + "\n")
        print(f"[data] HumanEval: {len(rows)} problems cached", flush=True)

    # Deterministic GSM8K subset (N = 100, fixed seed)
    subset_path = os.path.join(DATA_DIR, "gsm8k_subset_100.jsonl")
    if not os.path.exists(subset_path) or force:
        with open(gsm8k_path) as f:
            items = [json.loads(line) for line in f]
        rng = random.Random(GSM8K_SEED)
        sampled = rng.sample(items, GSM8K_SAMPLE_N)
        with open(subset_path, "w") as f:
            for i, it in enumerate(sampled):
                f.write(json.dumps({**it, "item_id": i}) + "\n")
        print(f"[data] GSM8K subset: {len(sampled)} items (seed {GSM8K_SEED})", flush=True)


def load_items(task: str, max_items: Optional[int] = None) -> List[Dict[str, Any]]:
    if task == "gsm8k":
        path = os.path.join(DATA_DIR, "gsm8k_subset_100.jsonl")
    else:
        path = os.path.join(DATA_DIR, "humaneval_test.jsonl")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{path} missing - run `python3 run_experiments.py --fetch-data` first")
    with open(path) as f:
        items = [json.loads(line) for line in f]
    if max_items:
        items = items[:max_items]
    return items


# ---------------------------------------------------------------------------
# Answer extraction & evaluation
# ---------------------------------------------------------------------------

NUM_RE = re.compile(r"-?\d[\d,]*(?:\.\d+)?")


def extract_gsm8k_answer(text: str) -> Optional[str]:
    """Extract the final answer: prefer the value after '####', else the last number."""
    text = text.strip()
    m = re.findall(r"####\s*(-?\d[\d,]*(?:\.\d+)?)", text)
    if m:
        return m[-1].replace(",", "")
    nums = NUM_RE.findall(text)
    if nums:
        return nums[-1].replace(",", "")
    return None


def normalize_number(s: str) -> float:
    return float(s.replace(",", ""))


def parse_gsm8k_gold(answer: str) -> str:
    """The gold GSM8K answer ends with '#### <number>'."""
    m = re.findall(r"####\s*(-?\d[\d,]*(?:\.\d+)?)", answer)
    return m[-1].replace(",", "") if m else answer.strip()


def extract_code(text: str) -> Optional[str]:
    """Extract a Python completion from the model response."""
    text = text.strip()
    if not text:
        return None
    # Prefer a fenced python block (the last one).
    blocks = re.findall(r"```(?:python)?\s*\n?(.*?)```", text, re.DOTALL)
    if blocks:
        return blocks[-1].strip("\n")
    # Otherwise strip the echoed prompt and leading prose up to the first def.
    if "def " in text:
        idx = text.find("def ")
        lines = text[idx:].splitlines()
        keep = []
        for ln in lines:
            # drop trailing prose that follows the code block
            if keep and not ln.strip():
                continue
            if keep and not ln[:1].isspace() and not ln.startswith(("def ", "from ",
                                                                    "import ", "#", "return ", "raise ", "assert ")):
                break
            keep.append(ln)
        out = "\n".join(keep).strip("\n")
        return out or None
    # Fall back to the raw response as the continuation of the prompt.
    return text


def run_humaneval_test(prompt: str, completion: Optional[str], test: str,
                       entry_point: str, timeout: float = 15.0) -> bool:
    """Execute prompt+completion against the unit tests in a sandboxed subprocess."""
    if not completion or not completion.strip():
        return False
    code = prompt.rstrip("\n") + "\n" + completion.strip("\n")
    harness = (
        "import sys\n"
        f"{code}\n"
        f"{test}\n"
        f"check({entry_point})\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(harness)
        tmp = f.name
    try:
        proc = subprocess.run(
            [sys.executable, "-I", tmp],
            capture_output=True, text=True, timeout=timeout,
        )
        return proc.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def evaluate_item(task: str, item: Dict[str, Any], response: str) -> Tuple[bool, bool, Optional[str]]:
    """Return (correct, parsed, extracted_value)."""
    if task == "gsm8k":
        extracted = extract_gsm8k_answer(response)
        if extracted is None:
            return False, False, None
        gold = parse_gsm8k_gold(item["answer"])
        try:
            correct = abs(normalize_number(extracted) - normalize_number(gold)) < 1e-9
        except (ValueError, TypeError):
            correct = False
        return correct, True, extracted
    else:  # humaneval
        completion = extract_code(response)
        if completion is None:
            return False, False, None
        passed = run_humaneval_test(item["prompt"], completion, item["test"],
                                    item["entry_point"])
        return passed, True, completion[:200]


# ---------------------------------------------------------------------------
# Ollama client
# ---------------------------------------------------------------------------

def ollama_models() -> List[str]:
    resp = requests.get(API_TAGS, timeout=30)
    resp.raise_for_status()
    return [m["name"] for m in resp.json().get("models", [])]


def check_models(required: List[str]) -> None:
    available = ollama_models()
    missing = [m for m in required if m not in available]
    if missing:
        sys.exit(
            f"[error] models not found in Ollama: {', '.join(missing)}\n"
            f"        pulled locally: {available}\n"
            f"        run `ollama pull <model>` first (this script never installs models)."
        )


def generate(model: str, prompt: str, temperature: float) -> Dict[str, Any]:
    """Call /api/generate; returns text, tokens, wall-clock seconds.

    Transient connection/timeout errors are retried with backoff; HTTP errors
    (e.g., 404 for a missing model) raise immediately instead of retrying.
    """
    options = {
        "temperature": temperature,
        "top_p": TOP_P if temperature > 0 else 1.0,
        "top_k": TOP_K if temperature > 0 else -1,
        "num_predict": NUM_PREDICT,
    }
    payload = {"model": model, "prompt": prompt, "stream": False, "options": options}
    last_err: Optional[Exception] = None
    for attempt, delay in enumerate(RETRY_BACKOFF):
        t0 = time.perf_counter()
        try:
            resp = requests.post(API_GENERATE, json=payload, timeout=REQ_TIMEOUT)
            if resp.status_code >= 400:
                raise RuntimeError(
                    f"Ollama HTTP {resp.status_code} for {model}: {resp.text[:200]}")
            resp.raise_for_status()
            data = resp.json()
            latency = time.perf_counter() - t0
            return {
                "text": data.get("response", ""),
                "tokens": int(data.get("eval_count", 0)),
                "latency_s": latency,
                "model_load_s": (data.get("load_duration") or 0) / 1e9,
            }
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exc:
            last_err = exc
            time.sleep(delay)
    raise RuntimeError(f"Ollama generate failed after retries for {model}: {last_err}")


# ---------------------------------------------------------------------------
# Grid construction
# ---------------------------------------------------------------------------

def build_grid(model: str, task: str, quick: bool = False,
               full: bool = False) -> List[Dict[str, Any]]:
    """Return a list of cell descriptors for one (model, task).

    Focused grid (default):
      * GSM8K:  direct/zs_cot/fs_cot at T in {0.0,0.3,0.7,1.0}; SC at T=0.7
                (paraphrase 1), plus all 4 paraphrases at the reference temp.
      * HumanEval: direct/zs_cot/fs_cot at T=0.0; SC at T=0.7 (paraphrase 1),
                plus 2 paraphrases at the reference temp (AER needs >= 2
                lexical levels).
    """
    cells = []
    if quick:
        for technique in TECHNIQUES:
            t = SC_T if technique == "self_consistency" else REF_T
            cells.append({"model": model, "task": task, "technique": technique,
                          "paraphrase": 1, "temperature": t})
        return cells

    if full:
        # full grid: every technique x every temperature x every paraphrase
        for technique in TECHNIQUES:
            temps = [SC_T] if technique == "self_consistency" else TEMPS
            for t in temps:
                for par in range(1, N_PARAPHRASES + 1):
                    cells.append({"model": model, "task": task, "technique": technique,
                                  "paraphrase": par, "temperature": t})
        return cells

    # main grid on paraphrase 1
    for technique in TECHNIQUES:
        if technique == "self_consistency":
            temps = [SC_T]
        elif task == "gsm8k":
            temps = TEMPS
        else:
            temps = [REF_T]
        for t in temps:
            cells.append({"model": model, "task": task, "technique": technique,
                          "paraphrase": 1, "temperature": t})
    # lexical factor at the reference temperature (paraphrase 1 already done)
    n_lex = N_PARAPHRASES if task == "gsm8k" else 2
    for par in range(2, n_lex + 1):
        for technique in TECHNIQUES:
            t = SC_T if technique == "self_consistency" else REF_T
            cells.append({"model": model, "task": task, "technique": technique,
                          "paraphrase": par, "temperature": t})
    return cells


# ---------------------------------------------------------------------------
# Execution with resumable checkpointing
# ---------------------------------------------------------------------------

def record_key(rec: Dict[str, Any]) -> Tuple[str, ...]:
    return (rec["model"], rec["task"], rec["technique"], str(rec["paraphrase"]),
            str(rec["temperature"]), str(rec["item_id"]), str(rec["sample"]))


def load_completed() -> set:
    path = os.path.join(RESULTS_DIR, "records.jsonl")
    done = set()
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    done.add(record_key(rec))
                except json.JSONDecodeError:
                    continue
    return done


def append_record(rec: Dict[str, Any]) -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, "records.jsonl")
    with open(path, "a") as f:
        f.write(json.dumps(rec) + "\n")


def run_cell(model: str, task: str, technique: str, paraphrase: int,
             temperature: float, items: List[Dict[str, Any]], done: set,
             max_samples: Optional[int] = None,
             deadline: Optional[float] = None) -> List[Dict[str, Any]]:
    """Execute one cell; returns per-item record list.  Skips completed records.

    If deadline is set (absolute perf_counter time), generation stops at the
    next item boundary once it is exceeded (records already written remain
    valid for resume).
    """
    builders = PROMPT_BUILDERS[task]
    templates = builders(paraphrase)
    prompt = templates["direct"] if technique == "direct" else templates["fs_cot"]
    if technique == "zs_cot":
        prompt = templates["zs_cot"]
    n_samples = SC_M if technique == "self_consistency" else 1
    if max_samples:
        n_samples = min(n_samples, max_samples)

    records: List[Dict[str, Any]] = []
    total = len(items) * n_samples
    run_idx = 0
    for item in items:
        if deadline is not None and time.perf_counter() > deadline:
            print(f"    [time budget reached, pausing cell]", flush=True)
            break
        if task == "gsm8k":
            filled = prompt.format(question=item["question"])
        else:
            filled = prompt.format(prompt=item["prompt"])
        for sample in range(n_samples):
            key = (model, task, technique, str(paraphrase), str(temperature),
                   str(item.get("item_id", item.get("task_id"))), str(sample))
            if key in done:
                run_idx += 1
                continue
            run_idx += 1
            out = generate(model, filled, temperature)
            correct, parsed, extracted = evaluate_item(task, item, out["text"])
            rec = {
                "model": model, "task": task, "technique": technique,
                "paraphrase": paraphrase, "temperature": temperature,
                "item_id": item.get("item_id", item.get("task_id")),
                "sample": sample,
                "response": out["text"],
                "extracted": extracted,
                "correct": correct,
                "parsed": parsed,
                "tokens": out["tokens"],
                "latency_s": out["latency_s"],
                "model_load_s": out["model_load_s"],
            }
            records.append(rec)
            append_record(rec)
            if run_idx % 10 == 0 or run_idx == total:
                print(f"    [{model}][{task}][{technique} p{paraphrase} T={temperature}] "
                      f"{run_idx}/{total}  "
                      f"(tok={out['tokens']}, {out['latency_s']:.1f}s)",
                      flush=True)
    return records


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def load_records() -> List[Dict[str, Any]]:
    path = os.path.join(RESULTS_DIR, "records.jsonl")
    if not os.path.exists(path):
        return []
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records


def aggregate(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute per-cell aggregates, SC vote accuracy, and the AER."""
    # Per-sample cell aggregates (accuracy, parse rate, tokens, latency).
    cells: Dict[Tuple[str, ...], Dict[str, Any]] = defaultdict(
        lambda: {"n": 0, "correct": 0, "parsed": 0, "tokens": 0.0,
                 "latency": 0.0})
    for r in records:
        ck = (r["model"], r["task"], r["technique"], str(r["paraphrase"]),
              str(r["temperature"]))
        c = cells[ck]
        c["n"] += 1
        c["correct"] += int(r["correct"])
        c["parsed"] += int(r["parsed"])
        c["tokens"] += r["tokens"]
        c["latency"] += r["latency_s"]

    # Self-consistency aggregation per (model, task, paraphrase, item).
    #  * GSM8K: plurality vote over the normalised extracted answer string
    #    (so "5" and "5.0" are the same answer); the sample's `correct` flag
    #    records whether its answer matched the gold.
    #  * HumanEval: programs cannot be plurality-voted, so the honest analogue
    #    is a majority-pass rule: the item counts as solved when the majority
    #    of its m samples pass the unit tests.
    sc_buckets: Dict[Tuple[str, str, str, str, str], Dict[str, List[bool]]] = defaultdict(
        lambda: defaultdict(list))
    sc_passes: Dict[Tuple[str, str, str, str, str], List[bool]] = defaultdict(list)
    # accumulated (wins, n_items, n_parsed) per cell key, so vote_accuracy is a
    # fraction across ALL items, not the last item's outcome
    sc_acc: Dict[Tuple[str, ...], List[int]] = defaultdict(lambda: [0, 0, 0])

    def _norm_sc_answer(r: Dict[str, Any]) -> str:
        ans = r.get("extracted")
        if ans is None:
            return "__UNPARSED__"
        if r["task"] == "gsm8k":
            try:
                return format(float(str(ans).replace(",", "")), "g")
            except (ValueError, TypeError):
                return str(ans)
        return str(ans)

    for r in records:
        if r["technique"] == "self_consistency":
            key = (r["model"], r["task"], str(r["paraphrase"]),
                   str(r["temperature"]), str(r["item_id"]))
            if r["task"] == "humaneval":
                sc_passes[key].append(r["correct"])
            else:
                sc_buckets[key][_norm_sc_answer(r)].append(r["correct"])

    sc_stats: Dict[Tuple[str, ...], Dict[str, float]] = {}
    # --- HumanEval: majority pass (accumulate across items) ---
    for key, flags in sc_passes.items():
        model, task, par, temp, _ = key
        ck = (model, task, "self_consistency", par, temp)
        m = len(flags)
        sc_acc[ck][1] += 1
        if sum(1 for f in flags if f) * 2 > m:  # strict majority
            sc_acc[ck][0] += 1
        sc_acc[ck][2] += 1
    # --- GSM8K: plurality over normalised answers (accumulate across items) ---
    for key, buckets in sc_buckets.items():
        model, task, par, temp, _ = key
        ck = (model, task, "self_consistency", par, temp)
        # Unbiased tie-break: among buckets tied for the plurality count,
        # pick the first-seen answer (insertion order).  The previous rule
        # resolved ties by preferring a bucket whose samples were correct
        # (max key (count, any(correct))), which silently inflated SC
        # accuracy; correctness must not influence which answer wins.
        winner = max(buckets.items(), key=lambda kv: len(kv[1]))
        winner_answer, winner_flags = winner
        sc_acc[ck][1] += 1
        if winner_answer != "__UNPARSED__" and any(winner_flags):
            sc_acc[ck][0] += 1
        if winner_answer != "__UNPARSED__":
            sc_acc[ck][2] += 1
    for ck, (wins, n_items, n_parsed) in sc_acc.items():
        sc_stats[ck] = {"vote_accuracy": wins / n_items if n_items else 0.0,
                        "vote_parse_rate": n_parsed / n_items if n_items else 0.0,
                        "vote_n_votes": n_items}

    # Build the aggregate table (cells + SC vote accuracy where applicable).
    table = []
    for ck in sorted(cells):
        c = cells[ck]
        row = {
            "model": ck[0], "task": ck[1], "technique": ck[2],
            "paraphrase": int(ck[3]), "temperature": float(ck[4]),
            "n": c["n"],
            "complete": cell_complete(ck[1], ck[2], c["n"]),
            "accuracy": c["correct"] / c["n"] if c["n"] else 0.0,
            "parse_rate": c["parsed"] / c["n"] if c["n"] else 0.0,
            "mean_tokens": c["tokens"] / c["n"] if c["n"] else 0.0,
            "mean_latency_s": c["latency"] / c["n"] if c["n"] else 0.0,
        }
        if row["technique"] == "self_consistency":
            sc_ck = (row["model"], row["task"], row["technique"],
                     str(row["paraphrase"]), str(row["temperature"]))
            if sc_ck in sc_stats:
                row["vote_accuracy"] = sc_stats[sc_ck]["vote_accuracy"]
                row["vote_parse_rate"] = sc_stats[sc_ck]["vote_parse_rate"]
                # headline accuracy for SC is the item-level vote, not per-sample
                row["accuracy"] = row["vote_accuracy"]
        table.append(row)

    # AER per (model, task) using the lexical cells at the reference temperature.
    aer: Dict[str, Dict[str, Dict[str, float]]] = {}
    for model in sorted({r["model"] for r in records}):
        for task in sorted({r["task"] for r in records}):
            ref_rows = [r for r in table
                        if r["model"] == model and r["task"] == task
                        and r["technique"] != "self_consistency"
                        and r["temperature"] == REF_T]
            alg_levels = sorted({r["technique"] for r in ref_rows})
            lex_levels = sorted({r["paraphrase"] for r in ref_rows})
            if len(alg_levels) < 2 or len(lex_levels) < 2:
                continue
            # require the complete technique x paraphrase rectangle, with every
            # cell at full item coverage (never estimate AER from partial cells)
            if len(ref_rows) != len(alg_levels) * len(lex_levels):
                continue
            if not all(r["complete"] for r in ref_rows):
                continue
            Y = {(r["technique"], r["paraphrase"]): r["accuracy"] for r in ref_rows}
            n_alg, n_lex = len(alg_levels), len(lex_levels)
            grand = sum(Y.values()) / len(Y)
            cf = n_alg * n_lex * grand ** 2  # correction factor
            ss_alg = sum(sum(Y[(a, l)] for l in lex_levels) ** 2
                         for a in alg_levels) / n_lex - cf
            ss_lex = sum(sum(Y[(a, l)] for a in alg_levels) ** 2
                         for l in lex_levels) / n_alg - cf
            ss_res = sum((v - grand) ** 2 for v in Y.values()) - ss_alg - ss_lex
            df_alg, df_lex = n_alg - 1, n_lex - 1
            df_res = df_alg * df_lex
            ms_alg = ss_alg / df_alg if df_alg else 0.0
            ms_lex = ss_lex / df_lex if df_lex else 0.0
            ms_res = ss_res / df_res if df_res else 0.0
            sig_alg = max((ms_alg - ms_res) / n_lex, 0.0)
            sig_lex = max((ms_lex - ms_res) / n_alg, 0.0)
            aer_val = sig_alg / (sig_alg + sig_lex) if (sig_alg + sig_lex) > 0 else 0.5
            aer.setdefault(model, {})
            aer[model][task] = {"aer": round(aer_val, 4),
                                "sigma_alg": round(sig_alg, 6),
                                "sigma_lex": round(sig_lex, 6)}

    return {"table": table,
            "sc_stats": {"__".join(k): v for k, v in sc_stats.items()},
            "aer": aer}


def write_results(aggregated: Dict[str, Any]) -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    # results.json
    with open(os.path.join(RESULTS_DIR, "results.json"), "w") as f:
        json.dump(aggregated, f, indent=2)
    # results.csv (flat aggregate table)
    rows = aggregated["table"]
    if rows:
        import csv
        cols = ["model", "task", "technique", "paraphrase", "temperature", "n",
                "accuracy", "parse_rate", "mean_tokens", "mean_latency_s",
                "vote_accuracy", "vote_parse_rate"]
        with open(os.path.join(RESULTS_DIR, "results.csv"), "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            writer.writeheader()
            for r in rows:
                writer.writerow(r)
    print(f"[results] wrote {RESULTS_DIR}/results.json and results.csv")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Local Ollama prompt-engineering benchmark")
    ap.add_argument("--fetch-data", action="store_true", help="download/cache benchmark data")
    ap.add_argument("--run", action="store_true", help="run the benchmark grid")
    ap.add_argument("--aggregate", action="store_true",
                    help="recompute results.json/csv from existing records")
    ap.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    ap.add_argument("--tasks", nargs="+", default=DEFAULT_TASKS)
    ap.add_argument("--max-items", type=int, default=None,
                    help="limit items per task (for smoke tests)")
    ap.add_argument("--fresh", action="store_true",
                    help="delete existing records.jsonl before running")
    ap.add_argument("--quick", action="store_true",
                    help="minimal smoke grid (reference temps only)")
    ap.add_argument("--full", action="store_true",
                    help="full grid: all temps x all paraphrases x both tasks "
                         "(longer than the default focused grid)")
    ap.add_argument("--max-samples", type=int, default=None,
                    help="cap self-consistency samples (for smoke tests)")
    ap.add_argument("--max-time", type=float, default=None,
                    help="stop after this many seconds (resumable chunks)")
    args = ap.parse_args()

    if args.fetch_data:
        fetch_data(force=True)
        return

    if args.aggregate:
        records = load_records()
        write_results(aggregate(records))
        return

    if args.fresh:
        rec_path = os.path.join(RESULTS_DIR, "records.jsonl")
        if os.path.exists(rec_path):
            os.remove(rec_path)
            print(f"[run] cleared {rec_path}", flush=True)

    if not args.run:
        ap.print_help()
        return

    fetch_data()
    check_models(args.models)

    done = load_completed()
    print(f"[run] resuming from {len(done)} completed generations", flush=True)
    deadline = (time.perf_counter() + args.max_time) if args.max_time else None
    total_cells = 0
    budget_hit = False
    for model in args.models:
        if budget_hit:
            break
        for task in args.tasks:
            if budget_hit:
                break
            cells = build_grid(model, task, quick=args.quick, full=args.full)
            # staged ordering: reference cells -> temp sweep -> paraphrases,
            # so the headline results table fills first
            def _stage(c):
                ref_temps = (SC_T,) if c["technique"] == "self_consistency" else (REF_T,)
                if c["paraphrase"] == 1 and c["temperature"] in ref_temps:
                    return 0
                if c["paraphrase"] == 1:
                    return 1
                return 2
            cells.sort(key=lambda c: (_stage(c), c["technique"], c["temperature"], c["paraphrase"]))
            total_cells += len(cells)
            items = load_items(task, args.max_items)
            print(f"\n[run] {model} / {task}: {len(cells)} cells x {len(items)} items",
                  flush=True)
            for cell in cells:
                if deadline is not None and time.perf_counter() > deadline:
                    print("[run] global time budget reached - pausing. "
                          "Re-run to resume.", flush=True)
                    budget_hit = True
                    break
                run_cell(model, task, cell["technique"], cell["paraphrase"],
                         cell["temperature"], items, done,
                         max_samples=args.max_samples, deadline=deadline)

    if budget_hit:
        print(f"\n[run] paused at time budget ({args.max_time}s chunk). "
              f"Records are safe; re-run to continue.", flush=True)
        return
    print(f"\n[run] done ({total_cells} cells). Aggregating ...", flush=True)
    records = load_records()
    write_results(aggregate(records))


if __name__ == "__main__":
    main()
