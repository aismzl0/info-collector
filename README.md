# info-collector

A small, polite web collector that fetches the Hacker News front page, extracts stories, and stores them in SQLite without duplicates.

It started as a course assignment and was reworked to follow the habits of real backend development: modular code, error handling, logging, tests, and respect for the target site's rules.

## Features

- **Modular pipeline**: fetching, parsing, storage, politeness rules, and the CLI live in separate modules.
- **Deduplication**: stories are stored in SQLite with the story id as the primary key, so saving the same story twice never creates a duplicate.
- **Polite crawling**: reads `robots.txt` before crawling, refuses to crawl if the rules cannot be loaded, honors `Crawl-delay` (30 seconds for Hacker News), and sends a descriptive User-Agent.
- **Error handling and logging**: timeouts, HTTP errors, and connection failures are logged to the screen and to `logs/collector.log` instead of crashing the program.
- **Offline mode**: `--from-file` parses a saved HTML page without touching the network, which makes development and testing fast and kind to the target site.
- **Tests**: 14 pytest tests that run without network access.

## Installation

Requires Python 3.10 or newer.

```powershell
git clone https://github.com/aismzl0/info-collector.git
cd info-collector
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
pip install pytest
```

## Usage

```powershell
# Fetch the front page (polite: waits between requests)
python -m collector.cli

# Fetch the first two pages
python -m collector.cli --pages 2

# Parse a saved HTML file instead of downloading (offline)
python -m collector.cli --from-file tests/fixtures/hn_sample.html

# Choose a different database file
python -m collector.cli --db data/other.db

# Show all options
python -m collector.cli --help
```

`--pages` accepts 1 to 3. Because Hacker News asks for a 30-second delay between requests, a 3-page crawl takes about two minutes.

## Sample output

````2026-11-28 05:08:26,698 INFO collector.fetcher: Fetched https://news.ycombinator.com/robots.txt(243 characters)
2026-11-28 05:08:26,701 INFO collector.pipeline: Using a delay of 30.0 seconds between requests
2026-11-28 05:08:26,704 INFO collector.politeness: Rate limit: sleeping 28.5 seconds
2026-11-28 05:08:57,038 INFO collector.fetcher: Fetched https://news.ycombinator.com/(32730 characters)
2026-11-28 05:08:57,194 INFO collector.politeness: Rate limit: sleeping 28.0 seconds
2026-11-28 05:09:26,557 INFO collector.fetcher: Fetched https://news.ycombinator.com/?p=2(32834 characters)
2026-11-28 05:09:26,600 INFO collector.pipeline: Done. 59 new stories saved```

## Running the tests

```powershell
python -m pytest -v
````

````platform win32 -- Python 3.11.6, pytest-9.2.0, pluggy-1.7.0 -- D:\imm\new_pro\info-collector.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\imm\new_pro\info-collector
configfile: pyproject.toml
collected 14 items

tests/test_parser.py::test_parses_stories_from_real_sample PASSED [ 7%]
tests/test_parser.py::test_relative_url_is_completed PASSED [ 14%]
tests/test_parser.py::test_row_without_link_is_skipped PASSED [ 21%]
tests/test_pipeline.py::test_first_page_is_home_page PASSED [ 28%]
tests/test_pipeline.py::test_second_page_uses_query_parameter PASSED [ 35%]
tests/test_politeness.py::test_allowed_path PASSED [ 42%]
tests/test_politeness.py::test_disallowed_path PASSED [ 50%]
tests/test_politeness.py::test_no_rules_means_refuse PASSED [ 57%]
tests/test_politeness.py::test_delay_uses_site_crawl_delay PASSED [ 64%]
tests/test_politeness.py::test_delay_falls_back_to_default PASSED [ 71%]
tests/test_politeness.py::test_rate_limiter_waits_between_requests PASSED [ 78%]
tests/test_storage.py::test_duplicate_ids_are_skipped PASSED [ 85%]
tests/test_storage.py::test_existing_row_is_not_overwritten PASSED [ 92%]
tests/test_storage.py::test_init_db_is_safe_to_call_twice PASSED [100%]

============================ 14 passed in 1.13s ============================```

## Project structure

````

info-collector/
├── src/collector/
│ ├── fetcher.py # download a page (User-Agent, timeout, error handling)
│ ├── hn_parser.py # HTML -> list of {id, title, url}
│ ├── storage.py # SQLite storage with id-based deduplication
│ ├── politeness.py # robots.txt rules and the rate limiter
│ ├── pipeline.py # robots -> rate limit -> download -> parse -> store
│ ├── cli.py # command-line interface (argparse)
│ └── log_config.py # logging to screen and file
├── tests/ # pytest tests and a saved sample page
├── pyproject.toml # project metadata and dependencies
└── requirements.txt # pinned versions used during development

```

## Challenges and solutions

<<< None >>>

## Future improvements

- Distinguish a missing `robots.txt` (HTTP 404, which by convention means "no restrictions") from a failed download. Today every failure is treated as "refuse to crawl".
- Add retries with backoff for temporary server errors.
- Add full-text search over the stored stories (SQLite FTS5).
- Use the stored stories as a knowledge base for question answering with a language model.

## Scope and compliance

Only public pages that `robots.txt` allows are fetched. Pages that require login are not collected.
```
