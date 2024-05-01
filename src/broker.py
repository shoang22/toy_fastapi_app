import taskiq_fastapi
from taskiq_nats import NatsBroker
from taskiq_redis import RedisAsyncResultBackend

from src.settings import settings


broker = NatsBroker(
    settings.nats_urls.split(","),
    queue="fastapi_app_queue",
).with_result_backend(
    RedisAsyncResultBackend(settings.redis_url),
)

taskiq_fastapi.init(broker, "src.app:get_app")
