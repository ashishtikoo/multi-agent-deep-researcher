"""
Contextual Retriever Agent – Pulls data from research papers, news, reports, and APIs.
"""

from pathlib import Path
from typing import Optional
from utils.file_reader import read_file
from utils.search import web_search, academic_search
from config import settings
from models import Source, SourceType


class RetrieverAgent:
    """
    The Contextual Retriever Agent is responsible for gathering information
    from multiple sources: web search, academic databases, news APIs, and reports.
    """

    def __init__(self, llm_model: Optional[str] = None):
        self.llm_model = llm_model

    def generate_search_queries(self, research_query: str, uploaded_docs: Optional[list[dict]] = None) -> list[dict]:
        """Generate targeted search queries for the research topic.
        Uses direct, well-crafted queries instead of LLM-generated ones for reliability."""
        queries = [
            {"query": research_query, "source_type": "web"},
            {"query": f"{research_query} latest research 2024 2025", "source_type": "academic"},
            {"query": f"{research_query} analysis and findings", "source_type": "web"},
            {"query": f"{research_query} news", "source_type": "web"},
            {"query": f"{research_query} studies and evidence", "source_type": "academic"},
        ]
        return queries

    def retrieve(self, research_query: str, max_hops: int = 3, uploaded_documents: Optional[list[dict]] = None) -> list[Source]:
        """
        Perform multi-hop retrieval: generate queries, search, and expand.
        Includes uploaded document content as additional sources.

        Args:
            research_query: The research question/topic.
            max_hops: Number of retrieval hops.
            uploaded_documents: List of dicts with 'name' and 'file_path' keys.
        """
        all_sources: list[Source] = []
        seen_urls = set()

        # Add uploaded documents as sources first
        if uploaded_documents:
            for doc in uploaded_documents:
                doc_name = doc.get("name", "Unknown")
                file_path = doc.get("file_path", "")
                if file_path and Path(file_path).exists():
                    content = read_file(file_path)
                    source = Source(
                        title=f"📄 Uploaded Document: {doc_name}",
                        url=f"file://{doc_name}",
                        source_type=SourceType.DOCUMENT,
                        snippet=content[:500] + "..." if len(content) > 500 else content,
                        content=content,
                    )
                    all_sources.append(source)
                    seen_urls.add(f"file://{doc_name}")

        queries = self.generate_search_queries(research_query, uploaded_documents)

        for query_info in queries:
            query = query_info["query"]
            source_type = query_info.get("source_type", "web")

            if source_type == "academic":
                results = academic_search(query, max_results=5)
            else:
                results = web_search(query, max_results=5)

            for source in results:
                if source.url not in seen_urls:
                    seen_urls.add(source.url)
                    all_sources.append(source)

        if max_hops > 1 and len(all_sources) > 0:
            key_topics = self._extract_key_topics(research_query)
            for topic in key_topics[:2]:
                followup = web_search(topic, max_results=3)
                for source in followup:
                    if source.url not in seen_urls:
                        seen_urls.add(source.url)
                        all_sources.append(source)

        return all_sources[:settings.max_sources_per_query]

    def _extract_key_topics(self, research_query: str) -> list[str]:
        """Extract key topics from the research query for follow-up searches."""
        # Extract meaningful keywords from the query
        keywords = [word.strip() for word in research_query.lower().split() if len(word) > 3]
        # Build follow-up queries from key terms
        topics = []
        for kw in keywords[:3]:
            topics.append(f"{kw} research evidence")
            topics.append(f"{kw} studies")
        return topics[:4]

    def retrieve_and_summarize(self, research_query: str) -> dict:
        """Retrieve sources and provide a brief summary of what was found."""
        sources = self.retrieve(research_query)
        return {
            "query": research_query,
            "sources_found": len(sources),
            "sources": [
                {
                    "title": s.title,
                    "url": s.url,
                    "type": s.source_type.value,
                    "snippet": s.snippet[:300],
                }
                for s in sources
            ],
        }
