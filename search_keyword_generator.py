import sys

MODEL = "llama3.2:latest"

SYSTEM_PROMPT = (
    "You convert a YouTube video title into ONE visual search keyword which will be used in image search for the video.\n"
    "Rules:\n"
    "- Output ONE keyword only\n"
    "- Maximum 1 word\n"
    "- No punctuation\n"
    "- No emojis\n"
    "- No explanations\n"
    "- Must describe something that can be photographed and directly related to the YouTube video title\n"
    "- Prioritize concrete, physical nouns over abstract concepts\n"
    "- Avoid vague words like life, world, society, nature\n"
    "- Example 1: 'What if we run out of air?' output: 'forest'\n"
    "- Example 2: 'Why Modern Life Feels Empty' output: 'street'\n"
)

def generate_search_keyword(title: str) -> str:
    from ollama import chat  # lazy import

    response = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Title: {title}"}
        ],
        options={
            "temperature": 0.4,
            "top_p": 0.9
        }
    )

    keyword = response["message"]["content"].strip().lower()

    # safety cleanup
    keyword = keyword.splitlines()[0]
    keyword = keyword.replace(".", "").replace(",", "")

    return keyword


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search_keyword_generator.py \"video title here\"")
        sys.exit(1)

    title = sys.argv[1]
    keyword = generate_search_keyword(title)
    print(keyword)
