import click
import os
from pathlib import Path
from dotenv import load_dotenv
from xfail.harness.task import load_task
from xfail.harness.runner import Runner
from xfail.harness.logger import Logger
from xfail.reports.generator import ReportGenerator


load_dotenv()


@click.group()
def cli():
    pass


@cli.command()
@click.option('--models', default='grok,gemini', help='Comma-separated list of models to run')
@click.option('--task-set', default=None, help='Task set to run (poc, swe, deceptive, etc.)')
@click.option('--task', default=None, help='Single task file to run')
@click.option('--output-dir', default='results', help='Output directory for results')
def run(models, task_set, task, output_dir):
    model_list = [m.strip() for m in models.split(',')]
    logger = Logger(output_dir)
    runner = Runner(logger=logger, use_classifier=True)
    
    task_files = []
    if task:
        task_files = [task]
    elif task_set:
        task_dir = Path(f'xfail/tasks/{task_set}')
        if task_dir.exists():
            task_files = list(task_dir.glob('*.yaml'))
        else:
            click.echo(f"Task set directory not found: {task_dir}")
            return
    else:
        task_dir = Path('xfail/tasks/poc')
        if task_dir.exists():
            task_files = list(task_dir.glob('*.yaml'))
    
    if not task_files:
        click.echo("No tasks found to run")
        return
    
    click.echo(f"Running {len(task_files)} tasks on {len(model_list)} models")
    
    all_logs = []
    for task_file in task_files:
        try:
            task = load_task(str(task_file))
            click.echo(f"Running task: {task.task_id}")
            
            for model in model_list:
                click.echo(f"  - {model}...", nl=False)
                log = runner.run_task(task, model)
                all_logs.append(log)
                logger.log_execution(log)
                
                status = "✓" if log.test_results['pass_rate'] == 1.0 else "✗"
                click.echo(f" {status}")
        except Exception as e:
            click.echo(f"Error running task {task_file}: {e}")
    
    click.echo(f"\nCompleted: {len(all_logs)} executions logged")


@cli.command()
@click.option('--run-id', required=True, help='Run ID to generate report for')
@click.option('--format', type=click.Choice(['html', 'markdown', 'both']), default='html')
@click.option('--output', default='reports', help='Output directory')
@click.option('--input-dir', default='results', help='Results directory')
def report(run_id, format, output, input_dir):
    logger = Logger(input_dir)
    
    try:
        logs = logger.load_run(run_id)
    except Exception as e:
        click.echo(f"Error loading run {run_id}: {e}")
        return
    
    if not logs:
        click.echo(f"No results found for run {run_id}")
        return
    
    generator = ReportGenerator(logs, run_id)
    output_dir = Path(output) / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if format in ['html', 'both']:
        html_path = output_dir / 'report.html'
        generator.generate_html(str(html_path))
        click.echo(f"Generated HTML report: {html_path}")
    
    if format in ['markdown', 'both']:
        md_path = output_dir / 'report.md'
        generator.generate_markdown(str(md_path))
        click.echo(f"Generated Markdown report: {md_path}")


@cli.command()
@click.option('--model-a', default='grok', help='First model')
@click.option('--model-b', default='gemini', help='Second model')
@click.option('--run', required=True, help='Run ID to diff')
@click.option('--input-dir', default='results', help='Results directory')
def diff(model_a, model_b, run, input_dir):
    logger = Logger(input_dir)
    
    try:
        logs = logger.load_run(run)
    except Exception as e:
        click.echo(f"Error loading run {run}: {e}")
        return
    
    logs_by_model = {}
    for log in logs:
        if log.model not in logs_by_model:
            logs_by_model[log.model] = {}
        logs_by_model[log.model][log.task_id] = log
    
    model_a_logs = logs_by_model.get(model_a, {})
    model_b_logs = logs_by_model.get(model_b, {})
    
    all_tasks = set(model_a_logs.keys()) | set(model_b_logs.keys())
    
    click.echo(f"\nFailure Pattern Comparison: {model_a} vs {model_b}")
    click.echo("=" * 80)
    
    for task_id in sorted(all_tasks):
        log_a = model_a_logs.get(task_id)
        log_b = model_b_logs.get(task_id)
        
        click.echo(f"\nTask: {task_id}")
        
        if log_a:
            codes_a = log_a.classifier_output.get('codes', []) if log_a.classifier_output else []
            pass_a = log_a.test_results.get('pass_rate', 0) == 1.0
            click.echo(f"  {model_a}: {'✓ PASS' if pass_a else '✗ FAIL'} - Codes: {codes_a}")
        else:
            click.echo(f"  {model_a}: NOT RUN")
        
        if log_b:
            codes_b = log_b.classifier_output.get('codes', []) if log_b.classifier_output else []
            pass_b = log_b.test_results.get('pass_rate', 0) == 1.0
            click.echo(f"  {model_b}: {'✓ PASS' if pass_b else '✗ FAIL'} - Codes: {codes_b}")
        else:
            click.echo(f"  {model_b}: NOT RUN")


def main():
    cli()


if __name__ == '__main__':
    main()
