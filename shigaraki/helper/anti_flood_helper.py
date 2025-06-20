from datetime import timedelta
from collections import defaultdict
import re


def parse_duration(duration_str):
    """Parses a duration string into a timedelta object."""
    time_units = {
        "s": "seconds",
        "m": "minutes",
        "h": "hours",
        "d": "days"
    }
    pattern = r"(\d+)([smhd])"
    matches = re.findall(pattern, duration_str.lower())
    if not matches:
        raise ValueError("Invalid duration format. Use a combination of s, m, h, d (e.g., '1d 2h 3m 4s').")

    kwargs = {}
    for value, unit in matches:
        kwargs[time_units[unit]] = kwargs.get(time_units[unit], 0) + int(value)
    return timedelta(**kwargs)

# Track user messages count and timestamps for flood detection
flood_tracker = defaultdict(lambda: {"count": 0, "timestamps": [], "messages": []})