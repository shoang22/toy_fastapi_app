from locust import HttpUser, task, tag


class User(HttpUser):
    @tag("block")
    @task
    def block(self):
        fp = "tests/files/test_med.txt"
        file = {"file": open(fp, "rb")}
        self.client.post("/block", files=file)

    @tag("insert")
    @task
    def insert(self):
        payload = {"key": "string", "value": "another string"}
        self.client.post("/insert", json=payload)
