import sys
import os
import pysrt
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeAudioClip,
    TextClip,
    CompositeVideoClip
)

SUBTITLE_STYLE = {
    "font": "Arial",
    "fontsize": 42,
    "color": "white",
    "stroke_color": "#FFD400",
    "stroke_width": 2,
    "method": "caption",
    "size": (1600, None)
}

def load_and_style_subtitles(srt_path, video_width, video_height):
    subs = pysrt.open(srt_path)
    subtitle_clips = []

    for sub in subs:
        start = sub.start.ordinal / 1000
        end = sub.end.ordinal / 1000
        duration = end - start

        txt = TextClip(
            sub.text,
            **SUBTITLE_STYLE,
            bg_color="rgba(0,0,0,0.7)"
        ).set_duration(duration)

        txt = txt.set_position(("center", video_height - 160)).set_start(start)
        subtitle_clips.append(txt)

    return subtitle_clips

def main():
    if len(sys.argv) < 6:
        print("Usage: python voice_plus_video.py silent_video.mp4 narration.wav subtitles.srt music.mp3 final_video.mp4")
        sys.exit(1)

    silent_video, narration_wav, srt_file, music_file, output = sys.argv[1:]

    video = VideoFileClip(silent_video)
    narration = AudioFileClip(narration_wav)
    music = AudioFileClip(music_file)

    # Duration enforcement
    narration_duration = narration.duration
    video = video.set_duration(narration_duration)

    # Music handling
    music = music.volumex(0.04)
    music = music.audio_fadein(2).audio_fadeout(3)

    if music.duration < narration_duration:
        music = music.loop(duration=narration_duration)
    else:
        music = music.subclip(0, narration_duration)

    final_audio = CompositeAudioClip([music, narration])

    # Subtitles
    subtitle_clips = load_and_style_subtitles(
        srt_file, video.w, video.h
    )

    final_video = CompositeVideoClip(
        [video] + subtitle_clips
    ).set_audio(final_audio)

    final_video.write_videofile(
        output,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

if __name__ == "__main__":
    main()
