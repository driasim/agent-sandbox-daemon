"""Subprocess sandbox runner with timeout and resource isolation."""

import sys
import os
import time
import tempfile
import subprocess
from pathlib import Path
from sandbox_daemon.models import ExecutionRequest, ExecutionResult
from sandbox_daemon.policy import SecurityPolicy


class SandboxRunner:
    """Executes untrusted agent scripts inside an isolated scratch workspace."""

    def __init__(self, python_binary: str = sys.executable):
        self.python_binary = python_binary

    def run(self, request: ExecutionRequest) -> ExecutionResult:
        # 1. Static security check
        violation = SecurityPolicy.validate_code(request.code, request.limits)
        if violation:
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=violation,
                duration_ms=0.0,
                timed_out=False,
                security_violation=violation,
            )

        start_time = time.perf_counter()

        # 2. Prepare isolated temporary scratchpad directory
        with tempfile.TemporaryDirectory(prefix="agent_sandbox_") as tmpdir:
            script_path = Path(tmpdir) / "main.py"
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(request.code)

            try:
                proc = subprocess.run(
                    [self.python_binary, str(script_path)],
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    timeout=request.limits.timeout_seconds,
                    env={"PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"},
                )
                duration_ms = (time.perf_counter() - start_time) * 1000

                stdout = proc.stdout[: request.limits.max_output_bytes]
                stderr = proc.stderr[: request.limits.max_output_bytes]

                return ExecutionResult(
                    success=(proc.returncode == 0),
                    exit_code=proc.returncode,
                    stdout=stdout,
                    stderr=stderr,
                    duration_ms=round(duration_ms, 2),
                    timed_out=False,
                )

            except subprocess.TimeoutExpired:
                duration_ms = (time.perf_counter() - start_time) * 1000
                return ExecutionResult(
                    success=False,
                    exit_code=-1,
                    stdout="",
                    stderr=f"Process timed out after {request.limits.timeout_seconds} seconds.",
                    duration_ms=round(duration_ms, 2),
                    timed_out=True,
                )
            except Exception as e:
                duration_ms = (time.perf_counter() - start_time) * 1000
                return ExecutionResult(
                    success=False,
                    exit_code=-1,
                    stdout="",
                    stderr=f"Execution error: {str(e)}",
                    duration_ms=round(duration_ms, 2),
                )
