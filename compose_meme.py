#!/usr/bin/env python3
"""Composite the GTA 6 meme: Vice City scene + real make.fun ghost + huge captions."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from collections import deque

ENTRY = "/home/hatch/workspace/makefun/gta6-meme-x-entry"
SCENE = ENTRY + "/media-generation-scene-0-f0e29fec-da8a-4c61-8e32-97cb960b4891.png"
MARK = ENTRY + "/mark-1024.png"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SIZE = 1024

# --- 1. Extract the ghost from the mark -------------------------------------
mark = Image.open(MARK).convert("RGBA")
arr = np.array(mark).astype(np.int16)
h, w, _ = arr.shape
r, g, b, a = arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3]

# Magenta disc/coin-fill: red high, green low, blue mid, red clearly above green.
magenta = (r > 110) & (g < 110) & (b > 50) & (b < 220) & ((r - g) > 70)
# Transparent or near-black pixels (outside the disc + the outer black ring).
dark_or_transparent = (a < 10) | ((r < 70) & (g < 70) & (b < 70))

# Flood-fill the border-connected dark/transparent region (outer ring).
remove = magenta.copy()
seen = np.zeros((h, w), dtype=bool)
q = deque()
for x in range(w):
    q.append((0, x)); q.append((h - 1, x))
for y in range(h):
    q.append((y, 0)); q.append((y, w - 1))
while q:
    y, x = q.popleft()
    if seen[y, x] or not dark_or_transparent[y, x]:
        continue
    seen[y, x] = True
    remove[y, x] = True
    if y > 0: q.append((y - 1, x))
    if y < h - 1: q.append((y + 1, x))
    if x > 0: q.append((y, x - 1))
    if x < w - 1: q.append((y, x + 1))

ghost_arr = np.array(mark).copy()
ghost_arr[remove] = (0, 0, 0, 0)
ghost = Image.fromarray(ghost_arr, "RGBA")
bbox = ghost.getbbox()
ghost = ghost.crop(bbox)
print("ghost crop bbox:", bbox, "size:", ghost.size)

# --- 2. Scene ----------------------------------------------------------------
scene = Image.open(SCENE).convert("RGB").resize((SIZE, SIZE), Image.LANCZOS)
canvas = scene.convert("RGBA")

# --- 3. Paste the ghost into the sky, upper right, tilted --------------------
GW = 340
ghost_r = ghost.resize((GW, int(ghost.height * GW / ghost.width)), Image.LANCZOS)
ghost_r = ghost_r.rotate(-8, resample=Image.BICUBIC, expand=True)

# Soft shadow to seat it in the scene.
shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
sh = Image.new("RGBA", ghost_r.size, (0, 0, 0, 0))
alpha = ghost_r.split()[3].point(lambda v: int(v * 0.45))
sh.putalpha(alpha)
gx, gy = 620, 150  # upper-right sky
shadow.paste(sh, (gx + 14, gy + 18), sh)
shadow = shadow.filter(ImageFilter.GaussianBlur(10))
canvas.alpha_composite(shadow)
canvas.alpha_composite(ghost_r, (gx, gy))

# --- 4. Captions --------------------------------------------------------------
draw = ImageDraw.Draw(canvas)

def fit_font(text, max_w, start=110):
    size = start
    while size > 20:
        f = ImageFont.truetype(FONT_PATH, size)
        if draw.textlength(text, font=f) <= max_w:
            return f, size
        size -= 2
    return ImageFont.truetype(FONT_PATH, 20), 20

def caption_block(lines, y_top, max_w=980):
    """Draw centred lines with a semi-transparent dark band behind them."""
    fonts = []
    heights = []
    for line in lines:
        f, s = fit_font(line, max_w)
        fonts.append(f)
        heights.append(f.getbbox(line)[3] - f.getbbox(line)[1])
    total_h = sum(heights) + 10 * (len(lines) - 1)
    band = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    bd.rectangle([0, y_top - 14, SIZE, y_top + total_h + 14], fill=(0, 0, 0, 110))
    canvas.alpha_composite(band)
    d = ImageDraw.Draw(canvas)
    y = y_top
    for line, f in zip(lines, fonts):
        tw = d.textlength(line, font=f)
        sw = max(3, f.size // 14)
        d.text(((SIZE - tw) / 2, y), line, font=f, fill=(255, 255, 255, 255),
               stroke_width=sw, stroke_fill=(0, 0, 0, 255))
        y += f.getbbox(line)[3] - f.getbbox(line)[1] + 10
    return y

caption_block(["WAITED 13 YEARS FOR GTA 6"], 28)
caption_block(["MY AI AGENT GOT PAID", "ON MAKE.FUN"], 800)

out = canvas.convert("RGB")
out.save(ENTRY + "/meme.png", "PNG")
out.resize((480, 480), Image.LANCZOS).save("/tmp/meme-480.png", "PNG")
print("saved meme.png", out.size)
