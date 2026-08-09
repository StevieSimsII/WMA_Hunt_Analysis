#!/usr/bin/env python3
"""Render the 2026-27 recommended application slate as a shareable PNG list."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "decision_2026_27.json"
OUT_PATHS = [
    ROOT / "assets" / "exports" / "2026-27-application-slate.png",
    Path("/opt/cursor/artifacts") / "2026-27-application-slate.png",
]


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def load_fonts():
    serif = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
    serif_reg = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"
    sans = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
    sans_med = "/usr/share/fonts/truetype/noto/NotoSans-Medium.ttf"
    sans_bold = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
    # Fallbacks if Medium/Bold missing
    for candidate, fallback in [
        (sans_med, sans),
        (sans_bold, sans),
        (serif, serif_reg),
    ]:
        if not Path(candidate).exists():
            if candidate == sans_med:
                sans_med = fallback
            elif candidate == sans_bold:
                sans_bold = fallback
            elif candidate == serif:
                serif = fallback
    return {
        "title": font(serif, 54),
        "subtitle": font(sans, 22),
        "rank": font(serif, 36),
        "hunt": font(sans_bold if Path(sans_bold).exists() else sans, 28),
        "meta": font(sans, 20),
        "label": font(sans_med if Path(sans_med).exists() else sans, 16),
        "footer": font(sans, 16),
    }


def category_short(cat: str) -> str:
    return {
        "primitive_weapon": "Primitive Weapon",
        "archery": "Archery",
        "gun": "Gun",
        "group": "Group",
        "youth": "Youth",
        "senior": "Senior",
        "refuge": "Refuge",
        "waterfowl": "Waterfowl",
    }.get(cat, cat.replace("_", " ").title())


def draw_vertical_gradient(img: Image.Image, top, bottom):
    w, h = img.size
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        for x in range(w):
            px[x, y] = (r, g, b, 255)


def add_soft_vignette(img: Image.Image):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    w, h = img.size
    d.ellipse((-w * 0.2, -h * 0.15, w * 1.2, h * 1.15), fill=(8, 18, 12, 55))
    blur = overlay.filter(ImageFilter.GaussianBlur(80))
    return Image.alpha_composite(img, blur)


def main():
    data = json.loads(DECISION.read_text())
    hunts = data["strategy"]
    fonts = load_fonts()

    width = 1200
    row_h = 118
    top_pad = 170
    bottom_pad = 90
    height = top_pad + len(hunts) * row_h + bottom_pad

    img = Image.new("RGBA", (width, height), (16, 36, 28, 255))
    draw_vertical_gradient(img, (18, 42, 32), (10, 22, 18))
    img = add_soft_vignette(img)
    draw = ImageDraw.Draw(img)

    # Atmosphere: soft amber wash near top
    wash = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wash)
    wd.ellipse((width * 0.15, -80, width * 0.85, 180), fill=(196, 146, 72, 35))
    img = Image.alpha_composite(img, wash.filter(ImageFilter.GaussianBlur(40)))
    draw = ImageDraw.Draw(img)

    # Header
    brand = data.get("brand") or "Delta Draw Hunts"
    season = data.get("season") or "2026-27"
    draw.text((64, 42), brand.upper(), font=fonts["label"], fill=(214, 176, 104, 255))
    draw.text((64, 68), "Hunts We Put In For", font=fonts["title"], fill=(244, 238, 220, 255))
    draw.text(
        (64, 132),
        f"{season} Mississippi WMA deer draw · 5 ranked choices",
        font=fonts["subtitle"],
        fill=(176, 190, 170, 255),
    )

    # Accent rule
    draw.line((64, 168, width - 64, 168), fill=(196, 146, 72, 160), width=2)

    left = 64
    right = width - 64

    for i, h in enumerate(hunts):
        y = top_pad + i * row_h
        # Row background strip
        band = Image.new("RGBA", (width, row_h - 12), (0, 0, 0, 0))
        bd = ImageDraw.Draw(band)
        bd.rounded_rectangle(
            (left - 8, 4, right + 8, row_h - 20),
            radius=18,
            fill=(255, 255, 255, 14 if i % 2 == 0 else 8),
        )
        img.paste(band, (0, y), band)
        draw = ImageDraw.Draw(img)

        rank = f"{i + 1}"
        draw.text((left + 8, y + 28), rank, font=fonts["rank"], fill=(196, 146, 72, 255))

        name = h["hunt_name"]
        draw.text((left + 70, y + 18), name, font=fonts["hunt"], fill=(245, 241, 228, 255))

        meta_left = (
            f"{h['date_label']}  ·  {category_short(h['category'])}  ·  "
            f"{h['permits_available']} permits"
        )
        draw.text((left + 70, y + 56), meta_left, font=fonts["meta"], fill=(168, 186, 164, 255))

        meta_right = (
            f"{h['rut_label']}  ·  {h['competition_label']} competition  ·  "
            f"{h['miles_drive']:.0f} mi"
        )
        draw.text((left + 70, y + 82), meta_right, font=fonts["label"], fill=(140, 158, 138, 255))

        score = f"{h['decision_score']:.2f}"
        sw = draw.textlength(score, font=fonts["rank"])
        draw.text((right - sw, y + 28), score, font=fonts["rank"], fill=(214, 176, 104, 255))
        label = "SCORE"
        lw = draw.textlength(label, font=fonts["label"])
        draw.text((right - lw, y + 70), label, font=fonts["label"], fill=(140, 158, 138, 255))

    # Footer
    window = data.get("application_window") or {}
    footer = (
        f"Application window {window.get('opens', '2026-07-15')} – "
        f"{window.get('closes', '2026-08-15')}  ·  From recommended cabin-focused slate"
    )
    draw.text((64, height - 48), footer, font=fonts["footer"], fill=(120, 138, 118, 255))

    rgb = img.convert("RGB")
    for path in OUT_PATHS:
        path.parent.mkdir(parents=True, exist_ok=True)
        rgb.save(path, "PNG", optimize=True)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
