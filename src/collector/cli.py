# argparse is Python's built-in tool for reading command-line arguments
import argparse

# Path turns a text argument into a path object
from pathlib import Path

# Our shared logging setup and the two pipeline entry points
from collector.log_config import setup_logging
from collector.pipeline import run_from_file, run_online
from collector.storage import DB_PATH


# Describe which arguments our program accepts, and read them
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Define the command-line options and parse them."""
    # The parser also generates the --help text automatically
    parser = argparse.ArgumentParser(
        description="Collect Hacker News stories politely and store them in SQLite."
    )
    # --pages takes an integer; default is 1 so a plain run is the smallest possible crawl
    parser.add_argument(
        "--pages", type=int, default=1, choices=[1,2,3],
        help="how many front pages to fetch (default: 1)",
    )
    # --db takes a path; type=Path converts the text into a Path object
    parser.add_argument(
        "--db", type=Path, default=DB_PATH,
        help="SQLite file to write to (default: data/stories.db)",
    )
    # --from-file switches to offline mode: parse a saved HTML file, no network
    parser.add_argument(
        "--from-file", type=Path, default=None,
        help="parse a saved HTML file instead of downloading (offline)",
    )
    # Read the real command line (or the list we pass in during tests)
    return parser.parse_args(argv)
  

# The program's entry point
def main(argv: list[str] | None = None) -> int:
    """Run the collector. Return 0 on success (a convention for exit codes)."""
    # Read the options the user typed
    args = parse_args(argv)
    # Start logging before any work happens
    setup_logging()
    # Offline mode if a file was given, otherwise the polite online crawl
    if args.from_file is not None:
        run_from_file(args.from_file, args.db)
    else:
        run_online(args.pages, args.db)
        return 0


# Runs only when this module is executed with "python -m collector.cli"
if __name__ == "__main__":
    # raise SystemExit(0) ends the program and passes 0 to the operating system
    raise SystemExit(main())