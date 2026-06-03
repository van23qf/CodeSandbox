from __future__ import annotations

import uuid

from fastapi import APIRouter

from app.logger import ExecutionLog, ExecutionLogger
from app.models.schemas import (
    ExecuteRequest,
    ExecuteResponse,
    HealthResponse,
    Language,
    LanguageInfo,
    LanguageListResponse,
)
from app.sandbox.base import BaseSandbox
from app.sandbox.docker import DockerSandbox
from app.sandbox.languages import LANGUAGES
from app.sandbox.subprocess import SubprocessSandbox

router = APIRouter(prefix="/api/v1")

_docker_sandbox = DockerSandbox()
_subprocess_sandbox = SubprocessSandbox()
execution_logger = ExecutionLogger()


def _get_sandbox() -> BaseSandbox:
    from app.config import settings
    mode = settings.SANDBOX_MODE.lower()
    if mode == "docker":
        return _docker_sandbox
    if mode == "subprocess":
        return _subprocess_sandbox
    if _docker_sandbox.is_available():
        return _docker_sandbox
    return _subprocess_sandbox


def _get_sandbox_mode() -> str:
    from app.config import settings
    mode = settings.SANDBOX_MODE.lower()
    if mode in ("docker", "subprocess"):
        return mode
    return "docker" if _docker_sandbox.is_available() else "subprocess"


@router.post("/execute", response_model=ExecuteResponse)
def execute_code(request: ExecuteRequest) -> ExecuteResponse:
    task_id = uuid.uuid4().hex[:12]
    sandbox = _get_sandbox()
    result = sandbox.execute(request, task_id)

    execution_logger.log(
        ExecutionLog(
            task_id=task_id,
            language=request.language.value,
            code_length=len(request.code),
            timeout=request.timeout,
            memory_limit=request.memory_limit,
            cpu_limit=request.cpu_limit,
            success=result.exit_code == 0,
            exit_code=result.exit_code,
            execution_time=result.execution_time,
        )
    )

    return ExecuteResponse(
        success=result.exit_code == 0,
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.exit_code,
        execution_time=result.execution_time,
        task_id=task_id,
    )


@router.get("/languages", response_model=LanguageListResponse)
def list_languages() -> LanguageListResponse:
    languages = [
        LanguageInfo(
            name=lang.value,
            display_name=cfg.display_name,
            version=cfg.version,
            default_extension=cfg.extension,
        )
        for lang, cfg in LANGUAGES.items()
    ]
    return LanguageListResponse(languages=languages)


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    docker_ok = _docker_sandbox.is_available()
    mode = _get_sandbox_mode()
    return HealthResponse(
        status="ok" if docker_ok else "degraded",
        docker_available=docker_ok,
        sandbox_mode=mode,
    )
