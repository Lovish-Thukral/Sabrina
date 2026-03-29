import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow,
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout
)
from PySide6.QtCore import Qt, QPoint


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Remove title bar
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMinimumSize(600, 400)

        self._drag_pos = None

        # Layout setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        top_bar = QHBoxLayout()

        # Close button
        close_btn = QPushButton("X")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close)

        top_bar.addStretch()
        top_bar.addWidget(close_btn)

        main_layout.addLayout(top_bar)
        central_widget.setLayout(main_layout)

    # --- DRAG LOGIC ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self._drag_pos:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())