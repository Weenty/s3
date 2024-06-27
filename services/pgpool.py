import asyncpg
from config.settings import settings
import logging

logger = logging.getLogger("fastapi")

class pgClient:
    def __init__(self, pool):
        self.pool = pool
        self.connection = None

    async def acquire(self):
        self.connection = await self.pool.acquire()

    async def release(self):
        if self.connection:
            await self.pool.release(self.connection)
            self.connection = None

    async def fetch(self, query, *args):
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(query, *args)
            return [dict(row) for row in rows]

    async def execute(self, query, *args):
        async with self.pool.acquire() as connection:
            result = await connection.execute(query, *args)
            return result


_pool = None

async def init_pool():
    dsn = settings.postgres_url
    pool = await asyncpg.create_pool(dsn=dsn)
    logger.info('new pool created')
    return pool

async def get_client():
    global _pool
    if _pool is None:
        _pool = await init_pool()
    logger.info('new client created')
    return pgClient(_pool)

async def run_migrate():
    try:
        client = await get_client()
        check_migrate = await client.fetch('''SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE    table_name   = 'statuses'
        );''')
        if check_migrate[0]['exists']:
            logger.info('Миграции уже применены')
            return
        sql = ''
        with open('./migrations/init.sql', 'r') as file:
            sql = file.read()
        
        await client.execute(sql)
        logger.info('Миграции успешно выполнены')
    except Exception as e:
        logger.error(e)