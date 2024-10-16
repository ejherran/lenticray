import os

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1' 

import redis
import time
import json
import tensorflow as tf
import torch
import numpy as np
import random

seed = 42
tf.random.set_seed(seed)
np.random.seed(seed)
random.seed(seed)
torch.manual_seed(seed)

torch.cuda.manual_seed(seed)
torch.cuda.manual_seed_all(seed)

torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

from loguru import logger

from ai.commons import enums, dto
from ai.workers import train, predict

def process_task(redis_cli, base_path, task):
    logger.info(f'Processing task: {task["id"]}')

    task['payload']['base_path'] = base_path

    if task['payload']['mode'] == enums.OperationMode.TRAIN.value:
        config = dto.TrainSettings(**task['payload'])
        worker = train
    elif task['payload']['mode'] == enums.OperationMode.PREDICT.value:
        config = dto.PredictSettings(**task['payload'])
        worker = predict
    else:
        raise ValueError('Invalid mode:', task['payload']['mode'])

    logger.info(config)
    redis_cli.set(config.id, 'RUNNING')

    worker.execute(config=config)

    redis_cli.set(config.id, 'FINISHED')

    logger.info(f'Task processed: {task["id"]}')


def execute(
    *,
    redis_cli,
    queue_name,
    base_path
) -> None:
    
    while True:
        try:
            _, task = redis_cli.blpop(queue_name)
        except redis.exceptions.ConnectionError:
            logger.warning('Error connecting to Redis. Retrying in 5 seconds...')
            time.sleep(5)
            continue
        
        try:
            task_def = json.loads(task)
        except json.JSONDecodeError:
            logger.error(f'Error decoding task: {task}')
            continue

        try:
            process_task(redis_cli, base_path, task_def)
        except Exception as e:
            redis_cli.set(task_def['id'], 'FAILED')
            logger.error(f'Error processing task: {task_def["id"]}')
            logger.exception(e)
