import sys
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = "gpt-5-mini"

SYSTEM_PROMPT = """
You are a YouTube title strategist.

YES:
- YES choose a specific angle, not a broad summary
- YES make it concrete and visual when possible
- YES imply tension, consequence, or psychological impact
- YES make it feel like a moment, scenario, or hidden truth
- YES make it clickable without sounding cheap

NO:
- NO generic phrasing
- NO vague philosophical titles
- NO “The Truth About…” or “Everything You Need to Know”
- NO emojis
- NO quotes
- NO hashtags
- NO clickbait lies
- NO explanations
- NO multiple options

Generate ONE title only.
Max 85 characters.
""".strip()


def generate_title(topic: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found.")

    client = OpenAI(api_key=api_key)

    user_prompt = f"""
Topic: {topic}

Choose a sharp, detailed angle.
Focus on a specific moment, consequence, or experience.
""".strip()

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    )

    title = response.choices[0].message.content.strip()
    return title


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gpt_title_generator.py \"your topic here\"")
        sys.exit(1)

    topic = sys.argv[1]
    title = generate_title(topic)
    print(title)
