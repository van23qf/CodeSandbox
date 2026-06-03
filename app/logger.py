from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ExecutionLog:
    task_id: str
    language: str
    code_length: int
    timeout: int
    memory_limit: str
    cpu_limit: float
    success: bool
    exit_code: int
    execution_time: float
    timestamp: float = field(default_factory=time.time)


class ExecutionLogger:
    def log(self, record: ExecutionLog) -> None:
        logger.info(
            "task_id=%s language=%s code_length=%d timeout=%d memory_limit=%s cpu_limit=%s success=%s exit_code=%d execution_time=%.3fs",
            record.task_id,
            record.language,
            record.code_length,
            record.timeout,
            record.memory_limit,
            record.cpu_limit,
            record.success,
            record.exit_code,
            record.execution_time,
        )