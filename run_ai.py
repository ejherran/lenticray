import redis

from loguru import logger

from ai import caster

_QUEUE_NAME = 'jobs'
_BASE_PATH = '/home/admin/project/lenticray/data'

def main():
    logger.info("Running caster...")
    caster.execute(
        redis_cli=redis.Redis(),
        queue_name=_QUEUE_NAME,
        base_path=_BASE_PATH
    )

if __name__ == '__main__':
    main()