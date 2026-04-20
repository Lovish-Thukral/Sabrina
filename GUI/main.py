import sys
import os
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QWidget
from PySide6.QtGui import QIcon, QColor, QPainter, QPainterPath, QFont, QPixmap
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QRect

_app  = None
_ROOT = os.path.dirname(os.path.abspath(__file__))
_ICON = None
for _name in ("icon.ico", "icon.png"):
    _path = os.path.join(_ROOT, _name)
    if os.path.exists(_path):
        _ICON = _path
        break


class SnackBar(QWidget):
    _BG     = QColor(28, 28, 28)
    _FG     = QColor(255, 255, 255)
    _SUB    = QColor(170, 170, 170)
    _GREEN  = QColor(72, 199, 142)
    _BLUE   = QColor(100, 160, 255)
    _RED    = QColor(240, 80, 80)
    _W, _H  = 300, 56
    _MARGIN = 20
    _RADIUS = 8

    def __init__(self):
        flags = (
            Qt.Tool
            | Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.WindowDoesNotAcceptFocus
        )
        super().__init__(None, flags)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFixedSize(self._W, self._H)

        self._dot_color = self._BLUE
        self._title     = ""
        self._sub       = ""
        self._opacity   = 0.0          # we track opacity ourselves

        # Animate a plain Python float via QPropertyAnimation on a Q_PROPERTY
        self._anim_in  = self._make_anim(0.0, 1.0, 200)
        self._anim_out = self._make_anim(1.0, 0.0, 350)
        self._anim_out.finished.connect(self.hide)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._anim_out.start)

    def _make_anim(self, start, end, ms):
        # Animate our own "opacity" property (defined via getter/setter below)
        a = QPropertyAnimation(self, b"opacity", self)
        a.setStartValue(float(start))
        a.setEndValue(float(end))
        a.setDuration(ms)
        a.setEasingCurve(QEasingCurve.OutCubic)
        return a

    # Qt property so QPropertyAnimation can drive it
    def getOpacity(self):
        return self._opacity

    def setOpacity(self, val):
        self._opacity = val
        self.update()           # trigger repaint on every frame

    opacity = property(getOpacity, setOpacity)

    # Make it a real Qt property
    from PySide6.QtCore import Property
    opacity = Property(float, getOpacity, setOpacity)

    def _reposition(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            screen.center().x() - self._W // 2,
            screen.bottom() - self._H - self._MARGIN - 30
        )

    def show_message(self, title: str, sub: str, dot_color: QColor, duration_ms: int = 3000):
        self._title     = title
        self._sub       = sub
        self._dot_color = dot_color
        self._reposition()

        self._anim_out.stop()
        self._timer.stop()
        self._opacity = 0.0

        self.show()
        self.raise_()
        self._anim_in.start()

        if duration_ms > 0:
            self._timer.start(duration_ms)

    def dismiss(self):
        self._timer.stop()
        self._anim_out.start()

    def paintEvent(self, _):
        if self._opacity <= 0.0:
            return

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Fill entire widget with solid bg first — no bleed possible
        p.fillRect(self.rect(), self._BG)

        # Apply our manual opacity to everything drawn after this
        p.setOpacity(self._opacity)

        # Rounded card
        path = QPainterPath()
        path.addRoundedRect(0, 0, self._W, self._H, self._RADIUS, self._RADIUS)
        p.fillPath(path, self._BG)

        # Coloured dot
        p.setBrush(self._dot_color)
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPoint(18, self._H // 2), 5, 5)

        # Title
        p.setPen(self._FG)
        f = QFont()
        f.setPixelSize(14)
        f.setWeight(QFont.Medium)
        p.setFont(f)
        p.drawText(QRect(34, 8, self._W - 42, 20), Qt.AlignVCenter | Qt.AlignLeft, self._title)

        # Subtitle
        p.setPen(self._SUB)
        f.setPixelSize(12)
        f.setWeight(QFont.Normal)
        p.setFont(f)
        p.drawText(QRect(34, 28, self._W - 42, 18), Qt.AlignVCenter | Qt.AlignLeft, self._sub)


class MainWindow:
    def __init__(self, stop_callback=None):
        global _app
        _app = QApplication.instance() or QApplication(sys.argv)
        _app.setQuitOnLastWindowClosed(False)

        self.stop_callback = stop_callback
        self._snack = SnackBar()
        self._build_tray()

    def _build_tray(self):
        self.tray = QSystemTrayIcon()
        if _ICON:
            self.tray.setIcon(QIcon(_ICON))
        else:
            px = QPixmap(16, 16)
            px.fill(QColor(100, 160, 255))
            self.tray.setIcon(QIcon(px))
        self.tray.setToolTip("Sabrina — Initializing...")

        menu = QMenu()
        self._status_action = menu.addAction("Initializing...")
        self._status_action.setEnabled(False)
        menu.addSeparator()
        quit_action = menu.addAction("Exit")
        quit_action.triggered.connect(self._exit)
        self.tray.setContextMenu(menu)

    def show(self):
        self.tray.show()
        QTimer.singleShot(300, lambda: self._snack.show_message(
            "Sabrina", "Setting up… please wait", SnackBar._BLUE, duration_ms=0
        ))

    def set_initializing(self):
        self._status_action.setText("Initializing...")
        self.tray.setToolTip("Sabrina — Initializing...")
        self._snack.show_message("Sabrina", "Setting up… please wait", SnackBar._BLUE, duration_ms=0)

    def set_ready(self):
        self._status_action.setText("Ready")
        self.tray.setToolTip("Sabrina — Ready")
        self._snack.show_message("Sabrina", "Ready!", SnackBar._GREEN, duration_ms=3000)

    def set_listening(self):
        self._status_action.setText("Listening...")
        self.tray.setToolTip("Sabrina — Listening...")
        self._snack.show_message("Sabrina", "Listening...", SnackBar._YELLOW, duration_ms=0)

    def set_responding(self):
        self._status_action.setText("Responding...")
        self.tray.setToolTip("Sabrina — Responding...")
        self._snack.show_message("Sabrina", "Thinking...", SnackBar._BLUE, duration_ms=0)

    def set_error(self, message: str):
        self._status_action.setText("Error")
        self.tray.setToolTip("Sabrina — Error")
        self._snack.show_message("Error", message, SnackBar._RED, duration_ms=5000)

    def _exit(self):
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            app.exit()


if __name__ == "__main__":
    win = MainWindow(stop_callback=lambda: print("Stopped."))
    win.show()

    QTimer.singleShot(2000, win.set_ready)
    QTimer.singleShot(5000, win.set_listening)
    QTimer.singleShot(8000, win.set_responding)
    QTimer.singleShot(11000, win.set_listening)

    sys.exit(_app.exec())