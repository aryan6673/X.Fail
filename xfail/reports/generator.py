import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from jinja2 import Template
from xfail.harness.classifier import FAILURE_CODES
from xfail.harness.logger import ExecutionLog


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>xFail Report - {{ run_id }}</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; }
        h1 { color: #333; }
        h2 { color: #666; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        .section { margin-bottom: 40px; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #f5f5f5; font-weight: bold; }
        .pass { background-color: #e8f5e9; }
        .fail { background-color: #ffebee; }
        .example { background-color: #f9f9f9; border-left: 4px solid #2196F3; padding: 15px; margin: 15px 0; }
        .code { font-family: monospace; background-color: #f4f4f4; padding: 2px 6px; }
        .taxonomy { margin: 10px 0; padding: 10px; background-color: #fff3cd; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>xFail Model Autopsy Report</h1>
    <p><strong>Run ID:</strong> {{ run_id }}</p>
    <p><strong>Generated:</strong> {{ timestamp }}</p>
    
    <div class="section">
        <h2>Executive Summary</h2>
        <p>{{ summary }}</p>
    </div>
    
    <div class="section">
        <h2>Model Comparison</h2>
        <table>
            <tr>
                <th>Model</th>
                <th>Tasks Run</th>
                <th>Pass Rate</th>
                <th>Failure Codes</th>
            </tr>
            {% for model_stats in model_statistics %}
            <tr>
                <td>{{ model_stats.model }}</td>
                <td>{{ model_stats.task_count }}</td>
                <td>{{ "%.1f"|format(model_stats.pass_rate * 100) }}%</td>
                <td>{{ model_stats.codes|join(", ") }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    
    <div class="section">
        <h2>Failure Mode Analysis</h2>
        <table>
            <tr>
                <th>Code</th>
                <th>Name</th>
                <th>Grok Count</th>
                <th>Gemini Count</th>
            </tr>
            {% for code, name in failure_codes.items() %}
            <tr>
                <td><code>{{ code }}</code></td>
                <td>{{ name }}</td>
                <td>{{ code_counts.get(code, {}).get('grok', 0) }}</td>
                <td>{{ code_counts.get(code, {}).get('gemini', 0) }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    
    <div class="section">
        <h2>Task Results</h2>
        {% for log in logs %}
        <div class="example">
            <h3>{{ log.task_id }} ({{ log.model }})</h3>
            <p><strong>Status:</strong> 
                {% if log.error %}
                    <span class="fail">ERROR: {{ log.error }}</span>
                {% else %}
                    <span class="{% if log.test_results.pass_rate == 1.0 %}pass{% else %}fail{% endif %}">
                        {{ "%.0f"|format(log.test_results.pass_rate * 100) }}% tests passed
                    </span>
                {% endif %}
            </p>
            {% if log.classifier_output %}
            <p><strong>Failure Codes:</strong> 
                {% if log.classifier_output.codes %}
                    {{ log.classifier_output.codes|join(", ") }} (confidence: {{ "%.1f"|format(log.classifier_output.confidence * 100) }}%)
                {% else %}
                    None
                {% endif %}
            </p>
            <p><strong>Analysis:</strong> {{ log.classifier_output.explanation }}</p>
            {% endif %}
        </div>
        {% endfor %}
    </div>
    
    <div class="section">
        <h2>Failure Taxonomy</h2>
        {% for code, name in failure_codes.items() %}
        <div class="taxonomy">
            <strong>{{ code }}: {{ name }}</strong>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

MARKDOWN_TEMPLATE = """# xFail Model Autopsy Report

**Run ID:** {{ run_id }}  
**Generated:** {{ timestamp }}

## Executive Summary

{{ summary }}

## Model Comparison

| Model | Tasks | Pass Rate | Failure Codes |
|-------|-------|-----------|---------------|
{% for model_stats in model_statistics %}
| {{ model_stats.model }} | {{ model_stats.task_count }} | {{ "%.1f"|format(model_stats.pass_rate * 100) }}% | {{ model_stats.codes|join(", ") }} |
{% endfor %}

## Failure Mode Analysis

| Code | Name | Grok | Gemini |
|------|------|------|--------|
{% for code, name in failure_codes.items() %}
| `{{ code }}` | {{ name }} | {{ code_counts.get(code, {}).get('grok', 0) }} | {{ code_counts.get(code, {}).get('gemini', 0) }} |
{% endfor %}

## Task Results

{% for log in logs %}
### {{ log.task_id }} ({{ log.model }})

**Status:** 
{% if log.error %}
❌ ERROR: {{ log.error }}
{% else %}
{{ "%.0f"|format(log.test_results.pass_rate * 100) }}% tests passed
{% endif %}

{% if log.classifier_output %}
**Failure Codes:** 
{% if log.classifier_output.codes %}
{{ log.classifier_output.codes|join(", ") }} (confidence: {{ "%.1f"|format(log.classifier_output.confidence * 100) }}%)
{% else %}
None
{% endif %}

**Analysis:** {{ log.classifier_output.explanation }}
{% endif %}

---

{% endfor %}

## Failure Taxonomy

{% for code, name in failure_codes.items() %}
- **{{ code }}**: {{ name }}
{% endfor %}
"""


class ReportGenerator:
    def __init__(self, logs: list[ExecutionLog], run_id: str):
        self.logs = logs
        self.run_id = run_id
    
    def generate_html(self, output_path: str) -> str:
        template = Template(HTML_TEMPLATE)
        html = template.render(
            run_id=self.run_id,
            timestamp=datetime.now().isoformat(),
            summary=self._generate_summary(),
            model_statistics=self._compute_model_statistics(),
            failure_codes=FAILURE_CODES,
            code_counts=self._count_failure_codes(),
            logs=self.logs,
        )
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html)
        
        return str(output_file)
    
    def generate_markdown(self, output_path: str) -> str:
        template = Template(MARKDOWN_TEMPLATE)
        markdown = template.render(
            run_id=self.run_id,
            timestamp=datetime.now().isoformat(),
            summary=self._generate_summary(),
            model_statistics=self._compute_model_statistics(),
            failure_codes=FAILURE_CODES,
            code_counts=self._count_failure_codes(),
            logs=self.logs,
        )
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(markdown)
        
        return str(output_file)
    
    def _generate_summary(self) -> str:
        if not self.logs:
            return "No results available."
        
        total_tasks = len(self.logs)
        passed_tasks = sum(1 for log in self.logs if log.test_results.get('pass_rate', 0) == 1.0)
        
        models = set(log.model for log in self.logs)
        
        summary = f"Executed {total_tasks} tasks across {len(models)} models. "
        summary += f"{passed_tasks} tasks fully passed. "
        
        all_codes = set()
        for log in self.logs:
            if log.classifier_output and log.classifier_output.get('codes'):
                all_codes.update(log.classifier_output['codes'])
        
        if all_codes:
            summary += f"Identified {len(all_codes)} distinct failure modes."
        
        return summary
    
    def _compute_model_statistics(self) -> list[dict]:
        model_stats = {}
        
        for log in self.logs:
            if log.model not in model_stats:
                model_stats[log.model] = {
                    "model": log.model,
                    "task_count": 0,
                    "passed": 0,
                    "codes": set(),
                }
            
            model_stats[log.model]["task_count"] += 1
            if log.test_results.get('pass_rate', 0) == 1.0:
                model_stats[log.model]["passed"] += 1
            
            if log.classifier_output and log.classifier_output.get('codes'):
                model_stats[log.model]["codes"].update(log.classifier_output['codes'])
        
        for stat in model_stats.values():
            stat["pass_rate"] = stat["passed"] / stat["task_count"] if stat["task_count"] > 0 else 0
            stat["codes"] = sorted(list(stat["codes"]))
        
        return sorted(model_stats.values(), key=lambda x: x["model"])
    
    def _count_failure_codes(self) -> dict:
        counts = {}
        
        for code in FAILURE_CODES.keys():
            counts[code] = {"grok": 0, "gemini": 0}
        
        for log in self.logs:
            if log.classifier_output and log.classifier_output.get('codes'):
                for code in log.classifier_output['codes']:
                    if code in counts:
                        if log.model == "grok":
                            counts[code]["grok"] += 1
                        elif log.model == "gemini":
                            counts[code]["gemini"] += 1
        
        return counts
