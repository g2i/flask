import redis
from src.config.environment import REDIS_URL

redis_client = redis.from_url(REDIS_URL)