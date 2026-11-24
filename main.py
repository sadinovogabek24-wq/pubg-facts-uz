
import os
import json
import subprocess
from pathlib import Path

from openai import OpenAI
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

def create_script():
    print("PUBG haqida 10 ta ma'lumot tayyorlanmoqda...")

    prompt = """
    PUBG Mobile haqida YouTube uchun qiziqarli video yarat.

    Talablar:
    - Aynan 10 ta qiziqarli ma'lumot.
    - O'zbek tilida yoz.
    - Har bir ma'lumotni batafsil tushuntir.
    - Kirish qismi qiziqarli bo'lsin.
    - Har bir faktni alohida raqamla.
    - Oxirida eng zo'r va hayratlanarli ma'lumot bo'lsin.
    - Video 5-15 daqiqalik bo'lsin.
    - Taxminan 900-1400 ta so'z ishlat.
    - Noto'g'ri ma'lumot to'qib chiqarma.
    - Tomoshabinni oxirigacha ushlab turadigan uslubda yoz.

    Faqat JSON qaytar:
    {"title":"Video nomi","script":"To'liq matn"}
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "Sen professional o'zbek YouTube ssenariy muallifisan."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.8
    )

    result = response.choices[0].message.content
    result = result.replace("```json", "").replace("```", "").strip()

    return json.loads(result)


def create_voice(script):
    print("Ovoz yaratilmoqda...")

    tts = gTTS(
        text=script,
        lang="uz",
        slow=False
    )

    audio_path = OUTPUT / "voice.mp3"
    tts.save(str(audio_path))

    return audio_path


def create_background(title):
    print("Video foni yaratilmoqda...")

    width, height = 1920, 1080

    img = Image.new("RGB", (width, height), (12, 18, 35))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        color = (
            12,
            min(60, 18 + y // 30),
            min(100, 35 + y // 20)
        )
        draw.line((0, y, width, y), fill=color)

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            75
        )
    except OSError:
        font = ImageFont.load_default()

    draw.text(
        (100, 400),
        "PUBG MOBILE",
        font=font,
        fill="white"
    )

    draw.text(
        (100, 520),
        title[:55],
        font=font,
        fill=(255, 190, 40)
    )

    image_path = OUTPUT / "background.png"
    img.save(image_path)

    return image_path


def create_video(audio, background):
    print("Video yig'ilmoqda...")

    video_path = OUTPUT / "pubg_video.mp4"

    command = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", str(background),
        "-i", str(audio),
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-vf", "scale=1920:1080",
        "-r", "30",
        str(video_path)
    ]

    subprocess.run(command, check=True)

    print("Video tayyor:", video_path)


def main():
    print("PUBG FACTS UZ avtomatik video tizimi ishga tushdi!")

    data = create_script()

    title = data["title"]
    script = data["script"]

    print("\nVIDEO NOMI:", title)

    with open(OUTPUT / "script.txt", "w", encoding="utf-8") as f:
        f.write(script)

    audio = create_voice(script)
    background = create_background(title)

    create_video(audio, background)

    with open(OUTPUT / "title.txt", "w", encoding="utf-8") as f:
        f.write(title)

    print("\nBARCHA ISHLAR YAKUNLANDI!")


if __name__ == "__main__":
    main()
