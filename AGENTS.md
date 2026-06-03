# AGENTS.md

## 项目概述

代码沙盒执行环境：FastAPI 服务，通过 Docker 容器或子进程安全执行用户提交的 Python/JavaScript 代码。

## 技术栈

- Python 3.12，包管理用 uv（`uv.lock` 已 gitignore）
- FastAPI + Uvicorn，Pydantic v2 校验，docker SDK

## 常用命令

```bash
uv run python main.py          # 启动开发服务器 (0.0.0.0:8000)
uv run pytest                  # 运行全部测试
uv run pytest tests/test_api.py::test_health  # 运行单个测试
uv run pytest -k "not docker"  # 跳过需要 Docker 的测试
```

## 架构

- `main.py` — 入口，启动 Uvicorn
- `app/core.py` — FastAPI 实例，挂载路由，初始化日志
- `app/api/routes.py` — API 路由 (`/api/v1/execute`, `/api/v1/languages`, `/api/v1/health`)
- `app/sandbox/` — 沙盒实现
  - `base.py` — `BaseSandbox` 抽象基类 + `SandboxResult` 数据类
  - `docker.py` — `DockerSandbox`（生产模式，容器隔离，只读文件系统，无网络）
  - `subprocess.py` — `SubprocessSandbox`（回退模式，无隔离）
  - `languages.py` — 语言配置（镜像名、命令模板、扩展名）
- `app/models/schemas.py` — Pydantic 请求/响应模型
- `app/config.py` — 环境变量配置（通过 `pydantic-settings` 从 `.env` 加载）
- `app/logger.py` — 执行日志（Python logging，写 `logs/app.log`）
- `docker/python/`、`docker/nodejs/` — 沙盒容器 Dockerfile

## 关键注意事项

- **沙盒模式**：`SANDBOX_MODE` 环境变量控制，`auto`（默认）优先 Docker，回退 subprocess；`docker` / `subprocess` 强制指定
- **Docker 镜像**：首次执行时自动构建（`codesandbox-python:latest`、`codesandbox-nodejs:latest`），构建路径从项目根目录的 `docker/` 子目录
- **测试**：Docker 相关测试用 `pytest.mark.skipif` 按运行时 Docker 可用性跳过，无 Docker 环境下只有基础验证测试能通过
- **环境变量**：从 `.env.example` 复制为 `.env`，`app/config.py` 通过 `pydantic-settings` 自动加载
- **日志目录**：默认写项目根目录 `logs/`（已在 `.gitignore`）
