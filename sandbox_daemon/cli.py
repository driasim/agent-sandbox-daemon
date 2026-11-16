"""CLI entrypoint for running sandboxed agent code."""

import argparse
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from sandbox_daemon.models import ExecutionRequest, ResourceLimits
from sandbox_daemon.runner import SandboxRunner

console = Console()


def main():
    parser = argparse.ArgumentParser(description="Secure code execution sandbox for LLM agents")
    parser.add_argument("--code", "-c", help="Python code string to execute")
    parser.add_argument("--file", "-f", help="Path to Python file to execute")
    parser.add_argument("--timeout", "-t", type=float, default=5.0, help="Max execution timeout in seconds")

    args = parser.parse_args()

    if not args.code and not args.file:
        console.print("[red]Error: Must provide either --code or --file[/red]")
        sys.exit(1)

    code = args.code
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            code = f.read()

    runner = SandboxRunner()
    limits = ResourceLimits(timeout_seconds=args.timeout)
    req = ExecutionRequest(code=code, limits=limits)

    console.print("[bold blue]Executing untrusted code in sandbox...[/bold blue]")
    res = runner.run(req)

    status_color = "green" if res.success else "red"
    console.print(Panel.fit(
        f"Status: [{status_color}]{'SUCCESS' if res.success else 'FAILED'}[/{status_color}]\n"
        f"Exit Code: {res.exit_code} | Duration: {res.duration_ms}ms | Timed Out: {res.timed_out}",
        title="Execution Summary",
    ))

    if res.stdout:
        console.print(Panel(res.stdout, title="STDOUT", style="green"))
    if res.stderr:
        console.print(Panel(res.stderr, title="STDERR / Violations", style="red"))

    sys.exit(0 if res.success else 1)


if __name__ == "__main__":
    main()
