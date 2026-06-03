from __future__ import annotations

import logging
import os
import tempfile
import time

import docker
from docker.errors import APIError, ImageNotFound, NotFound

from app.config import settings
from app.models.schemas import ExecuteRequest, Language
from app.sandbox.base import BaseSandbox, SandboxResult
from app.sandbox.languages import get_language_config

logger = logging.getLogger(__name__)


def _parse_memory_limit(limit: str) -> int:
    limit = limit.strip().lower()
    if limit.endswith("g"):
        return int(limit[:-1]) * 1024 * 1024 * 1024
    if limit.endswith("m"):
        return int(limit[:-1]) * 1024 * 1024
    if limit.endswith("k"):
        return int(limit[:-1]) * 1024
    return int(limit)


class DockerSandbox(BaseSandbox):
    def __init__(self) -> None:
        self._client: docker.DockerClient | None = None

    @property
    def client(self) -> docker.DockerClient:
        if self._client is None:
            self._client = docker.DockerClient(base_url=settings.DOCKER_HOST)
        return self._client

    def _ensure_image(self, image_name: str) -> None:
        try:
            self.client.images.get(image_name)
        except ImageNotFound:
            logger.info("镜像 %s 不存在，尝试构建...", image_name)
            self._build_image(image_name)

    def _build_image(self, image_name: str) -> None:
        if image_name.startswith("codesandbox-python"):
            dockerfile_dir = os.path.join(settings.DOCKER_DIR, "python")
        elif image_name.startswith("codesandbox-nodejs"):
            dockerfile_dir = os.path.join(settings.DOCKER_DIR, "nodejs")
        else:
            raise ValueError(f"未知的镜像: {image_name}")

        self.client.images.build(path=dockerfile_dir, tag=image_name, rm=True)
        logger.info("镜像 %s 构建完成", image_name)

    def execute(self, request: ExecuteRequest, task_id: str) -> SandboxResult:
        config = get_language_config(request.language)
        self._ensure_image(config.image)

        if settings.HOST_CODE_DIR:
            host_tmpdir = os.path.join(settings.HOST_CODE_DIR, f"codesandbox_{task_id}")
            tmpdir = os.path.join("/app/tmp", f"codesandbox_{task_id}")
            os.makedirs(tmpdir, exist_ok=True)
            os.chmod(tmpdir, 0o755)
        else:
            tmpdir = tempfile.mkdtemp(prefix=f"codesandbox_{task_id}_")
            os.chmod(tmpdir, 0o755)
            host_tmpdir = tmpdir

        code_file = os.path.join(tmpdir, f"main{config.extension}")
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(request.code)
        os.chmod(code_file, 0o644)

        mem_bytes = _parse_memory_limit(request.memory_limit)
        cpu_period = 100000
        cpu_quota = int(request.cpu_limit * cpu_period)

        container = None
        start_time = time.monotonic()
        try:

            container = self.client.containers.create(
                image=config.image,
                command=config.cmd_template,
                volumes=[f"{host_tmpdir}:/home/sandbox/code:ro"],
                mem_limit=mem_bytes,
                memswap_limit=mem_bytes,
                cpu_period=cpu_period,
                cpu_quota=cpu_quota,
                pids_limit=settings.PIDS_LIMIT,
                network_mode="none",
                read_only=True,
                tmpfs={"/tmp": f"size={settings.TMPFS_SIZE}"},
                user="sandbox",
                detach=True,
                labels={"codesandbox.task_id": task_id},
            )

            container.start()
            result = container.wait(timeout=request.timeout)
            elapsed = time.monotonic() - start_time

            exit_code = result.get("StatusCode", -1)
            stdout_raw = container.logs(stdout=True, stderr=False)
            stderr_raw = container.logs(stdout=False, stderr=True)

            stdout = stdout_raw.decode("utf-8", errors="replace")[:settings.MAX_OUTPUT_BYTES].rstrip("\n")
            stderr = stderr_raw.decode("utf-8", errors="replace")[:settings.MAX_OUTPUT_BYTES].rstrip("\n")

            return SandboxResult(
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                execution_time=round(elapsed, 3),
            )

        except Exception as exc:
            elapsed = time.monotonic() - start_time
            if "timeout" in str(exc).lower() or "timed out" in str(exc).lower():
                return SandboxResult(
                    stdout="",
                    stderr="执行超时，已终止",
                    exit_code=-1,
                    execution_time=round(elapsed, 3),
                )
            logger.exception("沙盒执行异常: %s", exc)
            return SandboxResult(
                stdout="",
                stderr=f"沙盒执行异常: {exc}",
                exit_code=-1,
                execution_time=round(elapsed, 3),
            )
        finally:
            if container is not None:
                try:
                    container.remove(force=True)
                except Exception:
                    pass
            try:
                os.remove(code_file)
                os.rmdir(tmpdir)
            except Exception:
                pass

    def is_available(self) -> bool:
        try:
            self.client.ping()
            return True
        except Exception:
            return False
