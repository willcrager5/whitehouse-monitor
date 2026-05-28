import json
import os
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import feedparser
from config import WH_RSS_URL, STATE_FILE, CUTOFF_DATE

_CUTOFF = datetime.fromisoformat(CUTOFF_DATE).replace(tzinfo=timezone.utc)


def _published_dt(entry) -> datetime | None:
    try:
        return parsedate_to_datetime(entry.get("published", ""))
    except Exception:
        return None


def load_state() -> set:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return set(json.load(f))
    return set()


def save_state(seen_ids: set) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(list(seen_ids), f)


def fetch_new_orders() -> tuple[list[dict], set]:
    seen = load_state()
    feed = feedparser.parse(WH_RSS_URL)
    new_orders = []

    for entry in feed.entries:
        entry_id = entry.get("id") or entry.get("link")
        if entry_id in seen:
            continue

        pub_dt = _published_dt(entry)
        if pub_dt and pub_dt < _CUTOFF:
            continue

        content = ""
        if entry.get("content"):
            content = entry["content"][0].get("value", "")
        if not content:
            content = entry.get("summary", "")

        new_orders.append({
            "id": entry_id,
            "title": entry.get("title", "Untitled"),
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
            "content": content,
        })

    return new_orders, seen
