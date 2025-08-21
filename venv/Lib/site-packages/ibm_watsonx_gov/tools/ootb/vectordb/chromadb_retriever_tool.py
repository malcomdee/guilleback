# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Annotated, Any, Optional, Type

from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr

from ibm_watsonx_gov.tools.schemas.vectordb_retrieval_schema import \
    ChromaDbRetrieverConfig


class RetrievalToolInput(BaseModel):
    query: Annotated[str, Field(description="Search query")]
    n_results: Annotated[Optional[int], Field(
        description="Number of results to return", default=5)]
    where: Annotated[Optional[dict], Field(
        description="A dict used to filter results by the metadata. E.g. {'source': 'student_info'} ", default=None)]
    where_document: Annotated[Optional[dict], Field(
        description="A dict used to filter by the documents. E.g. {$contains: 'My Text'}.", default=None)]


class ChromaDBRetrievalTool(BaseTool):
    """
    Tool for searching the ChromaDB vector database.

    Examples:
        Basic usage
            .. code-block:: python

                case-1 : With path 
                retriever_tool_config = {
                    "path": "./medium_db",
                    "collection_name":  "medium_articles",
                    "embedding_function": embedding_functions.OpenAIEmbeddingFunction(),
                    "n_results": 2
                }
}
                chromadb_tool = ChromaDBRetrievalTool(**retriever_tool_config)
                chromadb_tool.invoke({"query": "What is concept drift?"})
    """

    name: str = "chromadb_retrieval_tool"
    description: str = "Search ChromaDB vector database and return the top-k results"
    args_schema: Type[BaseModel] = RetrievalToolInput

    _retriever: any = PrivateAttr()
    _config = PrivateAttr()

    def __init__(self, **kwargs):
        """
        Arguments for creating a Chromadb retrieval tool which connects to a local or remote ChromaDB server.

        Args:
            path: Path to the database
            host: The hostname of the Chroma server. Defaults to "localhost". Required if path is not provided.
            port: The port of the Chroma server. Defaults to "8000". Required if path is not provided
            ssl: Whether to use SSL to connect to the Chroma server. Defaults to False.
            headers: A dictionary of headers to send to the Chroma server. Defaults to {}.
            settings: A dictionary of settings to communicate with the chroma server. Chromadb Settings object
            tenant: The tenant to use for this client. Defaults to the default tenant.
            database: The database to use for this client. Defaults to the default database.
            collection_name: Name of the collection where documents are stored
            embedding_function: Optional function to use to embed documents.
                                Uses the default embedding function if not provided.
            n_results: Optional number of results to return                    
        """
        super().__init__(**kwargs)

        from ibm_watsonx_gov.tools.utils.package_utils import \
            install_and_import_packages

        install_and_import_packages(["chromadb"])
        self._config = ChromaDbRetrieverConfig(**kwargs)
        self._validate_and_create_retriever(self._config)

        self._collection = self._retriever.get_collection(
            name=self._config.collection_name, embedding_function=self._config.embedding_function)

    def _run(self, query, run_manager: Optional[CallbackManagerForToolRun] = None, **kwargs):
        """Performs a Chromadb vector search and returns the top n_results content"""

        where = None
        where_document = None

        results = self._collection.query(
            query_texts=[query],
            where=where,
            where_document=where_document,
            n_results=self._config.n_results
        )

        return results['documents']

    def _validate_and_create_retriever(self, config: ChromaDbRetrieverConfig):
        import chromadb
        if config.path != None:
            self._retriever = chromadb.PersistentClient(config.path)
        else:
            from chromadb.config import DEFAULT_DATABASE, DEFAULT_TENANT
            tenant = config.tenant or DEFAULT_TENANT
            database = config.database or DEFAULT_DATABASE
            self._retriever = chromadb.HttpClient(host=config.host, port=config.port, ssl=config.ssl, headers=config.headers,
                                                  settings=config.settings, tenant=tenant, database=database)
