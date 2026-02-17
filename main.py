import os
import re
import time
import sys
import random

from app.utils.text_to_speech import text_to_wav
from app.generators.subtitle_generator import generate_subtitles
from app.utils.audio_mixer import mix_audio
from app.utils.final_compositor import compose_final_video
from app.utils.upload_video import upload_video
from app.utils.clean_up_junk import clear_folder
from app.generators.video_generator_video import generate_silent_video
from app.generators.thumbnail_generator import generate_thumbnail
from app.generators.gpt_text_generator import generate_text
from app.generators.gpt_title_generator import generate_title
from app.generators.gpt_description_generator import generate_description

DOMAINS = [
    "space"
]

def sanitize_filename(name: str) -> str:
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = name.lower()
    name = name.replace(" ", "_")

    return name

def main(duration_seconds: int):
    print("=== PIPELINE START ===")
    pipeline_start = time.time()

    # ---------- 1.1 SCRIPT ----------
    print("[1] Selecting the domain/topic...")
    topic = random.choice(DOMAINS)
    print(f"Chosen domain: {topic}")

    # ---------- 1. TITLE ----------
    print("[1.1] Generating title...")
    title = generate_title(topic)
    print(f"Title: {title}")
    safe_filename = sanitize_filename(title)

    # ---------- 2. SCRIPT ----------
    print("[2] Generating script...")
    script_text = generate_text(title, duration_seconds)

    with open(r"materials/temp/script.txt", "w", encoding="utf-8") as f:
        f.write(script_text)

    print("[2.1] Generating YouTube video description...")
    generated_description = generate_description(title, script_text)

    with open(r"materials/temp/description.txt", "w", encoding="utf-8") as f:
        f.write(generated_description)

    # ---------- 3. TEXT → SPEECH ----------
    print("[3] Generating narration.wav...")
    text_to_wav(script_text, r"materials/temp/narration.wav")

    if not os.path.exists(r"materials/temp/narration.wav"):
        raise RuntimeError("narration.wav was not created")

    # ---------- 4. SUBTITLES ----------
    print("[4] Generating narration.srt...")
    generate_subtitles(
        audio_path=r"materials/temp/narration.wav",
        output_srt=r"materials/temp/narration.srt"
    )

    print("[5] Generating silent video.mp4...")
    generate_silent_video(
        audio_path=r"materials/temp/narration.wav",
        image_count=40,
        keyword=topic,
        output_path=r"materials/temp/out.mp4"
    )

    if not os.path.exists(r"materials/temp/out.mp4"):
        raise RuntimeError("out.mp4 was not created")

    # ---------- 5. AUDIO MIX (VOICE + MUSIC) ----------
    print("[6] Mixing narration + background music...")
    mixed_audio_path = mix_audio(
        narration_wav=r"materials/temp/narration.wav",
        music_dir="materials/music"
    )

    if not os.path.exists(mixed_audio_path):
        raise RuntimeError("mixed_audio.wav was not created")

    # ---------- 6. FINAL COMPOSITION ----------
    print("[7] Compositing final video with subtitles...")
    final_video_path = compose_final_video(
        video_path=r"materials/temp/out.mp4",
        audio_path=mixed_audio_path,
        subtitle_path=r"materials/temp/narration.srt",
        output_path=fr"output/{safe_filename}.mp4"
    )

    # Thumbnail generation

    print("[8] Generating thumbnail...")
    try:
        thumbnail_path = generate_thumbnail(title)
    except Exception as e:
        print("Thumbnail generation failed:", e)
        thumbnail_path = None

    print("[9] Uploading video on YouTube...")
    path_to_video = fr"output/{safe_filename}.mp4"

    upload_video(
        file_path=path_to_video,
        title=title,
        description=generated_description,
        thumbnail_path=str(thumbnail_path)
    )

    print("=== PIPELINE DONE ===")
    print(f"Final result: {final_video_path}\n")

    # print("Cleaning up junk...")
    # to_be_cleaned = ["materials/temp", "materials/videos"]
    # for folder in to_be_cleaned:
    #     clear_folder(folder)
    #     print(f"'{folder}' is cleaned up")
    # print("Clean up is finished.")

    pipeline_end = time.time()
    total_seconds = int(pipeline_end - pipeline_start)

    minutes = total_seconds // 60
    seconds = total_seconds % 60

    print(f"Total pipeline time: {minutes}m {seconds}s")


# ---------- CLI ----------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py duration_seconds")
        sys.exit(1)

    duration = int(sys.argv[1])
    main(duration)


