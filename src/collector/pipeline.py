# logging records what happened, same pattern as the other modules
import logging
# Path is used for file paths (database file, local HTML file)
from pathlib import Path


# Reuse the pieces we built in earlier tasks
from collector.fetcher import fetch_page
from collector.hn_parser import BASE_URL, parse_stories
from collector.politeness import (
    DEFAULT_DELAY_SECONDS,
    RateLimiter,
    get_delay,
    is_allowed,
    load_robots,
)
from collector.storage import DB_PATH, get_connection, init_db, save_stories


# A logger named after this module
logger = logging.getLogger(__name__)


# Build the URL of page number N. Page 1 is the home page.
def build_page_url(page: int) -> str:
    """Return the URL for a front-page number (1 = home page)."""
    # The home page has no query parameter
    if page == 1:
        return BASE_URL
    # Later pages use ?p=N (check the "More" link in the sample HTML to confirm)
    return f"{BASE_URL}?p={page}"


# Parse one local HTML file and store the result. No network is used.
def run_from_file(html_path: Path, db_path: Path = DB_PATH) -> int:
    """Parse a saved HTML file and store its stories. Return the number of new rows."""
    # Read the saved page as text
    html = html_path.read_text(encoding="utf-8")
    # Turn the HTML into a list of story dictionaries
    stories = parse_stories(html)
    # Open the database and make sure the table exists
    conn = get_connection(db_path)
    init_db(conn)
    # Save the stories; the return value is how many were new
    new_rows = save_stories(conn,stories)
    # Always close the connection when finished
    conn.close()
    # Record the outcome
    logger.info("Parsed %s stories form file, %s new",len(stories),new_rows)
    return new_rows


# The full online pipeline: robots.txt -> rate limit -> download -> parse -> store
def run_online(pages: int, db_path: Path = DB_PATH) -> int:
    """Crawl the first `pages` front pages politely. Return the total number of new rows."""
    # Start with our default gap; it will be raised if robots.txt asks for more
    limiter = RateLimiter(DEFAULT_DELAY_SECONDS)

    # Downloading robots.txt is also a request, so it goes through the limiter
    limiter.wait()
    robots = load_robots(BASE_URL)

    # If rules could not be loaded, we refuse to crawl (fail closed) 
    if robots is None:
        logger.error("No robots.txt rules, so nothong will be crawled")
        return 0

    # Use the site's Crawl-delay if it is larger than our default
    limiter.min_interval = get_delay(robots)
    logger.info("Using a delay of %.1f seconds between requests", limiter.min_interval)

    # Open the database once and reuse the connection for every page
    conn = get_connection(db_path)
    init_db(conn)
    total_new = 0

    # range(1, pages + 1) gives 1, 2, ..., pages
    for page in range(1, pages + 1):
        url = build_page_url(page)
        # Check permission BEFORE sending anything
        if not is_allowed(robots, url):
            continue
        # Then wait if the previous request was too recent
        limiter.wait()
        html = fetch_page(url)
        # Download failed: the reason is already logged, move on to the next page
        if html is None:
            continue
        stories = parse_stories(html)
        total_new += save_stories(conn, stories)


    # Close the database and report
    conn.close()
    logger.info("Done. %s new stories saved", total_new)
    return total_new
