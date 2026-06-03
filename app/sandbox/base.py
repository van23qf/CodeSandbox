from __future__ import annotations

import abc
from dataclasses import dataclass

from app.models.schemas import ExecuteRequest


@dataclass
class SandboxResult:
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float


class BaseSandbox(abc.ABC):
    @abc.abstractmethod
    def execute(self, request: ExecuteRequest, task_id: str) -> SandboxResult:
        ...
