# GUI/GUI.py
import sys
import os
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer

_app = None

# Look for icon in root (one level up from this file)
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
        self.tray.setToolTip("Sabrina — Idle")

        menu = QMenu()
        self._status_action = menu.addAction("Idle")
        self._status_action.setEnabled(False)
        menu.addSeparator()
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self._exit)
        self.tray.setContextMenu(menu)

    def show(self):
        self.tray.show()

    def set_listening(self):
        self.tray.setToolTip("Sabrina — Listening....")
        self._status_action.setText("Listening....")

    def set_responding(self):
        self.tray.setToolTip("Sabrina — Responding........")
        self._status_action.setText("Responding........")

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
    win.show()

    QTimer.singleShot(1000, win.set_listening)
    QTimer.singleShot(4000, win.set_responding)
    QTimer.singleShot(7000, win.set_listening)

    sys.exit(_app.exec())