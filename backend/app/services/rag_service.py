"""RAG service for document Q&A using Local Ollama and ChromaDB."""

from typing import AsyncGenerator, List, Union, Dict, Any

import os
import json
import chromadb
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.schema import NodeWithScore, TextNode
from llama_index.core.vector_stores.types import MetadataFilters, MetadataFilter, FilterOperator
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore

from app.core.config import get_settings
from app.services.storage_service import StorageService

settings = get_settings()


class RAGService:
    """Service for Retrieval-Augmented Generation using Local Ollama & ChromaDB."""

    def __init__(self):
        """Initialize the RAG service."""
        # --- LOCAL LLM (OLLAMA) ---
        self.llm = Ollama(
            model="llama3.2:1b", 
            request_timeout=120.0
        )
        # --- LOCAL EMBEDDINGS ---
        self.embed_model = OllamaEmbedding(
            model_name="nomic-embed-text"
        )

        # --- LOCAL VECTOR STORAGE (CHROMADB) ---
        # Data is persisted locally in the backend/chroma_db directory
        db_path = os.path.join(os.getcwd(), "chroma_db")
        db = chromadb.PersistentClient(path=db_path)
        chroma_collection = db.get_or_create_collection("aura_intelligence")
        
        self.vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

        # Initialize storage service (MinIO)
        self.storage_service = StorageService()

        # Initialize storage context
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

        try:
            # Create/Load index
            self.index = VectorStoreIndex.from_vector_store(
                self.vector_store,
                embed_model=self.embed_model,
            )
        except Exception as e:
            print(f"CRITICAL: Failed to load vector index: {str(e)}")
            self.index = None

    async def stream_response(
        self,
        message: str,
        user_id: str,
        chat_id: str,
    ) -> AsyncGenerator[Union[str, Dict[str, Any]], None]:
        """Stream response for a user message."""
        if self.index is None:
            yield "The neural intelligence vault is currently undergoing maintenance. Please try again in 60 seconds."
            return

        try:
            # 1. Retrieve relevant documents
            relevant_docs = await self._retrieve_relevant_documents(
                message=message,
                user_id=user_id,
                top_k=10,
            )

            if not relevant_docs:
                yield "I'm sorry, I couldn't find any relevant information in your documents to answer your question."
                return

            # --- CITATION INJECTION (DEDUPLICATED) ---
            seen_sources = set()
            sources = []
            for doc in relevant_docs:
                unique_key = (doc.node.metadata.get("filename"), doc.node.metadata.get("page_number"))
                if unique_key not in seen_sources:
                    sources.append({
                        "id": doc.node.id_,
                        "filename": doc.node.metadata.get("filename", "Unknown Fragment"),
                        "page_number": doc.node.metadata.get("page_number", "N/A"),
                        "score": float(doc.score) if doc.score else 0.0
                    })
                    seen_sources.add(unique_key)
            
            # Emit metadata packet
            yield {"type": "metadata", "sources": sources[:4]} # Limit to top 4 unique sources for UI clarity

            # 2. Generate response with context
            context = self._format_context(relevant_docs)
            prompt = self._build_prompt(message, context)

            # 3. Stream response using Ollama
            async for chunk in self._generate_streaming_response(prompt):
                yield chunk

        except Exception as e:
            yield f"I'm sorry, an error occurred while processing your question: {str(e)}"

    async def _retrieve_relevant_documents(
        self,
        message: str,
        user_id: str,
        top_k: int = 6, # Reduced k for better prompt density
    ) -> List[NodeWithScore]:
        """Retrieve relevant documents using local vector search."""
        # Note: Chroma filters for user_id can be added to the retriever
        filters = MetadataFilters(
            filters=[
                MetadataFilter(key="user_id", value=str(user_id), operator=FilterOperator.EQ),
            ]
        )

        retriever = self.index.as_retriever(
            similarity_top_k=top_k,
            filters=filters,
        )

        nodes = await retriever.aretrieve(message)
        return nodes

    def _format_context(self, documents: List[NodeWithScore]) -> str:
        """Format documents as context for the prompt."""
        context_parts = []

        for i, doc in enumerate(documents, 1):
            content = doc.node.get_content()
            metadata = doc.node.metadata
            filename = metadata.get("filename", "Unknown")
            page = metadata.get("page_number", "N/A")

            # CRITICAL: We inject the filename DIRECTLY into the context so the LLM knows what it's reading
            context_parts.append(
                f"### [DOCUMENT SOURCE: {filename} | PAGE: {page}]\n{content}\n"
            )

        return "\n".join(context_parts)

    def _build_prompt(self, question: str, context: str) -> str:
        """Build prompt with question and context."""
        prompt = f"""SYSTEM: You are Aura, a high-precision Domain-Expert RAG Assistant. 
You are currently analyzing the user's uploaded documents.

CONTEXT FROM DOCUMENTS:
{context}

USER QUESTION: {question}

AURA RESPONSE:
YOU MUST PROVIDE AT LEAST 5 BULLET POINTS OF ANALYSIS. Do not be shallow. Go into the specific metrics and methodology found in the context.

## Analysis [TITLED BY TOPIC]
* Finding 1 with technical detail.
* Finding 2 with technical detail.
* Finding 3 with technical detail.
* Finding 4 with technical detail.
* Finding 5 with technical detail.

Now, answer the User Question using only the provided context. PROVIDE AT LEAST 5 BULLETS.

RESPONSE:"""

        return prompt

    async def _generate_streaming_response(
        self,
        prompt: str,
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response from Local Ollama."""
        response = await self.llm.astream_complete(prompt)

        async for chunk in response:
            if chunk.delta:
                yield chunk.delta

    async def add_document_to_index(
        self,
        nodes: List[TextNode],
    ) -> None:
        """Add parsed document nodes to local vector index."""
        if not nodes:
            return

        # Use the established storage context to add nodes to Chroma
        self.index = VectorStoreIndex(
            nodes,
            storage_context=self.storage_context,
            embed_model=self.embed_model,
        )

    async def delete_document_from_index(self, document_id: str, user_id: str) -> None:
        """Delete all nodes associated with a document_id and user_id from local index."""
        # ChromaDB deletion logic (simplified: re-initialize retriever if needed)
        # Note: For production, we'd use chroma_collection.delete(where=...)
        pass