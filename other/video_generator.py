import sys
import os
import requests
from io import BytesIO
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, vfx
import random

# ---- Pillow / MoviePy compatibility patch ----
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

UNSPLASH_SEARCH_URL = "https://api.unsplash.com/search/photos"
UNSPLASH_IMAGE_URL_KEY = "regular"  # or 'full', 'raw'
UNSPLASH_ACCESS_KEY = "WuB0eQNYWOP8RZeFZu-J2xD_k6lLm-UsdagO6WLIFQw"

def to_youtube_resolution(
    img: Image.Image,
    target_w: int = 1920,
    target_h: int = 1080
) -> Image.Image:
    img_w, img_h = img.size

    target_ratio = target_w / target_h
    img_ratio = img_w / img_h

    if img_ratio > target_ratio:
        # too wide → crop left/right
        new_w = int(img_h * target_ratio)
        left = (img_w - new_w) // 2
        img = img.crop((left, 0, left + new_w, img_h))
    else:
        # too tall → crop top/bottom
        new_h = int(img_w / target_ratio)
        top = (img_h - new_h) // 2
        img = img.crop((0, top, img_w, top + new_h))

    return img.resize((target_w, target_h), Image.LANCZOS)


def _download_images(count: int, output_dir: str, keyword: str) -> list[str]:
    os.makedirs(output_dir, exist_ok=True)
    paths = []

    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }

    params = {
        "query": keyword,
        "orientation": "landscape",
        "per_page": count,
        "page": random.randint(1, 10)
    }

    r = requests.get(
        UNSPLASH_SEARCH_URL,
        headers=headers,
        params=params,
        timeout=20
    )
    r.raise_for_status()

    results = r.json().get("results", [])
    if not results:
        raise RuntimeError("Unsplash returned no results")

    for i, item in enumerate(results[:count]):
        img_url = item["urls"][UNSPLASH_IMAGE_URL_KEY]
        path = os.path.join(output_dir, f"img_{i}.jpg")

        try:
            img_r = requests.get(img_url, timeout=20)
            img = Image.open(BytesIO(img_r.content)).convert("RGB")
            img = to_youtube_resolution(img)
            img.save(path, "JPEG", quality=95)
            paths.append(path)
        except Exception:
            continue

    if not paths:
        raise RuntimeError("No valid images downloaded")

    return paths

def ease(t):
    return t * t * (3 - 2 * t)

def generate_silent_video(
    audio_path: str,
    image_count: int,
    keyword: str,
    output_path: str,
    image_dir: str = r"materials/images"
) -> str:

    """
    Generates a silent video whose duration exactly matches audio_path.
    Returns output_path on success.
    """

    images = _download_images(image_count, image_dir, keyword)

    audio = AudioFileClip(audio_path)
    duration = audio.duration

    per_image = duration / len(images)
    clips = []

    for img in images:
        clip = ImageClip(img).set_duration(per_image)

        zoom_strength = 0.10  # 10%

        clip = (
            clip
            .fx(
                vfx.resize,
                lambda t: 1 + zoom_strength * ease(t / per_image)
            )
            .set_position(("center", "center"))
            .crop(
                x_center=clip.w / 2,
                y_center=clip.h / 2,
                width=1920,
                height=1080
            )
        )

        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose")
    video = video.set_duration(duration)

    video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio=False,
        threads=4
    )

    return output_path



# ---------------- CLI ----------------

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python video_generator.py audio.wav image_count keyword output.mp4")
        sys.exit(1)

    audio_path = sys.argv[1]
    image_count = int(sys.argv[2])
    keyword = sys.argv[3]
    output_path = sys.argv[4]

    generate_silent_video(audio_path, image_count, keyword, output_path)

    print(f"Video saved to {output_path}")
