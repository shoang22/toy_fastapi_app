import taskiq_fastapi
import pytest
import tempfile
from typing import Generator
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.app import get_app
from src.app import broker


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Backend for anyio pytest plugin.

    :return: backend name.
    """
    return "asyncio"


@pytest.fixture
def fastapi_app() -> FastAPI:
    return get_app()


@pytest.fixture(autouse=True)
def init_taskiq_deps(fastapi_app: FastAPI):
    # This is important part. Here we add dependency context,
    # this thing helps in resolving dependencies for tasks
    # for inmemory broker.
    taskiq_fastapi.populate_dependency_context(broker, fastapi_app)

    yield

    broker.custom_dependency_context = {}


@pytest.fixture
def client(fastapi_app: FastAPI) -> Generator[TestClient, None, None]:
    """
    Fixture that creates client for requesting server.

    :param fastapi_app: the application.
    :yield: client for the app.
    """
    with TestClient(app=fastapi_app, base_url="http://test") as ac:
        yield ac


def test_pass_json_file(client: TestClient):
    n = 10

    with tempfile.NamedTemporaryFile(delete=True) as f:
        f.write(b"123")
        f.flush()
        resp = client.post(
            "/",
            files={"file": f},
            params={
                "chunk_size": 10,
                "some_numbers": list(range(n)),
                # "custom_fields": '{"favorite_rapper": "yo_gotti"}'
            },
        )
    assert resp.status_code == 200
    print(resp.json())
    assert len(resp.json()["some_numbers"]) == n


def test_query(client: TestClient):
    body = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"title": "Search"}},
                    {"match": {"content": "Elasticsearch"}},
                ],
                "filter": [
                    {"term": {"status": "published"}},
                    {"range": {"publish_date": {"gte": "2015-01-01"}}},
                ],
            }
        }
    }
    resp = client.post("/query", json={"search": body})
    print(resp.json()["query"])
    assert resp.status_code == 200
