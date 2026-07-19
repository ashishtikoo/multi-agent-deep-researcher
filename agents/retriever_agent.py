"""
Contextual Retriever Agent – Pulls data from research papers, news, reports, and APIs.
"""

import json
import tempfile
from pathlib import Path
from typing import Optional
from langchain_core.messages import SystemMessage, HumanMessage
from utils.llm import create_llm
from utils.search import web_search, academic_search, search_all_sources
from utils.file_reader import read_file
from config import settings
from models import Source, SourceType


class RetrieverAgent:
    """
    The Contextual Retriever Agent is responsible for gathering information
    from multiple sources: web search, academic databases, news APIs, and reports.
    """

    SYSTEM_PROMPT = """You are an expert research assistant specializing in information retrieval.
Your job is to identify the best search queries to find relevant, high-quality sources
for a given research topic.

Generate targeted search queries that would yield the most comprehensive and diverse
results across different source types (academic papers, news articles, industry reports,
and general web sources).

Return your response as a JSON object with the following structure:
{
    "queries": [
        {"query": "specific search query", "source_type": "web|academic|news|reports"},
        ...
    ]
}

Be specific and creative with your queries. Consider different angles and perspectives.
Generate up to 5 queries.
"""

    def __init__(self, llm_model: Optional[str] = None):
        self.llm = create_llm(llm_model)
        self.max_queries = 5

    def generate_search_queries(self, research_query: str, uploaded_docs: Optional[list[dict]] = None) -> list[dict]:
        """Generate targeted search queries for the research topic."""
        user_message = f"Research query: {research_query}"
        if uploaded_docs:
            user_message += f"\n\nAdditional context from uploaded documents ({len(uploaded_docs)} file(s)): {', '.join(d['name'] for d in uploaded_docs)}"

        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]
        response = self.llm.invoke(messages)
        content = response.content.strip()

        # Parse JSON response
        try:
            # Handle markdown code blocks
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            result = json.loads(content)
            return result.get("queries", [])
        except json.JSONDecodeError:
            # Fallback: generate default queries
            return [
                {"query": research_query, "source_type": "web"},
                {"query": f"{research_query} latest research", "source_type": "academic"},
                {"query": f"{research_query} news", "source_type": "web"},
            ]

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
            key_topics = self._extract_key_topics(all_sources[:5])
            for topic in key_topics[:2]:
                followup = web_search(topic, max_results=3)
                for source in followup:
                    if source.url not in seen_urls:
                        seen_urls.add(source.url)
                        all_sources.append(source)

        return all_sources[:settings.max_sources_per_query]

    def _extract_key_topics(self, sources: list[Source]) -> list[str]:
        """Extract key topics from retrieved sources for follow-up queries."""
        sources_text = "\n".join(f"- {s.title}: {s.snippet[:200]}" for s in sources)

        user_message = f"Sources:\n{sources_text}"

        messages = [
            SystemMessage(content="Extract up to 3 key research topics from these sources. Return as a JSON array of strings."),
            HumanMessage(content=user_message),
        ]
        response = self.llm.invoke(messages)
        content = response.content.strip()
        try:
            if "```" in content:
                content = content.split("```")[1].strip()
            return json.loads(content)
        except json.JSONDecodeError:
            return [s.title for s in sources[:3]]

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
