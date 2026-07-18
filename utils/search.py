"""
Web search and retrieval utilities for the research agents.
"""

import json
from typing import Optional
from config import settings
from models import Source, SourceType


def web_search(query: str, max_results: int = 10) -> list[Source]:
    """
    Perform web search using Tavily API (primary) with DuckDuckGo fallback.
    Returns a list of Source objects.
    """
    sources = []

    # Try Tavily first
    if settings.tavily_api_key and settings.tavily_api_key not in ("", "your-tavily-key-here"):
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=settings.tavily_api_key)
            results = client.search(query, max_results=max_results)

            for r in results.get("results", [])[:max_results]:
                sources.append(Source(
                    title=r.get("title", "Untitled"),
                    url=r.get("url", ""),
                    source_type=SourceType.WEB,
                    snippet=r.get("content", ""),
                    relevance_score=r.get("score", 0.5),
                    published_date=r.get("published_date"),
                ))
        except Exception as e:
            print(f"Tavily search failed: {e}")

    # Fallback to DuckDuckGo
    if not sources:
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                for r in results:
                    sources.append(Source(
                        title=r.get("title", "Untitled"),
                        url=r.get("href", ""),
                        source_type=SourceType.WEB,
                        snippet=r.get("body", ""),
                        relevance_score=0.5,
                    ))
        except Exception as e:
            print(f"DuckDuckGo search failed: {e}")

    return sources


def academic_search(query: str, max_results: int = 10) -> list[Source]:
    """
    Search academic sources using Semantic Scholar API.
    """
    sources = []

    try:
        import urllib.request
        url = f"https://api.semanticscholar.org/graph/v1/paper/search"
        params = f"?query={query}&limit={max_results}&fields=title,authors,year,abstract,url,publicationTypes"
        req = urllib.request.Request(url + params)
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            for paper in data.get("data", [])[:max_results]:
                authors = ", ".join(a.get("name", "") for a in paper.get("authors", [])[:3])
                sources.append(Source(
                    title=paper.get("title", "Untitled"),
                    url=paper.get("url", "") or f"https://www.semanticscholar.org/paper/{paper.get('paperId', '')}",
                    source_type=SourceType.ACADEMIC,
                    snippet=paper.get("abstract", "") or "No abstract available",
                    relevance_score=0.7,
                    published_date=str(paper.get("year", "")),
                    author=authors,
                ))
    except Exception as e:
        print(f"Semantic Scholar search failed: {e}")

    # Fallback: web search with academic keywords
    if not sources:
        sources = web_search(f"academic paper {query}", max_results)
        for s in sources:
            if any(kw in s.url.lower() for kw in [".pdf", "scholar", "arxiv", "pubmed", "doi"]):
                s.source_type = SourceType.ACADEMIC

    return sources


def search_all_sources(query: str, max_results: int = 10) -> list[Source]:
    """Search across all available source types."""
    sources = []
    sources.extend(web_search(query, max_results))
    sources.extend(academic_search(query, max_results))
    return sources[:max_results]
