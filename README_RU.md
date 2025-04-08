# ConnectKit S3 [[en](./README.md)|*ru*]

___

ConnectKit S3 - это оболочка для boto3 и aioboto3 для упрощения работы с S3 хранилищами.

Включает в себя pydantic settings, шаблонный код.

## Установка

___

Для установки sync версии:

```shell
pip install ConnectKit-S3
```

Для установки async версии:

```shell
pip install ConnectKit-S3[async]
```

## Использование

___

Для подключения по умолчанию используются переменные settings.
Все переменные опциональны.

Первые три отвечают за настройку соединения по умолчанию,
требуется указать всё для его включения.

Bucket и регион по умолчанию используются, если программно не выбирается другой.

Переменные извлекаются из environment или `.env` файла:

    AWS_HOST=str               # Адрес S3 сервера
    AWS_ACCESS_KEY_ID=str      # Access key
    AWS_SECRET_ACCESS_KEY=str  # Secret key
    AWS_REGION=str             # Регион, если необходимо
    AWS_BUCKET=str             # Bucket по умолчанию

Для открытия соединения используются `s3` и `async_s3` функции.

Загрузка и скачивание файлов требует:

* Для синхронного режима требуется синхронный файловый дескриптор открытый в бинарном режиме.
* Для асинхронного режима требуется синхронный бинарный файловый дескриптор или aiofiles дескриптор

```python
from s3 import s3
from s3.asyncio import async_s3

# Synchronous
client = s3()
if client.has_file("s3_filename"):
    pass

# Asynchronous
client = await async_s3()

async with client() as conn:
    if conn.has_file("s3_filename"):
        pass
```

## Лицензия

___

ConnectKit S3 распространяется под [лицензией MIT](./LICENSE).