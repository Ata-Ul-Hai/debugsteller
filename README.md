# DebugStellar 🌟

An AI-powered autonomous Python debugging and optimization engine. DebugStellar automatically detects runtime errors, generates patches using a local LLM via [Ollama](https://ollama.com/), verifies fixes, and optimizes code complexity — all without sending your code to the cloud.

---

## Features

- **Auto-Fix** — Detects and repairs common Python runtime errors (e.g., `IndexError`, `RecursionError`, `NameError`, `TypeError`, `KeyError`)
- **Logic Repair** — Fixes code that runs but produces wrong output, guided by a plain-language description you provide
- **Code Optimization** — Improves algorithmic complexity (e.g., O(N²) → O(N)) with educational comments explaining the change
- **Safety Guard** — Verifies that any optimization preserves the original program's stdout before accepting it
- **Execution Trace** — Logs every iteration, patch, and strategy to a `debug_report.json` for full auditability
- **Streamlit UI** — LeetCode-style split-panel interface with code diff, console output, analysis, and raw trace tabs
- **PDF Support** — Upload a `.pdf` containing Python code and let the system extract and debug it

---

## Architecture

```
debugsteller/
├── app.py              # Streamlit web UI
├── main.py             # CLI entry point
├── src/
│   ├── controller.py   # Orchestrates the debug → repair → optimize pipeline
│   ├── patch_engine.py # Error analysis, LLM prompting, patch generation & optimization
│   ├── sandbox.py      # Runs code in isolated subprocesses with a timeout
│   └── logger.py       # Writes debug_report.json
├── tests/              # Sample buggy Python scripts for testing
├── fixed_tests/        # Output directory for fixed scripts
└── debug_report.json   # Generated report from the last run
```

### How it works

1. **Run** — The `Sandbox` executes the script in a subprocess (2-second timeout).
2. **Analyze** — If it fails, `PatchEngine` parses `stderr` to extract the error type, line number, and message.
3. **Patch** — Built-in heuristics handle simple cases (e.g., `RecursionError`, `NameError`). All others are sent to the local Ollama LLM.
4. **Iterate** — Steps 1–3 repeat up to `--iterations` times (default: 3).
5. **Logic Repair** *(optional)* — If `--description` is provided and the code runs but produces wrong output, the LLM applies a targeted logic fix.
6. **Optimize** — Once the code executes cleanly, the LLM proposes an optimized version. The sandbox verifies output parity before accepting it.
7. **Save** — The fixed/optimized code is written to `fixed_tests/` and a full report is saved to `debug_report.json`.

---

## Requirements

- Python 3.9+
- [Ollama](https://ollama.com/) running locally on `http://localhost:11434`

### Python dependencies

```
streamlit
pypdf
requests
rich
```

Install them with:

```bash
pip install streamlit pypdf requests rich
```

### Pull an Ollama model

```bash
ollama pull qwen2.5-coder:7b
```

Any model available in Ollama can be used via the `--model` flag.

---

## Usage

### Web UI (recommended)

```bash
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

1. Paste Python code (or upload a `.py`/`.pdf` file) in the left panel.
2. Optionally describe the expected behavior (e.g., *"Output should be [1, 2, 3]"*).
3. Click **Run Debugger**.
4. Review the fixed code, console output, and analysis in the right panel.

### CLI

```bash
python main.py <path-to-script.py> [options]
```

| Option | Default | Description |
|---|---|---|
| `--model` | `llama3` | Ollama model to use |
| `--iterations` | `3` | Maximum debugging iterations |
| `--description` | *(none)* | Plain-language description of expected behavior (enables Logic Repair mode) |

**Examples:**

```bash
# Basic debug with default model
python main.py tests/index_error_bug.py

# Use a specific model
python main.py tests/logic_error_bug.py --model qwen2.5-coder:7b

# Logic repair with a description
python main.py tests/off_by_one.py --model qwen2.5-coder:7b --description "The function should return the sum of all elements"
```

Fixed scripts are saved to `fixed_tests/` and a detailed report is written to `debug_report.json`.

---

## Output

After a run, `debug_report.json` contains:

| Field | Description |
|---|---|
| `original_code` | The input code as submitted |
| `repaired_code` | The final fixed (and optionally optimized) code |
| `traces` | Per-iteration log of error type, strategy, patch, and outcome |
| `optimization_report` | Big O complexity before/after, changes summary, and optimized code |
| `best_attempt` | Best intermediate result if the final run failed |
| `failure_explanation` | Reason for failure (or `"Success"`) |
| `timestamp` | When the report was generated |

---

## Test Cases

The `tests/` directory includes a variety of intentionally buggy scripts:

| File | Bug Type |
|---|---|
| `index_error_bug.py` | `IndexError` |
| `type_error_bug.py` | `TypeError` |
| `logic_error_bug.py` | Logic error (wrong output) |
| `off_by_one.py` | Off-by-one error |
| `infinite_recursion.py` | `RecursionError` |
| `recursion_bug.py` | Incorrect base case |
| `binary_search.py` | Faulty binary search |
| `bubble_sort.py` | Incorrect sort implementation |
| `slow_code.py` | Inefficient algorithm (optimization target) |
| `slow_unique_finder.py` | O(N²) → O(N) optimization target |
| `inefficient_string.py` | Inefficient string concatenation |
| `invalid_index.py` | Invalid list access |
| `hallucination_trap.py` | Edge-case logic trap |

---

## License

This project is open source. See the repository for license details.
