from gaspr.persistent.base import BasePersistentStorage
from gaspr.llms.base import BaseLlm
from gaspr.indexer.models import LlamaIndexResponse, LlamaIndexRefresh
from gaspr.indexer.base import BaseIndexer
from gaspr.persistent.models import File
from llama_index import GPTSimpleVectorIndex, Document
from typing import Any

class VectorIndexer(BaseIndexer):
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
        super().__init__(llm, storage, index_name="index_vector.json", **kwargs)
        self.index:GPTSimpleVectorIndex = None
        self.__validate_params__()

    def __validate_params__(self):
        """ validate indexer has necessary params to work """
        issues = []

        if self.llm.embedding_model is None:
            issues.append('Indexer requires an embedding model to be defined.')

        if len(issues) > 0:
            raise ValueError('\n'.join(issues))

    async def initialize(self) -> None:
        if self.index_init:
            raise Exception('Cannot re-initialize indexer. Create a new instance instead or call load_documents to refresh index from storage')
        
        if self.use_saved_index:
            index_file = await self._aget_index()
            if index_file is not None:
                self.index = GPTSimpleVectorIndex.load_from_string(index_file.content, 
                                                                   service_context=self.llm.get_servicecontext())
        
        if self.index is None:
            documents = await self.storage._aget_files()
            idocuments = [Document(document.content) for document in documents if not document.name == self.index_name]
            self.index = GPTSimpleVectorIndex.from_documents(idocuments, service_context=self.llm.get_servicecontext())           

        self.index_init = True