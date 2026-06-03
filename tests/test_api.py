from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core import app

client = TestClient(app)


def _docker_available() -> bool:
    try:
        import docker
        c = docker.from_env()
        c.ping()
        return True
    except Exception:
        return False


DOCKER_AVAILABLE = _docker_available()


def test_health():
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "docker_available" in data


def test_languages():
    resp = client.get("/api/v1/languages")
    assert resp.status_code == 200
    data = resp.json()
    assert "languages" in data
    names = [lang["name"] for lang in data["languages"]]
    assert "python" in names
    assert "javascript" in names


def test_execute_empty_code():
    resp = client.post("/api/v1/execute", json={"language": "python", "code": ""})
    assert resp.status_code == 422


def test_execute_invalid_language():
    resp = client.post("/api/v1/execute", json={"language": "rust", "code": "fn main() {}"})
    assert resp.status_code == 422


def test_execute_invalid_timeout():
    resp = client.post(
        "/api/v1/execute",
        json={"language": "python", "code": "print(1)", "timeout": 0},
    )
    assert resp.status_code == 422


@pytest.mark.skipif(
    not DOCKER_AVAILABLE,
    reason="Docker 不可用",
)
def test_execute_python():
    resp = client.post(
        "/api/v1/execute",
        json={"language": "python", "code": "print('hello world')"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "hello world" in data["stdout"]
    assert data["exit_code"] == 0
    assert data["execution_time"] > 0


@pytest.mark.skipif(
    not DOCKER_AVAILABLE,
    reason="Docker 不可用",
)
def test_execute_javascript():
    resp = client.post(
        "/api/v1/execute",
        json={"language": "javascript", "code": "console.log('hello world');"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "hello world" in data["stdout"]
    assert data["exit_code"] == 0


@pytest.mark.skipif(
    not DOCKER_AVAILABLE,
    reason="Docker 不可用",
)
def test_execute_python_error():
    resp = client.post(
        "/api/v1/execute",
        json={"language": "python", "code": "raise ValueError('test error')"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is False
    assert "test error" in data["stderr"]
    assert data["exit_code"] != 0
