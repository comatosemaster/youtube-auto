import sys

MODEL = "llama3.1:8b"

SYSTEM_PROMPT = (
    "You are writing a YouTube video description.\n"
    "Rules:\n"
    "- First line must be a strong 1-2 sentence hook summarizing the core idea\n"
    "- Then write 2-4 short paragraphs expanding the topic naturally\n"
    "- Use SEO-friendly phrasing without sounding robotic\n"
    "- Do NOT use emojis\n"
    "- Do NOT use markdown\n"
    "- Do NOT sound like a corporate marketer\n"
    "- Do NOT say 'in this video'\n"
    "- Keep it clean and readable\n"
    "- At the end, add 8-12 relevant hashtags on one line\n"
    "- Hashtags must relate to the topic naturally\n"
)

def generate_description(title: str, speech_text: str) -> str:
    from ollama import chat  # lazy import

    user_prompt = (
        f"Video Title: {title}\n\n"
        "Here is the spoken narration of the video:\n\n"
        f"{speech_text}\n\n"
        "Generate a YouTube description based on this narration."
    )

    response = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        options={
            "temperature": 0.6,
            "top_p": 0.9
        }
    )

    return response["message"]["content"].strip()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python yt_description_generator.py \"title\" \"speech_text_file.txt\"")
        sys.exit(1)

    title = sys.argv[1]
    speech_file_path = sys.argv[2]

    with open(speech_file_path, "r", encoding="utf-8") as f:
        speech_text = f.read()

    description = generate_description(title, speech_text)
    print(description)
