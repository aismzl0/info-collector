# logging is built into Python, no pip install needed
import logging

# Path helps us build file paths that work on any operating system
from pathlib import Path


# Set up logging once, at program start
def setup_logging(log_file: Path = Path("logs/collector.log")) -> None:
    """Send log messages to both the screen and a log file."""
    # Create the "logs" folder if it does not exist yet
    log_file.parent.mkdir(parents=True,exist_ok=True)
    # basicConfig sets the global logging behavior
    logging.basicConfig(
        # Show INFO and above (INFO, WARNING, ERROR); hide DEBUG
        level=logging.INFO,
        # Each line looks like: 2026-11-17 10:30:00 INFO fetcher: message
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        # handlers decide WHERE messages go: file and screen
        handlers=[
            # Write to the log file (utf-8 avoids garbled text on Windows)
            logging.FileHandler(log_file,encoding="utf-8"),
            # Also print to the terminal
            logging.StreamHandler(),
        ]
    )