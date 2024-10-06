import redis
import uuid
import json

r = redis.Redis()

def add_task(task_data):
    task_id = str(uuid.uuid4())
    task = {'id': task_id, 'payload': task_data}
    r.rpush('jobs', json.dumps(task))
    return task_id