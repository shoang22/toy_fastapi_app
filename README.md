You will first need to start the application. There are two options:

With uvicorn:
`make run-local`

With gunicorn:
`make run-local-gunicorn`


Then you can run a load test via Locust (configurable in `tests/locust.conf`) with:
`make load-test`



