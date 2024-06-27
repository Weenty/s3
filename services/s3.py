import aiobotocore.session
from config.settings import settings
import logging
import aiobotocore

logger = logging.getLogger("fastapi")

class S3_SERVICE:
    def __init__(self):
        self.region = "ru-central1"
        self.endpoint_url = settings.endpoint_url
        self.aws_secret_access_key = settings.bucket_value
        self.aws_access_key_id = settings.bucket_token

    async def get_client(self):
        session = aiobotocore.session.get_session()
        return session.create_client(
            's3',
            region_name=self.region,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_access_key_id=self.aws_access_key_id,
            endpoint_url=self.endpoint_url
        )

    async def ping(self):
        async with await self.get_client() as client:
            try:
                await client.list_objects_v2(Bucket=settings.bucket_name)
                logger.info('S3 бакет доступен!')
                return True
            except client.exceptions.ClientError as e:
                error_code = e.response.get('Error', {}).get('Code')
                if error_code == 'NoSuchBucket':
                    logger.error("S3 бакет не найден!.")
                elif error_code == 'AccessDenied':
                    logger.error("Отказано в доступе к бакету")
                else:
                    logger.error(f"Непредвиденная ошибка S3: {error_code}")
            return False

    async def upload_fileobj(self, fileobject, key):
        async with await self.get_client() as client:
            file_upload_response = await client.put_object(Bucket=settings.bucket_name, Key=key, Body=fileobject)
            if file_upload_response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                logger.info(f"File uploaded path : {settings.endpoint_url}/{settings.bucket_name}/{key}")
                return True
        return False