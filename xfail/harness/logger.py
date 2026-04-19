import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional
from datetime import datetime


@dataclass
class ExecutionLog:
    task_id: str
    model: str
    timestamp: str
    prompt: str
    output: str
    stop_reason: str
    test_results: dict
    classifier_output: Optional[dict] = None
    reasoning_quality_score: Optional[float] = None
    usage: Optional[dict] = None
    error: Optional[str] = None


class Logger:
    def __init__(self, output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def log_execution(self, log: ExecutionLog) -> str:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_dir = self.output_dir / run_id
        task_dir.mkdir(exist_ok=True)
        
        log_file = task_dir / f"{log.task_id}_{log.model}.json"
        
        with open(log_file, 'w') as f:
            json.dump(asdict(log), f, indent=2, default=str)
        
        return str(log_file)
    
    def load_run(self, run_id: str) -> list[ExecutionLog]:
        run_dir = self.output_dir / run_id
        logs = []
        
        for log_file in run_dir.glob("*.json"):
            with open(log_file, 'r') as f:
                data = json.load(f)
                logs.append(ExecutionLog(**data))
        
        return logs
