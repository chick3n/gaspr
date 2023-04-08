import abc
from typing import List
from gaspr.persistent.models import File

class BasePersistentStorage(metaclass=abc.ABCMeta):
    """ persistent storage base class interface """
    def __init__(self, **kwargs) -> None:
        pass

    @abc.abstractmethod
    async def _aget_files(self, path: str = None) -> List[File]:
        """ async get list of files from location """
        pass
    
    @abc.abstractmethod
    async def _adelete_file(self, filename: str, path: str = None) -> None:
        """ async delete file from location """

    @abc.abstractmethod
    async def _aupload_file_content(self, filename:str, content:str, path: str = None, overwrite: bool = True) -> None:
        """ upload file to location """
        pass

    @abc.abstractmethod
    async def _aupload_file(self, file: File, path: str = None, overwrite: bool = True) -> None:
        """ upload file to location """
        pass

    @abc.abstractmethod
    async def _aget_file(self, filename: str, path: str = None) -> File:
        """ get file from location """
        pass

    @abc.abstractmethod
    async def _aexists(self, filename: str, path: str = None) -> bool:
        pass