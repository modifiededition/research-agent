web_search_dec = {
    "name": "web_search",
    "description": "Search the web using Tavily API",
    "parameters": {
        "type": "object",
        "properties":{
            "query":{
                "type":"string",
                "description":"Search query string"
            },
            "limit":{
                "type":"integer",
                "description":"Maximum number of results to return"
            },
            "start_date":{
                "type":"string",
                "description":"Filter results from this date (format: YYYY-MM-DD )"
            },
            "end_date":{
                "type":"string",
                "description":"Filter results until this date (format: YYYY-MM-DD, optional)"
            }
        },
        "required": ["query"],
    }
}

arxiv_search_dec = {
    "name": "arxiv_search",
    "description": "Search academic papers on arXiv",
    "parameters": {
        "type": "object",
        "properties":{
            "query":{
                "type":"string",
                "description":"Search query string"
            },
            "max_results":{
                "type":"integer",
                "description":"Maximum number of papers to return"
            }
        },
        "required": ["query"],
    }
}

fetch_url_dec = {
    "name": "fetch_url",
    "description": "Fetch and extract content from a URL.",
    "parameters": {
        "type": "object",
        "properties":{
            "url":{
                "type":"string",
                "description":"The URL to fetch content from"
            }
        },
        "required": ["url"],
    }
}



