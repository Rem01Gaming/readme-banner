from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from io import BytesIO
from functools import lru_cache

app = Flask(__name__)

@lru_cache(maxsize=64)
def fetch_github_image(github_username):
    github_url = f"https://github.com/{github_username}.png"
    response = requests.get(github_url)
    profile_img = Image.open(BytesIO(response.content)).convert("RGBA")
    return profile_img

def create_image(github_username, message):
    img = Image.new('RGBA', (1235, 586), (0, 0, 0, 0))  # Transparent
    draw = ImageDraw.Draw(img)
    border_radius = 20
    draw.rounded_rectangle([(0, 0), img.size], border_radius, fill=(23, 12, 10, 255))

    profile_img = fetch_github_image(github_username)
    mask = Image.new("L", profile_img.size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0) + profile_img.size, fill=255)
    profile_img = ImageOps.fit(profile_img, mask.size, centering=(0.5, 0.5))
    profile_img.putalpha(mask)
    profile_img = profile_img.resize((110, 110))  # Resize to smaller circle
    img.paste(profile_img, (50, 100), profile_img)

    font_large = ImageFont.truetype("./fonts/ProductSans-Regular.ttf", 60)  # Use a bold, sans-serif font
    font_small = ImageFont.truetype("./fonts/FiraCode-Retina.ttf", 30)        # Smaller font for username

    draw.text((50, 250), message, fill="white", font=font_large)
    draw.text((50, 410), f"→ {github_username}", fill="white", font=font_small)

    output = BytesIO()
    img.save(output, format="WEBP")
    output.seek(0)

    return output

@app.route('/getbanner.webp')
def get_banner():
    github_username = request.args.get('github_usn', 'Rem01Gaming')
    message = request.args.get('msg', 'Welcome to my repository')
    img = create_image(github_username, message)
    return send_file(img, mimetype='image/webp')

#if __name__ == '__main__':
#    app.run()