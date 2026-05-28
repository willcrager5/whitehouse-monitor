import anthropic
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM = (
    "You are a policy analyst specializing in executive branch actions. "
    "Provide concise, accurate summaries without political framing."
)

PROMPT_TEMPLATE = """\
Summarize this presidential action using exactly this format:

**Title:** {title}
**Date:** {published}
**Type:** [Executive Order / Presidential Memorandum / Proclamation / other]

**Summary:** [2-3 sentence plain-English summary of what this does]

**Key Provisions:**
- [provision]
- [provision]
- [provision]

**Affected Agencies / Departments:**
- [agency]

**Key Implications:**
[2-3 sentences on practical impact — who is affected and how]

Full text:
{content}
"""


def summarize_order(order: dict) -> str:
    prompt = PROMPT_TEMPLATE.format(
        title=order["title"],
        published=order["published"],
        content=order["content"][:8000],  # stay well inside context
    )

    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text
