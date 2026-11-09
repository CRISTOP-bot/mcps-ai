"""Browser MCP Server - Interactive browser control via Playwright."""

import os
import asyncio
import json
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("Browser - opencode")

# Global browser instance
_browser = None
_page = None
_playwright = None


async def get_page():
    """Get or create the browser page."""
    global _browser, _page, _playwright

    if _page is not None:
        try:
            # Check if page is still alive
            await _page.evaluate("1 + 1")
            return _page
        except Exception:
            _page = None
            _browser = None

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise RuntimeError("Playwright not installed. Run: uv add playwright && playwright install chromium")

    if _playwright is None:
        _playwright = await async_playwright().start()

    if _browser is None:
        headless = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"
        _browser = await _playwright.chromium.launch(headless=headless)

    if _page is None:
        _page = await _browser.new_page()

    return _page


@mcp.tool
async def browser_navigate(url: str):
    """Navigate to a URL."""
    try:
        page = await get_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        title = await page.title()
        return {"url": page.url, "title": title}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def browser_click(selector: str):
    """Click an element by CSS selector."""
    try:
        page = await get_page()
        await page.click(selector, timeout=10000)
        return {"status": "clicked", "selector": selector}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def browser_fill(selector: str, text: str):
    """Fill an input field with text."""
    try:
        page = await get_page()
        await page.fill(selector, text, timeout=10000)
        return {"status": "filled", "selector": selector, "text": text}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def browser_type(selector: str, text: str, delay: int = 50):
    """Type text with human-like delay."""
    try:
        page = await get_page()
        await page.type(selector, text, delay=delay, timeout=10000)
        return {"status": "typed", "selector": selector, "text": text}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def browser_press(key: str):
    """Press a keyboard key (Enter, Tab, Escape, etc.)"""
    try:
        page = await get_page()
        await page.keyboard.press(key)
        return {"status": "pressed", "key": key}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def browser_get_text(selector: str = "body"):
    """Get text content of an element (default: whole page)."""
    try:
        page = await get_page()
        text = await page.inner_text(selector, timeout=10000)
        return {"text": text[:10000], "truncated": len(text) > 10000}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def browser_get_html(selector: str = "body"):
    """Get HTML content of an element."""
    try:
        page = await get_page()
        html = await page.inner_html(selector, timeout=10000)
        return {"html": html[:10000], "truncated": len(html) > 10000}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def browser_screenshot(full_page: bool = False):
    """Take a screenshot. Returns base64-encoded PNG."""
    try:
        page = await get_page()
        import base64
        screenshot = await page.screenshot(full_page=full_page)
        return {
            "screenshot_base64": base64.b64encode(screenshot).decode("utf-8"),
            "full_page": full_page,
            "size_bytes": len(screenshot),
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def browser_evaluate(script: str):
    """Execute JavaScript in the page and return the result."""
    try:
        page = await get_page()
        result = await page.evaluate(script)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def browser_wait(selector: str, timeout: int = 10000):
    """Wait for an element to appear."""
    try:
        page = await get_page()
        await page.wait_for_selector(selector, timeout=timeout)
        return {"status": "found", "selector": selector}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def browser_select(selector: str, option: str):
    """Select an option in a <select> dropdown."""
    try:
        page = await get_page()
        await page.select_option(selector, option, timeout=10000)
        return {"status": "selected", "selector": selector, "option": option}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def browser_scroll(direction: str = "down", amount: int = 500):
    """Scroll the page. direction: down/up."""
    try:
        page = await get_page()
        delta = amount if direction == "down" else -amount
        await page.evaluate(f"window.scrollBy(0, {delta})")
        return {"status": "scrolled", "direction": direction, "amount": amount}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def browser_back():
    """Go back in browser history."""
    try:
        page = await get_page()
        await page.go_back()
        return {"url": page.url, "title": await page.title()}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def browser_forward():
    """Go forward in browser history."""
    try:
        page = await get_page()
        await page.go_forward()
        return {"url": page.url, "title": await page.title()}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def browser_reload():
    """Reload the current page."""
    try:
        page = await get_page()
        await page.reload()
        return {"url": page.url, "title": await page.title()}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def browser_close():
    """Close the browser."""
    global _browser, _page, _playwright
    try:
        if _page:
            await _page.close()
        if _browser:
            await _browser.close()
        if _playwright:
            await _playwright.stop()
        _browser = None
        _page = None
        _playwright = None
        return {"status": "closed"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
async def browser_get_links():
    """Extract all links from the current page."""
    try:
        page = await get_page()
        links = await page.evaluate("""
            Array.from(document.querySelectorAll('a[href]')).map(a => ({
                text: a.innerText.trim().slice(0, 100),
                href: a.href,
            })).filter(l => l.text && l.href.startsWith('http'))
        """)
        return {"links": links[:50], "count": len(links)}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
