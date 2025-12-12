from PIL import Image, ImageDraw

# constants
px_per_in = 50
square_in = 80
size = square_in * px_per_in
img = Image.new("RGB", (size, size), "lightgray")
draw = ImageDraw.Draw(img)

# circle diameters
d_mid = 24 * px_per_in
d_large = 60 * px_per_in

cx, cy = size // 2, size // 2

# draw circles
for d in [d_large, d_mid]:
    r = d // 2
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline="black", width=25)

# load logo
logo = Image.open("robonation logo-black-icon_cropped.png").convert("RGBA")
max_logo = 12 * px_per_in
logo_ratio = min(max_logo / logo.width, max_logo / logo.height)
logo_resized = logo.resize(
    (int(logo.width * logo_ratio), int(logo.height * logo_ratio))
)
# paste centered
lx = cx - logo_resized.width // 2
ly = cy - logo_resized.height // 2
img.paste(logo_resized, (lx, ly), logo_resized)

# save
out_path = "helipad_big_logo.png"
img.save(out_path)
