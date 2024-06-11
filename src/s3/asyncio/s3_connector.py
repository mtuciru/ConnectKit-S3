import logging

import aioboto3
from async_lru import alru_cache
from typing import Optional

import botocore.exceptions
from aiofiles.threadpool.binary import AsyncBufferedReader, AsyncBufferedIOBase

from s3.settings import settings


class S3Instance():
    def __init__(self, client, logger, bucket):
        self._client = client
        self._logger = logger
        self._bucket = bucket

    async def has_file(self, object_name: str):
        try:
            await self._client.head_object(Bucket=self._bucket, Key=object_name)
            return True
        except botocore.exceptions.ClientError:
            return False

    async def upload_file(self, file: AsyncBufferedReader, object_name: str):
        await self._client.upload_fileobj(file, self._bucket, object_name)

    async def download_file(self, file: AsyncBufferedIOBase, object_name: str):
        if not await self.has_file(object_name):
            raise FileNotFoundError(f"File '{object_name}' not found")
        await file.seek(0)
        await self._client.download_fileobj(self._bucket, object_name, file)
        await file.seek(0)

    async def delete_file(self, object_name: str):
        if await self.has_file(object_name):
            await self._client.delete_object(Bucket=self._bucket, Key=object_name)

    async def create_bucket(self):
        try:
            try:
                await self._client.head_bucket(Bucket=self._bucket)
                return
            except botocore.exceptions.ClientError:
                pass
            await self._client.create_bucket(Bucket=self._bucket)
        except botocore.exceptions.ClientError as e:
            raise e
        except Exception as e:
            self._logger.warning(f"Could not create bucket: {type(e)}, {str(e)}")
            raise e

    async def generate_get_link(self, object_name, expiration: int = 3600):
        return await self._client.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': self._bucket, 'Key': object_name},
            ExpiresIn=expiration
        )

    async def __aenter__(self):
        self._client = await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ret = await self._client.__aexit__(exc_type, exc_val, exc_tb)
        return ret


class S3:
    def __init__(self, bucket: Optional[str] = None,
                 access_key_id: Optional[str] = None,
                 secret_access_key: Optional[str] = None,
                 region_name: Optional[str] = None,
                 endpoint_url: Optional[str] = None):
        self._logger = logging.getLogger(f"S3 on bucket '{bucket}'")
        self._bucket = bucket if bucket is not None else settings.AWS_BUCKET
        if access_key_id is None:
            self.session = aioboto3.session.Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                                    region_name=settings.AWS_REGION)
            self.endpoint_url = settings.AWS_HOST
        else:
            self.session = aioboto3.session.Session(aws_access_key_id=access_key_id,
                                                    aws_secret_access_key=secret_access_key,
                                                    region_name=region_name)
            self.endpoint_url = endpoint_url

    def __call__(self):
        s3client = self.session.client(service_name='s3', endpoint_url=self.endpoint_url)
        return S3Instance(s3client, self._logger, self._bucket)


@alru_cache(10)
async def async_s3(bucket: Optional[str] = None,
                   access_key_id: Optional[str] = None,
                   secret_access_key: Optional[str] = None,
                   region_name: Optional[str] = None,
                   endpoint_url: Optional[str] = None):
    s3 = S3(bucket=bucket,
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            region_name=region_name,
            endpoint_url=endpoint_url)
    async with s3() as client:
        await client.create_bucket()
    return s3
