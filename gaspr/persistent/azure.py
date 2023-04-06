from azure.storage.blob import BlobServiceClient
from azure.storage.blob.aio import BlobServiceClient as BlobServiceClientAIO
from azure.core.exceptions  import ResourceExistsError

from gaspr.persistent.base import BasePersistentStorage
from gaspr.persistent.models import File
from typing import Any, List
import os
import logging

class AzureStorage(BasePersistentStorage):
    """
    Azure Storage class for persistent storage using an Azure Storage Blob Service
    Can read, write, and delete blob files from provided container

    Required:
        ENVIRONMENT VARIABLES:
            - AZURE_STORAGE_CONN_STRING
            - AZURE_STORAGE_CONTAINER_NAME
    """
    def __init__(
            self,
            **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.conn_string = os.getenv("AZURE_STORAGE_CONN_STRING")
        self.container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

        if self.conn_string is None:
            raise ValueError('env AZURE_STORAGE_CONN_STRING missing')
        if self.container_name is None:
            raise ValueError('env AZURE_STORAGE_CONTAINER_NAME missing')


    async def _aget_files(self, path: str = None) -> List[File]:
        """
        Get all files from container with optional starts with text
        Args:
            path (str): prefix of blobs, this includes folder paths
        """
        bsc = BlobServiceClientAIO.from_connection_string(self.conn_string)

        files:List[File] = []
        async with bsc:
            cc = bsc.get_container_client(self.container_name)
            async for blob_properties in cc.list_blobs(path):
                bc = cc.get_blob_client(blob_properties)
                stream = await bc.download_blob()
                data = await stream.readall()

                files.append(File(name=blob_properties.name, content=data.decode('utf-8')))

        return files
    
    async def _adelete_file(self, filename: str, path: str = None) -> None:
        """
        Delete a file from azure storage container
        Args:
            filename (str): file name of the blob, can include the full path
            path? (str): prefix to the file name of the blob, this can include the folder path.
        """
        bsc = BlobServiceClientAIO.from_connection_string(self.conn_string)

        async with bsc:
            path = path or ''
            blob_name = path + filename
            bc = bsc.get_blob_client(self.container_name, blob_name)

            await bc.delete_blob()

    async def _aupload_file(self, file: File, path: str = None, overwrite: bool = True) -> None:
        """
        Upload a file to azure storage container
        Args:
            file (File): model of the file contents
            path? (str): prefix to the file name for the blob, this can be a folder path
            overwrite? (bool): overwrite the blob if it exists
        """
        bsc = BlobServiceClientAIO.from_connection_string(self.conn_string)
        async with bsc:
            path = path or ''
            blob_name = path + file.name
            bc = bsc.get_blob_client(self.container_name, blob_name)
            await bc.upload_blob(file.content, overwrite=overwrite)

    async def _aget_file(self, filename: str, path: str = None) -> File:
        """
        Download the blob from azure and decode to string utf-8
        Args:
            filename (str): name of the blob can include the full path
            path? (str): prefix to filename, can include the path
        """
        bsc = BlobServiceClientAIO.from_connection_string(self.conn_string)
        async with bsc:
            path = path or ''
            blob_name = path + filename
            bc = bsc.get_blob_client(self.container_name, blob_name)
            stream = await bc.download_blob()
            data = await stream.readall()

            return File(name=filename, content=data.decode('utf-8'))
        
    async def _aexists(self, filename: str, path: str = None) -> bool:
        """ check if a file exists """
        bsc = BlobServiceClientAIO.from_connection_string(self.conn_string)
        async with bsc:
            path = path or ''
            blob_name = path + filename
            bc = bsc.get_blob_client(self.container_name, blob_name)
            return await bc.exists()


    
    