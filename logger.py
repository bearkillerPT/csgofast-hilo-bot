import csv
import os
from datetime import datetime
from threading import Lock


class FileLogger:
    """Simple CSV file logger for game events.

    Writes rows with a timestamp. Ensures header is present.
    Methods:
      - log_bet(timestamp, bet_value, result, balance_before, balance_after)
      - log_event(event_type, details)
    """

    DEFAULT_FIELDS = [
        "timestamp",
        "type",
        "bet_value",
        "result",
        "balance_before",
        "balance_after",
        "details",
    ]

    def __init__(self, file_path: str = "game_logs.csv"):
        self.file_path = file_path
        self.lock = Lock()
        # Ensure directory exists
        directory = os.path.dirname(os.path.abspath(self.file_path))
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        # Create file and write header if needed
        if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0:
            with open(self.file_path, mode="a", newline='', encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=self.DEFAULT_FIELDS)
                writer.writeheader()

    def _write_row(self, row: dict):
        with self.lock:
            with open(self.file_path, mode="a", newline='', encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=self.DEFAULT_FIELDS)
                writer.writerow(row)

    def log_bet(self, bet_value, result, balance_before=None, balance_after=None, timestamp: str = None):
        """Log a bet event.

        result should be a short string like 'win' or 'loss'.
        """
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()
        row = {
            "timestamp": timestamp,
            "type": "bet",
            "bet_value": bet_value,
            "result": result,
            "balance_before": balance_before,
            "balance_after": balance_after,
            "details": "",
        }
        self._write_row(row)

    def log_event(self, event_type: str, details: str = "", timestamp: str = None):
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()
        row = {
            "timestamp": timestamp,
            "type": event_type,
            "bet_value": "",
            "result": "",
            "balance_before": "",
            "balance_after": "",
            "details": details,
        }
        self._write_row(row)


__all__ = ["FileLogger"]
