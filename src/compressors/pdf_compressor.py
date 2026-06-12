import os
import shutil
import subprocess
import sys
import threading
from typing import Callable

# Suppress the console window spawned by Ghostscript on Windows
_CREATION_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0


def get_ghostscript_path() -> str:
    """
    Resolve the absolute path to gswin64c.exe.

    Search order:
    1. gs_bin/ next to the bundled executable (sys._MEIPASS when frozen).
    2. gs_bin/ relative to this source file (manual vendor setups).
    3. System PATH (Ghostscript installed system-wide).
    """
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        # src/compressors/ → go up two levels to project root
        base = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )

    bundled = os.path.join(base, "gs_bin", "gswin64c.exe")
    if os.path.isfile(bundled):
        return bundled

    for name in ("gswin64c", "gswin32c", "gs"):
        found = shutil.which(name)
        if found:
            return found

    raise FileNotFoundError(
        "Ghostscript not found.\n"
        "Install it from https://www.ghostscript.com/ or place gswin64c.exe "
        "inside a gs_bin/ folder next to the application."
    )


def get_ghostscript_lib() -> str | None:
    """Return the bundled gs_lib path if present, for GS_LIB env variable."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )

    lib = os.path.join(base, "gs_lib")
    return lib if os.path.isdir(lib) else None


class PDFCompressorThread:
    def __init__(
        self,
        input_pdf: str,
        output_pdf: str,
        quality: str,
        on_progress: Callable[[int], None],
        on_finished: Callable[[str, int], None],
        on_error: Callable[[str], None],
    ) -> None:
        self._input_pdf = input_pdf
        self._output_pdf = output_pdf
        self._quality = quality
        self._on_progress = on_progress
        self._on_finished = on_finished
        self._on_error = on_error
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def _run(self) -> None:
        try:
            gs_path = get_ghostscript_path()

            env = os.environ.copy()
            gs_lib = get_ghostscript_lib()
            if gs_lib:
                env["GS_LIB"] = gs_lib

            cmd = [
                gs_path,
                "-dNOPAUSE",
                "-dBATCH",
                "-dSAFER",
                f"-dPDFSETTINGS=/{self._quality}",
                "-sDEVICE=pdfwrite",
                f"-sOutputFile={self._output_pdf}",
                self._input_pdf,
            ]

            self._on_progress(50)
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                creationflags=_CREATION_FLAGS,
            )

            if result.returncode != 0:
                stderr = result.stderr.decode("utf-8", errors="replace").strip()
                raise RuntimeError(
                    stderr or f"Ghostscript exited with code {result.returncode}"
                )

            self._on_progress(100)
            new_size_kb = os.path.getsize(self._output_pdf) // 1024
            self._on_finished(self._output_pdf, new_size_kb)

        except Exception as exc:
            self._on_error(str(exc))
