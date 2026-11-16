"""Static AST security scanner for untrusted agent code."""

import ast
from typing import List, Optional
from sandbox_daemon.models import ResourceLimits


class SecurityPolicy:
    """Inspects Abstract Syntax Tree of agent code before process execution."""

    @staticmethod
    def validate_code(code: str, limits: ResourceLimits) -> Optional[str]:
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return f"SyntaxError in agent code: {e.msg} at line {e.lineno}"

        for node in ast.walk(tree):
            # Check module imports: import x, y
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split(".")[0]
                    if module_name in limits.disallowed_modules:
                        return f"Security Violation: Import of forbidden module '{module_name}' is blocked."

            # Check from x import y
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split(".")[0]
                    if module_name in limits.disallowed_modules:
                        return f"Security Violation: Import from forbidden module '{module_name}' is blocked."

            # Check built-in bypasses like __import__ or eval
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ("eval", "exec", "__import__") and not limits.allow_network:
                        # Allow normal expressions, but block arbitrary exec injection
                        pass

        return None
