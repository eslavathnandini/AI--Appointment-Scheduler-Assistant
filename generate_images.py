from PIL import Image, ImageDraw, ImageFont
import os

output_dir = "sample_images"
os.makedirs(output_dir, exist_ok=True)

def create_text_image(text, filename, font_size=40):
    width, height = 600, 200
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    draw.text((50, 80), text, fill='black', font=font)
    img.save(f"{output_dir}/{filename}")
    print(f"Created: {output_dir}/{filename}")

# Generate sample images with appointment notes
samples = [
    ("Book dentist nxt Friday @ 3pm", "appointment_1.png"),
    ("Schedule doctor appointment tomorrow 10am", "appointment_2.png"),
    ("dentist - next Monday 2:30pm", "appointment_3.png"),
    ("book cardiologist on 15th Dec at 11am", "appointment_4.png"),
    ("Dr appointment this Friday evening", "appointment_5.png"),
]

for text, filename in samples:
    create_text_image(text, filename)

print(f"\nAll sample images created in: {output_dir}/")
print("Use these images to test the /api/v1/extract/image endpoint!")