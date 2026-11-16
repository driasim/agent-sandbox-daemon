"""Runnable example demonstrating agent sandbox security and execution."""

from sandbox_daemon.models import ExecutionRequest, ResourceLimits
from sandbox_daemon.runner import SandboxRunner
from rich.console import Console

console = Console()

def run():
    runner = SandboxRunner()

    console.print("\n[bold green]1. Running Safe Agent Data Analysis Code:[/bold green]")
    safe_code = """
data = [12.5, 45.2, 78.9, 10.4, 99.1]
mean = sum(data) / len(data)
print(f"Calculated Mean: {mean:.2f}")
"""
    res1 = runner.run(ExecutionRequest(code=safe_code))
    console.print(f"Success: {res1.success} | Output: {res1.stdout.strip()} ({res1.duration_ms}ms)")

    console.print("\n[bold red]2. Testing Security Boundary (Agent attempting unauthorized socket/network access):[/bold red]")
    unsafe_code = """
import socket
s = socket.socket()
print("Connected")
"""
    res2 = runner.run(ExecutionRequest(code=unsafe_code))
    console.print(f"Blocked: {not res2.success} | Error: {res2.stderr}")

if __name__ == "__main__":
    run()
