import os
import subprocess

FFMPEG = "ffmpeg"  # relies on ffmpeg in PATH (works on your machine)


def create_styled_ass(srt_path: str, ass_path: str):
    import pysubs2

    subs = pysubs2.load(srt_path)

    # FULL MANUAL ASS STYLE (this is the key)
    subs.styles["Default"] = pysubs2.SSAStyle()
    style = subs.styles["Default"]

    style.fontname = "Arial"
    style.fontsize = 20

    # ASS COLORS ARE BGR + ALPHA (00 = opaque)
    style.primarycolor = pysubs2.Color(255, 255, 255)   # white text
    style.outlinecolor = pysubs2.Color(0, 0, 0)     # ORANGE-YELLOW BORDER (BGR!)
    style.backcolor = pysubs2.Color(255, 85, 0)             # BLACK BOX

    style.primaryalpha = 0x00    # opaque text
    style.outlinealpha = 0x00    # opaque border
    style.backalpha = 0x00       # opaque box (IMPORTANT)

    style.borderstyle = 3        # BOXED subtitles
    style.outline = 3            # border thickness
    style.shadow = 0

    style.alignment = 2          # bottom-center (ASS spec)
    style.marginv = 40

    subs.save(ass_path)


    subs.styles["Default"] = style
    subs.save(ass_path)


def compose_final_video(
    video_path: str,
    audio_path: str,
    subtitle_path: str,
    output_path: str
) -> str:

    for p in (video_path, audio_path, subtitle_path):
        if not os.path.exists(p):
            raise FileNotFoundError(p)

    ass_path = r"materials/temp/styled_subtitles.ass"

    print("[final] Creating styled ASS subtitles...")
    create_styled_ass(subtitle_path, ass_path)

    print("[final] Burning subtitles + mixing audio...")
    cmd = [
        FFMPEG,
        "-y",
        "-i", video_path,
        "-i", audio_path,
        "-vf", f"subtitles={ass_path}",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]

    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

    if not os.path.exists(output_path):
        raise RuntimeError("Final video not created")

    return output_path


# ---------- CLI ----------
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 5:
        print(
            "Usage: python final_compositor.py "
            "video.mp4 mixed_audio.wav narration.srt final_video.mp4"
        )
        sys.exit(1)

    compose_final_video(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        sys.argv[4]
    )

    print("Final video created")
