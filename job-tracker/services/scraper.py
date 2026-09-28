"""Fetch a job posting URL and return clean text suitable for Claude extraction."""
import httpx
from bs4 import BeautifulSoup


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
}

# Tags whose content we always discard before extracting text
_DISCARD_TAGS = {"script", "style", "noscript", "nav", "header", "footer", "aside", "iframe"}


def fetch_and_clean(url: str, timeout: int = 15) -> str:
    """
    Fetch *url* and return cleaned plain text (max ~8 000 chars).
    Raises httpx.HTTPError or ValueError on failure.
    """
    with httpx.Client(headers=_HEADERS, follow_redirects=True, timeout=timeout) as client:
        response = client.get(url)
        response.raise_for_status()

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type and "application/xhtml" not in content_type:
        raise ValueError(f"URL did not return HTML (content-type: {content_type})")

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(list(_DISCARD_TAGS)):
        tag.decompose()

    # Prefer main content areas; fall back to full body
    for selector in ["main", "article", '[role="main"]', "#main-content", ".job-description", "body"]:
        container = soup.select_one(selector)
        if container:
            break

    text = container.get_text(separator="\n") if container else soup.get_text(separator="\n")

    # Collapse whitespace
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned = "\n".join(lines)

    # Truncate to avoid huge prompts
    return cleaned[:8000]
