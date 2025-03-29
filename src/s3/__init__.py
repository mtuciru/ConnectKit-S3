from s3.settings import settings

from s3.s3_connector import s3, S3

try:
    from s3 import asyncio

    __all__ = ["s3", "S3", "asyncio", "settings"]
except ImportError:
    __all__ = ["s3", "S3", "settings"]
    pass
