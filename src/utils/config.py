COLORS: dict[str, str] = {
    "bg": "#0F172A",
    "card": "#1E293B",
    "secondary": "#334155",
    "primary": "#3B82F6",
    "hover": "#2563EB",
    "success": "#22C55E",
    "error": "#EF4444",
    "text": "#F8FAFC",
    "text_secondary": "#94A3B8",
}

PDF_QUALITY_OPTIONS: list[str] = [
    "screen — Máxima compresión",
    "ebook — Buena compresión",
    "printer — Alta calidad",
    "prepress — Óptima impresión",
]

PDF_QUALITY_MAP: dict[str, str] = {
    "screen — Máxima compresión": "screen",
    "ebook — Buena compresión": "ebook",
    "printer — Alta calidad": "printer",
    "prepress — Óptima impresión": "prepress",
}

IMAGE_FORMATS: list[str] = ["JPEG", "PNG", "WEBP"]
IMAGE_EXTENSIONS: tuple[str, ...] = (".jpg", ".jpeg", ".png", ".webp", ".bmp")

APP_TITLE = "File Optimizer"
FONT_FAMILY = "Segoe UI"
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 680
