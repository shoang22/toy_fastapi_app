from locust import HttpUser, task
import tempfile


class User(HttpUser):
    @task
    def block(self):
        with tempfile.NamedTemporaryFile(delete=False) as fp:
            fp.write(b"What is going on?" * int(1e6))
            fp.flush()
            file = {"file": open(fp.name, "rb")}
            self.client.post("/block", files=file)