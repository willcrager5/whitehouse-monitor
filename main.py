import logging
import sys
import time

from scraper import fetch_new_orders, save_state
from summarizer import summarize_order
from notifier import post_to_slack, post_to_notion
from config import POLL_INTERVAL_SECONDS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def process_order(order: dict) -> None:
    log.info(f"Summarizing: {order['title']}")
    summary = summarize_order(order)
    post_to_slack(order, summary)
    log.info("  → posted to Slack")
    post_to_notion(order, summary)
    log.info("  → posted to Notion")


def run_once() -> None:
    new_orders, seen = fetch_new_orders()

    if not new_orders:
        log.info("No new presidential actions.")
        return

    log.info(f"Found {len(new_orders)} new action(s).")

    for order in new_orders:
        try:
            process_order(order)
            seen.add(order["id"])
            save_state(seen)
        except Exception:
            log.exception(f"Failed to process: {order['title']}")


def main() -> None:
    log.info("White House monitor started.")
    if "--once" in sys.argv:
        run_once()
    else:
        while True:
            run_once()
            log.info(f"Sleeping {POLL_INTERVAL_SECONDS}s until next poll...")
            time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
