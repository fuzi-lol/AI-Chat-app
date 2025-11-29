import httpx
from typing import List, Dict, Any, Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self):
        self.api_key = settings.tavily_api_key
        self.base_url = "https://api.tavily.com"
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_keepalive_connections=5)
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search the internet using Tavily API.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            search_depth: "basic" or "advanced"
            include_domains: List of domains to include in search
            exclude_domains: List of domains to exclude from search
        """
        if not self.api_key:
            raise Exception("Tavily API key not configured")

        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
            "include_answer": True,
            "include_images": False,
            "include_raw_content": False
        }

        if include_domains:
            payload["include_domains"] = include_domains
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains

        try:
            response = await self.client.post(
                f"{self.base_url}/search",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "query": query,
                "answer": data.get("answer", ""),
                "results": data.get("results", []),
                "search_metadata": {
                    "total_results": len(data.get("results", [])),
                    "search_depth": search_depth,
                    "max_results": max_results
                }
            }
            
        except httpx.RequestError as e:
            logger.error(f"Error connecting to Tavily API: {e}")
            raise Exception(f"Failed to connect to Tavily API: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Tavily API error: {e}")
            if e.response.status_code == 401:
                raise Exception("Invalid Tavily API key")
            elif e.response.status_code == 429:
                raise Exception("Tavily API rate limit exceeded")
            else:
                raise Exception(f"Tavily API error: {e}")

    def format_search_results_for_llm(self, search_data: Dict[str, Any]) -> str:
        """Format search results for inclusion in LLM prompt."""
        if not search_data.get("results"):
            return "No search results found."

        formatted_results = []
        
        # Add the direct answer if available
        if search_data.get("answer"):
            formatted_results.append(f"Direct Answer: {search_data['answer']}\n")

        # Add individual search results
        formatted_results.append("Search Results:")
        for i, result in enumerate(search_data["results"][:5], 1):  # Limit to top 5 results
            title = result.get("title", "No title")
            url = result.get("url", "")
            content = result.get("content", "No content available")
            
            # Truncate content if too long
            if len(content) > 300:
                content = content[:300] + "..."
            
            formatted_results.append(f"\n{i}. {title}")
            formatted_results.append(f"   URL: {url}")
            formatted_results.append(f"   Content: {content}")

        return "\n".join(formatted_results)

    async def health_check(self) -> bool:
        """Check if Tavily API is accessible."""
        if not self.api_key:
            return False
            
        try:
            # Simple test search
            response = await self.client.post(
                f"{self.base_url}/search",
                json={
                    "api_key": self.api_key,
                    "query": "test",
                    "max_results": 1
                }
            )
            return response.status_code == 200
        except:
            return False


# Global instance
search_service = SearchService()
