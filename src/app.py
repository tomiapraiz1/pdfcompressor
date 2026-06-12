from __future__ import annotations

import customtkinter as ctk
from tkinterdnd2 import TkinterDnD

from .screens.home_screen import HomeScreen
from .screens.image_screen import ImageScreen
from .screens.pdf_screen import PDFScreen
from .utils.config import APP_TITLE, COLORS, WINDOW_HEIGHT, WINDOW_WIDTH

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self) -> None:
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)
        self._screens: dict[str, ctk.CTkFrame] = {}
        self._current: ctk.CTkFrame | None = None
        self._configure_window()
        self._build_container()
        self._init_screens()
        self.show_home()

    def _configure_window(self) -> None:
        self.title(APP_TITLE)
        self.configure(fg_color=COLORS["bg"])
        self.resizable(False, False)
        self.update_idletasks()
        x = (self.winfo_screenwidth() - WINDOW_WIDTH) // 2
        y = (self.winfo_screenheight() - WINDOW_HEIGHT) // 2
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

    def _build_container(self) -> None:
        self._container = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        self._container.pack(fill="both", expand=True)

    def _init_screens(self) -> None:
        self._screens["home"] = HomeScreen(self._container, controller=self)
        self._screens["pdf"] = PDFScreen(self._container, controller=self)
        self._screens["image"] = ImageScreen(self._container, controller=self)

    def _navigate(self, name: str) -> None:
        if self._current is not None:
            self._current.pack_forget()
        self._current = self._screens[name]
        self._current.pack(fill="both", expand=True)

    def show_home(self) -> None:
        self._navigate("home")

    def show_pdf_screen(self) -> None:
        self._navigate("pdf")

    def show_image_screen(self) -> None:
        self._navigate("image")
