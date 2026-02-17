import os
import base64
import requests
from io import BytesIO
from PIL import Image, ImageOps
from dotenv import load_dotenv
from openai import OpenAI


# -----------------------------------------
# Setup
# -----------------------------------------

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
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=20
    )

    hook = response.choices[0].message.content.strip().upper()

    # Safety cleanup
    hook = hook.replace('"', "").replace("'", "").strip()

    return hook


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

    Do not use any other text.
    Do not include the original video title.
    Do not expand the hook.

    Visual theme:
    {title}

    Requirements:
    - Strong focal point
    - Clean background
    - High contrast
    - Cinematic quality
    - No clutter
    - No watermark
    - No AI artifacts
    - 16:9 layout

    Text styling:
    - First line YELLOW
    - Second line WHITE
    - Third line YELLOW if exists
    - Very large bold font
    - Thick black outline
    - Readable on mobile
    """

    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1536x1024",
        quality="medium"
    )

    if not result.data:
        raise RuntimeError("Image generation returned empty data.")

    image_data = result.data[0]

    # Handle base64 response (modern default)
    if getattr(image_data, "b64_json", None):
        image_bytes = base64.b64decode(image_data.b64_json)

    # Handle URL response (fallback)
    elif getattr(image_data, "url", None):
        response = requests.get(image_data.url)
        image_bytes = response.content

    else:
        raise RuntimeError("Image generation failed: no image data returned.")

    img = Image.open(BytesIO(image_bytes))

    # Crop properly to YouTube size without distortion
    img = ImageOps.fit(
        img,
        (1280, 720),
        Image.LANCZOS,
        centering=(0.5, 0.5)
    )

    img.save(OUTPUT_PATH)

    print(f"Thumbnail saved at: {OUTPUT_PATH}")

    return OUTPUT_PATH
