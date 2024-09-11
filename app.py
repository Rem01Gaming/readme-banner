from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from io import BytesIO
from functools import lru_cache

app = Flask(__name__)

@lru_cache(maxsize=1)
def create_cached_background():
    img = Image.new('RGBA', (1235, 586), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    border_radius = 20
    draw.rounded_rectangle([(0, 0), img.size], border_radius, fill=(23, 12, 10, 255))
    return img

@lru_cache(maxsize=64)
def fetch_github_image(github_username):
    github_url = f"https://github.com/{github_username}.png"
    try:
        response = requests.get(github_url, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching GitHub image for {github_username}: {e}")
        placeholder_img = Image.new('RGBA', (110, 110), (100, 100, 100, 255))
        draw = ImageDraw.Draw(placeholder_img)
        draw.text((10, 40), "N/A", fill="white")
        return placeholder_img
    
    profile_img = Image.open(BytesIO(response.content)).convert("RGBA")
    return profile_img

def create_image(github_username, message):
    img = create_cached_background().copy()
    draw = ImageDraw.Draw(img)

    profile_img = fetch_github_image(github_username)
    mask = Image.new("L", profile_img.size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0) + profile_img.size, fill=255)
    profile_img = ImageOps.fit(profile_img, mask.size, centering=(0.5, 0.5))
    profile_img.putalpha(mask)
    profile_img = profile_img.resize((110, 110))
    img.paste(profile_img, (50, 100), profile_img)

    try:
        font_large = ImageFont.truetype("./fonts/ProductSans-Regular.ttf", 60)
    except IOError:
        font_large = ImageFont.load_default()

    try:
        font_small = ImageFont.truetype("./fonts/FiraCode-Retina.ttf", 30)
    except IOError:
        font_small = ImageFont.load_default()  

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

# Uncomment if you wanted to run this with flask directly (DON'T DO THIS IN PROD!)
# if __name__ == '__main__':
#     app.run()
