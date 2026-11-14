# import beautifulsoup,which turns an HTML string into a serachable object
from bs4 import BeautifulSoup


# Take an html string,return a list of dictionaries(one dictionary per story)
def parse_stories(html:str) -> list[dict]:
    """Extract story titles and links from a Hacker News front page."""
    #Build a "soup" object;"html.parse" is python's built-in html parser
    soup = BeautifulSoup(html,"html.parser")
    #Create an empty list to collect the results
    stories = []
    # select() finds all <a> tags directly inside <span class="titleline">.
    # "span.titleline > a" is a CSS selector, the same syntax used in web styling.
    for link in soup.select("span.titleline > a"):
        # Add one dictionary to the list for each link found
        stories.append(
            {
                # get_text() returns the visible text between <a> and </a>
                # get("href") returns the value of the href attribute (the URL)
                "title":link.get_text(),
                "url":link.get("href"),
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

