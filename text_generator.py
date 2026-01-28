import sys

MODEL = "llama3.1:8b"
WORDS_PER_MINUTE = 150

SYSTEM_PROMPT = (
    "You are writing a continuous spoken narration for a YouTube video.\n"
    "Rules:\n"
    "- Do NOT greet the audience\n"
    "- Do NOT mention a channel or viewers\n"
    "- Do NOT use 'in conclusion' or summary phrases\n"
    "- Do NOT mention studies, dates, statistics, or named individuals\n"
    "- Do NOT sound academic or like a blog article\n"
    "- Write as one continuous exploratory thought\n"
    "- Use natural spoken English with varied sentence length\n"
    "- Maintain curiosity throughout\n"
    "- Don't spam questions, use questions but only when it's logical in flow\n"
    "- End without wrapping up or concluding\n"
    "- No emojis, no markdown, no headings\n"
)

def target_word_count(seconds: int) -> int:
    return int((seconds / 60) * WORDS_PER_MINUTE)

def generate_text(title: str, seconds: int) -> str:
    from ollama import chat  # lazy import

    words = target_word_count(seconds)

    user_prompt = (
        f"Topic: {title}\n"
        f"Write approximately {words} words.\n"
        f"The narration must last about {seconds} seconds when spoken calmly.\n"
        f"Explore the idea without giving final answers."
    )

    response = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        options={
            "temperature": 0.7,
            "top_p": 0.9
        }
    )

    return response["message"]["content"].strip()



if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python text_generator.py \"title\" duration_seconds")
        sys.exit(1)

    title = sys.argv[1]
    seconds = int(sys.argv[2])

    text = generate_text(title, seconds)
    print(text)
