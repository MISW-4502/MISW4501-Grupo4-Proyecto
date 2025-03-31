import redis
from src.config.config import Config

BLOCK_THRESHOLD = 5
BLOCK_DURATION_SECONDS = 15 * 60  # 15 minutos

# Conexión a Redis
redis_client = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=0)

def _key(ip):
    return f"ipblock:{ip}"

def is_ip_blocked(ip):
    key = _key(ip)
    count = redis_client.get(key)
    if count and int(count) >= BLOCK_THRESHOLD:
        return True
    return False

def register_failed_attempt(ip):
    key = _key(ip)
    current = redis_client.get(key)

    if current:
        redis_client.incr(key)
    else:
        redis_client.setex(key, BLOCK_DURATION_SECONDS, 1)

def reset_ip(ip):
    redis_client.delete(_key(ip))
