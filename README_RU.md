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

Первые четыре отвечают за настройку соединения по умолчанию,
требуется указать всё, кроме региона, для его включения.

Bucket по умолчанию используется, если программно не выбирается другой.

Переменные извлекаются из environment:

    AWS_HOST=str               # Адрес S3 сервера
    AWS_ACCESS_KEY_ID=str      # Access key
    AWS_SECRET_ACCESS_KEY=str  # Secret key
    AWS_REGION=str             # Регион, если необходимо
    AWS_BUCKET=str             # Bucket по умолчанию

Данные переменные можно переопределить:

```python
from s3.settings import settings

settings.AWS_BUCKET = "some_bucket"
```

> **!! ВНИМАНИЕ !!**
После создания подключения по умолчанию, изменение параметров settings для него игнорируется (выполняется кеширование).

Для открытия соединения используются `s3` и `async_s3` функции.

Загрузка и скачивание файлов требует:

* Для синхронного режима требуется синхронный файловый дескриптор открытый в бинарном режиме.
* Для асинхронного режима требуется бинарный файловый дескриптор aiofiles

```python
from s3 import s3, async_s3

# Синхронный вариант
client = s3()
if client.has_file("s3_filename"):
    pass

# Асинхронный вариант
client = async_s3

async with client() as conn:
    if conn.has_file("s3_filename"):
        pass

```

## Лицензия

___

ConnectKit S3 распространяется под [лицензией MIT](./LICENSE).