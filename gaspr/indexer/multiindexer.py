from gaspr.indexer.base import BaseIndexer
from gaspr.indexer import ListIndexer, VectorIndexer
from gaspr.persistent import File
from typing import Any
import asyncio
import uuid

class MultiIndexer():
    """Wrapper to hold multiple indexes"""
    indices:dict[str,BaseIndexer] = {}

    async def add_index(self, indexer:BaseIndexer, key:str = None, **kwargs:Any) -> str:
        """Add an index to the wrapper, return the unique identifier for index"""
        initialize = kwargs.get('initialize', False)
        key = key or str(uuid.uuid4())
        
        self.indices[key] = indexer
        if initialize:
            await indexer.initialize()

    @property
    def get_index(self, key:str) -> BaseIndexer:
        if key in self.indices:
            return self.indices[key]
        
        raise ValueError(f'{str(key)} index does not exist.')

    async def ainsert_file(self, file:File, **kwargs) -> None:
        """Add this file to all indexes"""
        overwrite = kwargs.get('overwrite', True)

        for _, indexer in self.indices.items():
            await indexer.aadd_file(file, overwrite=overwrite)

    async def aremove_file(self, filename:str, doc_id:str = None) -> None:
        """Remove file from all indices"""
        routines = []
        for _, indexer in self.indices.items():
            routines.append(asyncio.create_task(indexer.aremove_file(filename, doc_id)))

        await asyncio.wait(routines)

    async def asave_indices(self) -> None:
        """Save all indices"""
        tasks = [asyncio.create_task(indexer.asave()) for _, indexer in self.indices.items()]
        await asyncio.wait(tasks)


