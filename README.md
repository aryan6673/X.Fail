# xFail — Model Autopsy Benchmark

A curated evaluation harness that surfaces qualitative failure modes in LLM coding tasks — not just pass rates.

## Why xFail?

Existing benchmarks (HumanEval, MBPP, SWE-Bench) tell you *how often* a model succeeds. xFail tells you *why* it fails — in reproducible, taxonomized patterns.

**Use case:** Human Data teams designing training data based on specific, observed failure modes.

## Quick Start

### Setup

```bash
pip install -e .
cp .env.example .env
# Add your API keys to .env
```

### Run Benchmark

```bash
# Run proof-of-concept tasks against default models (grok, gemini)
xfail run --task-set poc

# Run against a specific model
xfail run --models grok --task-set poc

# Run a single task
xfail run --task xfail/tasks/poc/deceptive_001.yaml
```

### Generate Report

```bash
# After running, generate an HTML report
xfail report --run-id <TIMESTAMP> --format html

# Generate markdown instead
xfail report --run-id <TIMESTAMP> --format markdown

# Both
xfail report --run-id <TIMESTAMP> --format both
```

### Compare Models

```bash
xfail diff --model-a grok --model-b gemini --run <TIMESTAMP>
```

## Failure Mode Taxonomy

Every model output is tagged with one or more of these codes:

| Code | Name | Description |
|------|------|-------------|
| `SPEC-MIS` | Specification misread | Implements plausible but wrong interpretation |
| `INV-LOSS` | Invariant loss | Fails to maintain 2+ interacting constraints |
| `EDGE-OBO` | Edge case / off-by-one | Passes happy path, fails boundaries |
| `HALL-CON` | Hallucinated constraint | Invents a requirement not in the spec |
| `ABS-FAIL` | Poor abstraction | Solves specific case, doesn't generalize |
| `BIZ-FRAME` | Business framing gap | Fails when requirements are outcomes, not specs |
| `CTX-DROP` | Context drop | Loses constraints in multi-turn sessions |

## Project Structure

```
xfail/
├── models/          # API clients (Grok, Gemini)
├── harness/         # Task execution, scoring, classification
├── reports/         # Report generation
├── tasks/           # Task definitions
│   └── poc/         # Proof-of-concept tasks
├── cli.py           # Command-line interface
└── __init__.py

results/            # Execution logs (auto-generated)
reports/            # Generated reports (auto-generated)
```

## Task Format

Tasks are defined in YAML:

```yaml
task_id: my_task
category: deceptive  # one of: swe, deceptive, sysdesign, algo, multiturn
description: Brief description
difficulty: medium   # easy, medium, hard

prompt: |
  The task description goes here.
  Can be multi-line.

reference_solution: |
  def solution():
      # Reference implementation
      pass

test_cases:
  - input: "[1, 2, 3]"
    expected_output: "[3, 2, 1]"
    name: "basic_test"

scoring:
  auto_tests: 60          # % weight
  contradiction_flag: 25  # % weight
  reasoning_quality: 15   # % weight (human-scored 0–3)
```

## Generating Task Variants

Use the adversarial generator to create deliberately tricky variants:

```python
from xfail.harness.adversary import AdversaryGenerator
from xfail.harness.task import load_task

generator = AdversaryGenerator()
base_task = load_task("tasks/poc/deceptive_001.yaml")

# Create a deceptive variant
variant = generator.generate_deceptive_variant(base_task, variant_num=1)
```

## Report Output

Reports include:

1. **Executive summary** — top findings
2. **Model comparison** — pass rates and failure codes by model
3. **Failure mode analysis** — heatmap of codes × models
4. **Task results** — detailed logs with classifier output
5. **Taxonomy definitions** — reference for all 7 failure codes

Available in HTML and Markdown formats.

## Development

### Installing in Development Mode

```bash
pip install -e .
```

### Running Tests

```bash
# Currently uses real API calls—no mock testing
# See phase 6 in implementation plan
```

## API Keys

Required environment variables:

- `XAI_API_KEY` — xAI Grok API key
- `GEMINI_API_KEY` — Google Gemini API key

Copy `.env.example` to `.env` and fill in your keys.

## Design Notes

### Auto-Classification

Failure modes are classified using an LLM (Grok itself) that reads the prompt and output, then assigns one or more taxonomy codes. Human review is recommended for low-confidence predictions.

### Task Execution

- Uses simple `exec()` to run submitted code against test cases
- Captures all output, errors, and metadata
- No sandboxing yet (use with trusted inputs only in production)

### Multi-Turn Tasks

Each turn includes full conversation history + prior outputs. Constraints can be introduced in later turns to test context retention.

## Limitations & Future Work

- ❌ No code sandboxing (assumes trusted test environment)
- ❌ No async execution (runs sequentially)
- ❌ Limited to Python code (LLM flexibility may handle other languages)
- 🔜 Extend to other languages with language-specific test runners
- 🔜 Add custom scoring functions per task
- 🔜 Support for fine-grained prompt engineering (different system prompts per model)

## Contributing

Follow the code style in [.github/copilot-instructions.md](.github/copilot-instructions.md):
- Atomic commits (one thing per commit)
- Human-readable code, minimal comments
- No auto-generated documentation

## License

TBD
