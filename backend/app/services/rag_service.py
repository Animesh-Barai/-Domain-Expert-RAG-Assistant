"""RAG service for document Q&A."""

from typing import AsyncGenerator, List

import google.generativeai as genai
from cohere import Rerank
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import NodeWithScore
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini
from llama_index.vector_stores.pinecone import PineconeVectorStore

from app.core.config import get_settings
from app.services.storage_service import StorageService

settings = get_settings()


class RAGService:
    """Service for Retrieval-Augmented Generation."""

    def __init__(self):
        """Initialize the RAG service."""
        # Initialize Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.embed_model = GeminiEmbedding(
            model_name=settings.GEMINI_EMBEDDING_MODEL,
            api_key=settings.GEMINI_API_KEY,
        )
        self.llm = Gemini(
            model_name=settings.GEMINI_CHAT_MODEL,
            api_key=settings.GEMINI_API_KEY,
        )

        # Initialize Pinecone vector store
        self.vector_store = PineconeVectorStore(
            api_key=settings.PINECONE_API_KEY,
            index_name=settings.PINECONE_INDEX_NAME,
            environment=settings.PINECONE_ENVIRONMENT,
        )

        # Initialize Cohere reranker
        self.reranker = Rerank(api_key=settings.COHERE_API_KEY)

        # Initialize storage service
        self.storage_service = StorageService()

        # Create index
        self.index = VectorStoreIndex.from_vector_store(
            self.vector_store,
            embed_model=self.embed_model,
        )

    async def stream_response(
        self,
        message: str,
        user_id: str,
        chat_id: str,
    ) -> AsyncGenerator[str, None]:
        """Stream response for a user message."""
        try:
            # 1. Retrieve relevant documents
            relevant_docs = await self._retrieve_relevant_documents(
                message=message,
                user_id=user_id,
                top_k=20,  # Retrieve more for reranking
            )

            if not relevant_docs:
                yield "I'm sorry, I couldn't find any relevant information in your documents to answer your question."
                return

            # 2. Rerank documents
            reranked_docs = await self._rerank_documents(
                query=message,
                documents=relevant_docs,
                top_n=5,  # Keep top 5 after reranking
            )

            # 3. Generate response with context
            context = self._format_context(reranked_docs)
            prompt = self._build_prompt(message, context)

            # 4. Stream response
            async for chunk in self._generate_streaming_response(prompt):
                yield chunk

        except Exception as e:
            yield f"I'm sorry, an error occurred while processing your question: {str(e)}"

    async def _retrieve_relevant_documents(
        self,
        message: str,
        user_id: str,
        top_k: int = 10,
    ) -> List[NodeWithScore]:
        """Retrieve relevant documents using vector search."""
        # Create a query engine
        query_engine = self.index.as_query_engine(
            llm=self.llm,
            similarity_top_k=top_k,
            filters={"user_id": user_id},  # Only search user's documents
        )

        # Perform query
        response = await query_engine.aquery(message)

        # Return source nodes
        return response.source_nodes if hasattr(response, 'source_nodes') else []

    async def _rerank_documents(
        self,
        query: str,
        documents: List[NodeWithScore],
        top_n: int = 5,
    ) -> List[NodeWithScore]:
        """Rerank documents using Cohere."""
        if not documents:
            return []

        # Extract text from documents
        doc_texts = [doc.node.get_content() for doc in documents]

        try:
            # Rerank with Cohere
            rerank_results = self.reranker.reRank(
                model="rerank-english-v2.0",
                query=query,
                documents=doc_texts,
                topN=top_n,
                returnDocuments=False,
            )

            # Update scores and reorder
            reranked_docs = []
            for result in rerank_results.results:
                idx = result.index
                score = result.relevanceScore
                doc = documents[idx]
                doc.score = score
                reranked_docs.append(doc)

            return reranked_docs

        except Exception as e:
            print(f"Reranking failed: {e}")
            # Return original documents if reranking fails
            return documents[:top_n]

    def _format_context(self, documents: List[NodeWithScore]) -> str:
        """Format documents as context for the prompt."""
        context_parts = []

        for i, doc in enumerate(documents, 1):
            content = doc.node.get_content()
            metadata = doc.node.metadata

            # Add source information
            source = metadata.get("filename", "Unknown")
            page = metadata.get("page_number", "N/A")

            context_parts.append(
                f"Document {i} (Source: {source}, Page: {page}):\n{content}\n"
            )

        return "\n".join(context_parts)

    def _build_prompt(self, question: str, context: str) -> str:
        """Build prompt with question and context."""
        prompt = f"""You are a helpful AI assistant. Use the provided context to answer the user's question accurately and comprehensively.

Context:
{context}

Question: {question}

Instructions:
1. Use only the information provided in the context to answer the question
2. If the context doesn't contain the answer, say "I don't have enough information to answer this question based on the provided documents"
3. Provide specific details and cite sources when possible
4. Be concise but thorough

Answer:"""

        return prompt

    async def _generate_streaming_response(
        self,
        prompt: str,
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response from Gemini."""
        # Create Gemini model with streaming enabled
        model = genai.GenerativeModel(settings.GEMINI_CHAT_MODEL)

        # Generate content with streaming
        response = await model.generate_content_async(prompt, stream=True)

        # Yield chunks
        async for chunk in response:
            if chunk.text:
                yield chunk.text

    async def add_document_to_index(
        self,
        document_id: str,
        content: str,
        metadata: dict,
    ) -> None:
        """Add document content to vector index."""
        # This would be called by the document processing worker
        # Implementation would depend on how you structure your document chunks
        pass

    async def delete_document_from_index(self, document_id: str) -> None:
        """Delete document from vector index."""
        # This would be called when a document is deleted
        # Implementation would use Pinecone's delete API
        pass