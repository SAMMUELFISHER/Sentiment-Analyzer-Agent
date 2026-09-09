import os

from redis import asyncio as aioredis


REDIS_URL = os.getenv("REDIS_URL")

redis = aioredis.from_url(
    REDIS_URL,
    decode_responses=True,
)


USER_REQUESTS_PER_MINUTE = 5


async def check_user_rate_limit(user_id: str) -> bool:

    key = f"rate:user:{user_id}:minute"

    count = await redis.incr(key)

    if count == 1:
        await redis.expire(key, 60)

    return count <= USER_REQUESTS_PER_MINUTE