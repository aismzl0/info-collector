# Import the storage functions we want to test
from collector.storage import count_stories, get_connection, init_db, save_stories


# Helper: build a small list of fake stories (a plain function, not a test)
def make_stories():
    return [
        {"id": "1", "title": "First", "url": "https://example.com/a"},
        {"id": "2", "title": "Second", "url": "https://example.com/b"},
    ]


# Saving the same list twice must not create duplicates  
def test_duplicate_ids_are_skipped(tmp_path):
    # tmp_path is a fresh temporary folder, so this database is brand new
    conn = get_connection(tmp_path / "test.db")
    init_db(conn)
    stories = make_stories()
    # File save: both rows are new
    assert save_stories(conn, stories) == 2
    # Second save: both ids already exist, so nothing is inserted
    assert save_stories(conn, stories) == 0
    # The table still holds exactly 2 rows
    assert count_stories(conn) == 2
    conn.close()
    


# If an id already exists, the FIRST saved version is kept (INSERT OR IGNORE, not REPLACE)
def test_existing_row_is_not_overwritten(tmp_path):
    conn = get_connection(tmp_path / "test.db")
    init_db(conn)
    save_stories(conn, [{"id": "1", "title": "Old title", "url": "https://example.com/a"}])
    # Same id, different title
    save_stories(conn, [{"id": "1", "title": "New title", "url": "https://example.com/a"}])
    # Only one row, and it still has the old title
    assert count_stories(conn) == 1
    title = conn.execute("SELECT title FROM stories WHERE id = '1'").fetchone()[0]
    assert title == "Old title"
    conn.close()


# init_db uses CREATE TABLE IF NOT EXISTS, so calling it twice must not fail or erase data
def test_init_db_is_safe_to_call_twice(tmp_path):
    conn = get_connection(tmp_path / "test.db")
    init_db(conn)
    save_stories(conn, make_stories())
    # Calling init_db again must not raise an error or delete the rows
    init_db(conn)
    assert count_stories(conn) == 2
    conn.close()


