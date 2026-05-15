import redis
import os
import json

# connect to Upstash Redis using the URL from .env
redis_client = redis.from_url(
    os.getenv("REDIS_URL"),
    decode_responses=True       # returns strings instead of bytes
)

def cache_set(key, value, expiry=300):
    """
    Save data to Redis cache.
    key    → unique identifier e.g. "items:page:1"
    value  → any Python dict or list (we convert to JSON string)
    expiry → how long to keep in seconds (default 5 minutes)
    """
    redis_client.setex(key, expiry, json.dumps(value))

def cache_get(key):
    """
    Get data from Redis cache.
    Returns the data if found, None if not found or expired.
    """
    data = redis_client.get(key)
    if data:
        return json.load(data)      # convert JSON string back to Python dict
    return None

def cache_delete(key):
    """
    Delete a specific cache entry.
    Used when data changes — e.g. new item posted, delete items cache
    so next request gets fresh data from database.
    """
    redis_client.delete(key)

def cache_delete_pattern(pattern):
    """
    Delete all cache keys matching a pattern.
    e.g. cache_delete_pattern("items:*") deletes all item caches
    """
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)