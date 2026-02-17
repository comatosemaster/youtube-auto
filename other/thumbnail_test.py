from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

# Adjust this if needed
FONT_PATH = "Montserrat Extra Bold.otf"

# Make sure folder exists
os.makedirs("materials/thumbnails", exist_ok=True)

# Create black 1280x720 image
img = Image.new("RGB", (1280, 720), (0, 0, 0))

draw = ImageDraw.Draw(img)
font = ImageFont.truetype(FONT_PATH, 130)

hook_text = "THIS CHANGES EVERYTHING"

wrapped = textwrap.fill(hook_text, width=14)
lines = wrapped.split("\n")

x = 90
y = 220
spacing = 25

yellow = (255, 230, 0)
white = (255, 255, 255)

for i, line in enumerate(lines):
    color = yellow if i % 2 == 0 else white

    draw.text(
        (x, y),
        line,
        font=font,
        fill=color,
        stroke_width=8,
        stroke_fill=(0, 0, 0)
    )

    bbox = font.getbbox(line)
    height = bbox[3] - bbox[1]
    y += height + spacing

output_path = "materials/thumbnails/test_output.png"
img.save(output_path)

print("Saved to:", os.path.abspath(output_path))
