from django_redis import get_redis_connection

redis_cache_default = get_redis_connection("default")
