import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are writing a YouTube video description for a science channel.

Rules:
- First line: 1-2 sentence strong hook summarizing the core idea.
- Then 2-3 short explanatory paragraphs.
- Clear scientific tone.
- No storytelling fluff.
- No fictional narrative.
- No emojis.
- No markdown.
- Do NOT say 'in this video'.
- Keep total length under 220 words.
- Do NOT exceed 15 lines total (including hashtags).
- End with 8-10 relevant hashtags on ONE line.
"""


def generate_description(title: str, script_text: str) -> str:

    # Trim script to reduce token cost
    trimmed_script = script_text[:2000]

    user_prompt = f"""
Title: {title}

Script excerpt:
{trimmed_script}

- Keep total length under 220 words.
- Do NOT exceed 15 lines total (including hashtags).

Generate the YouTube description following ALL rules strictly.
"""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
    )

    description = response.choices[0].message.content.strip()

    # Hard safety enforcement (line limit)
    lines = description.splitlines()
    if len(lines) > 15:
        description = "\n".join(lines[:15])

    return description
