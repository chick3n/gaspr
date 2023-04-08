from gaspr.persistent.base import BasePersistentStorage
from gaspr.persistent.models import File
from typing import Any, List
import os
from pathlib import Path
import logging
import aiofiles

class FileSystem(BasePersistentStorage):
    """
    Local file system storage class

    Args:
        path (str): path to where the class should access files
        create_missing? (bool): create the folder(s) if missing from the path
    """
    def __init__(self, base_path:str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.base_path = Path(base_path)
        self.options = kwargs
        self.__create_missing()

        if not self.base_path.exists():
            raise ValueError(f'{base_path} does not exist')
        
    def __create_missing(self) -> None:
        """ Create any missing folders from the root path """
        if(self.options.get('create_missing', False)):
            #os.makedirs(self.base_path.resolve())
            self.base_path.mkdir(parents=True, exist_ok=True)

    async def _aget_files(self, path: str = None) -> List[File]:
        """ 
        get list of files from location 
        Args:
            path (str): path to the files from the base path
        """
        full_path = self.base_path.joinpath(path or '')
        if not full_path.resolve().exists():
            return []
        pathlist = full_path.glob("*")
        files:List[File] = []

        for pl in pathlist:
            if os.path.isdir(pl.resolve()):
                continue

            async with aiofiles.open(pl.resolve(), mode='r') as f:
                contents = await f.read()

            files.append(File(pl.name, contents))

        return files
    
    async def _adelete_file(self, filename: str, path: str = None) -> None:
        """
        async delete file from location
        Args:
            filename (str): files name
            path? (str): path within base_path if any 
        """
        full_path = self.base_path.joinpath(path or '', filename)
        if(full_path.exists() and os.path.isfile(full_path.resolve())):
            os.remove(full_path.resolve())

    async def _aupload_file_content(self, filename:str, content:str, path: str = None, overwrite: bool = True) -> None:
        """ 
        upload file to location 
        Args:
            file (File): file object for writing to filesystem
            path? (str): path within base_path if any
            overwrite? (bool): overwrite the file if it exists
        """
        await self._aupload_file(File(filename, content), path, overwrite)

    async def _aupload_file(self, file: File, path: str = None, overwrite: bool = True) -> None:
        """ 
        upload file to location 
        Args:
            file (File): file object for writing to filesystem
            path? (str): path within base_path if any
            overwrite? (bool): overwrite the file if it exists
        """
        full_path = self.base_path.joinpath(path or '')
        full_path.mkdir(exist_ok=True)
        
        if(full_path.joinpath(file.name).exists() and not overwrite):
            return
        
        async with aiofiles.open(full_path.joinpath(file.name).resolve(), mode='w') as f:
            await f.write(file.content)

    async def _aget_file(self, filename: str, path: str = None) -> File | None:
        """ 
        get file from location
        Args:
            filename (str): files name
            path? (str): path within base_path if any 
        """
        full_path = self.base_path.joinpath(path or '', filename)
        if full_path.exists():
            async with aiofiles.open(full_path.resolve(), mode='r') as f:
                contents = await f.read()
            return File(filename, contents)
        return None
    
    async def _aexists(self, filename: str, path: str = None) -> bool:
        """ check if a file exists """
        full_path = self.base_path.joinpath(path or '', filename)
        return full_path.exists()