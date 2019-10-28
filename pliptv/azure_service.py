import os
from typing import Optional

from azure.storage.blob import BlockBlobService

AZURE_SYNKER_BLOB_CONTAINER = os.getenv("AZURE_SYNKER_BLOB_CONTAINER")


def upload_to_azure(
    full_path_to_file: str,
    local_file_name: str,
    container_name: Optional[str] = AZURE_SYNKER_BLOB_CONTAINER,
) -> None:
    block_blob_service = BlockBlobService(
        account_name="synker", account_key=os.getenv("AZURE_SYNKER_BLOB_KEY")
    )
    block_blob_service.create_blob_from_path(
        container_name, local_file_name, full_path_to_file
    )


def upload_txt_to_azure(
    full_path_to_file: str,
    content_file_txt: str,
    container_name: Optional[str] = AZURE_SYNKER_BLOB_CONTAINER,
) -> str:
    """
    Save text to Azure blob
    :param full_path_to_file:
    :param content_file_txt:
    :param container_name:
    :return: url
    """
    account_name = os.getenv("AZURE_SYNKER_ACCOUNT_NAME")
    blob_container = os.getenv("AZURE_SYNKER_BLOB_CONTAINER")
    block_blob_service = BlockBlobService(
        account_name=account_name, account_key=os.getenv("AZURE_SYNKER_BLOB_KEY")
    )
    block_blob_service.create_blob_from_text(
        container_name, full_path_to_file, content_file_txt
    )
    return f"https://{account_name}.blob.core.windows.net/{blob_container}/{full_path_to_file}"


def get_blob_from_azure(
    local_file_name: str,
    full_path_to_file: str,
    container_name: Optional[str] = AZURE_SYNKER_BLOB_CONTAINER,
) -> None:
    block_blob_service = BlockBlobService(
        account_name="synker", account_key=os.getenv("AZURE_SYNKER_BLOB_KEY")
    )
    block_blob_service.get_blob_to_path(
        container_name, local_file_name, full_path_to_file
    )