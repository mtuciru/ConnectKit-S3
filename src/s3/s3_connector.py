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
        self.logger = logging.getLogger(f"S3 on bucket '{bucket}'")
        self.bucket = bucket if bucket is not None else settings.AWS_BUCKET
        if access_key_id is None:
            self.session = boto3.session.Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                                 aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                                 region_name=settings.AWS_REGION)
            self.s3client = self.session.client(service_name='s3', endpoint_url=settings.AWS_HOST)
        else:
            self.session = boto3.session.Session(aws_access_key_id=access_key_id,
                                                 aws_secret_access_key=secret_access_key,
                                                 region_name=region_name)
            self.s3client = self.session.client(service_name='s3', endpoint_url=endpoint_url)
        self.create_bucket()

    def has_file(self, object_name: str):
        try:
            self.s3client.head_object(Bucket=self.bucket, Key=object_name)
            return True
        except botocore.exceptions.ClientError:
            return False

    def upload_file(self, file: BufferedRandom, object_name: str):
        self.s3client.upload_fileobj(file, self.bucket, object_name)

    def download_file(self, file: BufferedRandom, object_name: str):
        if not self.has_file(object_name):
            raise FileNotFoundError(f"File '{object_name}' not found")
        file.seek(0)
        self.s3client.download_fileobj(self.bucket, object_name, file)
        file.seek(0)

    def delete_file(self, object_name: str):
        if self.has_file(object_name):
            self.s3client.delete_object(Bucket=self.bucket, Key=object_name)

    def create_bucket(self):
        try:
            try:
                self.s3client.head_bucket(Bucket=self.bucket)
                return
            except botocore.exceptions.ClientError:
                pass
            self.s3client.create_bucket(Bucket=self.bucket)
        except botocore.exceptions.ClientError as e:
            raise e
        except Exception as e:
            self.logger.warning(f"Could not create bucket: {type(e)}, {str(e)}")
            raise e

    def generate_get_link(self, object_name, expiration: int = 3600):
        return self.s3client.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': self.bucket, 'Key': object_name},
            ExpiresIn=expiration
        )


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
