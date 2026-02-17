import sys
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MODEL = "gpt-5-mini"
WORDS_PER_MINUTE = 150

SYSTEM_PROMPT = """
You are writing a spoken YouTube narration.

YES:
- YES strong psychological hook in the first 2–3 sentences
- YES introduce tension early
- YES escalate the idea gradually
- YES alternate short punchy sentences with longer reflective ones
- YES use vivid but simple imagery when possible
- YES maintain emotional undercurrent
- YES sound human and slightly dramatic but controlled
- YES vary sentence rhythm
- YES leave tension unresolved at the end

NO:
- NO greetings
- NO mentioning audience or channel
- NO summaries or conclusions
- NO phrases like "throughout history" or "since the dawn of time"
- NO academic tone
- NO statistics, dates, named individuals
- NO filler phrases
- NO repeating the topic wording
- NO safe neutral tone
- NO obvious AI phrasing

Write as one continuous narration.
No emojis. No markdown. No headings.
""".strip()


def target_word_count(seconds: int) -> int:
    return int((seconds / 60) * WORDS_PER_MINUTE)


def generate_text(title: str, seconds: int) -> str:
    words = target_word_count(seconds)

    user_prompt = f"""
Topic: {title}

Duration target: {seconds} seconds.
Approximate word count: {words}.

Structure:
1. Hook (first 10–15 seconds must create psychological tension)
2. Expansion of idea
3. Deeper unsettling turn
4. Open unresolved ending

Do not explain the topic academically.
Do not resolve the idea.
Keep it immersive.
""".strip()

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment.")

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python text_generator.py \"title\" duration_seconds")
        sys.exit(1)

    title = sys.argv[1]
    seconds = int(sys.argv[2])

    text = generate_text(title, seconds)
    print(text)
