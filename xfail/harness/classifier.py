from typing import Optional
from xfail.models.xai_client import XAIClient


FAILURE_CODES = {
    "SPEC-MIS": "Specification misread",
    "INV-LOSS": "Invariant loss",
    "EDGE-OBO": "Edge case / off-by-one",
    "HALL-CON": "Hallucinated constraint",
    "ABS-FAIL": "Poor abstraction",
    "BIZ-FRAME": "Business framing gap",
    "CTX-DROP": "Context drop",
}

CLASSIFICATION_PROMPT = """Analyze the following task prompt and model output to identify failure modes.

Task Prompt:
{prompt}

Model Output:
{output}

Based on these failure codes, classify the model's response:
- SPEC-MIS: Implements plausible but wrong interpretation
- INV-LOSS: Fails to maintain 2+ interacting constraints simultaneously
- EDGE-OBO: Passes happy path, fails boundary conditions
- HALL-CON: Invents a requirement not present in the spec
- ABS-FAIL: Solves the specific case, doesn't generalize as required
- BIZ-FRAME: Fails when requirements are outcomes, not technical specs
- CTX-DROP: Loses earlier constraints in multi-turn sessions

Respond with a JSON object containing:
{{
    "codes": ["CODE1", "CODE2"],
    "confidence": 0.85,
    "explanation": "Brief explanation of why these codes apply"
}}

If the output appears correct, respond with codes: [] and confidence: 1.0."""


class Classifier:
    def __init__(self):
        self.client = XAIClient()
    
    def classify(self, prompt: str, output: str) -> dict:
        messages = [
            {
                "role": "user",
                "content": CLASSIFICATION_PROMPT.format(prompt=prompt, output=output)
            }
        ]
        
        response = self.client.call(messages, temperature=0.3, max_tokens=500)
        
        try:
            import json
            result = json.loads(response["content"])
            return {
                "codes": result.get("codes", []),
                "confidence": result.get("confidence", 0.0),
                "explanation": result.get("explanation", ""),
            }
        except (json.JSONDecodeError, KeyError) as e:
            return {
                "codes": [],
                "confidence": 0.0,
                "explanation": f"Failed to parse classifier output: {str(e)}",
                "raw_output": response["content"],
            }
