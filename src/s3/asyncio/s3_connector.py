import asyncio
import logging
from io import BufferedReader, BufferedIOBase

import aioboto3
from async_lru import alru_cache
from typing import Optional, Union

import botocore.exceptions
from aiofiles.threadpool.binary import AsyncBufferedReader, AsyncBufferedIOBase

from s3.settings import settings


class AsyncS3Instance():
    def __init__(self, client, logger, bucket):
        self._client = client
        self._logger = logger
        self._bucket = bucket

    @property
    def s3client(self):
        return self._client

    async def has_file(self, object_name: str):
        try:
            await self._client.head_object(Bucket=self._bucket, Key=object_name)
            return True
        except botocore.exceptions.ClientError:
            return False

    @staticmethod
    async def _universal_zero_seek(file: Union[AsyncBufferedIOBase, BufferedIOBase]):
        result = file.seek(0)
        if asyncio.iscoroutine(file):
            result = await result
        return result

    async def upload_file(self, file: Union[AsyncBufferedReader, BufferedReader], object_name: str):
        await self._universal_zero_seek(file)
        await self._client.upload_fileobj(file, self._bucket, object_name)
        await self._universal_zero_seek(file)

    async def download_file(self, file: Union[AsyncBufferedIOBase, BufferedIOBase], object_name: str):
        if not await self.has_file(object_name):
            raise FileNotFoundError(f"File '{object_name}' not found in '{self._bucket}' bucket")
        await self._universal_zero_seek(file)
        await self._client.download_fileobj(self._bucket, object_name, file)
        await self._universal_zero_seek(file)

    async def delete_file(self, object_name: str):
        if await self.has_file(object_name):
            await self._client.delete_object(Bucket=self._bucket, Key=object_name)
        else:
            self._logger.warning(f"Deleting a nonexistent file '{object_name}' in '{self._bucket}' bucket")

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

    async def _generate_link(self, method: str, object_name: str, content_type: Optional[str], expiration: int) -> str:
        if not method.endswith("_object"):
            raise NotImplementedError(f"Method '{method}' not implemented")
        params = {'Bucket': self._bucket, 'Key': object_name}
        if content_type is not None:
            params['ContentType'] = content_type
        return await self._client.generate_presigned_url(
            ClientMethod=method,
            Params=params,
            ExpiresIn=expiration
        )

    async def generate_get_link(self, object_name, content_type: Optional[str] = None, expiration: int = 3600):
        return await self._generate_link('get_object', object_name, content_type, expiration)

    async def generate_put_link(self, object_name, content_type: Optional[str] = None, expiration: int = 3600):
        return await self._generate_link('put_object', object_name, content_type, expiration)

    async def __aenter__(self):
        self._client = await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ret = await self._client.__aexit__(exc_type, exc_val, exc_tb)
        return ret

    async def close(self):
        await self._client.close()


class AsyncS3:
    def __init__(self, bucket: Optional[str] = None,
                 access_key_id: Optional[str] = None,
                 secret_access_key: Optional[str] = None,
                 region_name: Optional[str] = None,
                 endpoint_url: Optional[str] = None):
        self._bucket = bucket if bucket is not None else settings.AWS_BUCKET
        self._logger = logging.getLogger(f"S3 on bucket '{self._bucket}'")
        if access_key_id is None:
            self._session = aioboto3.session.Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                                     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                                     region_name=settings.AWS_REGION)
            self._endpoint_url = settings.AWS_HOST
        else:
            self._session = aioboto3.session.Session(aws_access_key_id=access_key_id,
                                                     aws_secret_access_key=secret_access_key,
                                                     region_name=region_name)
            self._endpoint_url = endpoint_url

    @property
    def bucket(self):
        return self._bucket

    def __call__(self):
        s3client = self._session.client(service_name='s3', endpoint_url=self._endpoint_url)
        return AsyncS3Instance(s3client, self._logger, self._bucket)


@alru_cache(10)
async def async_s3(bucket: Optional[str] = None,
                   access_key_id: Optional[str] = None,
                   secret_access_key: Optional[str] = None,
                   region_name: Optional[str] = None,
                   endpoint_url: Optional[str] = None):
    s3 = AsyncS3(bucket=bucket,
                 access_key_id=access_key_id,
                 secret_access_key=secret_access_key,
                 region_name=region_name,
                 endpoint_url=endpoint_url)
    async with s3() as client:
        await client.create_bucket()
    return s3
