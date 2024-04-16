from locust import HttpUser, task


class User(HttpUser):
    @task
    def block(self):
        with open ("tests/files/test_long.txt", "rb") as fp:
            file = {"file": fp}
            self.client.post("/add", files=file)