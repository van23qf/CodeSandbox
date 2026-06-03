from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.config import settings


class Language(str, Enum):
    python = "python"
    javascript = "javascript"


class ExecuteRequest(BaseModel):
    language: Language
    code: str = Field(..., min_length=1, max_length=settings.MAX_CODE_LENGTH)
    timeout: int = Field(default=settings.DEFAULT_TIMEOUT, ge=1, le=settings.MAX_TIMEOUT, description="超时时间（秒）")
    memory_limit: str = Field(default=settings.DEFAULT_MEMORY_LIMIT, description="内存限制，如 128m、256m")
    cpu_limit: float = Field(default=settings.DEFAULT_CPU_LIMIT, ge=0.1, le=settings.MAX_CPU_LIMIT, description="CPU核心数限制")


class ExecuteResponse(BaseModel):
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float = Field(description="执行耗时（秒）")
    task_id: str


class LanguageInfo(BaseModel):
    name: str
    display_name: str
    version: str
    default_extension: str


class LanguageListResponse(BaseModel):
    languages: list[LanguageInfo]


class HealthResponse(BaseModel):
    status: str
    docker_available: bool
    sandbox_mode: str
