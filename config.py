import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_USER_ID = os.environ["SLACK_USER_ID"]
NOTION_API_KEY = os.environ["NOTION_API_KEY"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]

POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "3600"))
STATE_FILE = os.getenv("STATE_FILE", "processed_orders.json")
WH_RSS_URL = "https://www.whitehouse.gov/presidential-actions/feed/"
