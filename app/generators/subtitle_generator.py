import os
import whisper

def generate_subtitles(
    audio_path: str,
    output_srt: str = r"materials/temp/narration.srt",
    model_size: str = "small"
) -> str:
    if not os.path.exists(audio_path):
        raise FileNotFoundError(audio_path)

    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path, fp16=False)

    def fmt(t):
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = int(t % 60)
        ms = int((t - int(t)) * 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    with open(output_srt, "w", encoding="utf-8") as f:
        for i, seg in enumerate(result["segments"], start=1):
            f.write(f"{i}\n")
            f.write(f"{fmt(seg['start'])} --> {fmt(seg['end'])}\n")
            f.write(f"{seg['text'].strip()}\n\n")

    return output_srt


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python subtitle_generator.py narration.wav")
        exit(1)

    generate_subtitles(sys.argv[1])
    print("Subtitles generated")
