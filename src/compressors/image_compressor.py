import os
import threading
from typing import Callable

from PIL import Image

# Disable Pillow's decompression-bomb guard — this is a local desktop app
# where the user selects their own files, so the limit serves no purpose.
Image.MAX_IMAGE_PIXELS = None


class ImageCompressorThread:
    def __init__(
        self,
        input_files: list[str],
        output_folder: str,
        quality: int,
        output_format: str,
        on_progress: Callable[[int], None],
        on_finished: Callable[[list[dict]], None],
        on_error: Callable[[str], None],
    ) -> None:
        self._input_files = input_files
        self._output_folder = output_folder
        self._quality = quality
        self._output_format = output_format  # "JPEG" | "PNG" | "WEBP"
        self._on_progress = on_progress
        self._on_finished = on_finished
        self._on_error = on_error
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def _run(self) -> None:
        try:
            ext_map = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}
            out_ext = ext_map[self._output_format]
            results: list[dict] = []
            total = len(self._input_files)

            for i, path in enumerate(self._input_files):
                original_kb = os.path.getsize(path) // 1024
                img = Image.open(path)

                # Mode conversions for format compatibility
                if self._output_format == "JPEG" and img.mode in ("RGBA", "P", "LA"):
                    img = img.convert("RGB")
                elif self._output_format == "PNG" and img.mode == "P":
                    img = img.convert("RGBA")

                base = os.path.splitext(os.path.basename(path))[0]
                out_path = os.path.join(
                    self._output_folder, f"{base}_compressed{out_ext}"
                )

                save_kwargs: dict = {"optimize": True}
                if self._output_format in ("JPEG", "WEBP"):
                    save_kwargs["quality"] = self._quality

                img.save(out_path, format=self._output_format, **save_kwargs)

                new_kb = os.path.getsize(out_path) // 1024
                results.append(
                    {
                        "name": os.path.basename(path),
                        "output": out_path,
                        "original_kb": original_kb,
                        "compressed_kb": new_kb,
                    }
                )
                self._on_progress(int((i + 1) / total * 100))

            self._on_finished(results)
        except Exception as exc:
            self._on_error(str(exc))
