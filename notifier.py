import requests
from email.utils import parsedate_to_datetime
from config import SLACK_WEBHOOK_URL, NOTION_API_KEY, NOTION_DATABASE_ID

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


def _parse_iso_date(rss_date: str) -> str:
    """Convert RSS date string to ISO 8601 for Notion."""
    try:
        return parsedate_to_datetime(rss_date).strftime("%Y-%m-%d")
    except Exception:
        return ""


def post_to_slack(order: dict, summary: str) -> None:
    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"New Presidential Action: {order['title'][:140]}",
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": summary[:2900]},
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View Full Text"},
                        "url": order["link"],
                    }
                ],
            },
        ]
    }
    resp = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
    resp.raise_for_status()


def post_to_notion(order: dict, summary: str) -> None:
    iso_date = _parse_iso_date(order["published"])

    properties = {
        "Name": {"title": [{"text": {"content": order["title"]}}]},
        "URL": {"url": order["link"]},
        "Status": {"select": {"name": "New"}},
    }
    if iso_date:
        properties["Date"] = {"date": {"start": iso_date}}

    # Notion blocks have a 2000-char limit per paragraph; chunk if needed
    chunks = [summary[i : i + 2000] for i in range(0, len(summary), 2000)]
    children = [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": chunk}}]
            },
        }
        for chunk in chunks
    ]

    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": properties,
        "children": children,
    }

    resp = requests.post(
        "https://api.notion.com/v1/pages",
        headers=NOTION_HEADERS,
        json=payload,
        timeout=15,
    )
    resp.raise_for_status()
