from abc import ABC, abstractmethod
from gaspr.persistent.base import BasePersistentStorage
from gaspr.llms.base import BaseLlm
from gaspr.indexer.models import LlamaIndexResponse, LlamaIndexRefresh
from gaspr.persistent.models import File
from llama_index.indices.base import BaseGPTIndex, Document
from typing import Any

class BaseIndexer(ABC):
    """
    
    KwArgs:
        index_name? (str): override the index file name to save as, defaults to index.json
        use_saved_index? (bool): load existing index if storage instance has index_name present, defaults True
    """
    def __init__(self,
                 llm: BaseLlm,
                 storage: BasePersistentStorage,
                 **kwargs: Any) -> None:
        self.llm = llm
        self.storage = storage
        self.index_name = kwargs.get('index_name', 'index.json')
        self.use_saved_index = kwargs.get('use_saved_index', True)
        self.index:BaseGPTIndex = None
        self.index_init = False
        self.index_folder = kwargs.get('index_folder', 'indices')
    
    @classmethod
    async def create(cls, 
                     llm: BaseLlm, 
                     storage: BasePersistentStorage, 
                     **kwargs: Any):
        self = cls(llm, storage, **kwargs)
        await self.initialize()
        return self
    
    @property
    def _storage(self) -> BasePersistentStorage:
        return self.storage
    
    @abstractmethod
    async def initialize(self) -> None:
        pass
    
    def _fail_on_init(self):
        """helper to throw if index not initialized"""
        if not self.index_init:
            raise Exception('Initialize index before using indexer.')
        
    async def _aget_index(self) -> File | None:
        """retrieve the index if exists"""
        if await self.storage._aexists(self.index_name, self.index_folder):
            return await self.storage._aget_file(self.index_name, self.index_folder)
        return None
        
    async def refresh(self) -> LlamaIndexRefresh:
        """refresh the documents in the index with new or changed documents
        Todo: delete documents no longer existing that were still in index
        llamaindex index refresh doesnt work as expected """
        self._fail_on_init()
        
        documents = await self.storage._aget_files()
        #self.index.refresh([Document(document.content) for document in documents if not document.name == self.index_name])

    def query(self, prompt:str, **kwargs: Any) -> LlamaIndexResponse:
        self._fail_on_init()
        
        response = self.index.query(prompt)
        return LlamaIndexResponse(text=str(response))

    async def aquery(self, prompt:str, **kwargs: Any) -> LlamaIndexResponse:
        self._fail_on_init()

        response = await self.index.aquery(prompt)
        return LlamaIndexResponse(text=str(response))

    async def asave(self) -> None:
        """ Save index to storage system """
        self._fail_on_init()

        await self.storage._aupload_file(File(
            self.index_name,
            self.index.save_to_string()
        ), self.index_folder)

    async def adelete(self) -> None:
        """ Delete index """
        self._fail_on_init()

        await self.storage._adelete_file(self.index_name)

    async def aadd_file(self, file:File, overwrite:bool=True) -> str:
        await self.storage._aupload_file(file, overwrite=overwrite)
        document = Document(file.content)
        self.index.insert(document=document)
        return document.get_doc_id()

    async def aremove_file(self, filename:str, doc_id:str = None) -> None:
        await self.storage._adelete_file(filename)
        self.index.delete(doc_id or filename)