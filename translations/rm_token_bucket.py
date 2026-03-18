# This file was vibe coded to integrate the project to Redis for the sake of rate limiting.

import time
import redis
from django.conf import settings
from .rm_base import RateLimiter

# Single connection pool shared across all requests - avoids creating new connections per request
pool = redis.ConnectionPool.from_url(settings.REDIS_URL)

# Lua script that runs atomically inside Redis
# "Atomically" means no other request can interrupt between read and write - prevents race conditions
SCRIPT = """
local key = KEYS[1]                    -- Redis key for this client, e.g. "tb:127.0.0.1"
local capacity = tonumber(ARGV[1])     -- Maximum tokens the bucket can hold
local refill_rate = tonumber(ARGV[2])  -- Tokens added per second
local now = tonumber(ARGV[3])          -- Current timestamp passed in from Python

-- Read current token count and last refill time from Redis hash
-- If key doesn't exist yet (first request), defaults to full bucket
local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens = tonumber(bucket[1]) or capacity
local last_refill = tonumber(bucket[2]) or now

-- Refill tokens based on how much time has passed since last request
-- Cap at capacity so bucket never overflows
local elapsed = now - last_refill
local refilled = math.min(capacity, tokens + elapsed * refill_rate)

-- Not enough tokens - reject the request
if refilled < 1 then
    return 0
end

-- Consume one token, save updated state back to Redis
-- EXPIRE cleans up keys for clients that haven't made requests in an hour
redis.call('HMSET', key, 'tokens', refilled - 1, 'last_refill', now)
redis.call('EXPIRE', key, 3600)
return 1  -- Request allowed
"""

class TokenBucket(RateLimiter):
    def __init__(self, capacity=10, refill_rate=1):
        self.capacity = capacity        # max tokens (burst limit)
        self.refill_rate = refill_rate  # how fast tokens recover (tokens/second)
        self.client = redis.Redis(connection_pool=pool)
        self.script = self.client.register_script(SCRIPT)  # precompile script for reuse

    def is_allowed(self, key: str) -> bool:
        result = self.script(
            keys=[f"tb:{key}"],   # prefix "tb:" namespaces this key from other algorithms
            args=[self.capacity, self.refill_rate, time.time()]
        )
        return result == 1  # 1 = allowed, 0 = rate limited