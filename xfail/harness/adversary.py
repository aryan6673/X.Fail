from xfail.harness.task import Task
from typing import Optional


class AdversaryGenerator:
    def generate_deceptive_variant(self, base_task: Task, variant_num: int = 1) -> Task:
        new_id = f"{base_task.task_id}_deceptive_v{variant_num}"
        
        modifications = [
            self._swap_ascending_descending,
            self._inject_contradictory_example,
            self._misleading_variable_names,
            self._false_assumption_comment,
        ]
        
        modification = modifications[(variant_num - 1) % len(modifications)]
        new_prompt = modification(base_task.prompt)
        
        new_task = Task(
            task_id=new_id,
            category="deceptive",
            prompt=new_prompt,
            reference_solution=base_task.reference_solution,
            test_cases=base_task.test_cases,
            scoring=base_task.scoring,
            description=f"Deceptive variant: {base_task.description}",
        )
        return new_task
    
    def generate_sysdesign_variant(self, base_task: Task, variant_num: int = 1) -> Task:
        new_id = f"{base_task.task_id}_sysdesign_v{variant_num}"
        
        modifications = [
            self._add_edge_case_requirement,
            self._hidden_performance_constraint,
            self._adversarial_input_pattern,
        ]
        
        modification = modifications[(variant_num - 1) % len(modifications)]
        new_prompt = modification(base_task.prompt)
        
        new_task = Task(
            task_id=new_id,
            category="sysdesign",
            prompt=new_prompt,
            reference_solution=base_task.reference_solution,
            test_cases=base_task.test_cases,
            scoring=base_task.scoring,
            description=f"SysDesign variant: {base_task.description}",
        )
        return new_task
    
    def generate_algo_variant(self, base_task: Task, variant_num: int = 1) -> Task:
        new_id = f"{base_task.task_id}_algo_v{variant_num}"
        
        modifications = [
            self._hidden_complexity_requirement,
            self._performance_only_in_prose,
        ]
        
        modification = modifications[(variant_num - 1) % len(modifications)]
        new_prompt = modification(base_task.prompt)
        
        new_task = Task(
            task_id=new_id,
            category="algo",
            prompt=new_prompt,
            reference_solution=base_task.reference_solution,
            test_cases=base_task.test_cases,
            scoring=base_task.scoring,
            description=f"Algo variant: {base_task.description}",
        )
        return new_task
    
    def _swap_ascending_descending(self, prompt: str) -> str:
        return prompt.replace("ascending", "<ascending>").replace("descending", "ascending").replace("<ascending>", "descending")
    
    def _inject_contradictory_example(self, prompt: str) -> str:
        lines = prompt.split('\n')
        if len(lines) > 2:
            lines.insert(2, "Note: Despite the above, examples show opposite behavior for some cases.")
        return '\n'.join(lines)
    
    def _misleading_variable_names(self, prompt: str) -> str:
        replacements = [
            ("max_value", "min_threshold"),
            ("count", "total"),
            ("increment", "decrement"),
        ]
        result = prompt
        for old, new in replacements:
            if old in result:
                result = result.replace(old, new)
                break
        return result
    
    def _false_assumption_comment(self, prompt: str) -> str:
        lines = prompt.split('\n')
        for i, line in enumerate(lines):
            if '#' in line:
                lines.insert(i + 1, "# Note: Assumes input is always positive (incorrect assumption)")
                break
        return '\n'.join(lines)
    
    def _add_edge_case_requirement(self, prompt: str) -> str:
        return prompt + "\n\nEdge case: Must handle zero-length inputs without exceeding memory limits."
    
    def _hidden_performance_constraint(self, prompt: str) -> str:
        return prompt + "\n\nThis must complete in <100ms for competitive scenarios."
    
    def _adversarial_input_pattern(self, prompt: str) -> str:
        return prompt + "\n\nMust gracefully handle adversarial input patterns (e.g., all duplicates, reverse sorted)."
    
    def _hidden_complexity_requirement(self, prompt: str) -> str:
        return prompt + "\n\nNote: Brute force O(n²) solutions will not pass performance validation on large inputs."
    
    def _performance_only_in_prose(self, prompt: str) -> str:
        return prompt + "\n\nThe business case requires sub-linear scaling for 1M+ element datasets."
