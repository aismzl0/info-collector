# Import the rule-reading functions and the rate limiter
import time
from collector.politeness import RateLimiter, get_delay, is_allowed, parse_robots


# A made-up robots.txt, so these tests never touch the network
FAKE_ROBOTS = """
User-agent: *
Disallow: /private
Crawl-delay: 30
"""


# A path that is not disallowed shoould be allowed
def test_allowed_path():
    rules = parse_robots(FAKE_ROBOTS)
    assert is_allowed(rules, "https://example.com/news") is True


# A path under a Disallow rule should be refused
def test_disallowed_path():
    rules = parse_robots(FAKE_ROBOTS)
    assert is_allowed(rules, "https://example.com/private/page") is False


# If robots.txt counld not be loaded (None), we must refuse: "fail closed"
def test_no_rules_means_refuse():
    assert is_allowed(None, "https://example.com/news") is False


# The site's Crawl-delay (30) is larger than our default (2), so it wins
def test_delay_uses_site_crawl_delay():
    rules = parse_robots(FAKE_ROBOTS)
    assert get_delay(rules) == 30


# With no Crawl-delay line and no rules at all, fall back to our defalut
def test_delay_falls_back_to_default():
    assert get_delay(parse_robots("User-agent: *\nDisallow: /private")) == 2
    assert get_delay(None) == 2.0


# The second wait() call must pause until the minimum interval has passed
def test_rate_limiter_waits_between_requests():
    # A short interval keeps the test fast
    limiter = RateLimiter(min_interval=0.3)
    # The first call needs no waiting
    limiter.wait()
    start = time.monotonic()
    # The second call should sleep for about 0.3 seconds
    limiter.wait()
    elapsed = time.monotonic() - start
    # Allow a small tolerance for clock precision
    assert elapsed >= 0.25



