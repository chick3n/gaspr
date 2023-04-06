from llama_index import ServiceContext, LLMPredictor, LangchainEmbedding, PromptHelper
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import AzureOpenAI as AOAILangChain
from gaspr.llms.base import BaseLlm
import os
from typing import Any
import openai

class AzureOpenAI(BaseLlm):
    """
    Args:
        deployment (str): azure deployment id of openai model to use
    KwArgs:
        embedding_model? (str): the deployment id for the embedding model to use in Azure OpenAI
        apitype? (str): set the azure open ai type, defaults to azure
        version? (str): set the azure open ai version, defaults to 2023-03-15-preview
        max_input_size? (int): set the max input size for the prompter, defaults 2048
        num_output? (int): set the num output size for completion tokens, defaults 48
        max_chunk_overlap? (int): set the overlap chunk amount from embeddings, defaults 20
    Required:
        ENVIRONMENT VARIABLES:
            - OPENAI_BASEURI
            - OPENAI_KEY
    """
    def __init__(self, 
                 deployment_id: str, 
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.deployment_id = deployment_id
        self.embedding_model = kwargs.get('embedding_model', None)
        self.api_type = kwargs.get('apitype', "azure")
        self.api_base = os.getenv('OPENAI_BASEURI')
        self.api_version = kwargs.get('version', "2023-03-15-preview")
        self.api_key = os.getenv('OPENAI_KEY')
        self.max_input_size = kwargs.get('max_input_size', 2048)
        self.num_output = kwargs.get('num_output', 48)
        self.max_chunk_overlap = kwargs.get('max_chunk_overlap', 20) 

        # OpenAI configuration for Azure
        openai.api_type = self.api_type
        openai.api_base = self.api_base
        openai.api_version = self.api_version
        openai.api_key = self.api_key

        # Set OpenAI Key environ var that packages use just in case
        os.environ['OPENAI_API_KEY'] = self.api_key

        self.__validate_params__()

    def __validate_params__(self) -> None:
        """Validate all required params are set"""
        issues = []

        if self.deployment_id is None:
            issues.append('A Azure deployment id for model of choice is required.')
        if self.api_base is None:
            issues.append('Missing Azure OpenAI Base Uri, set env OPENAI_BASEURI.')
        if self.api_key is None:
            issues.append('Missing Azure OpenAI Key, set env OPENAI_KEY.')

        if len(issues) > 0:
            raise ValueError('\n'.join(issues))

    def get_prompthelper(self, **kwargs: Any) -> PromptHelper:
        """
        Return a prompt helper for LLM
        KwArgs:
            max_input_size? (int): set the max input size for the prompter, defaults 2048
            num_output? (int): set the num output size for completion tokens, defaults 48
            max_chunk_overlap? (int): set the overlap chunk amount from embeddings, defaults 20
        """
        max_input_size = kwargs.get('max_input_size', self.max_input_size)
        num_output = kwargs.get('num_output', self.num_output)
        max_chunk_overlap = kwargs.get('max_chunk_overlap', self.max_chunk_overlap)

        return PromptHelper(max_input_size, num_output, max_chunk_overlap)
    
    def get_embedding_llm(self) -> None:
        """ return an embedding model """

        if self.embedding_model is None:
            raise ValueError('Embedding deployment id is not defined.')

        return LangchainEmbedding(OpenAIEmbeddings(
            model=self.embedding_model
        ))
    
    def get_predictor(self) -> LLMPredictor:
        return LLMPredictor(llm=AOAILangChain(deployment_name=self.deployment_id, model_kwargs={
            "api_key": self.api_key,
            "api_base": self.api_base,
            "api_type": self.api_type,
            "api_version": self.api_version,
            "deployment_id": self.deployment_id,
            "engine": self.deployment_id,
        }))

    def get_servicecontext(self, **kwargs: Any) -> ServiceContext:
        return ServiceContext.from_defaults(
            llm_predictor=self.get_predictor(),
            embed_model=self.get_embedding_llm(),
            prompt_helper=self.get_prompthelper(**kwargs)
        )


