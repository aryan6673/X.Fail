#!/usr/bin/env python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from xfail.harness.task import load_task
from xfail.harness.adversary import AdversaryGenerator

print("Testing xFail core components...")

try:
    print("\n1. Loading POC tasks...")
    task_dir = Path("xfail/tasks/poc")
    
    for task_file in sorted(task_dir.glob("*.yaml")):
        task = load_task(str(task_file))
        print(f"   ✓ Loaded {task.task_id} ({task.category})")
        print(f"     - Test cases: {len(task.test_cases)}")
        print(f"     - Difficulty: {task.difficulty}")
    
    print("\n2. Testing adversarial generator...")
    base_task = load_task("xfail/tasks/poc/deceptive_001.yaml")
    
    generator = AdversaryGenerator()
    variant = generator.generate_deceptive_variant(base_task, variant_num=1)
    print(f"   ✓ Generated variant: {variant.task_id}")
    print(f"     - Category: {variant.category}")
    print(f"     - Description: {variant.description}")
    
    print("\n3. Validating task schema...")
    test_task = load_task("xfail/tasks/poc/algo_001.yaml")
    test_task.validate()
    print(f"   ✓ Task validation passed")
    
    print("\n All core components working!")
    
except Exception as e:
    print(f"\n Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
