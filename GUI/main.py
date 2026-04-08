# GUI/GUI.py
import sys
import os
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer

_app = None

_ROOT = os.path.dirname(os.path.abspath(__file__))
_ICON = None
for _name in ("icon.ico", "icon.png"):
    _path = os.path.join(_ROOT, _name)
    if os.path.exists(_path):
        _ICON = _path
        break


class MainWindow:
    def __init__(self, stop_callback=None):
        global _app
        if QApplication.instance() is None:
            _app = QApplication(sys.argv)
        else:
            _app = QApplication.instance()

        self.stop_callback = stop_callback
        self._build_tray()

    def _build_tray(self):
        self.tray = QSystemTrayIcon()

        if _ICON:
            self.tray.setIcon(QIcon(_ICON))
        else:
            # Fallback: blank 1x1 icon so OS doesn't render dots
            from PySide6.QtGui import QPixmap
            px = QPixmap(1, 1)
            px.fill()
            self.tray.setIcon(QIcon(px))

        self.tray.setToolTip("Sabrina — Initializing...")

        menu = QMenu()
        self._status_action = menu.addAction("Initializing...")
        self._status_action.setEnabled(False)
        menu.addSeparator()
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self._exit)
        self.tray.setContextMenu(menu)

    def show(self):
        self.tray.show()
        # Small delay so tray is fully registered before showing message
        QTimer.singleShot(500, self._notify_initializing)

    def _notify_initializing(self):
        self.tray.showMessage(
            "Sabrina",
            "Setting up... please wait.",
            QSystemTrayIcon.Information,
            3000
        )

    def set_initializing(self):
        """Call during heavy loading steps to keep tray label updated."""
        self._status_action.setText("Initializing...")
        self.tray.setToolTip("Sabrina — Initializing...")

    def set_ready(self):
        """Call once everything is loaded."""
        self._status_action.setText("Ready")
        self.tray.setToolTip("Sabrina — Ready")
        self.tray.showMessage("Sabrina", "Ready!", QSystemTrayIcon.Information, 2000)

    def set_listening(self):
        self._status_action.setText("Listening....")
        self.tray.setToolTip("Sabrina — Listening....")

    def set_responding(self):
        self._status_action.setText("Responding........")
        self.tray.setToolTip("Sabrina — Responding........")

    def set_error(self, message):
        self.tray.showMessage("Error detected", message, QSystemTrayIcon.Critical, 4000)

    def _exit(self):
        self.tray.hide()
        if self.stop_callback:
            self.stop_callback()
        if _app:
            _app.exit()


if __name__ == "__main__":
    def fake_stop():
        print("Terminated.")

    win = MainWindow(stop_callback=fake_stop)
    win.show()  # shows "Setting up..." balloon

    QTimer.singleShot(3000, win.set_ready)        # simulates load complete
    QTimer.singleShot(5000, win.set_listening)
    QTimer.singleShot(8000, win.set_responding)
    QTimer.singleShot(11000, win.set_listening)

    sys.exit(_app.exec())