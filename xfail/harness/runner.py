import subprocess
from pathlib import Path
from typing import Optional
from xfail.harness.task import Task
from xfail.harness.logger import Logger, ExecutionLog
from xfail.harness.classifier import Classifier
from xfail.models.xai_client import XAIClient
from xfail.models.gemini_client import GeminiClient


class Runner:
    def __init__(self, logger: Optional[Logger] = None, use_classifier: bool = True):
        self.logger = logger or Logger()
        self.use_classifier = use_classifier
        self.classifier = Classifier() if use_classifier else None
    
    def _get_model_client(self, model: str):
        if model == "grok":
            return XAIClient()
        elif model == "gemini":
            return GeminiClient()
        else:
            raise ValueError(f"Unknown model: {model}")
    
    def _run_tests(self, code: str, test_cases: list) -> dict:
        results = {}
        passed = 0
        
        for test in test_cases:
            try:
                local_vars = {}
                exec(code, {}, local_vars)
                
                for func_name in local_vars:
                    if not func_name.startswith('_'):
                        func = local_vars[func_name]
                        if callable(func):
                            test_input = eval(test.input)
                            expected = eval(test.expected_output)
                            actual = func(*test_input) if isinstance(test_input, tuple) else func(test_input)
                            
                            test_name = test.name or f"test_{len(results)}"
                            results[test_name] = {
                                "passed": actual == expected,
                                "expected": str(expected),
                                "actual": str(actual),
                            }
                            if actual == expected:
                                passed += 1
                            break
            except Exception as e:
                test_name = test.name or f"test_{len(results)}"
                results[test_name] = {
                    "passed": False,
                    "error": str(e),
                }
        
        total = len(test_cases) if test_cases else 1
        return {
            "passed": passed,
            "total": total,
            "pass_rate": (passed / total) if total > 0 else 0.0,
            "details": results,
        }
    
    def run_task(self, task: Task, model: str) -> ExecutionLog:
        client = self._get_model_client(model)
        
        messages = [{"role": "user", "content": task.prompt}]
        
        try:
            response = client.call(messages, temperature=0.7, max_tokens=4096)
            output = response["content"]
            
            test_results = self._run_tests(output, task.test_cases)
            
            classifier_output = None
            if self.use_classifier:
                classifier_output = self.classifier.classify(task.prompt, output)
            
            log = ExecutionLog(
                task_id=task.task_id,
                model=model,
                timestamp=__import__('datetime').datetime.now().isoformat(),
                prompt=task.prompt,
                output=output,
                stop_reason=response.get("stop_reason", "unknown"),
                test_results=test_results,
                classifier_output=classifier_output,
                usage=response.get("usage"),
                error=None,
            )
        except Exception as e:
            log = ExecutionLog(
                task_id=task.task_id,
                model=model,
                timestamp=__import__('datetime').datetime.now().isoformat(),
                prompt=task.prompt,
                output="",
                stop_reason="error",
                test_results={"passed": 0, "total": 0, "pass_rate": 0.0, "details": {}},
                classifier_output=None,
                usage=None,
                error=str(e),
            )
        
        return log
