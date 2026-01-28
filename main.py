import sys
import os

from title_generator import generate_title
from text_generator import generate_text
from text_to_speech import text_to_wav
from subtitle_generator import generate_subtitles
from video_generator import generate_silent_video
from audio_mixer import mix_audio
from final_compositor import compose_final_video
from search_keyword_generator import generate_search_keyword


def main(topic: str, duration_seconds: int):
    print("=== PIPELINE START ===")

    # ---------- 1. TITLE ----------
    print("[1] Generating title...")
    title = generate_title(topic)
    print(f"Title: {title}")

    print("[1.1] Generating search keyword...")
    search_keyword = generate_search_keyword(title)
    print(f"Search keyword: {search_keyword}")

    # ---------- 2. SCRIPT ----------
    print("[2] Generating script...")
    script_text = generate_text(title, duration_seconds)

    with open("script.txt", "w", encoding="utf-8") as f:
        f.write(script_text)

    # ---------- 3. TEXT → SPEECH ----------
    print("[3] Generating narration.wav...")
    text_to_wav(script_text, "narration.wav")

    if not os.path.exists("narration.wav"):
        raise RuntimeError("narration.wav was not created")

    # ---------- 4. SUBTITLES ----------
    print("[4] Generating narration.srt...")
    generate_subtitles(
        audio_path="narration.wav",
        output_srt="narration.srt"
    )

    print("[5] Generating silent video.mp4...")
    generate_silent_video(
        audio_path="narration.wav",
        image_count=20,
        keyword=search_keyword,
        output_path="out.mp4"
    )

    if not os.path.exists("out.mp4"):
        raise RuntimeError("out.mp4 was not created")

    # ---------- 5. AUDIO MIX (VOICE + MUSIC) ----------
    print("[6] Mixing narration + background music...")
    mixed_audio_path = mix_audio(
        narration_wav="narration.wav",
        music_dir="music"
    )

    if not os.path.exists(mixed_audio_path):
        raise RuntimeError("mixed_audio.wav was not created")

    # ---------- 6. FINAL COMPOSITION ----------
    print("[7] Compositing final video with subtitles...")
    final_video_path = compose_final_video(
        video_path="out.mp4",
        audio_path=mixed_audio_path,
        subtitle_path="narration.srt",
        output_path="final_video.mp4"
    )

    print("=== PIPELINE DONE ===")
    print(f"Final result: {final_video_path}")


# ---------- CLI ----------
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py \"topic\" duration_seconds")
        sys.exit(1)

    topic = sys.argv[1]
    duration = int(sys.argv[2])

    main(topic, duration)
