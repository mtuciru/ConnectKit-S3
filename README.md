# ConnectKit S3 [*en*|[ru](./README_RU.md)]

___

ConnectKit S3 is a wrapper for boto3 and aioboto3 to simplify working with S3 storages.

Includes pydantic settings, template code.

## Installation

___

To install the sync version:

```shell
pip install ConnectKit-S3
```

To install the async version:

```shell
pip install ConnectKit-S3[async]
```

## Usage

___
These variables from settings are used for connection by default.
All variables are optional.

The first four are responsible for setting up the default connection,
you need to specify everything except the region to enable it.

Bucket is used by default unless another one is programmatically selected.

Variables are extracted from the environment:

    AWS_HOST=str               # Address of S3 server
    AWS_ACCESS_KEY_ID=str      # Access key
    AWS_SECRET_ACCESS_KEY=str  # Secret key
    AWS_REGION=str             # Region, optional
    AWS_BUCKET=str             # Default bucket

These variables can be overridden:

```python
from s3.settings import settings

settings.AWS_BUCKET = "some_bucket"
```

> **!! Attention !!**
> After creating a default connection, changing the settings variables for it is ignored.

The `s3` and `async_s3` functions are used to open the connection.

Uploading and downloading files requires:

* Synchronous mode requires a synchronous file descriptor open in binary mode.
* Asynchronous mode requires the aiofiles binary file descriptor

```python
from s3 import s3
from s3.asyncio import async_s3

# Synchronous
client = s3()
if client.has_file("s3_filename"):
    pass

# Asynchronous
client = async_s3

async with client() as conn:
    if conn.has_file("s3_filename"):
        pass

```

## License

___

ConnectKit S3 is [MIT License](./LICENSE).