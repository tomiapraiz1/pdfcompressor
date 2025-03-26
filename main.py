import os
import sys

import ghostscript
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class PDFCompressorThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str, int)

    def __init__(self, input_pdf, output_pdf, quality):
        super().__init__()
        self.input_pdf = input_pdf
        self.output_pdf = output_pdf
        self.quality = quality

    def run(self):
        args = [
            "ps2pdf",
            "-dNOPAUSE",
            "-dBATCH",
            "-dSAFER",
            f"-dPDFSETTINGS=/{self.quality}",
            "-sDEVICE=pdfwrite",
            f"-sOutputFile={self.output_pdf}",
            self.input_pdf,
        ]

        self.progress.emit(50)
        ghostscript.Ghostscript(*args)
        self.progress.emit(100)

        new_size = os.path.getsize(self.output_pdf) // 1024
        self.finished.emit(self.output_pdf, new_size)


class PDFCompressor(QWidget):
    def __init__(self):
        super().__init__()
        self.pdf_path = None
        self.output_folder = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Compresor de PDF")
        self.setGeometry(100, 100, 600, 500)
        self.setStyleSheet(
            "background-color: #2E3440; color: #D8DEE9; font-size: 14px;"
        )
        self.setAcceptDrops(True)

        title_font = QFont("Arial", 14, QFont.Weight.Bold)

        self.label = QLabel("Arrastra un PDF aquí o selecciónalo", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(title_font)
        self.label.setStyleSheet(
            "color: #D8DEE9; padding: 10px; background-color: transparent;"
        )
        self.label.setGeometry(0, 0, self.width(), self.height())
        self.label.setWordWrap(True)

        self.btn_select = QPushButton("Seleccionar PDF", self)
        self.btn_select.setStyleSheet(
            "background-color: #5E81AC; color: white; padding: 10px; border-radius: 5px;"
        )
        self.btn_select.clicked.connect(self.select_pdf)

        self.pdf_name_label = QLabel("Nombre del archivo: No seleccionado", self)
        self.pdf_name_label.setStyleSheet("padding: 5px;")

        self.combo_quality = QComboBox(self)
        self.combo_quality.setStyleSheet(
            "background-color: #434C5E; color: white; padding: 5px; border-radius: 5px;"
        )
        self.combo_quality.addItems(
            [
                "screen (Máxima compresión)",
                "ebook (Buena compresión)",
                "printer (Alta calidad)",
                "prepress (Óptima impresión)",
            ]
        )

        self.btn_output = QPushButton("Seleccionar Carpeta de Salida", self)
        self.btn_output.setStyleSheet(
            "background-color: #5E81AC; color: white; padding: 10px; border-radius: 5px;"
        )
        self.btn_output.clicked.connect(self.select_output_folder)

        self.output_folder_label = QLabel("Carpeta de salida: No seleccionada", self)
        self.output_folder_label.setStyleSheet("padding: 5px;")

        self.file_name_input = QLineEdit(self)
        self.file_name_input.setPlaceholderText(
            "Nombre del archivo comprimido (sin extensión)"
        )
        self.file_name_input.setStyleSheet(
            "background-color: #3B4252; color: white; padding: 5px; border-radius: 5px;"
        )

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setStyleSheet(
            "QProgressBar { border: 2px solid #4C566A; border-radius: 5px; text-align: center; } QProgressBar::chunk { background-color: #A3BE8C; }"
        )
        self.progress_bar.setValue(0)

        self.btn_compress = QPushButton("⚡ Comprimir PDF", self)
        self.btn_compress.setStyleSheet(
            "background-color: #A3BE8C; color: black; padding: 10px; border-radius: 5px;"
        )
        self.btn_compress.setEnabled(False)
        self.btn_compress.clicked.connect(self.compress_pdf)

        self.size_label = QLabel("", self)
        self.size_label.setStyleSheet("padding: 5px;")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.btn_select)
        layout.addWidget(self.pdf_name_label)
        layout.addWidget(self.combo_quality)
        layout.addWidget(self.btn_output)
        layout.addWidget(self.output_folder_label)
        layout.addWidget(self.file_name_input)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.btn_compress)
        layout.addWidget(self.size_label)
        self.setLayout(layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.label.setText("Arrastra el archivo aquí...")

    def dragLeaveEvent(self, event):
        self.label.setText("Arrastra un PDF aquí o selecciónalo")

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(".pdf"):
                self.pdf_path = file_path
                self.label.setText(f"Seleccionado: {file_path}")
                self.pdf_name_label.setText(
                    f"Nombre del archivo: {os.path.basename(file_path)}"
                )
                self.btn_compress.setEnabled(True)
                self.show_file_size()

    def select_pdf(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Seleccionar PDF", "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.pdf_path = file_path
            self.label.setText(f"Seleccionado: {file_path}")
            self.pdf_name_label.setText(
                f"Nombre del archivo: {os.path.basename(file_path)}"
            )
            self.btn_compress.setEnabled(True)
            self.show_file_size()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Salida")
        if folder:
            self.output_folder = folder
            self.output_folder_label.setText(f"Carpeta de salida: {folder}")

    def show_file_size(self):
        size_kb = os.path.getsize(self.pdf_path) // 1024
        self.size_label.setText(f"Tamaño original: {size_kb} KB")

    def compress_pdf(self):
        if not self.pdf_path:
            return

        output_folder = (
            self.output_folder if self.output_folder else os.path.dirname(self.pdf_path)
        )
        custom_name = self.file_name_input.text().strip()
        output_pdf = os.path.join(
            output_folder,
            f"{custom_name}.pdf"
            if custom_name
            else os.path.basename(self.pdf_path).replace(".pdf", "_comprimido.pdf"),
        )

        quality_map = {
            "screen (Máxima compresión)": "screen",
            "ebook (Buena compresión)": "ebook",
            "printer (Alta calidad)": "printer",
            "prepress (Óptima impresión)": "prepress",
            "default (Por defecto)": "default",
        }
        selected_quality = quality_map[self.combo_quality.currentText()]

        self.progress_bar.setValue(0)
        self.thread = PDFCompressorThread(self.pdf_path, output_pdf, selected_quality)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.finished.connect(self.compression_done)
        self.thread.start()

    def compression_done(self, output_pdf, new_size):
        self.label.setText(f"PDF comprimido guardado en:\n{output_pdf}")
        self.size_label.setText(
            self.size_label.text() + f"\nTamaño comprimido: {new_size} KB"
        )
        self.progress_bar.setValue(100)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFCompressor()
    window.show()
    sys.exit(app.exec())
