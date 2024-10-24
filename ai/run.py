import redis

from loguru import logger

from system.core.config import settings
from system.workers import caster

def main():
    logger.info("Running caster...")

    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
    )

    caster.execute(
        redis_cli=redis_client,
        queue_name=settings.QUEUE_NAME,
        base_path=settings.BASE_PATH,
    )

if __name__ == '__main__':
    main()