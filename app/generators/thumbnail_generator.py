import os
import requests
from io import BytesIO
from PIL import Image, ImageOps
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_PATH = os.path.join(BASE_DIR, "materials", "thumbnails", "thumbnail.png")


# -----------------------------------------
# 1. HOOK GENERATOR
# -----------------------------------------

def generate_hook(title):

    prompt = f"""
You are a YouTube CTR strategist.

Create a 2-4 word powerful thumbnail hook.

Rules:
- Do NOT repeat the title.
- Maximum 4 words.
- No punctuation.
- No emojis.
- No quotes.
- Output ONLY the hook phrase.
- Clear and bold wording.

Title: {title}
"""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip().upper()


# -----------------------------------------
# 2. THUMBNAIL GENERATOR
# -----------------------------------------

def generate_thumbnail(title):

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    hook = generate_hook(title)

    prompt = f"""
Create a highly clickable YouTube thumbnail.

The hook text MUST be exactly:

{hook}

Do not modify the text.

General Requirements:

• High CTR composition
• Strong focal point
• Clean background
• No clutter
• Cinematic quality
• Professional color grading
• High contrast
• Sharp subject
• No AI artifacts
• No watermark
• No distorted elements
• 16:9 layout

Visual style should match the theme of:

{title}

If topic is:
- Space → cosmic scale, dramatic astronomy visuals
- Technology → modern tech visuals, sleek, sharp
- Psychology → conceptual or subtle human presence
- Abstract topic → symbolic visual metaphor

Do NOT force a human subject.
Use human only if contextually appropriate.

Text styling:

• First line YELLOW
• Second line WHITE
• Third line YELLOW if exists
• Very large bold modern YouTube font
• Thick black outline
• Clean readable layout
• Left or right placement depending on composition

Text must be readable at small mobile size.
"""

    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1536x1024",
        quality="medium"
    )

    image_url = result.data[0].url
    image_bytes = requests.get(image_url).content
    img = Image.open(BytesIO(image_bytes))

    img = ImageOps.fit(
        img,
        (1280, 720),
        Image.LANCZOS,
        centering=(0.5, 0.5)
    )

    img.save(OUTPUT_PATH)

    return OUTPUT_PATH
