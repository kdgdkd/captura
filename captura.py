import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QMenu, QFileDialog, QSystemTrayIcon,
                             QHBoxLayout, QVBoxLayout, QPushButton, QDialog, QFormLayout,
                             QLineEdit, QComboBox, QSpinBox, QCheckBox, QLabel)
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap, QCursor, QIcon, QFont, QPainterPath
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal, QObject, QTimer, QSettings
import keyboard

class HotkeyRecorder(QWidget):
    def __init__(self, initial_value, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.line_edit = QLineEdit(initial_value)
        self.line_edit.setReadOnly(True)
        self.btn = QPushButton("Grabar")
        self.btn.setFixedWidth(80)
        self.btn.clicked.connect(self.record_hotkey)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.btn)

    def record_hotkey(self):
        self.btn.setText("...")
        self.btn.setEnabled(False)
        self.line_edit.setPlaceholderText("Presione teclas...")
        self.line_edit.setText("")
        # Procesar eventos para asegurar que la UI se actualice antes de bloquear
        QApplication.processEvents()
        
        # keyboard.read_hotkey es bloqueante, lo cual es aceptable aquí 
        # mientras el usuario realiza la acción de presionar y soltar.
        try:
            new_hk = keyboard.read_hotkey(suppress=True)
            self.line_edit.setText(new_hk)
        except Exception as e:
            print(f"Error al grabar atajo: {e}")
        
        self.btn.setText("Grabar")
        self.btn.setEnabled(True)

    def text(self):
        return self.line_edit.text()

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de Captura")
        self.settings = QSettings("MiEmpresa", "Capturador")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Atajos con grabador
        self.hk_zone = HotkeyRecorder(self.settings.value("hotkey_zone", "print screen"))
        self.hk_full = HotkeyRecorder(self.settings.value("hotkey_full", "shift+print screen"))
        form.addRow("Atajo Captura Zona:", self.hk_zone)
        form.addRow("Atajo Pantalla Completa:", self.hk_full)

        # Modificadores
        self.mod_square = QComboBox()
        self.mod_square.addItems(["Control", "Shift", "Alt"])
        self.mod_square.setCurrentText(self.settings.value("mod_square", "Control"))
        form.addRow("Modificador Cuadrado (1:1):", self.mod_square)

        self.mod_prop = QComboBox()
        self.mod_prop.addItems(["Control", "Shift", "Alt"])
        self.mod_prop.setCurrentText(self.settings.value("mod_prop", "Shift"))
        form.addRow("Modificador Proporciones:", self.mod_prop)

        # Proporciones
        prop_layout = QHBoxLayout()
        self.prop_w = QSpinBox()
        self.prop_w.setRange(1, 9999)
        self.prop_w.setValue(int(self.settings.value("prop_w", 16)))
        self.prop_h = QSpinBox()
        self.prop_h.setRange(1, 9999)
        self.prop_h.setValue(int(self.settings.value("prop_h", 9)))
        prop_layout.addWidget(self.prop_w)
        prop_layout.addWidget(QLabel(":"))
        prop_layout.addWidget(self.prop_h)
        form.addRow("Proporciones preferidas:", prop_layout)

        # Zoom y Coordenadas
        self.zoom_enabled = QCheckBox()
        self.zoom_enabled.setChecked(self.settings.value("zoom_enabled", True, type=bool))
        form.addRow("Activar Lupa (Zoom):", self.zoom_enabled)

        self.show_coords = QCheckBox()
        self.show_coords.setChecked(self.settings.value("show_coords", True, type=bool))
        form.addRow("Mostrar Coordenadas:", self.show_coords)

        # Ubicación
        loc_layout = QHBoxLayout()
        self.save_dir = QLineEdit(self.settings.value("save_dir", os.path.expanduser('~')))
        btn_browse = QPushButton("...")
        btn_browse.clicked.connect(self.browse_dir)
        loc_layout.addWidget(self.save_dir)
        loc_layout.addWidget(btn_browse)
        form.addRow("Carpeta Auto-Guardado:", loc_layout)

        # Formato y calidad
        self.out_format = QComboBox()
        self.out_format.addItems(["PNG", "JPG"])
        self.out_format.setCurrentText(self.settings.value("out_format", "PNG"))
        form.addRow("Formato de salida:", self.out_format)

        self.out_quality = QSpinBox()
        self.out_quality.setRange(1, 100)
        self.out_quality.setValue(int(self.settings.value("out_quality", 100)))
        form.addRow("Calidad JPG (1-100):", self.out_quality)

        layout.addLayout(form)

        # Botones
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Guardar")
        btn_save.clicked.connect(self.save_settings)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

    def browse_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta", self.save_dir.text())
        if dir_path:
            self.save_dir.setText(dir_path)

    def save_settings(self):
        self.settings.setValue("hotkey_zone", self.hk_zone.text())
        self.settings.setValue("hotkey_full", self.hk_full.text())
        self.settings.setValue("mod_square", self.mod_square.currentText())
        self.settings.setValue("mod_prop", self.mod_prop.currentText())
        self.settings.setValue("prop_w", self.prop_w.value())
        self.settings.setValue("prop_h", self.prop_h.value())
        self.settings.setValue("zoom_enabled", self.zoom_enabled.isChecked())
        self.settings.setValue("show_coords", self.show_coords.isChecked())
        self.settings.setValue("save_dir", self.save_dir.text())
        self.settings.setValue("out_format", self.out_format.currentText())
        self.settings.setValue("out_quality", self.out_quality.value())
        self.accept()

