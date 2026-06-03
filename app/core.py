import logging
import os

from fastapi import FastAPI

from app.config import settings

os.makedirs(settings.LOG_DIR, exist_ok=True)

handlers = [logging.StreamHandler()]
try:
    handlers.append(logging.FileHandler(os.path.join(settings.LOG_DIR, "app.log"), encoding="utf-8"))
except PermissionError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=handlers,
)

from app.api.routes import router  # noqa: E402

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    title="CodeSandbox",
    description="代码沙盒执行环境，支持多语言代码安全运行",
    version="0.1.0",
)

app.include_router(router)