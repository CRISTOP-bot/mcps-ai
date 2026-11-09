"""Web Search MCP Server - Search the web via DuckDuckGo (no API key needed)."""

import os
import json
import urllib.request as urllib_request
import urllib.parse as urllib_parse
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("Web - opencode")


def decode_bing_url(href):
    """Decode Bing redirect URL to actual URL."""
    import base64, html as html_module
    # Unescape HTML entities first (&amp; -> &)
    href = html_module.unescape(href)
    if "ck/a?" in href:
        from urllib.parse import urlparse, parse_qs
        qs = parse_qs(urlparse(href).query)
        u = qs.get("u", [""])[0]
        if u.startswith("a1"):
            try:
                decoded = base64.urlsafe_b64decode(u[2:]).decode("utf-8")
                return decoded
            except Exception:
                pass
    return href


def ddg_search(query, max_results=10):
    """Search Bing and parse results."""
    try:
        url = f"https://www.bing.com/search?q={urllib_parse.quote_plus(query)}"
        req = urllib_request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
        })
        with urllib_request.urlopen(req, timeout=15) as r:
            html = r.read().decode("utf-8", errors="replace")

        import re
        results = []
        # Parse: <h2><a href="URL">title</a></h2>
        pattern = re.compile(r'<h2[^>]*><a[^>]+href="([^"]+)"[^>]*>([^<]+)</a></h2>', re.S)
        snippets = re.compile(r'<p[^>]*class="[^"]*b_lineclamp[^"]*"[^>]*>(.*?)</p>', re.S)

        snippet_texts = snippets.findall(html)

        for i, (href, title) in enumerate(pattern.findall(html)):
            href = decode_bing_url(href)
            title = re.sub(r'<[^>]+>', '', title).strip()
            title = title.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&#243;", "ó").replace("&#241;", "ñ")
            snippet = ""
            if i < len(snippet_texts):
                snippet = re.sub(r'<[^>]+>', ' ', snippet_texts[i]).strip()
                snippet = snippet.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&nbsp;", " ")
            results.append({"title": title, "url": href, "snippet": snippet})
            if len(results) >= max_results:
                break
        return results
    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool
async def web_search(query: str, max_results: int = 10):
    """Search the web using DuckDuckGo. No API key required."""
    results = ddg_search(query, max_results)
    return {"query": query, "results": results, "count": len(results)}


@mcp.tool
async def web_fetch(url: str, max_chars: int = 50000):
    """Fetch and return the text content of a web page."""
    try:
        req = urllib_request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib_request.urlopen(req, timeout=15) as r:
            content_type = r.headers.get("Content-Type", "")
            raw = r.read()

            if "text" in content_type or "json" in content_type:
                text = raw.decode("utf-8", errors="replace")
                # Strip HTML tags if it looks like HTML
                if "<html" in text.lower() or "<!doctype" in text.lower():
                    import re
                    text = re.sub(r'<script[^>]*>.*?</script>', ' ', text, flags=re.S | re.I)
                    text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.S | re.I)
                    text = re.sub(r'<[^>]+>', ' ', text)
                    text = re.sub(r'\s+', ' ', text).strip()
                return {"url": url, "content_type": content_type, "content": text[:max_chars], "truncated": len(text) > max_chars}
            else:
                return {"url": url, "content_type": content_type, "content": f"[Binary content: {len(raw)} bytes]", "truncated": False}
    except Exception as e:
        return {"error": str(e), "url": url}


@mcp.tool
async def web_news(query: str, max_results: int = 10):
    """Search recent news via DuckDuckGo."""
    results = ddg_search(f"{query} news", max_results)
    return {"query": query, "results": results, "count": len(results)}


@mcp.tool
async def web_weather(city: str):
    """Get weather for a city using wttr.in (no API key)."""
    try:
        url = f"https://wttr.in/{urllib_parse.quote_plus(city)}?format=3"
        req = urllib_request.Request(url, headers={"User-Agent": "curl/8.0"})
        with urllib_request.urlopen(req, timeout=10) as r:
            result = r.read().decode("utf-8", errors="replace")
        return {"city": city, "weather": result}
    except Exception as e:
        return {"error": str(e), "city": city}


if __name__ == "__main__":
    mcp.run(transport="stdio")
