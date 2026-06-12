from __future__ import annotations

import os
from tkinter import filedialog

import customtkinter as ctk
from tkinterdnd2 import DND_FILES

from ..compressors.pdf_compressor import PDFCompressorThread
from ..utils.config import COLORS, FONT_FAMILY, PDF_QUALITY_MAP, PDF_QUALITY_OPTIONS


class PDFScreen(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkBaseClass, controller) -> None:
        super().__init__(parent, fg_color=COLORS["bg"])
        self._controller = controller
        self.pdf_path: str | None = None
        self.output_folder: str | None = None
        self._compressor: PDFCompressorThread | None = None
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
        self._build_file_bar(scroll)  # row 2
        self._build_settings(scroll)  # row 3
        self._build_progress(scroll)  # row 4
        self._build_action(scroll)  # row 5
        self._build_results(scroll)  # row 6  (hidden until done)

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
            text="PDF Compressor",
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
            text="Arrastra tu PDF aquí",
            font=self._font(14, "bold"),
            text_color=COLORS["text"],
        )
        self._drop_label.pack(pady=(4, 2))

        ctk.CTkLabel(
            inner, text="o", font=self._font(12), text_color=COLORS["text_secondary"]
        ).pack()

        ctk.CTkButton(
            inner,
            text="Seleccionar archivo",
            font=self._font(13),
            fg_color=COLORS["secondary"],
            hover_color=COLORS["primary"],
            text_color=COLORS["text"],
            corner_radius=8,
            height=32,
            command=self._select_pdf,
        ).pack(pady=(6, 0))

        for widget in (self._drop_card, inner):
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self._on_drop)
            widget.dnd_bind("<<DragEnter>>", self._on_drag_enter)
            widget.dnd_bind("<<DragLeave>>", self._on_drag_leave)

    # ── File info bar ─────────────────────────────────────────────────────────

    def _build_file_bar(self, parent) -> None:
        bar = ctk.CTkFrame(parent, fg_color=COLORS["card"], corner_radius=10)
        bar.grid(row=2, column=0, sticky="ew", padx=32, pady=(8, 0))
        bar.columnconfigure(0, weight=1)

        self._file_name_label = ctk.CTkLabel(
            bar,
            text="Ningún archivo seleccionado",
            font=self._font(13),
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        self._file_name_label.grid(row=0, column=0, sticky="w", padx=16, pady=10)

        self._original_size_label = ctk.CTkLabel(
            bar,
            text="",
            font=self._font(12, "bold"),
            text_color=COLORS["text_secondary"],
            anchor="e",
        )
        self._original_size_label.grid(row=0, column=1, sticky="e", padx=16, pady=10)

    # ── Settings ──────────────────────────────────────────────────────────────

    def _build_settings(self, parent) -> None:
        card = ctk.CTkFrame(parent, fg_color=COLORS["card"], corner_radius=16)
        card.grid(row=3, column=0, sticky="ew", padx=32, pady=(10, 0))
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)

        # Quality
        q = ctk.CTkFrame(card, fg_color="transparent")
        q.grid(row=0, column=0, sticky="new", padx=(20, 10), pady=(18, 8))
        self._section_label(q, "Calidad de compresión")
        self._quality_combo = ctk.CTkComboBox(
            q,
            values=PDF_QUALITY_OPTIONS,
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
        self._quality_combo.set(PDF_QUALITY_OPTIONS[0])
        self._quality_combo.pack(fill="x")

        # Output folder
        f = ctk.CTkFrame(card, fg_color="transparent")
        f.grid(row=0, column=1, sticky="new", padx=(10, 20), pady=(18, 8))
        self._section_label(f, "Carpeta de salida")
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x")
        row.columnconfigure(0, weight=1)
        self._folder_label = ctk.CTkLabel(
            row,
            text="Misma carpeta del archivo",
            font=self._font(12),
            text_color=COLORS["text_secondary"],
            anchor="w",
            wraplength=190,
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

        # Output filename
        n = ctk.CTkFrame(card, fg_color="transparent")
        n.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 18))
        self._section_label(n, "Nombre del archivo de salida (opcional)")
        self._name_entry = ctk.CTkEntry(
            n,
            placeholder_text="documento_comprimido  (sin extensión)",
            font=self._font(13),
            fg_color=COLORS["secondary"],
            border_color=COLORS["secondary"],
            text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_secondary"],
            corner_radius=8,
            height=34,
        )
        self._name_entry.pack(fill="x")

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
            text="⚡  Comprimir PDF",
            font=self._font(15, "bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["hover"],
            text_color=COLORS["text"],
            corner_radius=12,
            height=46,
            state="disabled",
            command=self._compress_pdf,
        )
        self._btn_compress.grid(row=5, column=0, sticky="ew", padx=32, pady=(14, 0))

    # ── Results card ──────────────────────────────────────────────────────────

    def _build_results(self, parent) -> None:
        self._results_card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["card"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["success"],
        )
        self._results_card.columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(
            self._results_card,
            text="✓  Compresión completada",
            font=self._font(14, "bold"),
            text_color=COLORS["success"],
            anchor="w",
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=20, pady=(14, 8))

        self._stat_original = self._stat_block(self._results_card, "Tamaño original", 0)
        self._stat_compressed = self._stat_block(
            self._results_card, "Tamaño comprimido", 1
        )
        self._stat_reduction = self._stat_block(self._results_card, "Reducción", 2)

        self._res_path = ctk.CTkLabel(
            self._results_card,
            text="",
            font=self._font(11),
            text_color=COLORS["text_secondary"],
            anchor="w",
            wraplength=800,
        )
        self._res_path.grid(
            row=2, column=0, columnspan=3, sticky="w", padx=20, pady=(6, 14)
        )

    def _stat_block(self, parent, label: str, col: int) -> ctk.CTkLabel:
        pad_l, pad_r = (20, 6) if col == 0 else (6, 20) if col == 2 else (6, 6)
        block = ctk.CTkFrame(parent, fg_color=COLORS["secondary"], corner_radius=10)
        block.grid(row=1, column=col, padx=(pad_l, pad_r), pady=(0, 4), sticky="ew")
        ctk.CTkLabel(
            block, text=label, font=self._font(10), text_color=COLORS["text_secondary"]
        ).pack(padx=12, pady=(8, 2))
        val = ctk.CTkLabel(
            block, text="—", font=self._font(17, "bold"), text_color=COLORS["text"]
        )
        val.pack(padx=12, pady=(0, 8))
        return val

    # ── DnD ──────────────────────────────────────────────────────────────────

    def _on_drag_enter(self, _event) -> None:
        self._drop_card.configure(border_color=COLORS["primary"])

    def _on_drag_leave(self, _event) -> None:
        self._drop_card.configure(border_color=COLORS["secondary"])

    def _on_drop(self, event) -> None:
        self._drop_card.configure(border_color=COLORS["secondary"])
        path = event.data.strip().strip("{}")
        if path.lower().endswith(".pdf"):
            self._set_pdf(path)

    # ── File handling ─────────────────────────────────────────────────────────

    def _select_pdf(self) -> None:
        path = filedialog.askopenfilename(
            title="Seleccionar PDF", filetypes=[("PDF Files", "*.pdf")]
        )
        if path:
            self._set_pdf(path)

    def _select_output_folder(self) -> None:
        folder = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if folder:
            self.output_folder = folder
            display = folder if len(folder) <= 38 else f"...{folder[-35:]}"
            self._folder_label.configure(text=display)

    def _set_pdf(self, path: str) -> None:
        self.pdf_path = path
        size_kb = os.path.getsize(path) // 1024
        self._drop_label.configure(
            text=f"📄  {os.path.basename(path)}", text_color=COLORS["success"]
        )
        self._file_name_label.configure(
            text=f"📄  {os.path.basename(path)}", text_color=COLORS["text"]
        )
        self._original_size_label.configure(
            text=f"{size_kb:,} KB", text_color=COLORS["text"]
        )
        self._btn_compress.configure(state="normal")
        self._hide_results()

    def _build_output_path(self) -> str:
        folder = self.output_folder or os.path.dirname(self.pdf_path)
        name = self._name_entry.get().strip()
        filename = (
            f"{name}.pdf"
            if name
            else os.path.basename(self.pdf_path).replace(".pdf", "_comprimido.pdf")
        )
        return os.path.join(folder, filename)

    # ── Compression ───────────────────────────────────────────────────────────

    def _compress_pdf(self) -> None:
        if not self.pdf_path:
            return
        output_pdf = self._build_output_path()
        quality = PDF_QUALITY_MAP[self._quality_combo.get()]
        self._btn_compress.configure(state="disabled", text="Comprimiendo...")
        self._progress_bar.set(0)
        self._progress_label.configure(
            text="Procesando...", text_color=COLORS["text_secondary"]
        )
        self._hide_results()
        self._compressor = PDFCompressorThread(
            input_pdf=self.pdf_path,
            output_pdf=output_pdf,
            quality=quality,
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

    def _on_finished(self, output_pdf: str, new_size_kb: int) -> None:
        original_kb = os.path.getsize(self.pdf_path) // 1024
        reduction = (1 - new_size_kb / original_kb) * 100 if original_kb else 0.0

        def _update() -> None:
            self._progress_bar.set(1)
            self._progress_label.configure(
                text="Completado ✓", text_color=COLORS["success"]
            )
            self._btn_compress.configure(state="normal", text="⚡  Comprimir PDF")
            self._show_results(original_kb, new_size_kb, reduction, output_pdf)

        self.after(0, _update)

    def _on_error(self, message: str) -> None:
        self.after(
            0,
            lambda: (
                self._progress_label.configure(
                    text=f"Error: {message}", text_color=COLORS["error"]
                ),
                self._btn_compress.configure(state="normal", text="⚡  Comprimir PDF"),
            ),
        )

    # ── Results visibility ────────────────────────────────────────────────────

    def _show_results(
        self, original_kb: int, compressed_kb: int, reduction: float, path: str
    ) -> None:
        self._stat_original.configure(text=f"{original_kb:,} KB")
        self._stat_compressed.configure(text=f"{compressed_kb:,} KB")
        self._stat_reduction.configure(
            text=f"{reduction:.1f}%", text_color=COLORS["success"]
        )
        self._res_path.configure(text=f"📁  {path}")
        self._results_card.grid(row=6, column=0, sticky="ew", padx=32, pady=(14, 0))

    def _hide_results(self) -> None:
        self._results_card.grid_remove()
