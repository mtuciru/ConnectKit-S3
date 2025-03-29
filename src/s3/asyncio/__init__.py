try:
    from s3.asyncio.s3_connector import async_s3, AsyncS3, AsyncS3Instance

    __all__ = ["async_s3", "AsyncS3", "AsyncS3Instance"]
except ImportError:
    raise ImportError("Async functions disabled. Please install extra 'async'")
