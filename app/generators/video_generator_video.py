import sys
import os
import random
import requests
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PEXELS_SEARCH_URL = "https://api.pexels.com/videos/search"

if not PEXELS_API_KEY:
    raise ValueError("PEXELS_API_KEY not found in .env")

def _download_videos(count: int, output_dir: str, keyword: str, min_duration: float) -> list[str]:
    os.makedirs(output_dir, exist_ok=True)

    headers = {
        "Authorization": PEXELS_API_KEY
    }

    collected = []
    visited_pages = set()

    MAX_PAGES = 20  # safety cap
    MAX_ATTEMPTS = 40  # avoid infinite loops

    attempts = 0

    while len(collected) < count and attempts < MAX_ATTEMPTS:

        page = random.randint(1, MAX_PAGES)

        if page in visited_pages:
            attempts += 1
            continue

        visited_pages.add(page)

        params = {
            "query": keyword,
            "per_page": 30,
            "orientation": "landscape",
            "page": page
        }

        r = requests.get(
            PEXELS_SEARCH_URL,
            headers=headers,
            params=params,
            timeout=20
        )

        r.raise_for_status()

        results = r.json().get("videos", [])
        if not results:
            attempts += 1
            continue

        filtered = [v for v in results if v["duration"] >= min_duration]

        collected.extend(filtered)

        attempts += 1

    if len(collected) < count:
        raise RuntimeError(
            f"Only found {len(collected)} suitable videos after scanning random pages."
        )

    selected = random.sample(collected, count)

    paths = []

    for i, video in enumerate(selected):
        video_files = video["video_files"]
        best_file = max(video_files, key=lambda x: x["width"])
        video_url = best_file["link"]

        path = os.path.join(output_dir, f"vid_{i}.mp4")

        try:
            video_r = requests.get(video_url, timeout=60)
            with open(path, "wb") as f:
                f.write(video_r.content)
            paths.append(path)
        except Exception:
            continue

    if len(paths) < count:
        raise RuntimeError("Some downloads failed")

    return paths



def generate_silent_video(
    audio_path: str,
    image_count: int,
    keyword: str,
    output_path: str,
    video_dir: str = r"materials/videos"
) -> str:

    audio = AudioFileClip(audio_path)
    duration = audio.duration

    per_segment = duration / image_count

    videos = _download_videos(image_count, video_dir, keyword, per_segment)

    clips = []

    for vid in videos:
        clip = VideoFileClip(vid)

        max_start = clip.duration - per_segment
        start = random.uniform(0, max_start)
        end = start + per_segment

        trimmed = clip.subclip(start, end)

        # safer resize
        trimmed = trimmed.resize((1920, 1080))

        clips.append(trimmed)

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


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python video_generator.py audio.wav image_count keyword output.mp4")
        sys.exit(1)

    audio_path = sys.argv[1]
    image_count = int(sys.argv[2])
    keyword = sys.argv[3]
    output_path = sys.argv[4]

    generate_silent_video(audio_path, image_count, keyword, output_path)
