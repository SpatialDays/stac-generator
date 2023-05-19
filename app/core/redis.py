import redis
from rq import Queue

def create_redis_connection(host: str, port: int, db: int):
    return redis.Redis(host=host, port=port, db=db)

def create_rq_queue(redis_conn):
    return Queue(connection=redis_conn)
