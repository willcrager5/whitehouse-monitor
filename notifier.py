import requests
from email.utils import parsedate_to_datetime
from config import SLACK_BOT_TOKEN, SLACK_USER_IDS, NOTION_API_KEY, NOTION_DATABASE_ID

SLACK_HEADERS = {
    "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
    "Content-Type": "application/json",
}

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
    blocks = [
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

    for user_id in SLACK_USER_IDS:
        resp = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers=SLACK_HEADERS,
            json={"channel": user_id, "blocks": blocks},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if not data.get("ok"):
            raise RuntimeError(f"Slack API error for {user_id}: {data.get('error')}")


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
