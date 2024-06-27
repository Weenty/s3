from celery import Celery
from config.settings import settings
from PIL import Image
from services.s3 import S3_SERVICE
from io import BytesIO
import uuid
import os
import logging
from services.images import changeStatus, changePath
import asyncio
from config.constants import STATUSES
from services.pgpool import get_client

logger = logging.getLogger("fastapi")

celery = Celery(
    __name__,
    broker=settings.redis_url,
    backend=settings.redis_url
)

@celery.task(bind=True)
def resize_image_and_upload(self, id, bytes, filename):
    loop = asyncio.get_event_loop()
    filename = filename.replace(' ', '_')
    filename, file_extension = os.path.splitext(filename)
    client = loop.run_until_complete(get_client())
    try:
        bytes = BytesIO(bytes)
        uuid_split = str(uuid.uuid4()).split('-')
        path = f'{uuid_split[0]}/{uuid_split[1]}/{uuid_split[3]}/{filename}'
        
        client3S = S3_SERVICE()
        result = loop.run_until_complete(client3S.upload_fileobj(bytes, path + f'/original{file_extension}'))
        if not result:
            raise Exception('Произошла ошибка при загрузке файла в s3 бакет!')
        loop.run_until_complete(changePath(id, path, client))
        loop.run_until_complete(changeStatus(id, STATUSES['uploaded'], client))
        logger.info('Файл успешно загружен!')
        
        logger.info('Начало процессинка...')
        loop.run_until_complete(changeStatus(id, STATUSES['processing'], client))
        
        image = Image.open(bytes)
        width, height = image.size
        
        buf1 = BytesIO()
        buf2 = BytesIO()
        
        image_x2 = (image.resize((width*2, height*2)))
        image_x3 = (image.resize((width*3, height*3)))
        image_x2.save(buf1, format='JPEG')
        image_x3.save(buf2, format='JPEG')
        
        image_x2 = buf1.getvalue()
        image_x3 = buf1.getvalue()
        
        result1 = loop.run_until_complete(client3S.upload_fileobj(image_x2, path + f'/image_x2{file_extension}'))
        result2 = loop.run_until_complete(client3S.upload_fileobj(image_x3, path + f'/image_x3{file_extension}'))
        if not result1 or not result2:
            raise Exception('Произошла ошибка при загрузке файла в s3 бакет!')
        
        loop.run_until_complete(changeStatus(id, STATUSES['done'], client))
        logger.info('Процессинг завершен!')
    except Exception as e:
        logger.error(e)
        loop.run_until_complete(changeStatus(id, STATUSES['error'], client))