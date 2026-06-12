from __future__ import annotations

import customtkinter as ctk
from PIL import Image, ImageDraw


def _rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)


def make_pdf_icon(size: int = 52) -> ctk.CTkImage:
    """Document icon with folded corner and text lines."""
    s = size * 2  # draw at 2x then downscale for smooth edges
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    bg   = _rgba("#1D3A6B")
    fg   = _rgba("#60A5FA")
    fold = _rgba("#2A5494")

    m  = s // 10       # margin
    fc = s * 28 // 100  # fold corner size

    # ── Document body ────────────────────────────────────────────────────────
    d.polygon([
        (m,            m),
        (s - m - fc,   m),
        (s - m,        m + fc),
        (s - m,        s - m),
        (m,            s - m),
    ], fill=bg)

    # ── Fold flap ────────────────────────────────────────────────────────────
    d.polygon([
        (s - m - fc, m),
        (s - m,      m + fc),
        (s - m - fc, m + fc),
    ], fill=fold)

    # ── Fold crease ──────────────────────────────────────────────────────────
    w = max(2, s // 32)
    d.line([(s - m - fc, m), (s - m, m + fc)], fill=fg, width=w)

    # ── Text lines ───────────────────────────────────────────────────────────
    lx0 = m + s // 8
    lx1 = s - m - s // 8
    lh  = max(3, s // 24)
    lr  = max(2, s // 32)
    for frac, alpha_val, trim in [
        (0.58, 255, 0),
        (0.70, 190, s // 8),
        (0.80, 130, s // 5),
    ]:
        ly = int(s * frac)
        d.rounded_rectangle(
            [lx0, ly - lh, lx1 - trim, ly + lh],
            radius=lr,
            fill=_rgba("#60A5FA", alpha_val),
        )

    img = img.resize((size, size), Image.LANCZOS)
    return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))


def make_image_icon(size: int = 52) -> ctk.CTkImage:
    """Photo icon: frame with sun and mountain silhouette."""
    s = size * 2
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    bg      = _rgba("#1A3D2E")
    fg      = _rgba("#4ADE80")
    fg_sky  = _rgba("#4ADE80", 70)
    fg_sun  = _rgba("#4ADE80", 160)
    fg_mtn  = _rgba("#4ADE80", 210)

    m = s // 10
    r = s // 8

    # ── Frame background ─────────────────────────────────────────────────────
    d.rounded_rectangle([m, m, s - m, s - m], radius=r, fill=bg)

    # ── Sky tint (top half) ──────────────────────────────────────────────────
    d.rounded_rectangle([m + 3, m + 3, s - m - 3, s // 2 + r],
                        radius=r - 2, fill=fg_sky)

    # ── Sun ──────────────────────────────────────────────────────────────────
    cr = s // 9
    cx, cy = s * 7 // 16, s * 6 // 16
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=fg_sun)

    # ── Mountain silhouette ──────────────────────────────────────────────────
    d.polygon([
        (m + 2,         s - m - 2),
        (s * 5 // 16,   s * 9 // 16),
        (s * 3 // 8,    s * 10 // 16),
        (s * 9 // 16,   s * 7 // 16),
        (s * 11 // 16,  s * 10 // 16),
        (s - m - 2,     s - m - 2),
    ], fill=fg_mtn)

    # ── Border ───────────────────────────────────────────────────────────────
    bw = max(3, s // 22)
    d.rounded_rectangle([m, m, s - m, s - m], radius=r, outline=fg, width=bw)

    img = img.resize((size, size), Image.LANCZOS)
    return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
