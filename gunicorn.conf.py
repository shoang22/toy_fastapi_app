import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
# threads = workers
max_requests = 1000
max_requests_jitter = 20 
worker_class = "src.uvicorn_utils.MyUvicornWorker"
reload = True
loglevel = "debug"
errorlog = "gunicorn_error.log"
accesslog = "gunicorn_access.log"
timeout = 171
graceful_timeout = 171