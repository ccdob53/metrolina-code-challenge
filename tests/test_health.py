import re
from datetime import datetime, timezone

import requests


def test_api_is_reachable(base_url):
    response = requests.get(f"{base_url}/Test/TestEndpoint")

    # Check status code and response format
    assert response.status_code == 200
    assert response.text is not None

    # Regex to remove extra digits from microseconds if present (e.g. "2024-06-01T12:34:56.123456789Z" -> "2024-06-01T12:34:56.123456Z")
    timestamp_str = re.sub(r"(\.\d{6})\d+", r"\1", response.text.strip('"'))
    parsed = datetime.fromisoformat(timestamp_str)

    # Check timestamp is within 10 seconds of current time (to account for network latency)
    now_utc = datetime.now(timezone.utc)
    diff = abs((parsed.astimezone(timezone.utc) - now_utc).total_seconds())
    assert diff < 10, f"Timestamp too far from current time: {diff} seconds off"

    # Check timezone offset is either -4 or -5 hours (Eastern Time with/without DST)
    offset_hours = parsed.utcoffset().total_seconds() / 3600
    assert offset_hours in [
        -4.0,
        -5.0,
    ], f"Unexpected timezone offset: {offset_hours} hours"
