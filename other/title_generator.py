import sys

MODEL = "llama3.2:latest"

SYSTEM_PROMPT = (
    "You are a YouTube title generator.\n"
    "Rules:\n"
    "- Generate ONE title only\n"
    "- Max 80 characters\n"
    "- No emojis\n"
    "- No quotes\n"
    "- No explanations\n"
    "- Make it clear, curious, and clickable\n"
)

def generate_title(topic: str) -> str:
    from ollama import chat   # lazy import

    response = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Topic: {topic}"}
        ],
        options={
            "temperature": 0.6,
            "top_p": 0.9
        }
    )

    return response["message"]["content"].strip('"').strip("'")



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python title_generator.py \"your topic here\"")
        sys.exit(1)

    topic = sys.argv[1]
    title = generate_title(topic)
    print(title)
