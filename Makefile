run-local:
	uvicorn src.app:app --reload --port 8000

run-local-gunicorn:
	gunicorn src.app:app

load-test:
	locust --config tests/locust.conf