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

```
2026-11-28 06:02:09,444 ERROR collector.fetcher: Request failed for https://news.ycombinator.com/robots.txt: ('Connection aborted.', ConnectionResetError(10054, '远程主机强迫关闭了一个现有的连接。', None, 10054, None))
2026-11-28 06:02:09,444 WARNING collector.politeness: Could not load https://news.ycombinator.com/robots.txt; will refuse to crawl
2026-11-28 06:02:09,445 ERROR collector.pipeline: No robots.txt rules, so nothong will be crawled
2026-11-28 06:03:22,508 INFO collector.fetcher: Fetched https://news.ycombinator.com/robots.txt (243 characters)
2026-11-28 06:03:22,511 INFO collector.pipeline: Using a delay of 30.0 seconds between requests
2026-11-28 06:03:22,512 INFO collector.politeness: Rate limit: sleeping 28.2 seconds
2026-11-28 06:03:52,559 INFO collector.fetcher: Fetched https://news.ycombinator.com/ (32910 characters)
2026-11-28 06:03:52,708 INFO collector.politeness: Rate limit: sleeping 28.0 seconds
2026-11-28 06:04:23,380 INFO collector.fetcher: Fetched https://news.ycombinator.com/?p=2 (32715 characters)
2026-11-28 06:04:23,439 INFO collector.pipeline: Done. 4 new stories saved
```

## Running the tests

```powershell
python -m pytest -v
```

Result: `14 passed`

## Project structure

```
info-collector/
├── src/collector/
│   ├── fetcher.py      # download a page (User-Agent, timeout, error handling)
│   ├── hn_parser.py    # HTML -> list of {id, title, url}
│   ├── storage.py      # SQLite storage with id-based deduplication
│   ├── politeness.py   # robots.txt rules and the rate limiter
│   ├── pipeline.py     # robots -> rate limit -> download -> parse -> store
│   ├── cli.py          # command-line interface (argparse)
│   └── log_config.py   # logging to screen and file
├── tests/              # pytest tests and a saved sample page
├── pyproject.toml      # project metadata and dependencies
└── requirements.txt    # pinned versions used during development
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
