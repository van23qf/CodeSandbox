from __future__ import annotations

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    SANDBOX_MODE: str = "auto"
    DOCKER_HOST: str = "unix:///var/run/docker.sock"
    HOST_CODE_DIR: str = ""

    SANDBOX_DEFAULT_TIMEOUT: int = 10
    SANDBOX_MAX_TIMEOUT: int = 300
    SANDBOX_DEFAULT_MEMORY_LIMIT: str = "128m"
    SANDBOX_DEFAULT_CPU_LIMIT: float = 1.0
    SANDBOX_MAX_CPU_LIMIT: float = 4.0
    SANDBOX_PIDS_LIMIT: int = 64
    SANDBOX_TMPFS_SIZE: str = "64m"
    SANDBOX_MAX_OUTPUT_BYTES: int = 1024 * 1024
    SANDBOX_MAX_CODE_LENGTH: int = 102400

    @property
    def DOCKER_DIR(self) -> str:
        return str(Path(__file__).resolve().parent.parent / "docker")

    @property
    def LOG_DIR(self) -> str:
        return str(Path(__file__).resolve().parent.parent / "logs")

    @property
    def DEFAULT_TIMEOUT(self) -> int:
        return self.SANDBOX_DEFAULT_TIMEOUT

    @property
    def MAX_TIMEOUT(self) -> int:
        return self.SANDBOX_MAX_TIMEOUT

    @property
    def DEFAULT_MEMORY_LIMIT(self) -> str:
        return self.SANDBOX_DEFAULT_MEMORY_LIMIT

    @property
    def DEFAULT_CPU_LIMIT(self) -> float:
        return self.SANDBOX_DEFAULT_CPU_LIMIT

    @property
    def MAX_CPU_LIMIT(self) -> float:
        return self.SANDBOX_MAX_CPU_LIMIT

    @property
    def PIDS_LIMIT(self) -> int:
        return self.SANDBOX_PIDS_LIMIT

    @property
    def TMPFS_SIZE(self) -> str:
        return self.SANDBOX_TMPFS_SIZE

    @property
    def MAX_OUTPUT_BYTES(self) -> int:
        return self.SANDBOX_MAX_OUTPUT_BYTES

    @property
    def MAX_CODE_LENGTH(self) -> int:
        return self.SANDBOX_MAX_CODE_LENGTH


settings = Settings()
