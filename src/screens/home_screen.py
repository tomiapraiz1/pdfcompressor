from __future__ import annotations

import customtkinter as ctk

from ..utils.config import COLORS, FONT_FAMILY
from ..utils.icons import make_image_icon, make_pdf_icon

# Accent colors per tool (border on hover)
_CARD_ACCENTS = {
    "pdf":   {"border": "#3B82F6"},
    "image": {"border": "#22C55E"},
}


class _ToolCard(ctk.CTkFrame):
    """Clickable tool card with Pillow-rendered icon."""

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        icon_image: ctk.CTkImage,
        title: str,
        description: str,
        badge: str,
        accent_key: str,
        on_click,
        **kwargs,
    ) -> None:
        accent = _CARD_ACCENTS[accent_key]
        super().__init__(
            parent,
            fg_color=COLORS["card"],
            corner_radius=22,
            border_width=1,
            border_color=COLORS["secondary"],
            cursor="hand2",
            **kwargs,
        )
        self._on_click = on_click
        self._normal_bg = COLORS["card"]
        self._hover_bg = "#253347"
        self._normal_border = COLORS["secondary"]
        self._hover_border = accent["border"]

        # ── Icon (CTkImage — always centered, no glyph-width issues) ─────────
        ctk.CTkLabel(
            self,
            image=icon_image,
            text="",
            fg_color="transparent",
            anchor="center",
        ).pack(fill="x", pady=(30, 0))

        # ── Title ────────────────────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
            text_color=COLORS["text"],
            fg_color="transparent",
        ).pack(pady=(14, 0))

        # ── Description ──────────────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text=description,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLORS["text_secondary"],
            fg_color="transparent",
            wraplength=210,
            justify="center",
        ).pack(pady=(6, 16))

        # ── Divider ──────────────────────────────────────────────────────────
        ctk.CTkFrame(
            self,
            height=1,
            fg_color=COLORS["secondary"],
        ).pack(fill="x", padx=20)

        # ── Badge (formats / stat) ───────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text=badge,
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=accent["border"],
            fg_color="transparent",
        ).pack(pady=(12, 20))

        # ── "Open" arrow ─────────────────────────────────────────────────────
        self._arrow = ctk.CTkLabel(
            self,
            text="→",
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            text_color=accent["border"],
            fg_color="transparent",
        )
        self._arrow.pack(pady=(0, 18))

        self._bind_recursive(self)

    def _bind_recursive(self, widget) -> None:
        widget.bind("<Enter>", self._on_enter, add="+")
        widget.bind("<Leave>", self._on_leave, add="+")
        widget.bind("<Button-1>", lambda _e: self._on_click(), add="+")
        for child in widget.winfo_children():
            self._bind_recursive(child)

    def _on_enter(self, _event) -> None:
        self.configure(fg_color=self._hover_bg, border_color=self._hover_border)

    def _on_leave(self, _event) -> None:
        self.configure(fg_color=self._normal_bg, border_color=self._normal_border)


class HomeScreen(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkBaseClass, controller) -> None:
        super().__init__(parent, fg_color=COLORS["bg"])
        self._controller = controller
        self._build()

    def _build(self) -> None:
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True)
        outer.rowconfigure(0, weight=1)
        outer.rowconfigure(1, weight=0)
        outer.rowconfigure(2, weight=1)
        outer.columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(outer, fg_color="transparent")
        inner.grid(row=1, column=0)

        # ── Logo / badge ─────────────────────────────────────────────────────
        badge = ctk.CTkFrame(
            inner,
            fg_color="#1e3a5f",
            corner_radius=20,
        )
        badge.pack(pady=(0, 20))
        ctk.CTkLabel(
            badge,
            text="⚡  File Optimizer",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color="#60A5FA",
            fg_color="transparent",
        ).pack(padx=18, pady=6)

        # ── Headline ─────────────────────────────────────────────────────────
        ctk.CTkLabel(
            inner,
            text="Optimiza tus archivos,\nsin complicaciones",
            font=ctk.CTkFont(family=FONT_FAMILY, size=34, weight="bold"),
            text_color=COLORS["text"],
            justify="center",
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            inner,
            text="Elige una herramienta para comenzar",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14),
            text_color=COLORS["text_secondary"],
        ).pack(pady=(0, 40))

        # ── Cards ────────────────────────────────────────────────────────────
        cards_row = ctk.CTkFrame(inner, fg_color="transparent")
        cards_row.pack()

        _ToolCard(
            cards_row,
            icon_image=make_pdf_icon(52),
            title="PDF Compressor",
            description="Reduce el tamaño de tus PDFs\nconservando la calidad",
            badge="Screen · Ebook · Printer · Prepress",
            accent_key="pdf",
            on_click=self._controller.show_pdf_screen,
            width=265,
        ).pack(side="left", padx=16)

        _ToolCard(
            cards_row,
            icon_image=make_image_icon(52),
            title="Image Compressor",
            description="Comprime imágenes en lote\nJPG, PNG y WEBP",
            badge="JPEG · PNG · WEBP",
            accent_key="image",
            on_click=self._controller.show_image_screen,
            width=265,
        ).pack(side="left", padx=16)

        # ── Footer tagline ────────────────────────────────────────────────────
        ctk.CTkLabel(
            inner,
            text="100% local · sin conexión a internet · sin límite de archivos",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=COLORS["secondary"],
        ).pack(pady=(32, 0))
