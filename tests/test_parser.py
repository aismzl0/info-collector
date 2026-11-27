# Path lets us build a file path relative to THIS test file
from pathlib import Path
# Import the function we want to test (works because of "pip install -e .")
from collector.hn_parser import parse_stories


# __file__ is the path of this test file. Building the fixture path from it means
# the tests work no matter which folder you run pytest
FIXTURE = Path(__file__).parent / "fixtures" / "hn_sample.html"


# Test 1: the saved real page produces stories that have the shape we expect
def test_parses_stories_from_real_sample():
    # Read the frozen sample page (no network)
    html = FIXTURE.read_text(encoding="utf-8")
    stories = parse_stories(html)
    # The sample is a fixed file, so the count never changes
    assert len(stories) == 30
    # Every story must have a non-empty id and title, and a full http(s) URL
    for story in stories:
        assert story["id"]
        assert story["title"]
        assert story["url"].startswith("http")


# Test 2: a relative link like "item?id=1" must become a full URL
def test_relative_url_is_completed():
    # A tiny hand-written page with exactly one story, so the expected answer is obvious
    html = """
    <table><tr class="athing" id="1">
      <td><span class="titleline"><a href="item?id=1">Ask HN: test</a></span></td>
    </tr></table>
    """
    stories = parse_stories(html)
    assert stories == [
        {"id": "1", "title": "Ask HN: test", "url": "https://news.ycombinator.com/item?id=1"}  
    ]


# Test 3: a row with no title link is skipped instead of crashing the parser
def test_row_without_link_is_skipped():
    # This row has an id but no <a> link inside
    html = '<table><tr class="athing" id="2"></tr></table>'
    assert parse_stories(html) == []
