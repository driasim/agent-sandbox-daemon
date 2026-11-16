"""Data models for execution requests and sandboxed results."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ResourceLimits(BaseModel):
    timeout_seconds: float = 5.0
    max_output_bytes: int = 100_000
    allow_network: bool = False
    disallowed_modules: List[str] = Field(
        default_factory=lambda: [
            "subprocess",
            "shutil",
            "socket",
            "ctypes",
            "pty",
            "resource",
            "posix",
        ]
    )


class ExecutionRequest(BaseModel):
    code: str
    language: str = "python"
    limits: ResourceLimits = Field(default_factory=ResourceLimits)


class ExecutionResult(BaseModel):
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    timed_out: bool = False
    security_violation: Optional[str] = None
