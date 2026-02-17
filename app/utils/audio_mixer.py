import os
import random
from moviepy.editor import AudioFileClip, CompositeAudioClip
from moviepy.audio.fx.volumex import volumex
from moviepy.audio.fx.audio_loop import audio_loop

def pick_random_music(music_dir: str) -> str:
    files = [
        f for f in os.listdir(music_dir)
        if f.lower().endswith((".mp3", ".wav", ".aac"))
    ]
    if not files:
        raise RuntimeError("No music files found")
    return os.path.join(music_dir, random.choice(files))


def mix_audio(
    narration_wav: str,
    music_dir: str = "music",
    output_wav: str = r"materials/temp/mixed_audio.wav",
    music_volume: float = 0.04,
    fade_in: float = 2.0,
    fade_out: float = 3.0
) -> str:
    narration = AudioFileClip(narration_wav)
    music = AudioFileClip(pick_random_music(music_dir)).fx(volumex, music_volume)

    if music.duration < narration.duration:
        music = music.fx(audio_loop, duration=narration.duration)
    else:
        music = music.subclip(0, narration.duration)

    music = music.audio_fadein(fade_in).audio_fadeout(fade_out)

    final_audio = CompositeAudioClip([music, narration])
    final_audio.write_audiofile(output_wav, fps=44100)

    # Explicit cleanup (Windows fix)
    final_audio.close()
    music.close()
    narration.close()

    return output_wav


if __name__ == "__main__":
    mix_audio("narration.wav")
    print("mixed_audio.wav created")
