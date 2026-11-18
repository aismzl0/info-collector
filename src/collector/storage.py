# sqlite3 is built into Python, so no pip install is needed
import sqlite3
# Path helps us build file paths that work on any operating system
from pathlib import Path


#Where the database file lives. The "data" folder is created automatically.
DB_PATH = Path("data/stories.db")


# Open (or create) the database file and return a connection object.
# "conn" is our line of communication with the database.
def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Open a connection to the SQLite database, creating folders if needed."""
    # Make sure the folder that will hold the database file exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    # Connect; if the file does not exist yet, SQLite creates it
    return sqlite3.connect(db_path)


# Create the table if it is not there yet
# `-> None`：type annotation, indicating that this function "has no return value"
def init_db(conn:sqlite3.Connection) -> None:
    """Create the stories table if it does not already exist."""
    # execute() sends one SQL statement to the database
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS stories (
            id          TEXT PRIMARY KEY,               --unique story id from HM
            title       TEXT NOT NULL,                  --must not be empty
            url         TEXT NOT NULL,                  --full link
            fetched_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP    --filled in automatically
        )
        """
    )
    # commit() makes the change permanent; without it the change can be lost
    conn.commit()


# Save many stories at once and report how many were actually new
def save_stories(conn: sqlite3.Connection,stories: list[dict]) ->int:
    """Insert stories, skipping ones whose id already exists. Return the new-row count."""
    # executemany() runs the same SQL once for each dictionary in the list.
    # :id, :title and :url are placeholders filled from each dictionary's keys.
    cursor = conn.executemany(
        "INSERT OR IGNORE INTO stories (id,title,url) VALUES (:id,:title,:url)",
        stories,
    )
    # Make the inserts permanent
    conn.commit()
    # rowcount is the number of rows really inserted (ignored duplicates count as 0)
    return cursor.rowcount


# Count how many rows are currently in the table
def count_stories(conn:sqlite3.Connection) -> int:
    """Return the total number of stored stories."""
    # fetchone() returns the first result row as a tuple, e.g. (30,)
    # [0] picks the first (and only) value out of that tuple
    return conn.execute("SELECT COUNT(*) FROM stories").fetchone()[0]


# Runs only when this file is executed directly: a small demo of deduplication
if __name__ == "__main__":
    # Two fake stories, just for this demo
    demo = [
        {"id":"1","title":"First story","url":"https://example.com/a"},
        {"id":"2","title":"Second story", "url": "https://example.com/b"}
    ]
    conn = get_connection()
    init_db(conn)
    # Save the same list twice to prove duplicates are skipped
    print("First save, new rows:", save_stories(conn, demo))
    print("Second save, new rows:", save_stories(conn, demo))
    print("Total rows in table:", count_stories(conn))
    # Close the connection when we are done
    conn.close()