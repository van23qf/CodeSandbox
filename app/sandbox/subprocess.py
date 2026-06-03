from __future__ import annotations

import logging
import os
import subprocess
import tempfile
import time

from app.config import settings
from app.models.schemas import ExecuteRequest, Language
from app.sandbox.base import BaseSandbox, SandboxResult

logger = logging.getLogger(__name__)

COMMANDS: dict[str, list[str]] = {
    "python": ["python3"],
    "javascript": ["node"],
}


class SubprocessSandbox(BaseSandbox):
    def execute(self, request: ExecuteRequest, task_id: str) -> SandboxResult:
        ext = ".py" if request.language == Language.python else ".js"
        cmd_prefix = COMMANDS[request.language.value]

        tmpdir = tempfile.mkdtemp(prefix=f"codesandbox_{task_id}_")
        code_file = os.path.join(tmpdir, f"main{ext}")
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(request.code)

        start_time = time.monotonic()
        try:
            proc = subprocess.run(
                cmd_prefix + [code_file],
                capture_output=True,
                timeout=request.timeout,
            )
            elapsed = time.monotonic() - start_time

            stdout = proc.stdout.decode("utf-8", errors="replace")[:settings.MAX_OUTPUT_BYTES].rstrip("\n")
            stderr = proc.stderr.decode("utf-8", errors="replace")[:settings.MAX_OUTPUT_BYTES].rstrip("\n")

            return SandboxResult(
                stdout=stdout,
                stderr=stderr,
                exit_code=proc.returncode,
                execution_time=round(elapsed, 3),
            )
        except subprocess.TimeoutExpired:
            elapsed = time.monotonic() - start_time
            return SandboxResult(
                stdout="",
                stderr="执行超时，已终止",
                exit_code=-1,
                execution_time=round(elapsed, 3),
            )
        except Exception as exc:
            elapsed = time.monotonic() - start_time
            logger.exception("沙盒执行异常: %s", exc)
            return SandboxResult(
                stdout="",
                stderr=f"沙盒执行异常: {exc}",
                exit_code=-1,
                execution_time=round(elapsed, 3),
            )
        finally:
            try:
                os.remove(code_file)
                os.rmdir(tmpdir)
            except Exception:
                pass

    def is_available(self) -> bool:
        return True
