import anthropic
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM = (
    "You are a policy analyst specializing in executive branch actions. "
    "Provide concise, accurate summaries without political framing."
)

PROMPT_TEMPLATE = """\
Summarize this presidential action using exactly this format.
Use Slack formatting: *bold* for labels (single asterisk), not markdown **bold**.

*Title:* {title}
*Date:* {published}
*Type:* [Executive Order / Presidential Memorandum / Proclamation / other]

*Summary:* [2-3 sentence plain-English summary of what this does]

*Key Provisions:*
- [provision]
- [provision]
- [provision]

*Affected Agencies / Departments:*
- [agency]

*Key Implications:*
[2-3 sentences on practical impact — who is affected and how]

Full text:
{content}
"""


RELEVANT_TOPICS = [
    "financial services",
    "artificial intelligence",
    "fintech",
    "wealth management",
    "asset management",
    "banking",
    "securities",
    "investment",
    "capital markets",
]

RELEVANCE_PROMPT = """\
Does this presidential action materially affect any of these topics?
- Financial services
- Artificial intelligence
- Fintech
- Wealth management
- Asset management

Title: {title}

Content: {content}

Reply with a single word: YES or NO."""


def is_relevant(order: dict) -> bool:
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=5,
        messages=[{
            "role": "user",
            "content": RELEVANCE_PROMPT.format(
                title=order["title"],
                content=order["content"][:3000],
            ),
        }],
    )
    return message.content[0].text.strip().upper().startswith("YES")


def summarize_order(order: dict) -> str:
    prompt = PROMPT_TEMPLATE.format(
        title=order["title"],
        published=order["published"],
        content=order["content"][:8000],  # stay well inside context
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text
