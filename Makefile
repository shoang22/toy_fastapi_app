.PHONY: test

test:
    PYTHONPATH=. pytest

APP_PATH=src.app:get_app

redis:
	docker run -d --name redis-stack -p 6379:6379 redis/redis-stack:latest

run-local:
	uvicorn ${APP_PATH} --reload --port 8000

taskiq:
	taskiq worker src.broker:broker --reload

stop-redis:
	docker container stop redis-stack
	docker container remove redis-stack

run-local-gunicorn:
	gunicorn ${APP_PATH}

nats:
	docker run -d \
		--name nats \
		-p 4222:4222 \
		-v ./nats-server.conf:/etc/nats/nats-server.conf \
		nats:2.9.15-alpine \
		-m 8222 \
		-c /etc/nats/nats-server.conf \

stop-nats:
	docker container stop nats
	docker container remove nats

run:
	docker compose up --detach --build

stop:
	docker compose down

load-test:
	locust --config tests/locust.conf
