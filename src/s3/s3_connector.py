import logging
from functools import lru_cache
from io import BufferedRandom
from typing import Optional

import boto3

import botocore.exceptions

from s3.settings import settings


class S3:
    def __init__(self, bucket: Optional[str] = None,
                 access_key_id: Optional[str] = None,
                 secret_access_key: Optional[str] = None,
                 region_name: Optional[str] = None,
                 endpoint_url: Optional[str] = None):
        self._bucket = bucket if bucket is not None else settings.AWS_BUCKET
        self._logger = logging.getLogger(f"S3 on bucket '{self._bucket}'")
        if access_key_id is None:
            self._session = boto3.session.Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                                  region_name=settings.AWS_REGION)
            self._s3client = self._session.client(service_name='s3', endpoint_url=settings.AWS_HOST)
        else:
            self._session = boto3.session.Session(aws_access_key_id=access_key_id,
                                                  aws_secret_access_key=secret_access_key,
                                                  region_name=region_name)
            self._s3client = self._session.client(service_name='s3', endpoint_url=endpoint_url)
        self.create_bucket()

    @property
    def bucket(self):
        return self._bucket

    @property
    def s3client(self):
        return self._s3client

    def has_file(self, object_name: str):
        try:
            self._s3client.head_object(Bucket=self._bucket, Key=object_name)
            return True
        except botocore.exceptions.ClientError:
            return False

    def upload_file(self, file: BufferedRandom, object_name: str):
        self._s3client.upload_fileobj(file, self._bucket, object_name)

    def download_file(self, file: BufferedRandom, object_name: str):
        if not self.has_file(object_name):
            raise FileNotFoundError(f"File '{object_name}' not found in '{self._bucket}' bucket")
        file.seek(0)
        self._s3client.download_fileobj(self._bucket, object_name, file)
        file.seek(0)

    def delete_file(self, object_name: str):
        if self.has_file(object_name):
            self._s3client.delete_object(Bucket=self._bucket, Key=object_name)
        else:
            self._logger.warning(f"Deleting a nonexistent file '{object_name}' in '{self._bucket}' bucket")

    def create_bucket(self):
        try:
            try:
                self._s3client.head_bucket(Bucket=self._bucket)
                return
            except botocore.exceptions.ClientError:
                pass
            self._s3client.create_bucket(Bucket=self._bucket)
        except botocore.exceptions.ClientError as e:
            raise e
        except Exception as e:
            self._logger.warning(f"Could not create bucket: {type(e)}, {str(e)}")
            raise e

    def _generate_link(self, method: str, object_name: str, content_type: Optional[str], expiration: int) -> str:
        if not method.endswith("_object"):
            raise NotImplementedError(f"Method '{method}' not implemented")
        params = {'Bucket': self._bucket, 'Key': object_name}
        if content_type is not None:
            params['ContentType'] = content_type
        return self._s3client.generate_presigned_url(
            ClientMethod=method,
            Params=params,
            ExpiresIn=expiration
        )

    def generate_get_link(self, object_name, content_type: Optional[str] = None, expiration: int = 3600):
        return self._generate_link('get_object', object_name, content_type, expiration)

    def generate_put_link(self, object_name, content_type: Optional[str] = None, expiration: int = 3600):
        return self._generate_link('put_object', object_name, content_type, expiration)


@lru_cache(10)
def s3(bucket: Optional[str] = None,
       access_key_id: Optional[str] = None,
       secret_access_key: Optional[str] = None,
       region_name: Optional[str] = None,
       endpoint_url: Optional[str] = None):
    return S3(bucket=bucket,
              access_key_id=access_key_id,
              secret_access_key=secret_access_key,
              region_name=region_name,
              endpoint_url=endpoint_url)
