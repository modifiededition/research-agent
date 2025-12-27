import requests
from bs4 import BeautifulSoup
import fitz
import xml.etree.ElementTree as ET
from typing import Optional
from config import get_config

def web_search(query: str, limit:int = 5, start_date: str = "", end_date:str = "") -> str:
    """
    Search the web using Tavily API.

    Args:
        query: Search query string
        limit: Maximum number of results to return (default: 5)
        start_date: Filter results from this date (format: YYYY-MM-DD, optional)
        end_date: Filter results until this date (format: YYYY-MM-DD, optional)

    Returns:
        Formatted string containing search results with title, URL, and content
    """
    try:
        config = get_config()
        headers = {
            "Authorization" : f"Bearer {config.TAVILY_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            url = "https://api.tavily.com/search",
            headers = headers,
            json={
                "query": query,
                "max_results": limit,
                "start_date": start_date,
                "end_date": end_date
            },
            
        )
        data = response.json()
        
        output = ""
        for r in data.get("results", []):
            output += f"Title: {r.get('title', '')}\n"
            output += f"URL: {r.get('url', '')}\n"
            output += f"Content: {r.get('content', '')}\n\n"
        return output if output else "No results found. Try modifying the query."
    except Exception as e:
        return f"Error performing web search: {str(e)}"

def arxiv_search(query: str, max_results: int = 5) -> str:
    """
    Search academic papers on arXiv.
    
    Args:
        query: Search query string for academic papers
        max_results: Maximum number of papers to return (default: 5)
    
    Returns:
        Formatted string containing paper details (title, authors, published date, URL, abstract)
    """
    response = requests.get(
        "http://export.arxiv.org/api/query",
        params={
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }
    )
    
    # Parse XML response
    root = ET.fromstring(response.content)
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    
    output = ""
    for entry in root.findall("atom:entry", namespace):
        title = entry.find("atom:title", namespace).text.strip()
        summary = entry.find("atom:summary", namespace).text.strip()
        published = entry.find("atom:published", namespace).text[:10]
        
        # Get authors
        authors = [a.find("atom:name", namespace).text 
                   for a in entry.findall("atom:author", namespace)]
        authors_str = ", ".join(authors[:3])
        if len(authors) > 3:
            authors_str += " et al."
        
        # Get URL
        url = entry.find("atom:id", namespace).text
        
        output += f"Title: {title}\n"
        output += f"Authors: {authors_str}\n"
        output += f"Published: {published}\n"
        output += f"URL: {url}\n"
        output += f"Abstract: {summary[:500]}...\n\n"
    
    return output if output else "No results found. Try modifying the query."

def fetch_url(url: str) -> str:
    """
    Fetch and extract content from a URL. Automatically handles different URL types.
    
    Args:
        url: The URL to fetch content from
    
    Returns:
        Extracted text content from the URL
    """
    
    # for arXiv url
    if "arxiv" in url:
        return fetch_arxiv_paper(arxiv_url = url)
        
    # Check if PDF
    if url.endswith(".pdf"):
        return fetch_pdf(url)
    
    # Regular webpage
    # For JavaScript-rendered dynamic content, this function may return incomplete 
    # or empty content. If the returned content appears incomplete or mentions JavaScript 
    # requirement, use fetch_url_with_jina() instead.

    content =  fetch_webpage(url)
    if _is_content_sufficient(content):
        return content
        
    return fetch_url_using_jina(url)

def _is_content_sufficient(content: Optional[str]) -> bool:
    """
    Determine if fetched content is sufficient/complete.
    """
    if not content or not isinstance(content, str):
        return False
    
    content_lower = content.lower()
    
    # Check for common indicators of incomplete content
    javascript_indicators = [
        "javascript is required",
        "enable javascript",
        "javascript must be enabled",
        "please enable js",
        "this page requires javascript"
    ]
    
    if any(indicator in content_lower for indicator in javascript_indicators):
        return False
    
    # Check minimum content length
    if len(content.strip()) < 200:
        return False
    
    return True

def fetch_webpage(url: str) -> str:
    """Fetch and extract text from HTML page"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove scripts, styles, nav, footer
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        
        # Get text
        text = soup.get_text(separator="\n", strip=True)
        
        # Clean up whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = "\n".join(lines)
        
        return text

    except Exception as e:
        return f"Error fetching webpage: {str(e)}"

def fetch_pdf(url: str) -> str:
    """Fetch and extract text from PDF"""
    try:
        response = requests.get(url, timeout=30)
        
        # Load PDF from bytes
        doc = fitz.open(stream=response.content, filetype="pdf")
        
        text = ""
        for page in doc:
            text += page.get_text()
        
        doc.close()
        return text
    except Exception as e:
        return f"Error fetching PDF: {str(e)}"

def fetch_arxiv_paper(arxiv_url: str) -> str:
    """Fetch full arXiv paper content"""
    
    # Convert any arXiv URL to PDF URL
    # http://arxiv.org/abs/2404.04365 -> http://arxiv.org/pdf/2404.04365.pdf
    if "/abs/" in arxiv_url:
        pdf_url = arxiv_url.replace("/abs/", "/pdf/") + ".pdf"
    elif "/pdf/" in arxiv_url:
        pdf_url = arxiv_url if arxiv_url.endswith(".pdf") else arxiv_url + ".pdf"
    elif "/html/" in arxiv_url:
        pdf_url = arxiv_url if arxiv_url.endswith(".pdf") else arxiv_url + ".pdf"
    else:
        return "Invalid arXiv URL"
    
    return fetch_pdf(pdf_url)


def fetch_url_using_jina(url: str) -> str:
    """
    Fetch and render URL content using Jina Reader API with full JavaScript rendering.
    
    USE THIS ONLY WHEN: fetch_url() returns incomplete content, empty results, or 
    indicates JavaScript is required. This is specifically for dynamic/JavaScript-rendered 
    websites where standard fetching fails.
    
    Examples of when to use:
        - Single-page applications (SPAs)
        - Websites that load content via JavaScript
        - When fetch_url() returns minimal content like just a title
    
    Args:
        url: The URL to fetch and render
    
    Returns:
        Fully rendered page content in markdown format
    """
    try:
        response = requests.get(
            f"https://r.jina.ai/{url}",
            headers={"Accept": "text/markdown"},
        )
        return response.text if response.text else "No content extracted."
    except Exception as e:
        return f"Error fetching URL with Jina: {str(e)}"
