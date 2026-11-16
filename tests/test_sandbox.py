"""Unit tests for agent-sandbox-daemon."""

from sandbox_daemon.models import ExecutionRequest, ResourceLimits
from sandbox_daemon.runner import SandboxRunner


def test_safe_execution_succeeds():
    runner = SandboxRunner()
    code = "print(sum([1, 2, 3, 4, 5]))"
    req = ExecutionRequest(code=code)
    res = runner.run(req)

    assert res.success is True
    assert res.exit_code == 0
    assert "15" in res.stdout
    assert res.security_violation is None


def test_security_blocks_subprocess():
    runner = SandboxRunner()
    code = "import subprocess\nsubprocess.run(['ls'])"
    req = ExecutionRequest(code=code)
    res = runner.run(req)

    assert res.success is False
    assert res.security_violation is not None
    assert "forbidden module 'subprocess'" in res.stderr


def test_security_blocks_socket():
    runner = SandboxRunner()
    code = "import socket\ns = socket.socket()"
    req = ExecutionRequest(code=code)
    res = runner.run(req)

    assert res.success is False
    assert "forbidden module 'socket'" in res.stderr


def test_timeout_enforcement():
    runner = SandboxRunner()
    code = "import time\ntime.sleep(2.0)\nprint('done')"
    limits = ResourceLimits(timeout_seconds=0.5)
    req = ExecutionRequest(code=code, limits=limits)
    res = runner.run(req)

    assert res.success is False
    assert res.timed_out is True
