# xFail — Model Autopsy Benchmark

![xFail banner](assets/X.Fail.png)

A focused evaluation harness built to expose the real failure modes of LLM code reasoning. This isn’t a pass/fail scoreboard; it’s a diagnostic layer for models that are pretending to understand requirements.

![version](https://img.shields.io/badge/version-v0.1.1-orange)

## Why xFail?

Benchmarks like HumanEval, MBPP, and SWE-Bench measure surface accuracy. xFail is designed to classify failure behavior and tie it to concrete model breakdowns.

Target audience:
- Human Data teams refining training sets
- Evaluation engineers exploring model weaknesses
- Researchers building more resilient code assistance

## Quick Start

### Setup

```bash
pip install -e .
cp .env.example .env
# Add API keys to .env
```

### Run the benchmark

```bash
xfail run --task-set poc
```

Run a specific model:

```bash
xfail run --models grok --task-set poc
```

Run a single task:

```bash
xfail run --task xfail/tasks/poc/deceptive_001.yaml
```

### Generate a report

```bash
xfail report --run-id <TIMESTAMP> --format html
```

Markdown output:

```bash
xfail report --run-id <TIMESTAMP> --format markdown
```

Both:

```bash
xfail report --run-id <TIMESTAMP> --format both
```

### Compare models

```bash
xfail diff --model-a grok --model-b gemini --run <TIMESTAMP>
```

## Failure Mode Taxonomy

Every result is tagged with one or more failure codes.

| Code | Name | Description |
|------|------|-------------|
| `SPEC-MIS` | Specification misread | Model implements a plausible but incorrect interpretation |
| `INV-LOSS` | Invariant loss | Model violates interacting constraints or invariants |
| `EDGE-OBO` | Edge case / off-by-one | Model handles the happy path but fails boundaries |
| `HALL-CON` | Hallucinated constraint | Model invents requirements that are not present |
| `ABS-FAIL` | Poor abstraction | Model overfits a specific case instead of generalizing |
| `BIZ-FRAME` | Business framing gap | Model fails when intent is expressed as an outcome rather than a spec |
| `CTX-DROP` | Context drop | Model loses constraints during multi-turn interactions |

## Project Structure

```
xfail/
├── models/          # API clients for Grok and Gemini
├── harness/         # task execution, scoring, and classification
├── reports/         # report generation logic
├── tasks/           # task definitions
│   └── poc/         # proof-of-concept tasks
├── cli.py           # command-line entrypoint
└── __init__.py

results/            # generated execution logs
reports/            # generated report artifacts
```

## Task Format

Tasks are defined in YAML.

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
      pass

test_cases:
  - input: "[1, 2, 3]"
    expected_output: "[3, 2, 1]"
    name: "basic_test"

scoring:
  auto_tests: 60
  contradiction_flag: 25
  reasoning_quality: 15
```

## Generating Task Variants

Use the adversarial generator to create tricky variants from a base task.

```python
from xfail.harness.adversary import AdversaryGenerator
from xfail.harness.task import load_task

generator = AdversaryGenerator()
base_task = load_task("tasks/poc/deceptive_001.yaml")
variant = generator.generate_deceptive_variant(base_task, variant_num=1)
```

## Report Output

Reports include:

1. Executive summary with core findings
2. Model comparison with pass rates and failure codes
3. Failure mode analysis showing code frequency per model
4. Task-level details with classifier output
5. Taxonomy definitions for all failure categories

Supported output formats: HTML and Markdown.

## Development

### Install in development mode

```bash
pip install -e .
```

### Running tests

```bash
# Tests currently use real API calls.
# Mocking is not yet implemented.
```

## API Keys

Required environment variables:

- `XAI_API_KEY` — xAI Grok API key
- `GEMINI_API_KEY` — Google Gemini API key

Copy `.env.example` to `.env` and fill in the keys.

## Design Notes

### Auto-classification

Failure mode classification is performed by an LLM analyzing prompt, output, and expected behavior, then assigning taxonomy codes. Low-confidence predictions should be validated manually.

### Task execution

The runner executes submitted code against test cases using `exec()`, captures output, errors, and metadata, and records the execution trace. There is no sandboxing yet; use only trusted inputs in production.

### Multi-turn tasks

Each turn includes full conversation state and prior outputs. This makes it possible to test whether the model retains constraints across interactions.

## Limitations & Future Work

- No code sandboxing yet
- Execution is sequential, not asynchronous
- Currently focused on Python tasks
- Future work: language-specific runners for additional languages
- Future work: richer scoring functions per task
- Future work: finer-grained prompt control per model

## Contributing

Follow the repo’s code style and commit habits:

- small, focused commits
- readable code
- minimal comments
- no generated documentation

## License

TBD
