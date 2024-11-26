import datetime
import logging
import os

from azure.storage.blob import BlobClient

AZURE_SYNKER_BLOB_CNX_STRING = os.getenv("AZURE_SYNKER_BLOB_CNX_STRING")
AZURE_SYNKER_BLOB_CONTAINER = os.getenv("AZURE_SYNKER_BLOB_CONTAINER")

logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
logger.setLevel(logging.WARNING)


def upload_to_azure(
    full_path_to_file: str,
    local_file_name: str,
    container_name: str = str(AZURE_SYNKER_BLOB_CONTAINER),
    connection_string: str = str(AZURE_SYNKER_BLOB_CNX_STRING),
) -> str:
    """upload file to Azure storage

    Args:
        full_path_to_file (str): file path to upload to Azure storage
        local_file_name (str): file name to upload to Azure storage
        container_name (str, optional): Azure storage container name . Defaults to str(AZURE_SYNKER_BLOB_CONTAINER).
        connection_string (str, optional): Azure storage connection string . Defaults to str(AZURE_SYNKER_BLOB_CNX_STRING).

    Returns:
        str: file url
    """
    blob = BlobClient.from_connection_string(
        conn_str=connection_string,
        container_name=container_name,
        blob_name=full_path_to_file,
    )

    with open(local_file_name, "rb", encoding="utf8") as data:
        blob.upload_blob(data)

    return f"https://{blob.account_name}.blob.core.windows.net/{container_name}/{full_path_to_file}"


def upload_bytes_to_azure(
    full_path_to_file: str,
    content_file_txt: str,
    container_name: str = str(AZURE_SYNKER_BLOB_CONTAINER),
    connection_string: str = str(AZURE_SYNKER_BLOB_CNX_STRING),
) -> str:
    """
    Save bytes to Azure blob
    :param connection_string:
    :param full_path_to_file:
    :param content_file_txt:
    :param container_name:
    :return: url
    """

    blob = BlobClient.from_connection_string(
        conn_str=connection_string,
        container_name=container_name,
        blob_name=full_path_to_file,
    )
    blob.upload_blob(
        content_file_txt,
        if_unmodified_since=datetime.datetime.now(tz=datetime.timezone.utc),
    )

    return f"https://{blob.account_name}.blob.core.windows.net/{container_name}/{full_path_to_file}"


def get_blob_from_azure(
    local_file_name: str,
    full_path_to_file: str,
    container_name: str = str(AZURE_SYNKER_BLOB_CONTAINER),
    connection_string: str = str(AZURE_SYNKER_BLOB_CNX_STRING),
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
