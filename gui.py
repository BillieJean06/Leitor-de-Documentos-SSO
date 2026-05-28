import sys
import os
import subprocess
import fitz
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QFileDialog, QScrollArea, 
                             QLabel, QCheckBox, QGridLayout, QMessageBox,
                             QRadioButton, QButtonGroup)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from extractor import process_pdf
from exporter import export_to_excel

class OCRWorker(QThread):
    finished = pyqtSignal(str, str, str) # status, output_path, error_msg

    def __init__(self, pdf_path, output_path):
        super().__init__()
        self.pdf_path = pdf_path
        self.output_path = output_path

    def run(self):
        try:
            # --optimize 0 desliga a otimização de imagem, acelerando muito o processo
            process = subprocess.run([
                "ocrmypdf", "-l", "por", "--force-ocr", "--optimize", "0",
                "--invalidate-digital-signatures", self.pdf_path, self.output_path
            ], capture_output=True, text=True)
            
            if process.returncode != 0:
                self.finished.emit("error", "", f"Código: {process.returncode}\nDetalhes: {process.stderr[:500]}")
            else:
                self.finished.emit("success", self.output_path, "")
        except Exception as e:
            self.finished.emit("error", "", str(e))

class PDFPageWidget(QWidget):
    def __init__(self, page_num, pixmap):
        super().__init__()
        self.page_num = page_num
        
        layout = QVBoxLayout()
        
        # Thumbnail image
        self.img_label = QLabel()
        self.img_label.setPixmap(pixmap)
        # Scaled thumbnail for better visualization
        self.img_label.setScaledContents(True)
        self.img_label.setFixedSize(150, 212) # A4 ratio roughly
        layout.addWidget(self.img_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Checkbox for selection
        self.checkbox = QCheckBox(f"Página {page_num + 1}")
        layout.addWidget(self.checkbox, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(layout)
        
    def is_selected(self):
        return self.checkbox.isChecked()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Leitor de Documentos SSO")
        self.setGeometry(100, 100, 800, 600)
        
        self.pdf_path = None
        self.pages_widgets = []
        
        self.init_ui()
        
    def init_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Top controls
        top_layout = QHBoxLayout()
        
        # Document Type Selection
        self.radio_pcmso = QRadioButton("PCMSO")
        self.radio_pgr = QRadioButton("PGR")
        self.radio_pcmso.setChecked(True) # Default
        
        self.doc_type_group = QButtonGroup()
        self.doc_type_group.addButton(self.radio_pcmso)
        self.doc_type_group.addButton(self.radio_pgr)
        
        top_layout.addWidget(QLabel("Tipo de Documento:"))
        top_layout.addWidget(self.radio_pcmso)
        top_layout.addWidget(self.radio_pgr)

        self.btn_load = QPushButton("Carregar PDF")
        self.btn_load.clicked.connect(self.load_pdf)

        self.btn_ocr = QPushButton("Aplicar OCR")
        self.btn_ocr.clicked.connect(self.apply_ocr)
        self.btn_ocr.setEnabled(False)
        self.btn_ocr.setToolTip("Transforma um PDF escaneado em texto selecionável. O app pode travar por alguns minutos.")

        self.btn_extract = QPushButton("Extrair Selecionados e Exportar")
        self.btn_extract.clicked.connect(self.extract_and_export)
        self.btn_extract.setEnabled(False)

        top_layout.addStretch()
        top_layout.addWidget(self.btn_load)
        top_layout.addWidget(self.btn_ocr)
        top_layout.addWidget(self.btn_extract)
        
        # Scroll area for pages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)
        
        # Selection controls
        selection_layout = QHBoxLayout()
        self.btn_select_all = QPushButton("Selecionar Todas")
        self.btn_select_all.clicked.connect(self.select_all)
        self.btn_deselect_all = QPushButton("Desmarcar Todas")
        self.btn_deselect_all.clicked.connect(self.deselect_all)
        
        selection_layout.addWidget(self.btn_select_all)
        selection_layout.addWidget(self.btn_deselect_all)
        selection_layout.addStretch()
        
        main_layout.addLayout(top_layout)
        main_layout.addLayout(selection_layout)
        main_layout.addWidget(self.scroll_area)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
    def load_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.pdf_path = file_path
            self.render_pages()
            self.btn_extract.setEnabled(True)
            self.btn_ocr.setEnabled(True)
            
    def render_pages(self):
        # Clear previous pages
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)
        self.pages_widgets.clear()
        
        try:
            doc = fitz.open(self.pdf_path)
            
            row, col = 0, 0
            max_cols = 4 # Adjust based on window size later if needed
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                # Render page to image (zoom for better quality thumbnail)
                pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
                
                # Convert to QImage and then QPixmap
                img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
                qpixmap = QPixmap.fromImage(img)
                
                page_widget = PDFPageWidget(page_num, qpixmap)
                self.pages_widgets.append(page_widget)
                
                self.grid_layout.addWidget(page_widget, row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
                    
            doc.close()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar PDF:\n{str(e)}")

    def extract_and_export(self):
        selected_pages = [w.page_num for w in self.pages_widgets if w.is_selected()]
        
        if not selected_pages:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione pelo menos uma página.")
            return
            
        # Define onde salvar a planilha
        save_path, _ = QFileDialog.getSaveFileName(self, "Salvar Planilha", "", "Excel Files (*.xlsx)")
        
        if not save_path:
            return
            
        if not save_path.endswith('.xlsx'):
            save_path += '.xlsx'
            
        # Processar
        try:
            QMessageBox.information(self, "Aguarde", "Processando as páginas selecionadas... Isso pode demorar um pouco.")
            doc_type = 'pgr' if self.radio_pgr.isChecked() else 'pcmso'
            extracted_data = process_pdf(self.pdf_path, selected_pages, doc_type)

            if not extracted_data:
                QMessageBox.warning(self, "Aviso", "Nenhum dado encontrado nas páginas selecionadas com as regras atuais.")
                return
                
            success, msg = export_to_excel(extracted_data, save_path)
            
            if success:
                QMessageBox.information(self, "Sucesso", msg)
            else:
                QMessageBox.critical(self, "Erro", msg)
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro durante a extração:\n{str(e)}")

    def select_all(self):
        for widget in self.pages_widgets:
            widget.checkbox.setChecked(True)

    def deselect_all(self):
        for widget in self.pages_widgets:
            widget.checkbox.setChecked(False)

    def apply_ocr(self):
        if not self.pdf_path:
            return
            
        base, ext = os.path.splitext(self.pdf_path)
        output_path = f"{base}_ocr{ext}"
        
        # Desabilitar botões para evitar cliques duplos
        self.btn_ocr.setEnabled(False)
        self.btn_load.setEnabled(False)
        self.btn_extract.setEnabled(False)
        self.setWindowTitle("Leitor de Documentos SSO - PROCESSANDO OCR... (Isso pode demorar, não feche!)")
        
        self.ocr_thread = OCRWorker(self.pdf_path, output_path)
        self.ocr_thread.finished.connect(self.on_ocr_finished)
        self.ocr_thread.start()

    def on_ocr_finished(self, status, output_path, error_msg):
        self.btn_ocr.setEnabled(True)
        self.btn_load.setEnabled(True)
        self.btn_extract.setEnabled(True)
        self.setWindowTitle("Leitor de Documentos SSO")
        
        if status == "success":
            self.pdf_path = output_path
            self.render_pages()
            QMessageBox.information(self, "Sucesso", "OCR finalizado! O PDF escaneado agora é pesquisável.")
        else:
            QMessageBox.critical(self, "Erro no OCR", f"O OCR falhou:\n{error_msg}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
