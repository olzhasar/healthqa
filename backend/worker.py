from redis import Redis
from rq import Connection, Queue, Worker

from app.config import settings

listen = ["default"]

conn = Redis.from_url(settings.REDIS_URL)
queue = Queue(connection=conn)


if __name__ == "__main__":
    with Connection(conn):
        worker = Worker([queue], connection=conn)
        worker.work()
