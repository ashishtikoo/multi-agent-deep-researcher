"""
Contextual Retriever Agent – Pulls data from research papers, news, reports, and APIs.
"""

import json
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from utils.llm import create_llm
from utils.search import web_search, academic_search, search_all_sources
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

Given a research query, generate up to {max_queries} targeted search queries that would
yield the most comprehensive and diverse results across different source types
(academic papers, news articles, industry reports, and general web sources).

Return your response as a JSON object with the following structure:
{{
    "queries": [
        {{"query": "specific search query", "source_type": "web|academic|news|reports"}},
        ...
    ]
}}

Be specific and creative with your queries. Consider different angles and perspectives.
"""

    def __init__(self, llm_model: Optional[str] = None):
        self.llm = create_llm(llm_model)
        self.max_queries = 5

    def generate_search_queries(self, research_query: str) -> list[dict]:
        """Generate targeted search queries for the research topic."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.SYSTEM_PROMPT),
            ("human", "Research query: {research_query}"),
        ])
        chain = prompt | self.llm
        response = chain.invoke({
            "research_query": research_query,
            "max_queries": self.max_queries,
        })
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

    def retrieve(self, research_query: str, max_hops: int = 3) -> list[Source]:
        """
        Perform multi-hop retrieval: generate queries, search, and expand.
        """
        all_sources: list[Source] = []
        seen_urls = set()

        # Generate search queries
        queries = self.generate_search_queries(research_query)

        # Execute searches
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

        # Multi-hop: expand with follow-up queries on key topics found
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
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Extract up to 3 key research topics from these sources. Return as a JSON array of strings."),
            ("human", "Sources:\n" + "\n".join(f"- {s.title}: {s.snippet[:200]}" for s in sources)),
        ])
        chain = prompt | self.llm
        response = chain.invoke({})
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
