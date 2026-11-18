# import beautifulsoup,which turns an HTML string into a serachable object
from bs4 import BeautifulSoup
# urljoin combines a base URL and a relative URL into one complete URL
from urllib.parse import urljoin
# logging lets us record skipped rows instead of silently ignoring them
import logging
# A logger named after this module
logger = logging.getLogger(__name__)


# The site's base address, used to complete relative links like "item?id=123"
BASE_URL = "https://news.ycombinator.com/"

# Take an html string,return a list of dictionaries(one dictionary per story)
def parse_stories(html:str) -> list[dict]:
    """Extract story titles and links from a Hacker News front page."""
    #Build a "soup" object;"html.parse" is python's built-in html parser
    soup = BeautifulSoup(html,"html.parser")
    #Create an empty list to collect the results
    stories = []

    # Each story is a <tr> tag with class "athing"; loop over all of them
    for row in soup.select("tr.athing"):
        # Read this row's "id" attribute, which is the story's unique number
        story_id = row.get("id")
        # Inside this row, find the first title link (select_one returns one tag or None)
        link = row.select_one("span.titleline>a")
        # If the row has no id or no link, skip it and move to the next row
        if story_id is None or link is None:
            # %s placeholders are filled by the extra arguments (lazy formatting)
            logger.warning("Skipped a row: id=%s, has_link=%s",story_id,link is not None)
            continue
        # Get the raw href value, which may be relative like "item?id=123"
        href = link.get("href")
        # Add one dictionary to the list for this story
        stories.append(
            {
                # The unique id, stored as a string
                "id":story_id,
                # The visible title text
                "title":link.get_text(),
                # urljoin leaves full URLs unchanged and completes relative ones
                "url": urljoin(BASE_URL,href),
            }
        )

    # Give the finished list back to whoever called this function
    return stories

# Runs only when this file is executed directly
if __name__ == "__main__":
    # Import Path to read the saved sample page
    from pathlib import Path

    # Read the local sample file as a string (no network needed)
    html = Path("tests/fixtures/hn_sample.html").read_text(encoding="utf-8")
    # Parse it
    stories = parse_stories(html)
    # Print how many stories were found
    print(f"Found {len(stories)} stories")
    # Print the first 5;stories[:5] is a "slice" meaning items 0 to 4
    for story in stories[:5]:
        print(story)

