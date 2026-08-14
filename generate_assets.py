"""Generate favicon.png and og-image.png for mohdarif.com matching the site theme."""
from PIL import Image, ImageDraw, ImageFont

# ---- palette (matches index.html CSS variables) ----
BG_TOP = (7, 16, 29)      # #07101d
BG_MID = (10, 21, 39)     # #0a1527
BG_BOT = (8, 17, 31)      # #08111f
TEXT = (237, 243, 255)    # #edf3ff
MUTED = (169, 186, 217)   # #a9bad9
PRIMARY = (98, 208, 255)  # #62d0ff
PRIMARY2 = (156, 123, 255)# #9c7bff


def load_font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def vgradient(w, h, c1, c2, c3):
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        if t < 0.46:
            tt = t / 0.46
            a, b = c1, c2
        else:
            tt = (t - 0.46) / 0.54
            a, b = c2, c3
        r = int(a[0] + (b[0] - a[0]) * tt)
        g = int(a[1] + (b[1] - a[1]) * tt)
        bl = int(a[2] + (b[2] - a[2]) * tt)
        for x in range(w):
            px[x, y] = (r, g, bl)
    return img


def radial_glow(base, cx, cy, radius, color, max_alpha):
    """Soft additive radial glow."""
    w, h = base.size
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    gp = glow.load()
    for y in range(max(0, cy - radius), min(h, cy + radius)):
        for x in range(max(0, cx - radius), min(w, cx + radius)):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if d < radius:
                a = (1 - d / radius) ** 2 * max_alpha
                gp[x, y] = (int(color[0] * a), int(color[1] * a), int(color[2] * a))
    # additive blend
    bp = base.load()
    for y in range(h):
        for x in range(w):
            br, bg_, bb = bp[x, y]
            gr, gg, gb = gp[x, y]
            bp[x, y] = (min(255, br + gr), min(255, bg_ + gg), min(255, bb + gb))
    return base


# ============ OG IMAGE 1200x630 ============
W, H = 1200, 630
og = vgradient(W, H, BG_TOP, BG_MID, BG_BOT)
og = radial_glow(og, 180, 120, 480, PRIMARY, 0.16)
og = radial_glow(og, 1050, 60, 460, PRIMARY2, 0.14)
d = ImageDraw.Draw(og)

# thin top accent line
d.rectangle([0, 0, W, 5], fill=PRIMARY)

# eyebrow
eb = load_font(28, bold=True)
d.text((80, 120), "SECURITY RESEARCHER  •  DEFCON & BLACK HAT SPEAKER", font=eb, fill=PRIMARY)

# name
name = load_font(104, bold=True)
d.text((78, 168), "Mohammad Arif", font=name, fill=TEXT)

# title
title = load_font(46, bold=True)
d.text((80, 300), "Product Security Engineer", font=title, fill=TEXT)
d.text((80, 360), "AI/ML Security  •  AppSec  •  Cloud  •  DevSecOps", font=load_font(38), fill=MUTED)

# credential pills
pill_font = load_font(28, bold=True)
pills = ["5+ yrs", "50+ repos secured", "100+ engineers trained", "Hall of Fame"]
x = 80
y = 470
for p in pills:
    bbox = d.textbbox((0, 0), p, font=pill_font)
    tw = bbox[2] - bbox[0]
    pad = 26
    d.rounded_rectangle([x, y, x + tw + pad * 2, y + 56], radius=28,
                        outline=(255, 255, 255), width=1, fill=(255, 255, 255))
    # translucent look: redraw fill darker
    d.rounded_rectangle([x, y, x + tw + pad * 2, y + 56], radius=28,
                        fill=(20, 32, 52))
    d.text((x + pad, y + 12), p, font=pill_font, fill=MUTED)
    x += tw + pad * 2 + 16

# domain bottom-right
dom = load_font(30, bold=True)
bbox = d.textbbox((0, 0), "mohdarif.com", font=dom)
d.text((W - 80 - (bbox[2] - bbox[0]), 560), "mohdarif.com", font=dom, fill=PRIMARY)

og.save("og-image.png", optimize=True)
print("wrote og-image.png", og.size)


# ============ FAVICON 512x512 ============
S = 512
fav = Image.new("RGBA", (S, S), (0, 0, 0, 0))
fd = ImageDraw.Draw(fav)
# rounded square bg
fd.rounded_rectangle([8, 8, S - 8, S - 8], radius=110, fill=BG_MID)
# subtle inner border
fd.rounded_rectangle([8, 8, S - 8, S - 8], radius=110, outline=(98, 208, 255, 90), width=6)
# "0x" monogram (nods to Zero0x00) in primary
mono = load_font(280, bold=True)
text = "0x"
bbox = fd.textbbox((0, 0), text, font=mono)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
fd.text(((S - tw) / 2 - bbox[0], (S - th) / 2 - bbox[1] - 10), text, font=mono, fill=PRIMARY)
fav.save("favicon.png", optimize=True)
# small 32x32 ico-style png
fav.resize((32, 32), Image.LANCZOS).save("favicon-32.png", optimize=True)
print("wrote favicon.png + favicon-32.png")
