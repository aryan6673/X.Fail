from dataclasses import dataclass, field
from typing import Optional
import yaml
from pathlib import Path


@dataclass
class ScoringWeights:
    auto_tests: float = 60
    contradiction_flag: float = 25
    reasoning_quality: float = 15

    def validate(self):
        total = self.auto_tests + self.contradiction_flag + self.reasoning_quality
        if abs(total - 100) > 0.01:
            raise ValueError(f"Scoring weights must sum to 100, got {total}")


@dataclass
class TestCase:
    input: str
    expected_output: str
    name: Optional[str] = None


@dataclass
class Task:
    task_id: str
    category: str
    prompt: str
    reference_solution: str
    test_cases: list[TestCase] = field(default_factory=list)
    scoring: ScoringWeights = field(default_factory=ScoringWeights)
    description: Optional[str] = None
    difficulty: str = "medium"

    def validate(self):
        if not self.task_id:
            raise ValueError("task_id cannot be empty")
        if self.category not in ["swe", "deceptive", "sysdesign", "algo", "multiturn"]:
            raise ValueError(f"Invalid category: {self.category}")
        if not self.prompt:
            raise ValueError("prompt cannot be empty")
        if not self.reference_solution:
            raise ValueError("reference_solution cannot be empty")
        self.scoring.validate()


@dataclass
class Turn:
    user_input: str
    constraints: list[str] = field(default_factory=list)
    expected_behavior: Optional[str] = None


@dataclass
class MultiTurnTask(Task):
    turns: list[Turn] = field(default_factory=list)

    def validate(self):
        super().validate()
        if not self.turns:
            raise ValueError("MultiTurn tasks must have at least one turn")


def load_task(file_path: str) -> Task:
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    
    if data.get('category') == 'multiturn':
        task = MultiTurnTask(
            task_id=data['task_id'],
            category=data['category'],
            prompt=data.get('prompt', ''),
            reference_solution=data.get('reference_solution', ''),
            description=data.get('description'),
            difficulty=data.get('difficulty', 'medium'),
            scoring=ScoringWeights(**data.get('scoring', {})),
            turns=[Turn(**turn) for turn in data.get('turns', [])]
        )
    else:
        task = Task(
            task_id=data['task_id'],
            category=data['category'],
            prompt=data['prompt'],
            reference_solution=data['reference_solution'],
            description=data.get('description'),
            difficulty=data.get('difficulty', 'medium'),
            scoring=ScoringWeights(**data.get('scoring', {})),
            test_cases=[TestCase(**tc) for tc in data.get('test_cases', [])]
        )
    
    task.validate()
    return task
