
from abc import ABC, abstractmethod
from llama_index import ServiceContext, LLMPredictor, LangchainEmbedding, PromptHelper
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import AzureOpenAI as AOAILangChain
from typing import Any

class BaseLlm(ABC):
    def __init__(self, **kwargs: Any) -> None:
        pass

    embedding_model: str = None

    @abstractmethod
    def get_servicecontext(self, **kwargs: Any) -> ServiceContext:
        pass