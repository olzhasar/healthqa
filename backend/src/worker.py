from redis import Redis
from rq import Connection, Queue, Worker

from app.config import settings

listen = ["default"]

conn = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_RQ_DB)
queue = Queue(connection=conn)


if __name__ == "__main__":
    with Connection(conn):
        worker = Worker([queue], connection=conn)
        worker.work()
