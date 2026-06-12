from __future__ import annotations

import os
from tkinter import filedialog

import customtkinter as ctk
from tkinterdnd2 import DND_FILES

from ..compressors.image_compressor import ImageCompressorThread
from ..utils.config import COLORS, FONT_FAMILY, IMAGE_EXTENSIONS, IMAGE_FORMATS


class ImageScreen(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkBaseClass, controller) -> None:
        super().__init__(parent, fg_color=COLORS["bg"])
        self._controller = controller
        self._files: list[str] = []
        self.output_folder: str | None = None
        self._compressor: ImageCompressorThread | None = None
        self._build()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _font(self, size: int, weight: str = "normal") -> ctk.CTkFont:
        return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)

    def _section_label(self, parent, text: str) -> None:
        ctk.CTkLabel(
            parent,
            text=text.upper(),
            font=self._font(10),
            text_color=COLORS["text_secondary"],
            anchor="w",
        ).pack(anchor="w", pady=(0, 5))

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self) -> None:
        scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg"],
            scrollbar_button_color=COLORS["secondary"],
            scrollbar_button_hover_color=COLORS["primary"],
        )
        scroll.pack(fill="both", expand=True)
        scroll.columnconfigure(0, weight=1)

        self._build_topbar(scroll)  # row 0
        self._build_drop_zone(scroll)  # row 1
        self._build_file_list(scroll)  # row 2
        self._build_settings(scroll)  # row 3
        self._build_progress(scroll)  # row 4
        self._build_action(scroll)  # row 5
        self._build_results(scroll)  # row 6

        ctk.CTkFrame(scroll, fg_color="transparent", height=24).grid(row=7, column=0)

    # ── Top bar ───────────────────────────────────────────────────────────────

    def _build_topbar(self, parent) -> None:
        bar = ctk.CTkFrame(parent, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="ew", padx=32, pady=(20, 0))

        ctk.CTkButton(
            bar,
            text="← Volver",
            font=self._font(13),
            fg_color="transparent",
            hover_color=COLORS["secondary"],
            text_color=COLORS["text_secondary"],
            corner_radius=8,
            height=30,
            width=90,
            command=self._controller.show_home,
        ).pack(side="left")

        ctk.CTkLabel(
            bar,
            text="Image Compressor",
            font=self._font(22, "bold"),
            text_color=COLORS["text"],
        ).pack(side="left", padx=16)

    # ── Drop zone ─────────────────────────────────────────────────────────────

    def _build_drop_zone(self, parent) -> None:
        self._drop_card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["card"],
            corner_radius=16,
            border_width=2,
            border_color=COLORS["secondary"],
        )
        self._drop_card.grid(row=1, column=0, sticky="ew", padx=32, pady=(14, 0))

        inner = ctk.CTkFrame(self._drop_card, fg_color="transparent")
        inner.pack(pady=20, padx=32)

        ctk.CTkLabel(
            inner, text="⬆", font=self._font(28), text_color=COLORS["primary"]
        ).pack()

        self._drop_label = ctk.CTkLabel(
            inner,
            text="Arrastra imágenes aquí (JPG, PNG, WEBP, BMP)",
            font=self._font(14, "bold"),
            text_color=COLORS["text"],
        )
        self._drop_label.pack(pady=(4, 2))

        ctk.CTkLabel(
            inner, text="o", font=self._font(12), text_color=COLORS["text_secondary"]
        ).pack()

        ctk.CTkButton(
            inner,
            text="Seleccionar archivos",
            font=self._font(13),
            fg_color=COLORS["secondary"],
            hover_color=COLORS["primary"],
            text_color=COLORS["text"],
            corner_radius=8,
            height=32,
            command=self._select_files,
        ).pack(pady=(6, 0))

        for widget in (self._drop_card, inner):
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self._on_drop)
            widget.dnd_bind("<<DragEnter>>", self._on_drag_enter)
            widget.dnd_bind("<<DragLeave>>", self._on_drag_leave)

    # ── File list ─────────────────────────────────────────────────────────────

    def _build_file_list(self, parent) -> None:
        self._file_list_frame = ctk.CTkFrame(
            parent, fg_color=COLORS["card"], corner_radius=10
        )
        self._file_list_frame.grid(row=2, column=0, sticky="ew", padx=32, pady=(8, 0))
        self._file_list_frame.columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self._file_list_frame, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(10, 4))

        self._file_count_label = ctk.CTkLabel(
            header,
            text="Ningún archivo seleccionado",
            font=self._font(13),
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        self._file_count_label.pack(side="left")

        ctk.CTkButton(
            header,
            text="Limpiar",
            font=self._font(11),
            fg_color=COLORS["secondary"],
            hover_color=COLORS["error"],
            text_color=COLORS["text"],
            corner_radius=6,
            height=24,
            width=60,
            command=self._clear_files,
        ).pack(side="right")

        self._file_items_frame = ctk.CTkFrame(
            self._file_list_frame, fg_color="transparent"
        )
        self._file_items_frame.pack(fill="x", padx=16, pady=(0, 10))

    # ── Settings ──────────────────────────────────────────────────────────────

    def _build_settings(self, parent) -> None:
        card = ctk.CTkFrame(parent, fg_color=COLORS["card"], corner_radius=16)
        card.grid(row=3, column=0, sticky="ew", padx=32, pady=(10, 0))
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)
        card.columnconfigure(2, weight=1)

        # Output format
        fmt = ctk.CTkFrame(card, fg_color="transparent")
        fmt.grid(row=0, column=0, sticky="new", padx=(20, 8), pady=(18, 18))
        self._section_label(fmt, "Formato de salida")
        self._format_combo = ctk.CTkComboBox(
            fmt,
            values=IMAGE_FORMATS,
            font=self._font(13),
            fg_color=COLORS["secondary"],
            border_color=COLORS["secondary"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["hover"],
            dropdown_fg_color=COLORS["card"],
            dropdown_hover_color=COLORS["secondary"],
            dropdown_font=self._font(13),
            text_color=COLORS["text"],
            corner_radius=8,
            state="readonly",
        )
        self._format_combo.set("JPEG")
        self._format_combo.pack(fill="x")

        # Quality slider
        ql = ctk.CTkFrame(card, fg_color="transparent")
        ql.grid(row=0, column=1, sticky="new", padx=8, pady=(18, 18))
        self._quality_title = ctk.CTkLabel(
            ql,
            text="CALIDAD  (1–95)",
            font=self._font(10),
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        self._quality_title.pack(anchor="w", pady=(0, 5))
        self._quality_value_label = ctk.CTkLabel(
            ql,
            text="85",
            font=self._font(20, "bold"),
            text_color=COLORS["primary"],
        )
        self._quality_value_label.pack()
        self._quality_slider = ctk.CTkSlider(
            ql,
            from_=1,
            to=95,
            number_of_steps=94,
            fg_color=COLORS["secondary"],
            progress_color=COLORS["primary"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["hover"],
            command=self._on_quality_change,
        )
        self._quality_slider.set(85)
        self._quality_slider.pack(fill="x", pady=(4, 0))

        # Output folder
        out = ctk.CTkFrame(card, fg_color="transparent")
        out.grid(row=0, column=2, sticky="new", padx=(8, 20), pady=(18, 18))
        self._section_label(out, "Carpeta de salida")
        row = ctk.CTkFrame(out, fg_color="transparent")
        row.pack(fill="x")
        row.columnconfigure(0, weight=1)
        self._folder_label = ctk.CTkLabel(
            row,
            text="Misma carpeta",
            font=self._font(12),
            text_color=COLORS["text_secondary"],
            anchor="w",
            wraplength=160,
        )
        self._folder_label.grid(row=0, column=0, sticky="w")
        ctk.CTkButton(
            row,
            text="Cambiar",
            font=self._font(12),
            fg_color=COLORS["secondary"],
            hover_color=COLORS["primary"],
            text_color=COLORS["text"],
            corner_radius=8,
            height=28,
            width=72,
            command=self._select_output_folder,
        ).grid(row=0, column=1, padx=(8, 0))

    def _on_quality_change(self, val: float) -> None:
        self._quality_value_label.configure(text=str(int(val)))

    # ── Progress ──────────────────────────────────────────────────────────────

    def _build_progress(self, parent) -> None:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=4, column=0, sticky="ew", padx=32, pady=(10, 0))
        frame.columnconfigure(0, weight=1)

        self._progress_bar = ctk.CTkProgressBar(
            frame,
            mode="determinate",
            fg_color=COLORS["secondary"],
            progress_color=COLORS["primary"],
            corner_radius=6,
            height=6,
        )
        self._progress_bar.set(0)
        self._progress_bar.pack(fill="x")

        self._progress_label = ctk.CTkLabel(
            frame,
            text="",
            font=self._font(11),
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        self._progress_label.pack(anchor="w", pady=(3, 0))

    # ── Action button ─────────────────────────────────────────────────────────

    def _build_action(self, parent) -> None:
        self._btn_compress = ctk.CTkButton(
            parent,
            text="⚡  Comprimir imágenes",
            font=self._font(15, "bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["hover"],
            text_color=COLORS["text"],
            corner_radius=12,
            height=46,
            state="disabled",
            command=self._compress,
        )
        self._btn_compress.grid(row=5, column=0, sticky="ew", padx=32, pady=(14, 0))

    # ── Results ───────────────────────────────────────────────────────────────

    def _build_results(self, parent) -> None:
        self._results_card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["card"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["success"],
        )
        # Hidden until compression is done
        self._results_inner = ctk.CTkFrame(self._results_card, fg_color="transparent")
        self._results_inner.pack(fill="x", padx=20, pady=14)

    # ── DnD ──────────────────────────────────────────────────────────────────

    def _on_drag_enter(self, _event) -> None:
        self._drop_card.configure(border_color=COLORS["primary"])

    def _on_drag_leave(self, _event) -> None:
        self._drop_card.configure(border_color=COLORS["secondary"])

    def _on_drop(self, event) -> None:
        self._drop_card.configure(border_color=COLORS["secondary"])
        raw = self.tk.splitlist(event.data)
        new = [p for p in raw if p.lower().endswith(IMAGE_EXTENSIONS)]
        self._add_files(new)

    # ── File handling ─────────────────────────────────────────────────────────

    def _select_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Seleccionar imágenes",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png *.webp *.bmp"),
                ("Todos los archivos", "*.*"),
            ],
        )
        if paths:
            self._add_files(list(paths))

    def _select_output_folder(self) -> None:
        folder = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if folder:
            self.output_folder = folder
            display = folder if len(folder) <= 28 else f"...{folder[-25:]}"
            self._folder_label.configure(text=display)

    def _add_files(self, paths: list[str]) -> None:
        for p in paths:
            if p not in self._files:
                self._files.append(p)
        self._refresh_file_list()

    def _clear_files(self) -> None:
        self._files.clear()
        self._refresh_file_list()

    def _refresh_file_list(self) -> None:
        for w in self._file_items_frame.winfo_children():
            w.destroy()

        if not self._files:
            self._file_count_label.configure(text="Ningún archivo seleccionado")
            self._btn_compress.configure(state="disabled")
            return

        self._file_count_label.configure(
            text=f"{len(self._files)} imagen{'es' if len(self._files) != 1 else ''} seleccionada{'s' if len(self._files) != 1 else ''}"
        )

        for p in self._files:
            row = ctk.CTkFrame(
                self._file_items_frame, fg_color=COLORS["secondary"], corner_radius=6
            )
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(
                row,
                text=f"📷  {os.path.basename(p)}",
                font=self._font(12),
                text_color=COLORS["text"],
                anchor="w",
            ).pack(side="left", padx=10, pady=5)
            size_kb = os.path.getsize(p) // 1024
            ctk.CTkLabel(
                row,
                text=f"{size_kb:,} KB",
                font=self._font(11),
                text_color=COLORS["text_secondary"],
                anchor="e",
            ).pack(side="right", padx=10, pady=5)

        self._btn_compress.configure(state="normal")

    def _resolve_output_folder(self, fallback_file: str) -> str:
        return self.output_folder or os.path.dirname(fallback_file)

    # ── Compression ───────────────────────────────────────────────────────────

    def _compress(self) -> None:
        if not self._files:
            return
        folder = self._resolve_output_folder(self._files[0])
        quality = int(self._quality_slider.get())
        fmt = self._format_combo.get()

        self._btn_compress.configure(state="disabled", text="Comprimiendo...")
        self._progress_bar.set(0)
        self._progress_label.configure(
            text="Procesando...", text_color=COLORS["text_secondary"]
        )
        self._hide_results()

        self._compressor = ImageCompressorThread(
            input_files=self._files,
            output_folder=folder,
            quality=quality,
            output_format=fmt,
            on_progress=self._on_progress,
            on_finished=self._on_finished,
            on_error=self._on_error,
        )
        self._compressor.start()

    def _on_progress(self, value: int) -> None:
        self.after(
            0,
            lambda v=value: (
                self._progress_bar.set(v / 100),
                self._progress_label.configure(text=f"Procesando... {v}%"),
            ),
        )

    def _on_finished(self, results: list[dict]) -> None:
        def _update() -> None:
            self._progress_bar.set(1)
            self._progress_label.configure(
                text="Completado ✓", text_color=COLORS["success"]
            )
            self._btn_compress.configure(state="normal", text="⚡  Comprimir imágenes")
            self._show_results(results)

        self.after(0, _update)

    def _on_error(self, message: str) -> None:
        self.after(
            0,
            lambda: (
                self._progress_label.configure(
                    text=f"Error: {message}", text_color=COLORS["error"]
                ),
                self._btn_compress.configure(
                    state="normal", text="⚡  Comprimir imágenes"
                ),
            ),
        )

    # ── Results visibility ────────────────────────────────────────────────────

    def _show_results(self, results: list[dict]) -> None:
        for w in self._results_inner.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            self._results_inner,
            text=f"✓  {len(results)} imagen{'es' if len(results) != 1 else ''} comprimida{'s' if len(results) != 1 else ''}",
            font=self._font(14, "bold"),
            text_color=COLORS["success"],
            anchor="w",
        ).pack(anchor="w", pady=(0, 8))

        for r in results:
            reduction = (
                (1 - r["compressed_kb"] / r["original_kb"]) * 100
                if r["original_kb"]
                else 0.0
            )
            row = ctk.CTkFrame(
                self._results_inner, fg_color=COLORS["secondary"], corner_radius=8
            )
            row.pack(fill="x", pady=3)
            row.columnconfigure(0, weight=1)

            ctk.CTkLabel(
                row,
                text=f"📷  {r['name']}",
                font=self._font(12),
                text_color=COLORS["text"],
                anchor="w",
            ).grid(row=0, column=0, sticky="w", padx=12, pady=(8, 2))

            stats = f"{r['original_kb']:,} KB → {r['compressed_kb']:,} KB  (−{reduction:.1f}%)"
            ctk.CTkLabel(
                row,
                text=stats,
                font=self._font(11),
                text_color=COLORS["success"]
                if reduction > 0
                else COLORS["text_secondary"],
                anchor="w",
            ).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 8))

            ctk.CTkLabel(
                row,
                text=f"📁  {os.path.dirname(r['output'])}",
                font=self._font(10),
                text_color=COLORS["text_secondary"],
                anchor="e",
            ).grid(row=0, column=1, rowspan=2, sticky="e", padx=12)

        self._results_card.grid(row=6, column=0, sticky="ew", padx=32, pady=(14, 0))

    def _hide_results(self) -> None:
        self._results_card.grid_remove()
