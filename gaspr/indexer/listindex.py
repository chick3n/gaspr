from gaspr.persistent.base import BasePersistentStorage
from gaspr.llms.base import BaseLlm
from gaspr.indexer.models import LlamaIndexResponse, LlamaIndexRefresh
from gaspr.indexer.base import BaseIndexer
from gaspr.persistent.models import File
from llama_index import GPTListIndex, Document, QueryMode
from typing import Any

class ListIndexer(BaseIndexer):
    """
    Llama-Index wrapper

    Args:
        llm (BaseLlm): 
        storage (BasePersistentStorage): persistent storage class for managing index document(s)
    """
    def __init__(self, 
                 llm: BaseLlm,
                 storage: BasePersistentStorage,
                 **kwargs: Any) -> None:
        super().__init__(llm, storage, index_name="index_list.json", **kwargs)
        self.index:GPTListIndex = None

        self.__validate_params__()

    def __validate_params__(self):
        """ validate indexer has necessary params to work """
        issues = []

        if len(issues) > 0:
            raise ValueError('\n'.join(issues))

    async def initialize(self) -> None:
        if self.index_init:
            raise Exception('Cannot re-initialize indexer. Create a new instance instead or call load_documents to refresh index from storage')
        
        if self.use_saved_index:
            index_file = await self._aget_index()
            if index_file is not None:
                self.index = GPTListIndex.load_from_string(index_file.content, 
                                                                   service_context=self.llm.get_servicecontext())
        
        if self.index is None:
            documents = await self.storage._aget_files()
            idocuments = [Document(document.content) for document in documents if not document.name == self.index_name]
            self.index = GPTListIndex.from_documents(idocuments, service_context=self.llm.get_servicecontext())           

        self.index_init = True

    def query(self, prompt: str, **kwargs: Any) -> LlamaIndexResponse:
        self._fail_on_init()

        if kwargs.get('summarize', False):
            return self.__sumquery(prompt, **kwargs)
        
        response = self.index.query(prompt)
        return LlamaIndexResponse(text=str(response)) 

    def __sumquery(self, prompt: str, **kwargs: Any) -> LlamaIndexResponse:
        self._fail_on_init()
        
        response = self.index.query(prompt, mode=QueryMode.SUMMARIZE)
        return LlamaIndexResponse(text=str(response))
        