class SignalBridge(QObject):
    trigger_capture = pyqtSignal()
    trigger_full = pyqtSignal()

class CaptureOverlay(QWidget):
    def __init__(self, full_screenshot):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.full_screenshot = full_screenshot
        self.ratio = self.full_screenshot.devicePixelRatio()
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.Tool)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self.begin = QPoint()
        self.end = QPoint()
        self.current_pos = QPoint()
        self.is_selecting = False
        self.selection_rect = QRect()
        
        self.mode = 'new_selection' 
        self.active_handle = None
        self.drag_offset = QPoint()
        
        self.panel = QWidget(self)
        self.panel.setStyleSheet("""
            QWidget { background-color: #2b2b2b; border: 1px solid #1a1a1a; border-radius: 4px; }
            QPushButton { 
                min-width: 70px;
                padding: 4px 2px; 
                border: 1px solid #444444; 
                background-color: #404040; 
                color: #eeeeee; 
                font-size: 11px; 
                font-weight: bold; 
                border-radius: 2px;
            }
            QPushButton:hover { background-color: #0078d7; color: #ffffff; border: 1px solid #005a9e; }
        """)
        layout = QHBoxLayout(self.panel)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        self.btn_copy = QPushButton("Copiar")
        self.btn_auto = QPushButton("Auto")
        self.btn_save = QPushButton("Guardar...")
        self.btn_cancel = QPushButton("Cancelar")
        
        layout.addWidget(self.btn_copy)
        layout.addWidget(self.btn_auto)
        layout.addWidget(self.btn_save)
        layout.addWidget(self.btn_cancel)
        
        self.btn_copy.clicked.connect(self.on_copy_clicked)
        self.btn_auto.clicked.connect(self.on_auto_save_clicked)
        self.btn_save.clicked.connect(self.on_save_clicked)
        self.btn_cancel.clicked.connect(self.close)
        
        self.panel.hide()

    def get_handle_at(self, pos):
        if self.selection_rect.isNull():
            return None
        HANDLE_SIZE = 12
        r = self.selection_rect
        handles = {
            'top_left': QRect(r.left() - HANDLE_SIZE//2, r.top() - HANDLE_SIZE//2, HANDLE_SIZE, HANDLE_SIZE),
            'top_right': QRect(r.right() - HANDLE_SIZE//2, r.top() - HANDLE_SIZE//2, HANDLE_SIZE, HANDLE_SIZE),
            'bottom_left': QRect(r.left() - HANDLE_SIZE//2, r.bottom() - HANDLE_SIZE//2, HANDLE_SIZE, HANDLE_SIZE),
            'bottom_right': QRect(r.right() - HANDLE_SIZE//2, r.bottom() - HANDLE_SIZE//2, HANDLE_SIZE, HANDLE_SIZE)
        }
        for name, rect in handles.items():
            if rect.contains(pos):
                return name
        return None

    def paintEvent(self, event):
        painter = QPainter(self)
        logical_rect = self.rect()
        painter.drawPixmap(logical_rect, self.full_screenshot)
        painter.fillRect(logical_rect, QColor(0, 0, 0, 120))

        settings = QSettings("MiEmpresa", "Capturador")
        zoom_enabled = settings.value("zoom_enabled", True, type=bool)
        show_coords = settings.value("show_coords", True, type=bool)

        handle = self.get_handle_at(self.current_pos)
        show_lupa = False
        
        if zoom_enabled:
            if self.mode in ['new_selection', 'resizing']:
                show_lupa = True
            elif not self.is_selecting:
                if self.selection_rect.isNull() or handle is not None or not self.selection_rect.contains(self.current_pos):
                    show_lupa = True

        if show_lupa and not self.current_pos.isNull():
            # ... (líneas de ejes omitidas para brevedad en la explicación, pero presentes en el código)
            pen = QPen(QColor(255, 255, 255, 100), 1, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawLine(0, self.current_pos.y(), self.width(), self.current_pos.y())
            painter.drawLine(self.current_pos.x(), 0, self.current_pos.x(), self.height())

            mag_size = 120
            zoom = 4
            offset = 40
            
            possible_points = [
                (self.current_pos.x() + offset, self.current_pos.y() + offset),
                (self.current_pos.x() - offset - mag_size, self.current_pos.y() + offset),
                (self.current_pos.x() + offset, self.current_pos.y() - offset - mag_size),
                (self.current_pos.x() - offset - mag_size, self.current_pos.y() - offset - mag_size)
            ]
            
            target_rect = None
            for tx, ty in possible_points:
                rect = QRect(tx, ty, mag_size, mag_size)
                in_screen = rect.left() >= 0 and rect.top() >= 0 and \
                            rect.right() <= self.width() and rect.bottom() <= self.height()
                if in_screen and not rect.intersects(self.selection_rect):
                    target_rect = rect
                    break
            
            if target_rect is None:
                for tx, ty in possible_points:
                    rect = QRect(tx, ty, mag_size, mag_size)
                    if rect.left() >= 0 and rect.top() >= 0 and \
                       rect.right() <= self.width() and rect.bottom() <= self.height():
                        target_rect = rect
                        break
            
            if target_rect is None:
                target_rect = QRect(self.current_pos.x() + offset, self.current_pos.y() + offset, mag_size, mag_size)

            # Dibujar coordenadas encima de la lupa
            if show_coords:
                coord_text = f"X: {self.current_pos.x()} Y: {self.current_pos.y()}"
                painter.setFont(QFont("Arial", 7))
                fm = painter.fontMetrics()
                tw = fm.horizontalAdvance(coord_text)
                th = fm.height()
                
                # Posición: centrada horizontalmente sobre la lupa
                tx = target_rect.center().x() - tw // 2
                ty = target_rect.top() - 5
                
                # Dibujar fondo pequeño para legibilidad
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(0, 0, 0, 150))
                painter.drawRect(tx - 2, ty - th + 2, tw + 4, th)
                
                painter.setPen(QColor(255, 255, 255))
                painter.drawText(tx, ty, coord_text)

            src_w = mag_size // zoom
            src_h = mag_size // zoom
            src_rect = QRect(0, 0, src_w, src_h)
            src_rect.moveCenter(self.current_pos)
            
            physical_src_rect = QRect(src_rect.topLeft() * self.ratio, src_rect.size() * self.ratio)
            magnified_pixmap = self.full_screenshot.copy(physical_src_rect)
            
            painter.save()
            path = QPainterPath()
            path.addEllipse(target_rect.toRectF())
            painter.setClipPath(path)
            painter.drawPixmap(target_rect, magnified_pixmap)
            painter.restore()
            
            painter.setPen(QPen(Qt.GlobalColor.white, 1))
            painter.drawEllipse(target_rect)
            
            painter.setPen(QPen(QColor(128, 128, 128, 180), 1))
            center = target_rect.center()
            cross_size = 30
            painter.drawLine(center.x() - cross_size, center.y(), center.x() + cross_size, center.y())
            painter.drawLine(center.x(), center.y() - cross_size, center.x(), center.y() + cross_size)

        if not self.selection_rect.isNull():
            painter.drawPixmap(self.selection_rect, self.full_screenshot, 
                               QRect(self.selection_rect.topLeft() * self.ratio, 
                                     self.selection_rect.size() * self.ratio))
            pen = QPen(QColor(255, 255, 255), 1)
            painter.setPen(pen)
            painter.drawRect(self.selection_rect)
            
            painter.setBrush(QColor("#0078d7"))
            painter.setPen(QPen(Qt.GlobalColor.white, 1))
            h_size = 8
            pts = [self.selection_rect.topLeft(), self.selection_rect.topRight(), 
                   self.selection_rect.bottomLeft(), self.selection_rect.bottomRight()]
            for pt in pts:
                painter.drawRect(pt.x() - h_size//2, pt.y() - h_size//2, h_size, h_size)

            w_px = int(self.selection_rect.width() * self.ratio)
            h_px = int(self.selection_rect.height() * self.ratio)
            text = f"{w_px} × {h_px}"
            
            font = QFont("Arial", 8)
            painter.setFont(font)
            from PyQt6.QtGui import QFontMetrics
            fm = QFontMetrics(font)
            text_w = fm.horizontalAdvance(text)
            text_h = fm.height()
            
            padding = 4
            bg_w = text_w + padding * 2
            bg_h = text_h + padding * 2
            
            x_pos = self.selection_rect.left()
            if x_pos + bg_w > self.width():
                x_pos = self.width() - bg_w
                
            y_pos = self.selection_rect.top() - bg_h - 4
            if y_pos < 0:
                y_pos = self.selection_rect.bottom() + 4
                if y_pos + bg_h > self.height():
                    y_pos = self.selection_rect.bottom() - bg_h - 4

            bg_rect = QRect(x_pos, y_pos, bg_w, bg_h)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(0, 0, 0, 180))
            painter.drawRect(bg_rect)
            
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(bg_rect, Qt.AlignmentFlag.AlignCenter, text)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.current_pos = event.pos()
            
            if not self.selection_rect.isNull():
                handle = self.get_handle_at(self.current_pos)
                if handle:
                    self.mode = 'resizing'
                    self.active_handle = handle
                    self.is_selecting = True
                    self.panel.hide()
                    return
                elif self.selection_rect.contains(self.current_pos):
                    self.mode = 'moving'
                    self.drag_offset = self.current_pos - self.selection_rect.topLeft()
                    self.is_selecting = True
                    self.setCursor(Qt.CursorShape.ClosedHandCursor)
                    self.panel.hide()
                    return
                else:
                    self.selection_rect = QRect()
                    self.panel.hide()
            
            self.mode = 'new_selection'
            self.begin = event.pos()
            self.end = self.begin
            self.is_selecting = True
            self.panel.hide()
            self.update()
            
        elif event.button() == Qt.MouseButton.RightButton:
            self.close()

    def update_selection(self):
        if not self.is_selecting or self.mode != 'new_selection':
            return
            
        settings = QSettings("MiEmpresa", "Capturador")
        mod_sq_str = settings.value("mod_square", "Control")
        mod_pr_str = settings.value("mod_prop", "Shift")
        
        def str_to_mod(s):
            if s == "Shift": return Qt.KeyboardModifier.ShiftModifier
            if s == "Alt": return Qt.KeyboardModifier.AltModifier
            return Qt.KeyboardModifier.ControlModifier
            
        mod_sq = str_to_mod(mod_sq_str)
        mod_pr = str_to_mod(mod_pr_str)
        
        modifiers = QApplication.keyboardModifiers()
        
        dx = self.current_pos.x() - self.begin.x()
        dy = self.current_pos.y() - self.begin.y()
        
        if dx == 0 and dy == 0:
            self.end = self.current_pos
            self.selection_rect = QRect(self.begin, self.end).normalized()
            return

        sign_x = 1 if dx >= 0 else -1
        sign_y = 1 if dy >= 0 else -1
        
        if modifiers & mod_sq:
            side = max(abs(dx), abs(dy))
            self.end = QPoint(self.begin.x() + side * sign_x, self.begin.y() + side * sign_y)
        elif modifiers & mod_pr:
            prop_w = int(settings.value("prop_w", 16))
            prop_h = int(settings.value("prop_h", 9))
            
            abs_dx = abs(dx)
            abs_dy = abs(dy)
            
            if prop_w > 0 and prop_h > 0:
                if abs_dx / prop_w > abs_dy / prop_h:
                    h = int(abs_dx * prop_h / prop_w)
                    self.end = QPoint(int(self.begin.x() + dx), int(self.begin.y() + h * sign_y))
                else:
                    w = int(abs_dy * prop_w / prop_h)
                    self.end = QPoint(int(self.begin.x() + w * sign_x), int(self.begin.y() + dy))
            else:
                self.end = self.current_pos
        else:
            self.end = self.current_pos
            
        self.selection_rect = QRect(self.begin, self.end).normalized()

    def mouseMoveEvent(self, event):
        self.current_pos = event.pos()
        
        if self.is_selecting:
            if self.mode == 'new_selection':
                self.update_selection()
            elif self.mode == 'moving':
                new_top_left = self.current_pos - self.drag_offset
                new_rect = QRect(new_top_left, self.selection_rect.size())
                
                if new_rect.left() < 0: new_rect.moveLeft(0)
                if new_rect.top() < 0: new_rect.moveTop(0)
                if new_rect.right() > self.width(): new_rect.moveRight(self.width())
                if new_rect.bottom() > self.height(): new_rect.moveBottom(self.height())
                
                self.selection_rect = new_rect
            elif self.mode == 'resizing':
                r = self.selection_rect
                if self.active_handle == 'top_left':
                    r.setTopLeft(self.current_pos)
                elif self.active_handle == 'top_right':
                    r.setTopRight(self.current_pos)
                elif self.active_handle == 'bottom_left':
                    r.setBottomLeft(self.current_pos)
                elif self.active_handle == 'bottom_right':
                    r.setBottomRight(self.current_pos)
                self.selection_rect = r.normalized()
        else:
            if not self.selection_rect.isNull():
                handle = self.get_handle_at(self.current_pos)
                if handle in ['top_left', 'bottom_right']:
                    self.setCursor(Qt.CursorShape.SizeFDiagCursor)
                elif handle in ['top_right', 'bottom_left']:
                    self.setCursor(Qt.CursorShape.SizeBDiagCursor)
                elif self.selection_rect.contains(self.current_pos):
                    self.setCursor(Qt.CursorShape.OpenHandCursor)
                else:
                    self.setCursor(Qt.CursorShape.CrossCursor)
            else:
                self.setCursor(Qt.CursorShape.CrossCursor)
                
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_selecting = False
            if self.selection_rect.width() > 5 and self.selection_rect.height() > 5:
                if self.mode == 'moving':
                    self.setCursor(Qt.CursorShape.OpenHandCursor)
                self.show_export_menu(QCursor.pos())
            else:
                self.selection_rect = QRect()
                self.panel.hide()
                
            self.mode = None
            self.update()

    def keyPressEvent(self, event):
        key = event.key()
        
        if key == Qt.Key.Key_Escape:
            self.close()
            return

        # Shortcuts only work if there is an active selection and buttons are visible
        if not self.selection_rect.isNull() and self.panel.isVisible():
            if key in (Qt.Key.Key_G, Qt.Key.Key_S):
                self.on_save_clicked()
                return
            
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_C):
                self.on_copy_clicked()
                return

        # Update geometry live if modifier is pressed
        self.update_selection()
        self.update()

    def keyReleaseEvent(self, event):
        self.update_selection()
        self.update()

    def show_export_menu(self, pos):
        self.panel.adjustSize()
        x = self.selection_rect.right() - self.panel.width()
        y = self.selection_rect.bottom() + 10
        if y + self.panel.height() > self.height():
            y = self.selection_rect.top() - self.panel.height() - 10
            
        if x < 0: x = 0
            
        self.panel.move(x, y)
        self.panel.show()

    def on_copy_clicked(self):
        self.btn_copy.setStyleSheet("background-color: #0078d7; color: white; border-radius: 2px;")
        self.copy_to_clipboard()
        QTimer.singleShot(200, self.close)
        
    def on_auto_save_clicked(self):
        settings = QSettings("MiEmpresa", "Capturador")
        save_dir = settings.value("save_dir", os.path.expanduser('~'))
        fmt = settings.value("out_format", "PNG").lower()
        quality = int(settings.value("out_quality", 100))
        
        from datetime import datetime
        fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{fecha_str}_captura.{fmt}"
        path = os.path.join(save_dir, filename)
        
        os.makedirs(save_dir, exist_ok=True)
        
        if self.get_cropped_pixmap().save(path, format=fmt.upper(), quality=quality):
            print(f"Auto-guardado en {path}")
            self.btn_auto.setStyleSheet("background-color: #0078d7; color: white; border-radius: 2px;")
            QTimer.singleShot(200, self.close)
        else:
            print(f"Error al auto-guardar en {path}")

    def on_save_clicked(self):
        if self.save_to_file():
            self.btn_save.setStyleSheet("background-color: #0078d7; color: white; border-radius: 2px;")
            QTimer.singleShot(200, self.close)

    def get_cropped_pixmap(self):
        physical_rect = QRect(self.selection_rect.topLeft() * self.ratio, 
                              self.selection_rect.size() * self.ratio)
        return self.full_screenshot.copy(physical_rect)

    def copy_to_clipboard(self):
        QApplication.clipboard().setPixmap(self.get_cropped_pixmap())
        print("Copiado al portapapeles.")

    def save_to_file(self):
        settings = QSettings("MiEmpresa", "Capturador")
        fmt = settings.value("out_format", "PNG").lower()
        quality = int(settings.value("out_quality", 100))
        save_dir = settings.value("save_dir", os.path.expanduser('~'))
        
        from datetime import datetime
        fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = os.path.join(save_dir, f"{fecha_str}_captura.{fmt}")
        
        filter_str = "PNG (*.png);;JPG (*.jpg)" if fmt == "png" else "JPG (*.jpg);;PNG (*.png)"
        
        path, _ = QFileDialog.getSaveFileName(self, "Guardar imagen", default_name, filter_str)
        if path:
            self.get_cropped_pixmap().save(path, quality=quality)
            print(f"Guardado en {path}")
            return True
        return False

class ScreenshotApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.bridge = SignalBridge()
        self.bridge.trigger_capture.connect(self.start_capture)
        self.bridge.trigger_full.connect(self.capture_full_screen)
        
        self.setup_tray_icon()
        self.setup_hotkeys()
        
        print("Herramienta iniciada. Usa los atajos (por defecto 'print screen') o el icono en la bandeja.")

    def setup_hotkeys(self):
        keyboard.unhook_all()
        settings = QSettings("MiEmpresa", "Capturador")
        hk_zone = settings.value("hotkey_zone", "print screen")
        hk_full = settings.value("hotkey_full", "shift+print screen")
        
        try:
            keyboard.add_hotkey(hk_zone, lambda: self.bridge.trigger_capture.emit(), suppress=True)
        except Exception as e:
            print(f"Advertencia: No se pudo suprimir atajo zona '{hk_zone}': {e}. Se intentará sin supresión.")
            try:
                keyboard.add_hotkey(hk_zone, lambda: self.bridge.trigger_capture.emit())
            except Exception as e2:
                print(f"Error al registrar atajo zona: {e2}")

        try:
            keyboard.add_hotkey(hk_full, lambda: self.bridge.trigger_full.emit(), suppress=True)
        except Exception as e:
            print(f"Advertencia: No se pudo suprimir atajo full '{hk_full}': {e}. Se intentará sin supresión.")
            try:
                keyboard.add_hotkey(hk_full, lambda: self.bridge.trigger_full.emit())
            except Exception as e2:
                print(f"Error al registrar atajo full: {e2}")

    def create_placeholder_icon(self):
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#0078d7"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, 56, 56)
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Arial", 30, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "S")
        painter.end()
        return QIcon(pixmap)

    def get_app_icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), "captura.ico")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        else:
            return self.create_placeholder_icon()

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self.get_app_icon(), self.app)
        self.app.setWindowIcon(self.get_app_icon())
        self.tray_icon.setToolTip("Capturador de Pantalla Python")
        
        tray_menu = QMenu()
        capture_action = tray_menu.addAction("Nueva captura (Zona)")
        capture_action.triggered.connect(self.start_capture)
        
        full_capture_action = tray_menu.addAction("Capturar Pantalla Completa")
        full_capture_action.triggered.connect(self.capture_full_screen)
        
        tray_menu.addSeparator()
        
        settings_action = tray_menu.addAction("Configuración")
        settings_action.triggered.connect(self.open_settings)
        
        restart_action = tray_menu.addAction("Reiniciar")
        restart_action.triggered.connect(self.restart_app)
        
        tray_menu.addSeparator()
        quit_action = tray_menu.addAction("Salir")
        quit_action.triggered.connect(self.app.quit)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def open_settings(self):
        dialog = SettingsDialog()
        if dialog.exec():
            self.setup_hotkeys()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.start_capture()

    def capture_full_screen(self):
        screen = self.app.primaryScreen()
        full_screenshot = screen.grabWindow(0)
        
        self.overlay = CaptureOverlay(full_screenshot)
        self.overlay.selection_rect = self.overlay.rect()
        self.overlay.show_export_menu(QCursor.pos())

    def restart_app(self):
        print("Reiniciando herramienta...")
        os.execl(sys.executable, sys.executable, *sys.argv)

    def start_capture(self):
        if hasattr(self, 'overlay') and self.overlay:
            try:
                if self.overlay.isVisible():
                    return
            except RuntimeError:
                self.overlay = None

        screen = QApplication.screenAt(QCursor.pos())
        if not screen:
            screen = self.app.primaryScreen()
            
        full_screenshot = screen.grabWindow(0)
        self.overlay = CaptureOverlay(full_screenshot)
        self.overlay.show()

    def run(self):
        self.app.exec()

if __name__ == "__main__":
    app = ScreenshotApp()
    app.run()