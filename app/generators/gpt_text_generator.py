import sys
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MODEL = "gpt-5-mini"
WORDS_PER_MINUTE = 150

SYSTEM_PROMPT = """
You are writing a spoken YouTube narration for a science and technology channel.

YES:
- YES start with a clear conceptual hook (not emotional drama).
- YES define the core mechanism or problem early.
- YES explain how the system works step by step.
- YES use precise but accessible language.
- YES introduce cause-and-effect reasoning.
- YES use technical terminology when appropriate (but explain it clearly).
- YES include mechanisms, processes, constraints, trade-offs.
- YES build logical progression.
- YES maintain intellectual tension through complexity, not drama.
- YES end with an open scientific question or unresolved technical limitation.

NO:
- NO storytelling format.
- NO fictional scenarios.
- NO personal perspective.
- NO emotional manipulation.
- NO cinematic imagery.
- NO vague phrases like "something changed".
- NO filler sentences.
- NO dramatic cliffhanger language.
- NO audience addressing.
- NO greetings.
- NO summaries like "in conclusion".

Write as one continuous scientific narration.
No emojis. No markdown. No headings.
""".strip()


def target_word_count(seconds: int) -> int:
    return int((seconds / 60) * WORDS_PER_MINUTE)


def generate_text(title: str, seconds: int) -> str:
    words = target_word_count(seconds)

    user_prompt = f"""
    Topic: {title}

    Target duration: {seconds} seconds.
    The narration should be close to {words} words (±10%).
    Do not significantly underwrite or overwrite the target length.

    Structure:
    1. Technical hook introducing the core scientific or technological issue.
    2. Explanation of the underlying mechanism or system.
    3. Analysis of constraints, weaknesses, or edge cases.
    4. Forward-looking unresolved scientific or engineering challenge.

    Focus on clarity, reasoning, and mechanism.
    Avoid storytelling.
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
        ],
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
