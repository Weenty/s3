from fastapi import FastAPI
import importlib
import os
from config.settings import settings, BASE_DIR
from services.s3 import S3_SERVICE
from services.pgpool import get_client, _pool, init_pool, run_migrate
import logging

logger = logging.getLogger("fastapi")

app = FastAPI()

async def create_app():
    app = FastAPI(debug=settings.debug)
    routes_dir = os.path.join(BASE_DIR, 'routes')

    for filename in os.listdir(routes_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = f'.{filename[:-3]}'
            module = importlib.import_module(module_name, package='routes')
            if hasattr(module, 'router'):
                app.include_router(module.router)
    return app

@app.on_event("startup")
async def startup_event():
    app_instance = await create_app()
    app.router.routes.extend(app_instance.router.routes)
    app.state.pool = _pool
    
    client3S = S3_SERVICE()
    await client3S.ping()
    
    try:
        client = await get_client()
        rows = await client.fetch('SELECT 1 AS "up"')
        if rows[0]['up'] == 1:
            logger.info('Успешное подключение к базе данных!')
    except Exception as e:
        logger.error('Ошибка подключения к базе данных')
        logger.error(e)
        raise e


@app.on_event("shutdown")
async def shutdown():
    await app.state.pool.close()