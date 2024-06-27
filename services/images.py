from .pgpool import get_client
import logging
from fastapi import HTTPException
from config.constants import STATUSES
from config.settings import settings
import json
logger = logging.getLogger("fastapi")
async def insert_file(filePath, client=None):
    try:
        if not client:
            client = await get_client()
        rows = await client.fetch('INSERT INTO files (filepath, status) VALUES ($1, $2) RETURNING id', filePath, STATUSES['pending'])
        return rows[0]['id']
    except Exception as e:
        logger.error(e)
        raise HTTPException(400, 'Ошибка при добавлении файла в базу данных')

async def changeStatus(id, status, client=None):
    if not client:
        client = await get_client()
    await client.execute('UPDATE files SET status = $1 WHERE id = $2', status, id)

async def changePath(id, path, client=None):
    if not client:
        client = await get_client()
    await client.execute('UPDATE files SET "filepath" = $1 WHERE id = $2', path, id)
    
async def get_files(page):
    client = await get_client()
    page = page or 1
    limit = 25
    offset = (limit * page) - limit
    rows = await client.fetch(f'''
    SELECT
        f.id AS "id",
        s.value AS "status",
        json_build_object(
                    'original', CASE WHEN f.filepath IS NULL OR f.filepath='' THEN NULL ELSE CONCAT_WS('', '{settings.endpoint_url}/', f.filepath, '/original.jpg') END,
                    'image_x2', CASE WHEN f.filepath IS NULL OR f.filepath='' THEN NULL ELSE CONCAT_WS('', '{settings.endpoint_url}/', f.filepath, '/image_x2.jpg') END,
                    'image_x3', CASE WHEN f.filepath IS NULL OR f.filepath='' THEN NULL ELSE CONCAT_WS('', '{settings.endpoint_url}/', f.filepath, '/image_x3.jpg') END
        ) AS "files"
        FROM files f
    INNER JOIN statuses s ON s.id = f.status
    ORDER BY f.id DESC
    OFFSET $1 LIMIT $2
    ''', offset, limit)
    for i in range(len(rows)):
        rows[i]['files'] = json.loads(rows[i]['files'])
    return rows
    
    
    