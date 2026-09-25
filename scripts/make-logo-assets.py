#!/usr/bin/env python3
"""Generate site logo assets from the ORIGINAL logo (brief rev 4, 2026-09-25).

Source of record: /Users/brendanhummel/Library/Mobile Documents/com~apple~CloudDocs/
  Hummelllc/HummelLLCLogo.png  (1144x1104 RGBA, white background, founder-final)

Outputs (all derived from the source; no hand-editing):
  assets/logo.png            trimmed full logo (mark + wordmark) — header brand
  assets/favicon-32.png      32x32 H-monogram mark
  assets/favicon-180.png     180x180 H-monogram mark (apple-touch-icon)
  favicon.ico                16/32/48 H-monogram mark, legacy browsers
  assets/og-image.png        1200x630 white canvas with trimmed logo centered

Re-run:  python3 scripts/make-logo-assets.py
"""
import os
from PIL import Image

SRC = "/Users/brendanhummel/Library/Mobile Documents/com~apple~CloudDocs/Hummelllc/HummelLLCLogo.png"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def trim_white(img: Image.Image, tol: int = 245) -> Image.Image:
    """Crop transparent/white margins."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    flat = Image.alpha_composite(bg, img).convert("L")
    bbox = flat.point(lambda p: 255 if p < tol else 0).getbbox()
    if bbox:
        img = img.crop(bbox)
    return img


def split_mark(img: Image.Image) -> Image.Image:
    """Split stacked logo into (H monogram, wordmark); return the monogram."""
    g = img.convert("L")
    w, h = g.size
    # dark-pixel density per row
    dark = g.point(lambda p: 1 if p < 128 else 0)
    rows = [sum(dark.crop((0, y, w, y + 1)).getdata()) for y in range(h)]
    # rows that are (near) empty of dark ink
    threshold = max(2, int(w * 0.02))
    gap_rows = [y for y in range(h) if rows[y] <= threshold]
    # longest central run of gap rows in the middle band (30%..75%)
    lo, hi = int(h * 0.30), int(h * 0.75)
    best_run, best_start, best_end = 0, lo, lo
    cur, cur_start = 0, lo
    for y in range(lo, hi):
        if y in gap_rows and rows[y] <= threshold:
            if cur == 0:
                cur_start = y
            cur += 1
            if cur > best_run:
                best_run, best_start, best_end = cur, cur_start, y + 1
        else:
            cur = 0
    if best_run >= 3:
        split_y = (best_start + best_end) // 2
        return img.crop((0, 0, w, split_y))
    return img  # fallback: no reliable split — use full logo


def square_canvas(img: Image.Image, size: int) -> Image.Image:
    """Fit mark on a white square canvas, small pad."""
    pad = max(2, size // 16)
    inner = size - pad * 2
    im = img.copy()
    im.thumbnail((inner, inner), Image.LANCZOS)
    canvas = Image.new("RGB", (size, size), "white")
    x = (size - im.width) // 2
    y = (size - im.height) // 2
    canvas.paste(im.convert("RGB"), (x, y))
    return canvas


def main() -> None:
    if not os.path.exists(SRC):
        raise SystemExit(f"Logo source not found: {SRC}")
    logo = Image.open(SRC)
    print(f"source: {SRC} ({logo.width}x{logo.height})")

    trimmed = trim_white(logo)
    mark = trim_white(split_mark(trimmed))
    print(f"trimmed logo: {trimmed.size}, mark: {mark.size}")

    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    trimmed.convert("RGB").save(os.path.join(ROOT, "assets", "logo.png"))
    square_canvas(mark, 32).save(os.path.join(ROOT, "assets", "favicon-32.png"))
    square_canvas(mark, 180).save(os.path.join(ROOT, "assets", "favicon-180.png"))
    # multi-size ico (16/32/48) for legacy browsers
    imgs = [square_canvas(mark, 16), square_canvas(mark, 32), square_canvas(mark, 48)]
    imgs[0].save(os.path.join(ROOT, "favicon.ico"), append_images=imgs[1:], format="ICO")

    # OG image: 1200x630 white canvas, trimmed logo centered at ~58% height
    og = Image.new("RGB", (1200, 630), "white")
    logo_h = int(630 * 0.58)
    lm = trimmed.copy()
    lm.thumbnail((int(logo_h * trimmed.width / trimmed.height), logo_h), Image.LANCZOS)
    og.paste(lm.convert("RGB"), ((1200 - lm.width) // 2, (630 - lm.height) // 2))
    og.save(os.path.join(ROOT, "assets", "og-image.png"))

    for p in ("assets/logo.png", "assets/favicon-32.png", "assets/favicon-180.png",
              "favicon.ico", "assets/og-image.png"):
        full = os.path.join(ROOT, p)
        out = Image.open(full)
        print(f"wrote {p}  ({out.width}x{out.height})")


if __name__ == "__main__":
    main()