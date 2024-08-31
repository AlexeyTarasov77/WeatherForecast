import os

import redis

conn = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=os.environ["REDIS_PORT"],
    db=2,
    decode_responses=True,
)
