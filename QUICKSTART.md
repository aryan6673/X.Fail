# xFail Quick Start Guide

## Installation

```bash
# Clone and enter directory
cd xfail

# Install dependencies
pip install -e .

# Copy environment file
cp .env.example .env
# Edit .env and add your API keys:
#   XAI_API_KEY=your_xai_key
#   GEMINI_API_KEY=your_gemini_key
```

## Running the Benchmark

### Run proof-of-concept (3 tasks × 2 models)
```bash
xfail run --task-set poc
```

### Run against a single model
```bash
xfail run --models grok --task-set poc
```

### Run a specific task
```bash
xfail run --task xfail/tasks/poc/deceptive_001.yaml --models grok,gemini
```

## Generating Reports

After running, reports are saved to `results/`. Generate an analysis:

```bash
# Find your run timestamp
ls results/

# Generate HTML report
xfail report --run-id 20260420_120000 --format html

# Generate Markdown report
xfail report --run-id 20260420_120000 --format markdown

# Both
xfail report --run-id 20260420_120000 --format both
```

Reports appear in `reports/<run-id>/`

## Comparing Models

Side-by-side failure pattern comparison:

```bash
xfail diff --model-a grok --model-b gemini --run 20260420_120000
```

Shows which failure codes (SPEC-MIS, INV-LOSS, etc.) each model encountered.

## Project Structure

```
xfail/
├── models/          # API clients
│   ├── xai_client.py
│   └── gemini_client.py
├── harness/         # Core execution
│   ├── task.py      # Task schema + loader
│   ├── runner.py    # Task execution
│   ├── classifier.py  # Failure mode auto-classification
│   ├── adversary.py # Variant generator
│   └── logger.py    # Result capture
├── reports/         # Report generation
│   └── generator.py
├── tasks/           # Task definitions (YAML)
│   └── poc/         # 3 proof-of-concept tasks
└── cli.py           # Command-line interface

results/            # Execution logs (auto-created)
reports/            # Generated reports (auto-created)
```

## Key Concepts

### Task Categories
- **deceptive**: Spec contradictions, misleading examples
- **sysdesign**: Edge cases that break naive implementations
- **algo**: Performance requirements hidden in prose
- **swe**: Real ambiguous GitHub issues
- **multiturn**: Multi-turn constraint conflicts

### Failure Mode Taxonomy
| Code | Meaning |
|------|---------|
| SPEC-MIS | Wrong interpretation of the spec |
| INV-LOSS | Failed to maintain multiple constraints |
| EDGE-OBO | Off-by-one or boundary condition failure |
| HALL-CON | Made up a requirement not in the spec |
| ABS-FAIL | Solved specific case, doesn't generalize |
| BIZ-FRAME | Misunderstood outcome vs. technical requirement |
| CTX-DROP | Lost context in multi-turn task |

### Understanding Results

Each execution produces a JSON log with:
- Model output
- Test pass/fail results
- Auto-classified failure codes + confidence
- Token usage metadata

Reports aggregate these into:
1. Executive summary
2. Per-model failure patterns
3. Cross-model findings (universal vs. model-specific failures)
4. Annotated examples showing what went wrong

## For Development

### Adding New Tasks

Create a YAML file in `xfail/tasks/<category>/`:

```yaml
task_id: my_task_001
category: deceptive
description: Brief description
difficulty: medium

prompt: |
  The task description...

reference_solution: |
  def my_function():
      pass

test_cases:
  - input: "args"
    expected_output: "result"
    name: "test_name"

scoring:
  auto_tests: 60
  contradiction_flag: 25
  reasoning_quality: 15
```

Then load and run with:
```bash
xfail run --task xfail/tasks/my_category/my_task_001.yaml
```

### Generating Task Variants

```python
from xfail.harness.task import load_task
from xfail.harness.adversary import AdversaryGenerator

task = load_task("xfail/tasks/poc/deceptive_001.yaml")
generator = AdversaryGenerator()

# Creates adversarial variants
variant = generator.generate_deceptive_variant(task, variant_num=1)
```

## Troubleshooting

### "API key not found"
Ensure `.env` has `XAI_API_KEY` and/or `GEMINI_API_KEY` set.

### "No tasks found"
Run from the xfail root directory. Tasks are in `xfail/tasks/poc/`.

### Reports not generating
Check that results are in `results/` by running:
```bash
ls results/
```

Pick a timestamp and use it with `xfail report --run-id <timestamp>`.

## Next Steps

1. Set up `.env` with API keys
2. Run the POC: `xfail run --task-set poc`
3. Generate a report: `xfail report --run-id <timestamp>`
4. Compare models: `xfail diff --model-a grok --model-b gemini --run <timestamp>`

The report shows per-model failure patterns — this is the insight that drives training data design.
