# `agent-sandbox-daemon` 🛡️

[![CI](https://github.com/driasim/agent-sandbox-daemon/actions/workflows/ci.yml/badge.svg)](https://github.com/driasim/agent-sandbox-daemon/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Lightweight, secure code execution sandbox and process boundary for LLM agents.**

When your AI agent generates Python code to analyze data, plot charts, or calculate metrics, running it with `eval()` or bare `subprocess.run()` is a severe security vulnerability.

`agent-sandbox-daemon` provides a turnkey execution sandbox with:
1. **Static AST Analysis:** Blocks dangerous imports (`subprocess`, `socket`, `ctypes`, `shutil`) before execution even begins.
2. **Subprocess Boundary:** Runs scripts in ephemeral, isolated temporary working directories.
3. **Strict Timeout Enforcement:** Automatically kills infinite loops or stalling code.
4. **Byte-Level Output Truncation:** Prevents context window overflows from runaway print statements.

---

## ⚡ Quickstart

### Installation

```bash
git clone https://github.com/driasim/agent-sandbox-daemon.git
cd agent-sandbox-daemon
pip install -e .
```

### CLI Usage

Execute untrusted code safely from the terminal:

```bash
agent-sandbox run --code "print(sum(range(100)))"
```

With timeout limit:

```bash
agent-sandbox run --code "import time; time.sleep(10)" --timeout 2.0
```

---

## 🐍 Python SDK Usage

```python
from sandbox_daemon.models import ExecutionRequest, ResourceLimits
from sandbox_daemon.runner import SandboxRunner

runner = SandboxRunner()

# Safe Code Execution
request = ExecutionRequest(
    code="""
data = [10, 20, 30]
print(f"Total: {sum(data)}")
""",
    limits=ResourceLimits(timeout_seconds=3.0)
)

result = runner.run(request)
print("Output:", result.stdout)
print("Duration:", result.duration_ms, "ms")

# Unsafe Code Execution (Automatically Blocked)
unsafe_request = ExecutionRequest(code="import socket; s = socket.socket()")
blocked_result = runner.run(unsafe_request)
print("Blocked:", blocked_result.security_violation)
```

---

## 🧪 Running Tests

```bash
pytest -v tests/
```

---

## 📄 License
MIT © Ibrahim Aliyu Saddique (`@driasim`)
