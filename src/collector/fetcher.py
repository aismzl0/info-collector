# Import the third-party library "requests", which sends HTTP requests
import requests
# logging lets us record what happened instead of using print
import logging


# Create a logger named after this module, so log lines show where they came from
logger = logging.getLogger(__name__)

# Identify our program to the server. Headers must be ASCII only.
USER_AGENT = "info-collector/0.1(student project; +https://github.com/aismzl0/info-collector)"

# Maximum number of seconds to wait for the server before giving up
TIMEOUT_SECONDS = 10


# Return the HTML string on success, or None on failure ("str | None" means either one)
def fetch_page(url:str) -> str | None:
    """Download a web page. Return its HTML, or None if anything goes wrong."""
    # Headers dictionary carrying our identity
    headers = {"User-Agent":USER_AGENT}
    # "try" means: attempt this block; if a listed error occurs, jump to "except"
    try:
        # Send the GET request and wait at most TIMEOUT_SECONDS
        response = requests.get(url,headers=headers,timeout=TIMEOUT_SECONDS)
        # Raise HTTPError for 4xx/5xx status codes (parentheses call the method)
        response.raise_for_status
    # Timeout is a subclass of RequestException, so it must be listed FIRST
    except requests.exceptions.Timeout:
        # Record an ERROR-level message including the URL
        logger.error("Timeout after %s seconds: %s",TIMEOUT_SECONDS,url)
        return None
    # The server answered, but with 4xx or 5xx
    except requests.exceptions.HTTPError as e:
        # e.response.status_code is the number such as 404 or 503
        logger.error("HTTP %s for %s",e.response.status_code,url)
        return None
    # Catch-all for other network problems (DNS failure, connection refused, ...)
    except requests.exceptions.RequestException as e:
        logger.error("Request failed for %s: %s",url,e)
        return None
    # Only reached when no exception happened
    logger.info("Fetched %s(%s characters)",url, len(response.text))
    # Return the page content
    return response.text


# Runs only when this file is executed directly
if __name__ =="__main__":
    # Import Path to save the file, and our logging setup
    from pathlib import Path
    from collector.log_config import setup_logging

    # Start logging before doing anything else
    setup_logging()

    # Download the Hacker News front page
    html = fetch_page("https://news.ycombinator.com/")
    # "if html is None" means the download failed
    if html is None:
        # Stop here;the reason is already in the log
        logger.error("Nothing saved because the download failed")
    else:  
        # Create a path object pointing to where we want to save the file
        out = Path("tests/fixtures/hn_sample.html")
        # Create the parent folder if missing
        out.parent.mkdir(parents=True, exist_ok=True)
        # Write the HTML string into the file using UTF-8 encoding
        out.write_text(html, encoding="utf-8")
        # Record success
        logger.info("Saved to %s", out)

