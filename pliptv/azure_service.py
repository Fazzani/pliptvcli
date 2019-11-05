import os
from typing import Optional

from azure.storage.blob import BlobClient

AZURE_SYNKER_BLOB_CNX_STRING = os.getenv("AZURE_SYNKER_BLOB_CNX_STRING")
AZURE_SYNKER_BLOB_CONTAINER = os.getenv("AZURE_SYNKER_BLOB_CONTAINER")


def upload_to_azure(
    full_path_to_file: str,
    local_file_name: str,
    container_name: Optional[str] = AZURE_SYNKER_BLOB_CONTAINER,
    connection_string: Optional[str] = AZURE_SYNKER_BLOB_CNX_STRING,
) -> None:
    blob = BlobClient.from_connection_string(
        conn_str=connection_string,
        container_name=container_name,
        blob_name=full_path_to_file,
    )

    with open(local_file_name, "rb") as data:
        blob.upload_blob(data)


def get_blob_from_azure(
    local_file_name: str,
    full_path_to_file: str,
    container_name: Optional[str] = AZURE_SYNKER_BLOB_CONTAINER,
    connection_string: Optional[str] = AZURE_SYNKER_BLOB_CNX_STRING,
) -> None:
    blob = BlobClient.from_connection_string(
        conn_str=connection_string,
        container_name=container_name,
        blob_name=full_path_to_file,
    )

    with open(local_file_name, "wb") as my_blob:
        stream = blob.download_blob()
        data = stream.readall()
        my_blob.write(data)
