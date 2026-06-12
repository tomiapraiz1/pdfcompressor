from __future__ import annotations

import customtkinter as ctk

from ..utils.config import COLORS, FONT_FAMILY


class _ToolCard(ctk.CTkFrame):
    """A clickable card with hover color animation."""

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        icon: str,
        title: str,
        description: str,
        on_click,
        **kwargs,
    ) -> None:
        super().__init__(
            parent,
            fg_color=COLORS["card"],
            corner_radius=20,
            cursor="hand2",
            **kwargs,
        )
        self._on_click = on_click
        self._normal = COLORS["card"]
        self._hovered = COLORS["secondary"]

        ctk.CTkLabel(
            self,
            text=icon,
            font=ctk.CTkFont(family=FONT_FAMILY, size=44),
            fg_color="transparent",
            text_color=COLORS["text"],
        ).pack(pady=(32, 6))

        ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(family=FONT_FAMILY, size=17, weight="bold"),
            text_color=COLORS["text"],
            fg_color="transparent",
        ).pack()

        ctk.CTkLabel(
            self,
            text=description,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLORS["text_secondary"],
            fg_color="transparent",
            wraplength=220,
        ).pack(pady=(6, 32))

        self._bind_recursive(self)

    def _bind_recursive(self, widget) -> None:
        widget.bind("<Enter>", self._on_enter, add="+")
        widget.bind("<Leave>", self._on_leave, add="+")
        widget.bind("<Button-1>", lambda _e: self._on_click(), add="+")
        for child in widget.winfo_children():
            self._bind_recursive(child)

    def _on_enter(self, _event) -> None:
        self.configure(fg_color=self._hovered)

    def _on_leave(self, _event) -> None:
        self.configure(fg_color=self._normal)


class HomeScreen(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkBaseClass, controller) -> None:
        super().__init__(parent, fg_color=COLORS["bg"])
        self._controller = controller
        self._build()

    def _build(self) -> None:
        # Vertically center content using a transparent outer grid
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True)
        outer.rowconfigure(0, weight=1)
        outer.rowconfigure(1, weight=0)
        outer.rowconfigure(2, weight=1)
        outer.columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(outer, fg_color="transparent")
        inner.grid(row=1, column=0)

        # ── Header ──────────────────────────────────────────────────────────
        ctk.CTkLabel(
            inner,
            text="File Optimizer",
            font=ctk.CTkFont(family=FONT_FAMILY, size=32, weight="bold"),
            text_color=COLORS["text"],
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            inner,
            text="Elige una herramienta para comenzar",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14),
            text_color=COLORS["text_secondary"],
        ).pack(pady=(0, 44))

        # ── Cards ────────────────────────────────────────────────────────────
        cards_row = ctk.CTkFrame(inner, fg_color="transparent")
        cards_row.pack()

        _ToolCard(
            cards_row,
            icon="📄",
            title="PDF Compressor",
            description="Reduce el tamaño de tus PDFs conservando la calidad",
            on_click=self._controller.show_pdf_screen,
            width=270,
            height=220,
        ).pack(side="left", padx=14)

        _ToolCard(
            cards_row,
            icon="🖼️",
            title="Image Compressor",
            description="Comprime imágenes JPG, PNG y WEBP en lote",
            on_click=self._controller.show_image_screen,
            width=270,
            height=220,
        ).pack(side="left", padx=14)
