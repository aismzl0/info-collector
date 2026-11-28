# Import only the pure function we want to test; it never touches the network
from collector.pipeline import build_page_url
# Page 1 is the home page, with no query parameter
def test_first_page_is_home_page():
    assert build_page_url(1) == "https://news.ycombinator.com/"


# Later page must match the site's own "More" link, which is "?p=2"
def test_second_page_uses_query_parameter():
    assert build_page_url(2) == "https://news.ycombinator.com/?p=2"