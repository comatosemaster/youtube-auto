import sys
import asyncio
import edge_tts
import os

VOICE = "en-US-GuyNeural"  # natural, neutral

def read_text_file(path: str) -> str:
    with open(path, "rb") as f:
        raw = f.read()

    # Detect UTF-16 (PowerShell redirection)
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16").strip()

    return raw.decode("utf-8", errors="ignore").strip()

async def _text_to_wav_async(text: str, output_path: str):
    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE,
        rate="+0%",
        volume="+0%"
    )
    await communicate.save(output_path)

def text_to_wav(text: str, output_path: str):
    asyncio.run(_text_to_wav_async(text, output_path))


# ---------------- CLI ----------------

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python text_to_speech.py input.txt output.wav")
        sys.exit(1)

    input_file = sys.argv[1]
    output_wav = sys.argv[2]

    if not os.path.exists(input_file):
        print("Input text file not found")
        sys.exit(1)

    text = read_text_file(input_file)
    text_to_wav(text, output_wav)

    print(f"WAV saved to {output_wav}")
