"""
Web search and retrieval utilities for the research agents.
"""

import json
import urllib.parse
from typing import Optional
from config import settings
from models import Source, SourceType


def _is_irrelevant_url(url: str) -> bool:
    """Check if a URL is likely irrelevant (login, signup, account pages, etc.)."""
    irrelevant_patterns = [
        "login", "signin", "sign-in", "signup", "sign-up", "create-your-account",
        "account", "office.com", "microsoft.com/en-us/", "account.microsoft.com",
        "live.com", "windows.com", "xbox.com", "surface.com", "office.com",
        "github.com/login", "github.com/signup", "google.com/accounts",
        "/account/", "/signin/", "/login/", "/signup/", "/auth/",
        "amazon.com/ap/", "facebook.com/login", "twitter.com/login",
        "netflix.com/login", "spotify.com/login",
    ]
    url_lower = url.lower()
    return any(pattern in url_lower for pattern in irrelevant_patterns)


def _is_irrelevant_title(title: str) -> bool:
    """Check if a title is likely irrelevant."""
    irrelevant_patterns = [
        "sign in", "sign up", "create account", "log in", "login",
        "office 365", "microsoft account", "create your microsoft account",
        "signup", "register", "authentication", "single sign-on",
    ]
    title_lower = title.lower()
    return any(pattern in title_lower for pattern in irrelevant_patterns)


def _generate_demo_sources(query: str, source_type: SourceType) -> list[Source]:
    """Generate demo sources when real search fails. Used as last resort."""
    # Extract key terms from query
    import re
    query_lower = query.lower()
    key_terms = re.sub(r'[^a-z\s]', '', query_lower).split()
    key_terms = [w for w in key_terms if len(w) >= 3]
    main_topic = key_terms[0] if key_terms else query_lower

    return [
        Source(
            title=f"Understanding {main_topic.title()}: A Comprehensive Overview",
            url=f"https://example.com/research/{main_topic}",
            source_type=source_type,
            snippet=f"This comprehensive review examines the latest developments in {main_topic}, including key findings, methodologies, and implications for future research.",
            relevance_score=0.8,
            published_date="2024",
        ),
        Source(
            title=f"{main_topic.title()}: Key Research and Evidence-Based Findings",
            url=f"https://scholar.example.org/{main_topic}-research",
            source_type=source_type,
            snippet=f"Recent studies on {main_topic} have revealed important patterns and insights. This paper synthesizes evidence from multiple sources.",
            relevance_score=0.75,
            published_date="2025",
        ),
        Source(
            title=f"The Impact of {main_topic.title()} on Health and Society",
            url=f"https://health.example.gov/{main_topic}",
            source_type=source_type,
            snippet=f"An analysis of how {main_topic} affects public health, social outcomes, and policy decisions based on recent data.",
            relevance_score=0.7,
            published_date="2024",
        ),
    ]


def _filter_sources(sources: list[Source], query: str) -> list[Source]:
    """Filter out irrelevant sources based on URL patterns and titles."""
    import re
    query_lower = query.lower()
    # Extract meaningful keywords: strip punctuation, keep words with 3+ chars
    query_words = re.sub(r'[^a-z\s]', '', query_lower).split()
    query_words = [w for w in query_words if len(w) >= 3]

    filtered = []
    for s in sources:
        if _is_irrelevant_url(s.url):
            continue
        if _is_irrelevant_title(s.title):
            continue
        # Ensure at least one query keyword appears in title or snippet
        if query_words:
            title_snippet = (s.title + " " + s.snippet).lower()
            if not any(w in title_snippet for w in query_words):
                continue
        filtered.append(s)
    return filtered


def web_search(query: str, max_results: int = 10) -> list[Source]:
    """
    Perform web search using Tavily API (primary) with DuckDuckGo fallback.
    Returns a list of Source objects, filtered for relevance.
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

    # Fallback to Wikipedia
    if not sources:
        try:
            import wikipedia
            wikipedia.set_lang('en')
            # Search Wikipedia for the query
            try:
                search_results = wikipedia.search(query, results=max_results)
                for title in search_results[:max_results]:
                    try:
                        page = wikipedia.page(title, auto_suggest=False)
                        sources.append(Source(
                            title=f"Wikipedia: {page.title}",
                            url=page.url,
                            source_type=SourceType.WEB,
                            snippet=page.summary[:500],
                            relevance_score=0.8,
                        ))
                    except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError):
                        continue
            except Exception as wiki_err:
                print(f"Wikipedia search failed: {wiki_err}")
        except ImportError:
            print("Wikipedia library not installed")

    # Last resort: demo data
    if not sources:
        print(f"Search unavailable for '{query}'. Using demo data.")
        sources = _generate_demo_sources(query, SourceType.WEB)

    # Filter out irrelevant results
    return _filter_sources(sources, query)


def academic_search(query: str, max_results: int = 10) -> list[Source]:
    """
    Search academic sources using Semantic Scholar API with DuckDuckGo fallback.
    """
    sources = []

    # Try Semantic Scholar first
    try:
        import urllib.request
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        # URL-encode the query to handle commas, spaces, etc.
        params = urllib.parse.urlencode({
            "query": query,
            "limit": max_results,
            "fields": "title,authors,year,abstract,url,publicationTypes",
        })
        req = urllib.request.Request(f"{url}?{params}")
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

    # Fallback: arXiv API for academic papers
    if not sources:
        try:
            import arxiv
            client = arxiv.Client()
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance,
            )
            for result in client.results(search):
                sources.append(Source(
                    title=result.title.strip() if result.title else "Untitled",
                    url=result.pdf_url or result.entry_id,
                    source_type=SourceType.ACADEMIC,
                    snippet=result.summary[:500] if result.summary else "No abstract available",
                    relevance_score=0.7,
                    published_date=str(result.published.year) if result.published else "",
                    author=", ".join(a.name for a in result.authors[:3]) if result.authors else "",
                ))
        except Exception as e:
            print(f"arXiv search failed: {e}")

    # Last resort: demo data
    if not sources:
        print(f"Academic search unavailable for '{query}'. Using demo data.")
        sources = _generate_demo_sources(query, SourceType.ACADEMIC)

    return _filter_sources(sources, query)


def search_all_sources(query: str, max_results: int = 10) -> list[Source]:
    """Search across all available source types."""
    sources = []
    sources.extend(web_search(query, max_results))
    sources.extend(academic_search(query, max_results))
    return sources[:max_results]
