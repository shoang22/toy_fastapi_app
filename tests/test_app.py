import pytest
import json
import tempfile
from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_pass_json_file():
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
    assert resp.status_code
    print(resp.json())
    assert len(resp.json()["some_numbers"]) == n


def test_create_file():
    # Because we are using a json param, "custom_fields" will not be converted to a json by pydantic
    resp = client.post(
        "/create",
        json={"chunk_size": 4, "custom_fields": json.dumps({"this": "kinda crazy"})},
    )
    assert resp.status_code == 200
