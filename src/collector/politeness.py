# logging records what happened (same pattern as the other modules)
import logging
# time gives us the clock (monotonic) and the pause function (sleep)
import time
# urljoin builds a full URL from a base address and a path
from urllib.parse import urljoin
# RobotFileParser is Python's built-in reader for robots.txt rules
from urllib.robotparser import RobotFileParser
# Reuse our own downloader and identity string from fetcher.py
from fetcher import USER_AGENT, fetch_page

# A logger named after this module
logger = logging.getLogger(__name__)

# The minimum pause between requests, even if robots.txt does not ask for one
DEFAULT_DELAY_SECONDS = 2.0


# Turn the TEXT of a robots.txt file into a rules object we can query
def parse_robots(text: str) -> RobotFileParser:
    """Parse robots.txt text. No network is used here, which makes it easy to test."""
    # Create an empty rules object
    parser = RobotFileParser()
    # parse() wants a list of lines, so split the text at line breaks
    parser.parse(text.splitlines())
     # Return the filled rules object
    return parser


# Download robots.txt from a site and parse it
def load_robots(base_url: str) -> RobotFileParser | None:
    """Fetch and parse a site's robots.txt. Return None if it cannot be loaded."""
    # "/robots.txt" starts with "/", so urljoin places it at the site root
    robots_url = urljoin(base_url,"/robots.txt")
    # Download it with our own fetcher (our User-Agent, timeout and logging)
    text = fetch_page(robots_url)
    # If the download failed, we do not know the rules
    if text is None:
        logger.warning("Could not load %s; will refuse to crawl",robots_url)
        return None
    # Otherwise turn the text into a rules object
    return parse_robots(text)


# Ask: "am I allowed to fetch this URL?"
def is_allowed(parser:RobotFileParser | None, url: str) -> bool:
    """Return True only if robots.txt rules were loaded AND they allow this URL."""
    # No rules loaded: fail closed, meaning we refuse
    if parser is None:
        return False
    # can_fetch checks our identity against the rules for this URL
    allowed = parser.can_fetch(USER_AGENT,url)
    # Record refusals so we can see them in the log
    if not allowed:
        logger.warning("robots.txt does not allow fetching %s",url)
    return allowed


# Work out how many seconds to wait between requests
def get_delay(parser: RobotFileParser |None) -> float:
    """Use the larger of our default delay and the site's Crawl-delay."""
    # Start from our own default
    delay = DEFAULT_DELAY_SECONDS
    # Only look at the rules if we actually have them
    if parser is not None:
        # crawl_delay returns a number, or None if the site did not set one
        crawl_delay = parser.crawl_delay(USER_AGENT)
        # If the site asked for a delay, never go below it
        if crawl_delay is not None:
            delay = max(delay,float(crawl_delay))
    return  delay


# A class bundles data (last request time) with behavior (wait)
class RateLimiter:
    """Make sure at least min_interval seconds pass between two requests."""

    # __init__ runs automatically when we create an object: RateLimiter(2.0)
    # "self" is the object being created; it carries the data between calls
    def __init__(self,min_interval: float) -> None:
        # Remember the mininum gap
        self.min_interval = min_interval
        # None means "no request has been made yet"
        self.last_request_time: float | None = None


    # Call this right BEFORE every request
    def wait(self) -> None:
        """Sleep if the previous request was too recent."""
        # The very first request needs no waiting
        if self.last_request_time is not None:
            # How long ago was the last request?
            elapsed = time.monotonic() - self.last_request_time
            # How much of the minimun gap is still left?
            remaining = self.min_interval - elapsed
            # Only sleep if there is time left to wait
            if remaining > 0:
                logger.info("Rate limit: sleeping %.1f seconds", remaining)
                # Pause the program
                time.sleep(remaining)
        # Record "now" as the time of this request.
        # monotonic() never jumps backwards, even if the system clock is changed.
        self.last_request_time = time.monotonic()
        

# Runs only when this file is executed directly: an offline demo (no network)
if __name__ == "__main__":
    # Reuse the shared logging setup
    from log_config import setup_logging

    # Start logging first
    setup_logging()

    # A made-up robots.txt, so the demo never touches any real website
    fake_robots = """
User-agent: *
Disallow: /private
Crawl-delay: 5
"""
    # Parse the fake rules
    rules = parse_robots(fake_robots)
    # "/" is not disallowed, so this should be True
    print("Allowed '/' :", is_allowed(rules,"https://example.com"))
    # This path starts with /private, so this should be False
    print("Allowed '/private/x':",is_allowed(rules, "https://example.com/private/x"))
    # The site asks for 5 seconds, which is larger than our 2-second default
    print("Delay:", get_delay(rules))
    # With no rules loaded we must refuse (fail closed)
    print("Allowed with no rules:", is_allowed(None, "https://example.com/"))

    # Test the limiter: 3 "requests" with a 1-second minimum gap
    limiter = RateLimiter(min_interval=1.0)
    # Remember when the test started
    start = time.monotonic()
    # Repeat 3 times; "_" would also work, but i lets us print the number
    for i in range(3):
        # Wait if needed, then pretend to send a request
        limiter.wait()
        print(f"Request {i + 1} at {time.monotonic() - start:.1f}s")