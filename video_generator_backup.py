import sys
import os
import requests
from io import BytesIO
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

PICSUM_URL = "https://picsum.photos/1920/1080"

def _download_images(count: int, output_dir: str) -> list[str]:
    os.makedirs(output_dir, exist_ok=True)
    paths = []

    for i in range(count):
        path = os.path.join(output_dir, f"img_{i}.jpg")
        r = requests.get(PICSUM_URL, timeout=20)

        try:
            img = Image.open(BytesIO(r.content))
            img = img.convert("RGB")
            img.save(path, "JPEG")
            paths.append(path)
        except Exception:
            continue

    if not paths:
        raise RuntimeError("No valid images downloaded")

    return paths


def generate_silent_video(
    audio_path: str,
    image_count: int,
    output_path: str,
    image_dir: str = "images"
) -> str:
    """
    Generates a silent video whose duration exactly matches audio_path.
    Returns output_path on success.
    """

    images = _download_images(image_count, image_dir)

    audio = AudioFileClip(audio_path)
    duration = audio.duration

    per_image = duration / len(images)
    clips = []

    for img in images:
        clips.append(ImageClip(img).set_duration(per_image))

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
    if len(sys.argv) < 4:
        print("Usage: python video_generator.py audio.wav image_count output.mp4")
        sys.exit(1)

    audio_path = sys.argv[1]
    image_count = int(sys.argv[2])
    output_path = sys.argv[3]

    generate_silent_video(audio_path, image_count, output_path)
    print(f"Video saved to {output_path}")
