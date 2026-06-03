# CodeSandbox

代码沙盒执行环境，通过 Docker 容器安全执行用户提交的 Python/JavaScript 代码。

## 特性

- **安全隔离**：Docker 容器隔离，只读文件系统，无网络访问
- **资源限制**：可配置 CPU、内存、超时、进程数限制
- **多语言支持**：Python 3.12、JavaScript (Node.js 22)
- **自动回退**：Docker 不可用时自动降级到 subprocess 模式
- **执行日志**：记录每次执行的元数据

## 快速开始

### 环境要求

- Python 3.12+
- Docker（推荐）或本地 Python/Node.js 环境
- [uv](https://docs.astral.sh/uv/) 包管理器

### 本地开发

```bash
# 安装依赖
uv sync

# 复制环境配置
cp .env.example .env

# 启动服务
uv run python main.py
```

服务启动后访问 http://localhost:8000

### Docker 部署

```bash
# 构建所有镜像（沙盒镜像 + 项目镜像）
./build.sh all

# 或分步构建
./build.sh sandbox  # 仅构建沙盒镜像
./build.sh project  # 仅构建项目镜像

# 启动服务
docker-compose up -d
```

## API 接口

### 执行代码

```http
POST /api/v1/execute
Content-Type: application/json

{
  "language": "python",
  "code": "print('Hello, World!')",
  "timeout": 10,
  "memory_limit": "128m",
  "cpu_limit": 1.0
}
```

响应：

```json
{
  "success": true,
  "stdout": "Hello, World!",
  "stderr": "",
  "exit_code": 0,
  "execution_time": 0.123,
  "task_id": "abc123def456"
}
```

### 支持的语言

```http
GET /api/v1/languages
```

响应：

```json
{
  "languages": [
    {
      "name": "python",
      "display_name": "Python",
      "version": "3.12",
      "default_extension": ".py"
    },
    {
      "name": "javascript",
      "display_name": "JavaScript (Node.js)",
      "version": "22",
      "default_extension": ".js"
    }
  ]
}
```

### 健康检查

```http
GET /api/v1/health
```

响应：

```json
{
  "status": "ok",
  "docker_available": true,
  "sandbox_mode": "docker"
}
```

## 配置

环境变量配置（`.env` 文件）：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SANDBOX_MODE` | `auto` | 沙盒模式：`auto`/`docker`/`subprocess` |
| `SANDBOX_DEFAULT_TIMEOUT` | `10` | 默认超时时间（秒） |
| `SANDBOX_MAX_TIMEOUT` | `300` | 最大超时时间（秒） |
| `SANDBOX_DEFAULT_MEMORY_LIMIT` | `128m` | 默认内存限制 |
| `SANDBOX_DEFAULT_CPU_LIMIT` | `1.0` | 默认 CPU 核心数限制 |
| `SANDBOX_MAX_CPU_LIMIT` | `4.0` | 最大 CPU 核心数限制 |
| `SANDBOX_PIDS_LIMIT` | `64` | 最大进程数 |
| `SANDBOX_TMPFS_SIZE` | `64m` | /tmp 目录大小 |
| `SANDBOX_MAX_OUTPUT_BYTES` | `1048576` | 输出最大字节数（1MB） |
| `SANDBOX_MAX_CODE_LENGTH` | `102400` | 代码最大长度（100KB） |
| `DOCKER_HOST` | `unix:///var/run/docker.sock` | Docker daemon 地址 |
| `HOST_CODE_DIR` | - | 宿主机代码临时目录（Docker-out-of-Docker 部署时需要） |

## 沙盒模式

- **docker**：生产推荐，容器隔离，安全级别最高
- **subprocess**：回退模式，无隔离，仅用于开发测试
- **auto**：自动检测 Docker 可用性，优先使用 docker 模式

## 安全措施

Docker 模式下的安全隔离：

- 只读文件系统，代码通过卷挂载只读访问
- 无网络访问（`network_mode: none`）
- 非特权用户运行（`user: sandbox`）
- 资源限制：内存、CPU、进程数、超时
- 临时文件系统（tmpfs）用于 /tmp 目录
- 容器执行完毕立即销毁

## 项目结构

```
.
├── app/
│   ├── api/routes.py      # API 路由
│   ├── config.py          # 配置管理
│   ├── core.py            # FastAPI 应用
│   ├── logger.py          # 执行日志
│   ├── models/schemas.py  # Pydantic 模型
│   └── sandbox/
│       ├── base.py        # 沙盒基类
│       ├── docker.py      # Docker 沙盒实现
│       ├── subprocess.py  # Subprocess 沙盒实现
│       └── languages.py   # 语言配置
├── docker/
│   ├── python/Dockerfile  # Python 沙盒镜像
│   └── nodejs/Dockerfile  # Node.js 沙盒镜像
├── tests/                 # 测试用例
├── main.py                # 入口文件
├── build.sh               # 镜像构建脚本
├── docker-compose.yml     # Docker Compose 配置
├── Dockerfile             # 项目镜像
└── pyproject.toml         # 项目配置
```

## 测试

```bash
# 运行全部测试
uv run pytest

# 运行单个测试
uv run pytest tests/test_api.py::test_health

# 跳过需要 Docker 的测试
uv run pytest -k "not docker"

# 快速测试
curl -X POST \
http://localhost:8001/api/v1/execute \
-H "Content-Type: application/json" \
-d '{
  "language":"javascript",
  "code":"console.log(1+2)"
}'
```

## 开发

```bash
# 安装开发依赖
uv sync --extra dev

# 启动服务（热重载）
uv run uvicorn app.core:app --reload
```

## License

MIT
