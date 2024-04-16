import requests
from joblib import delayed, Parallel
from fastapi.testclient import TestClient

from src.app import app


BASE_URL = "http://127.0.0.1:8000"

def call_api(i):
    print(f"Submitting job {i}")
    with open("tests/files/test_long.txt", "rb") as f:
        file = {"file": f}
        resp = requests.post(BASE_URL + "/block", files=file)    
        assert resp.status_code == 200
        return resp.json()


if __name__ == "__main__":
    results = Parallel(n_jobs=128)(delayed(call_api)(i) for i in range(1000))
    print("Done")
