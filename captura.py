import sys
import os
import winreg
import tempfile
import subprocess  
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (QApplication, QWidget, QMenu, QFileDialog, QSystemTrayIcon,
                             QHBoxLayout, QVBoxLayout, QPushButton, QDialog, QFormLayout,
                             QLineEdit, QComboBox, QSpinBox, QCheckBox, QLabel, QGroupBox,
                             QScrollArea) 
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap, QCursor, QIcon, QFont, QPainterPath
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal, QObject, QTimer, QSettings, QSize
import keyboard

# Iconos SVG para los botones de la barra de captura
ICON_AUTO = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><rect width="256" height="256" fill="none"/><path d="M128,189.09l54.72,33.65a8.4,8.4,0,0,0,12.52-9.17l-14.88-62.79,48.7-42A8.46,8.46,0,0,0,224.27,94L160.36,88.8,135.74,29.2a8.36,8.36,0,0,0-15.48,0L95.64,88.8,31.73,94a8.46,8.46,0,0,0-4.79,14.83l48.7,42L60.76,213.57a8.4,8.4,0,0,0,12.52,9.17Z" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="20"/></svg>'''

ICON_COPY = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><rect width="256" height="256" fill="none"/><rect x="40" y="72" width="144" height="144" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="20"/><polyline points="72 40 216 40 216 184" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="20"/></svg>'''

ICON_SAVE = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><rect width="256" height="256" fill="none"/><line x1="128" y1="144" x2="128" y2="32" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="20"/><polyline points="216 144 216 208 40 208 40 144" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="20"/><polyline points="168 104 128 144 88 104" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="20"/></svg>'''

ICON_OPEN = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><rect width="256" height="256" fill="none"/><path d="M92.69,216H48a8,8,0,0,1-8-8V163.31a8,8,0,0,1,2.34-5.65L165.66,34.34a8,8,0,0,1,11.31,0L221.66,79a8,8,0,0,1,0,11.31L98.34,213.66A8,8,0,0,1,92.69,216Z" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="20"/><line x1="136" y1="64" x2="192" y2="120" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="20"/><line x1="164" y1="92" x2="68" y2="188" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="20"/><line x1="95.49" y1="215.49" x2="40.51" y2="160.51" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="20"/></svg>'''

ICON_CANCEL = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><rect width="256" height="256" fill="none"/><line x1="200" y1="56" x2="56" y2="200" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="20"/><line x1="200" y1="200" x2="56" y2="56" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="20"/></svg>'''

class HotkeyRecorder(QWidget):
    key_signal = pyqtSignal(str)
    active_recorder = None

    def __init__(self, initial_value, parent=None):
        super().__init__(parent)
        self.is_recording = False
        self.hook_id = None
        self.recorded_keys = []
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.line_edit = QLineEdit(initial_value)
        self.line_edit.setReadOnly(True)
        self.btn = QPushButton("Grabar")
        self.btn.setFixedWidth(80)
        self.btn.setFocusPolicy(Qt.FocusPolicy.NoFocus) 
        self.btn.clicked.connect(self.toggle_recording)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.btn)
        
        self.key_signal.connect(self._add_key)

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        # Si hay otro grabador activo, lo detenemos
        if HotkeyRecorder.active_recorder and HotkeyRecorder.active_recorder != self:
            HotkeyRecorder.active_recorder.stop_recording()
            
        HotkeyRecorder.active_recorder = self
        self.is_recording = True
        self.btn.setText("Listo")
        self.btn.setStyleSheet("background-color: #ff4444; color: white; font-weight: bold;")
        self.line_edit.setText("")
        self.line_edit.setPlaceholderText("Presione teclas...")
        self.recorded_keys = []
        
        # Desactivar atajos globales para evitar que se disparen mientras grabamos
        keyboard.unhook_all()
        
        # Iniciamos el hook para capturar teclas
        self.hook_id = keyboard.hook(self._on_key_event)

    def stop_recording(self):
        if not self.is_recording:
            return
            
        self.is_recording = False
        self.btn.setText("Grabar")
        self.btn.setStyleSheet("")
        if self.hook_id:
            keyboard.unhook(self.hook_id)
            self.hook_id = None
        
        if HotkeyRecorder.active_recorder == self:
            HotkeyRecorder.active_recorder = None

    def _on_key_event(self, event):
        if event.event_type == keyboard.KEY_DOWN:
            # Emitimos la señal para actualizar la UI desde el hilo principal
            self.key_signal.emit(event.name)

    def _add_key(self, key_name):
        # Evitar capturar teclas de activación del botón si se usa el teclado para pulsar "Listo"
        if key_name in ("space", "enter") and not self.recorded_keys:
            return
            
        if key_name not in self.recorded_keys:
            self.recorded_keys.append(key_name)
            self.line_edit.setText("+".join(self.recorded_keys))

    def text(self):
        return self.line_edit.text()

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de Captura")
        self.settings = QSettings("kdgdkd", "Captura")
        self.init_ui()


    def check_modifier_conflicts(self):
        """Verifica si hay conflictos entre modificadores y actualiza la UI"""
        # Lista de todos los combos de modificadores
        mod_combos = [
            (self.mod_lock, "Bloquear proporción"),
            (self.mod_prop, "Forzar preferidas"),
            (self.mod_inv_prop, "Invertir preferidas")
        ]
        
        
        # Reiniciar todos los combos
        for combo, _ in mod_combos:
            combo.setStyleSheet("")
            combo.setToolTip("")
            # Restaurar todos los items
            for i in range(combo.count()):
                combo.model().item(i).setEnabled(True)
        
        # Verificar conflictos
        used_mods = {}
        for combo, name in mod_combos:
            mod = combo.currentText()
            if mod != "---":
                if mod in used_mods:
                    # Conflicto encontrado
                    conflicted_combo = used_mods[mod]
                    # Marcar ambos combos como conflictivos
                    combo.setStyleSheet("""
                        QComboBox {
                            color: #ff6b6b;
                            border: 1px solid #ff6b6b;
                            background-color: #3a2020;
                        }
                        QComboBox QAbstractItemView {
                            color: #ff6b6b;
                        }
                    """)
                    combo.setToolTip(f"¡Conflicto! El modificador '{mod}' ya está asignado a '{conflicted_combo}'")
                    
                    conflicted_combo.setStyleSheet("""
                        QComboBox {
                            color: #ff6b6b;
                            border: 1px solid #ff6b6b;
                            background-color: #3a2020;
                        }
                        QComboBox QAbstractItemView {
                            color: #ff6b6b;
                        }
                    """)
                    conflicted_combo.setToolTip(f"¡Conflicto! El modificador '{mod}' también está asignado a '{name}'")
                else:
                    used_mods[mod] = combo
        
        # Deshabilitar modificadores ya usados en otros combos
        for combo, _ in mod_combos:
            current_mod = combo.currentText()
            for other_combo, _ in mod_combos:
                if other_combo != combo:
                    other_mod = other_combo.currentText()
                    if other_mod != "---" and other_mod != current_mod:
                        # Deshabilitar el modificador usado en el otro combo
                        for i in range(combo.count()):
                            if combo.itemText(i) == other_mod:
                                combo.model().item(i).setEnabled(False)

    def init_ui(self):
        self.resize(480, 550)
        
        # Layout principal de la ventana
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # --- ÁREA DE SCROLL ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        # Contenedor interno que irá dentro del scroll
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8) # Espaciado más compacto entre secciones

        # ==========================================
        # SUBSECCIÓN 1: Atajos y Proporciones
        # ==========================================
        group_shortcuts = QGroupBox("Atajos")
        form_shortcuts = QFormLayout(group_shortcuts)
        form_shortcuts.setContentsMargins(10, 15, 10, 10)
        form_shortcuts.setVerticalSpacing(4) # Más compacto

        self.hk_zone = HotkeyRecorder(self.settings.value("hotkey_zone", "print screen"))
        self.hk_full = HotkeyRecorder(self.settings.value("hotkey_full", "shift+print screen"))
        form_shortcuts.addRow("Capturar Zona:", self.hk_zone)
        form_shortcuts.addRow("Capturar Pantalla:", self.hk_full)

        self.mod_lock = QComboBox()
        self.mod_lock.addItems(["---", "Ctrl", "Shift", "Alt"])
        self.mod_lock.setCurrentText(self.settings.value("mod_lock", "Ctrl"))
        form_shortcuts.addRow("Bloquear proporción:", self.mod_lock)

        self.mod_prop = QComboBox()
        self.mod_prop.addItems(["---", "Ctrl", "Shift", "Alt"])
        self.mod_prop.setCurrentText(self.settings.value("mod_prop", "Shift"))
        form_shortcuts.addRow("Forzar preferidas:", self.mod_prop)

        self.mod_inv_prop = QComboBox()
        self.mod_inv_prop.addItems(["---", "Ctrl", "Shift", "Alt"])
        self.mod_inv_prop.setCurrentText(self.settings.value("mod_inv_prop", "Alt"))
        form_shortcuts.addRow("Invertir preferidas:", self.mod_inv_prop)

        prop_layout = QHBoxLayout()
        self.prop_w = QSpinBox()
        self.prop_w.setRange(1, 9999)
        self.prop_w.setValue(int(self.settings.value("prop_w", 9)))
        self.prop_h = QSpinBox()
        self.prop_h.setRange(1, 9999)
        self.prop_h.setValue(int(self.settings.value("prop_h", 16)))
        prop_layout.addWidget(self.prop_w)
        prop_layout.addWidget(QLabel(":"))
        prop_layout.addWidget(self.prop_h)
        form_shortcuts.addRow("Proporciones preferidas:", prop_layout)
        
        # Conectar eventos para detectar conflictos de modificadores
        self.mod_lock.currentTextChanged.connect(self.check_modifier_conflicts)
        self.mod_prop.currentTextChanged.connect(self.check_modifier_conflicts)
        self.mod_inv_prop.currentTextChanged.connect(self.check_modifier_conflicts)
        
        layout.addWidget(group_shortcuts)

        # ==========================================
        # SUBSECCIÓN 2: Lupa y Coordenadas
        # ==========================================
        group_magnifier = QGroupBox("Lupa")
        form_magnifier = QFormLayout(group_magnifier)
        form_magnifier.setContentsMargins(10, 15, 10, 10)
        form_magnifier.setVerticalSpacing(4)

        self.zoom_enabled = QCheckBox()
        self.zoom_enabled.setChecked(self.settings.value("zoom_enabled", True, type=bool))
        form_magnifier.addRow("Activar Lupa:", self.zoom_enabled)

        self.default_zoom = QSpinBox()
        self.default_zoom.setRange(1, 20)
        self.default_zoom.setValue(int(self.settings.value("default_zoom", 4)))
        form_magnifier.addRow("Zoom:", self.default_zoom)

        self.default_mag_size = QSpinBox()
        self.default_mag_size.setRange(60, 400)
        self.default_mag_size.setSingleStep(10)
        self.default_mag_size.setValue(int(self.settings.value("default_mag_size", 120)))
        form_magnifier.addRow("Tamaño:", self.default_mag_size)

        self.show_coords = QCheckBox()
        self.show_coords.setChecked(self.settings.value("show_coords", True, type=bool))
        form_magnifier.addRow("Mostrar coordenadas:", self.show_coords)
        
        layout.addWidget(group_magnifier)

        # ==========================================
        # SUBSECCIÓN 3: Auto
        # ==========================================
        group_auto = QGroupBox("Auto")
        form_auto = QFormLayout(group_auto)
        form_auto.setContentsMargins(10, 15, 10, 10)
        form_auto.setVerticalSpacing(4)

        self.auto_action = QComboBox()
        self.auto_action.addItems(["Guardar", "Abrir", "Copiar", "---"])
        self.auto_action.setCurrentText(self.settings.value("auto_action", "Guardar"))
        form_auto.addRow("Acción 'Auto':", self.auto_action)

        loc_layout = QHBoxLayout()
        self.save_dir = QLineEdit(self.settings.value("save_dir", os.path.expanduser('~')))
        self.btn_browse = QPushButton("...")
        self.btn_browse.clicked.connect(self.browse_dir)
        loc_layout.addWidget(self.save_dir)
        loc_layout.addWidget(self.btn_browse)
        form_auto.addRow("Guardar en:", loc_layout)

        editor_layout = QHBoxLayout()
        self.editor_path = QLineEdit(self.settings.value("editor_path", ""))
        self.editor_path.setPlaceholderText("Ruta de editor (.exe) o URL (https://...)")
        self.btn_editor_browse = QPushButton("...")
        self.btn_editor_browse.clicked.connect(self.browse_editor)
        self.btn_paste_url = QPushButton("📋")
        self.btn_paste_url.setFixedWidth(30)
        self.btn_paste_url.setToolTip("Pegar URL del portapapeles")
        self.btn_paste_url.clicked.connect(self.paste_url)
        editor_layout.addWidget(self.editor_path)
        editor_layout.addWidget(self.btn_paste_url)
        editor_layout.addWidget(self.btn_editor_browse)
        form_auto.addRow("Abrir con:", editor_layout)

        # Lógica de activación/desactivación para Auto
        self.auto_action.currentTextChanged.connect(self.update_auto_state)
        self.update_auto_state(self.auto_action.currentText())

        layout.addWidget(group_auto)

        # ==========================================
        # SUBSECCIÓN 4: General
        # ==========================================
        group_general = QGroupBox("General")
        form_general = QFormLayout(group_general)
        form_general.setContentsMargins(10, 15, 10, 10)
        form_general.setVerticalSpacing(4)

        self.auto_start = QCheckBox()
        self.auto_start.setChecked(self.is_auto_start_enabled())
        form_general.addRow("Iniciar con Windows:", self.auto_start)

        self.out_format = QComboBox()
        self.out_format.addItems(["PNG", "JPG"])
        self.out_format.setCurrentText(self.settings.value("out_format", "PNG"))
        form_general.addRow("Formato de salida:", self.out_format)

        self.out_quality = QSpinBox()
        self.out_quality.setRange(1, 100)
        self.out_quality.setValue(int(self.settings.value("out_quality", 100)))
        form_general.addRow("Calidad JPG:", self.out_quality)

        # Lógica de activación/desactivación para calidad JPG
        self.out_format.currentTextChanged.connect(self.update_quality_state)
        self.update_quality_state(self.out_format.currentText())

        layout.addWidget(group_general)

        # ==========================================
        # ENSAMBLAJE FINAL
        # ==========================================
        # Añadimos el contenedor al scroll
        scroll_area.setWidget(container)
        
        # Añadimos el scroll al layout principal
        main_layout.addWidget(scroll_area)

        # Botón Guardar (Queda FUERA del scroll, siempre visible abajo)
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Guardar")
        btn_save.setMinimumWidth(100)
        btn_save.clicked.connect(self.save_settings)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        
        main_layout.addLayout(btn_layout)
        
        # Verificar conflictos iniciales
        self.check_modifier_conflicts()

    def update_quality_state(self, fmt):
        self.out_quality.setEnabled(fmt == "JPG")

    def browse_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta", self.save_dir.text())
        if dir_path:
            self.save_dir.setText(dir_path)




    def browse_editor(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar editor o URL", "", 
                                               "Ejecutables (*.exe);;Todos los archivos (*.*)")
        if path:
            self.editor_path.setText(path)

    def paste_url(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if text:
            from urllib.parse import urlparse
            parsed = urlparse(text)
            if parsed.scheme in ('http', 'https', 'ftp'):
                self.editor_path.setText(text)
            else:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self,
                    "No es una URL",
                    "El texto del portapapeles no parece ser una URL válida.",
                    QMessageBox.StandardButton.Ok
                )

    def update_auto_state(self, action):
        is_guardar = (action == "Guardar")
        self.save_dir.setEnabled(is_guardar)
        self.btn_browse.setEnabled(is_guardar)
        
        is_abrir = (action == "Abrir")
        self.editor_path.setEnabled(is_abrir)
        self.btn_editor_browse.setEnabled(is_abrir)

    def save_settings(self):
        # Verificar conflictos antes de guardar
        mods = {
            self.mod_lock.currentText(): "Bloquear proporción",
            self.mod_prop.currentText(): "Forzar preferidas", 
            self.mod_inv_prop.currentText(): "Invertir preferidas"
        }
        
        # Eliminar "---" del diccionario
        mods = {k: v for k, v in mods.items() if k != "---"}
        
        if len(mods) != len(set(mods.keys())):
            # Hay modificadores duplicados
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, 
                "Conflicto de modificadores",
                "Hay modificadores asignados a múltiples funciones.\n"
                "Por favor, asigna modificadores diferentes o usa '---' para desactivarlos.",
                QMessageBox.StandardButton.Ok
            )
            return
        
        # Validar editor_path
        editor_path = self.editor_path.text().strip()
        if editor_path:
            from urllib.parse import urlparse
            parsed = urlparse(editor_path)
            is_url = parsed.scheme in ('http', 'https', 'ftp')
            is_valid_path = os.path.exists(editor_path) or os.path.isabs(editor_path)
            
            if not (is_url or is_valid_path):
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self,
                    "Ruta no válida",
                    f"'{editor_path}' no es una ruta válida ni una URL.\n"
                    "Por favor, introduce una ruta de archivo existente o una URL válida.",
                    QMessageBox.StandardButton.Ok
                )
                return
        
        self.settings.setValue("hotkey_zone", self.hk_zone.text())
        self.settings.setValue("hotkey_full", self.hk_full.text())
        self.settings.setValue("mod_lock", self.mod_lock.currentText())
        self.settings.setValue("mod_prop", self.mod_prop.currentText())
        self.settings.setValue("mod_inv_prop", self.mod_inv_prop.currentText())
        self.settings.setValue("prop_w", self.prop_w.value())
        self.settings.setValue("prop_h", self.prop_h.value())
        self.settings.setValue("zoom_enabled", self.zoom_enabled.isChecked())
        self.settings.setValue("default_zoom", self.default_zoom.value())
        self.settings.setValue("default_mag_size", self.default_mag_size.value())
        self.settings.setValue("show_coords", self.show_coords.isChecked())
        self.settings.setValue("auto_action", self.auto_action.currentText())
        self.settings.setValue("editor_path", editor_path)
        self.settings.setValue("save_dir", self.save_dir.text())
        self.settings.setValue("out_format", self.out_format.currentText())
        self.settings.setValue("out_quality", self.out_quality.value())
        self.set_auto_start(self.auto_start.isChecked())
        self.accept()

    def get_run_key(self):
        return r"Software\Microsoft\Windows\CurrentVersion\Run"

    def is_auto_start_enabled(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.get_run_key(), 0, winreg.KEY_READ) as key:
                val, _ = winreg.QueryValueEx(key, "CapturaKdgdkd")
                return True
        except FileNotFoundError:
            return False

    def set_auto_start(self, enable):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.get_run_key(), 0, winreg.KEY_ALL_ACCESS)
            if enable:
                exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
                winreg.SetValueEx(key, "CapturaKdgdkd", 0, winreg.REG_SZ, f'"{exe_path}"')
            else:
                try:
                    winreg.DeleteValue(key, "CapturaKdgdkd")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Error configurando auto-inicio: {e}")

class SignalBridge(QObject):
    trigger_capture = pyqtSignal()
    trigger_full = pyqtSignal()

class CaptureOverlay(QWidget):

    FEEDBACK_STYLE = """
        QPushButton { 
            min-width: 30px;
            min-height: 30px;
            max-width: 30px;
            max-height: 30px;
            padding: 4px;
            background-color: #e0e0e0; 
            border: 1px solid #cccccc;
            border-radius: 4px;
        }
    """


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
        self.activateWindow()
        self.raise_()
        self.proporcion_cache = {}
        
        self.begin = QPoint()
        self.end = QPoint()
        self.current_pos = QPoint()
        self.is_selecting = False
        self.selection_rect = QRect()
        
        settings = QSettings("kdgdkd", "Captura")
        self.zoom = int(settings.value("default_zoom", 4))
        self.mag_size = int(settings.value("default_mag_size", 120))

        # Definir proporciones estándar
        self.proporciones_estandar = [
            (1, 1),   # Cuadrado
            (4, 3),   # Tradicional
            (3, 2),   # Fotografía
            (16, 9),  # Widescreen
            (16, 10), # Monitores
            (21, 9),  # Ultrawide
            (9, 16),  # Vertical
            (3, 1),   # Panorámico
            (1, 3),   # Vertical extremo
            (5, 4),   # Formato antiguo
            (3, 4),   # Vertical tradicional
            (2, 3),   # Vertical fotografía
        ]

        self.mode = 'new_selection' 
        self.active_handle = None
        self.drag_offset = QPoint()
        self.resize_anchor = None  # Vértice opuesto fijo durante el resize
        
        self.panel = QWidget(self)
        self.panel.setStyleSheet("""
            QWidget { 
                background-color: #2b2b2b; 
                border: 1px solid #1a1a1a; 
                border-radius: 6px; 
            }
            QPushButton { 
                min-width: 30px;
                min-height: 30px;
                max-width: 30px;
                max-height: 30px;
                padding: 4px; 
                border: 1px solid #555555; 
                background-color: #3a3a3a; 
                border-radius: 4px;
                color: #ffffff;
            }
            QPushButton:hover { 
                background-color: #e0e0e0; 
                border: 1px solid #cccccc;
                color: #1a1a1a;
            }
            QPushButton:pressed { 
                background-color: #c0c0c0; 
                border: 1px solid #aaaaaa;
                color: #1a1a1a;
            }
        """)
        
        layout = QHBoxLayout(self.panel)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)
        
        icon_size = 18

        # Iconos para estado normal (blanco sobre fondo oscuro)
        self.icon_auto_light = self.create_svg_icon(ICON_AUTO, "#ffffff", icon_size)
        self.icon_copy_light = self.create_svg_icon(ICON_COPY, "#ffffff", icon_size)
        self.icon_save_light = self.create_svg_icon(ICON_SAVE, "#ffffff", icon_size)
        self.icon_open_light = self.create_svg_icon(ICON_OPEN, "#ffffff", icon_size)
        self.icon_cancel_light = self.create_svg_icon(ICON_CANCEL, "#ffffff", icon_size)

        # Iconos para estado hover (oscuro sobre fondo claro)
        self.icon_auto_dark = self.create_svg_icon(ICON_AUTO, "#1a1a1a", icon_size)
        self.icon_copy_dark = self.create_svg_icon(ICON_COPY, "#1a1a1a", icon_size)
        self.icon_save_dark = self.create_svg_icon(ICON_SAVE, "#1a1a1a", icon_size)
        self.icon_open_dark = self.create_svg_icon(ICON_OPEN, "#1a1a1a", icon_size)
        self.icon_cancel_dark = self.create_svg_icon(ICON_CANCEL, "#1a1a1a", icon_size)


        self.btn_auto = QPushButton()
        self.install_icon_swap(self.btn_auto, self.icon_auto_light, self.icon_auto_dark)
        self.btn_auto.setIconSize(QSize(icon_size, icon_size))
        self.btn_auto.setToolTip("Auto")
        self.btn_auto.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_copy = QPushButton()
        self.install_icon_swap(self.btn_copy, self.icon_copy_light, self.icon_copy_dark)
        self.btn_copy.setIconSize(QSize(icon_size, icon_size))
        self.btn_copy.setToolTip("Copiar al portapapeles")
        self.btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_save = QPushButton()
        self.install_icon_swap(self.btn_save, self.icon_save_light, self.icon_save_dark)
        self.btn_save.setIconSize(QSize(icon_size, icon_size))
        self.btn_save.setToolTip("Guardar como...")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_open = QPushButton()
        self.install_icon_swap(self.btn_open, self.icon_open_light, self.icon_open_dark)
        self.btn_open.setIconSize(QSize(icon_size, icon_size))
        self.btn_open.setToolTip("Abrir con...")
        self.btn_open.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_cancel = QPushButton()
        self.install_icon_swap(self.btn_cancel, self.icon_cancel_light, self.icon_cancel_dark)
        self.btn_cancel.setIconSize(QSize(icon_size, icon_size))
        self.btn_cancel.setToolTip("Cancelar")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.btn_cancel.setStyleSheet("""
            QPushButton { 
                min-width: 30px;
                min-height: 30px;
                max-width: 30px;
                max-height: 30px;
                padding: 4px; 
                border: 1px solid #555555; 
                background-color: #3a3a3a; 
                border-radius: 4px;
                color: #ffffff;
            }
            QPushButton:hover { 
                background-color: #FF8C00; 
                color: #1a1a1a;
            }
            QPushButton:pressed { 
                background-color: #E07000; 
                color: #1a1a1a;
            }
        """)
        # Solo añadimos el botón Auto si no está desactivado ("---")
        if settings.value("auto_action", "Guardar") != "---":
            layout.addWidget(self.btn_auto)
            
        layout.addWidget(self.btn_copy)
        layout.addWidget(self.btn_save)
        layout.addWidget(self.btn_open)
        layout.addWidget(self.btn_cancel)
        
        self.btn_auto.clicked.connect(self.on_auto_clicked)  
        self.btn_copy.clicked.connect(self.on_copy_clicked)
        self.btn_save.clicked.connect(self.on_save_clicked)
        self.btn_open.clicked.connect(self.on_open_with_clicked)
        self.btn_cancel.clicked.connect(self.close)

        
        self.panel.hide()

    def install_icon_swap(self, button, icon_normal, icon_hover):
        """Instala event filter para cambiar iconos al hacer hover"""
        button.setIcon(icon_normal)
        button._icon_normal = icon_normal
        button._icon_hover = icon_hover
        button.enterEvent = lambda e: button.setIcon(button._icon_hover)
        button.leaveEvent = lambda e: button.setIcon(button._icon_normal)

    def create_svg_icon(self, svg_string, color="#ffffff", size=18):
        """Convierte un string SVG en un QIcon con un color específico"""
        # Reemplazar currentColor por el color deseado
        colored_svg = svg_string.replace('stroke="currentColor"', f'stroke="{color}"')
        colored_svg = colored_svg.replace('stroke="currentColor"', f'stroke="{color}"')
        
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        renderer = QSvgRenderer(bytes(colored_svg, 'utf-8'))
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return QIcon(pixmap)

    def obtener_proporcion_info(self, w, h):
        """
        Compara la proporción actual con las estándar y devuelve:
        - None si no coincide con ninguna
        - (proporcion, '') si es exacta
        - (proporcion, '+') si el lado corto es demasiado corto (rectángulo más alargado)
        - (proporcion, '-') si el lado corto es demasiado largo (rectángulo más cuadrado)
        """
        if w == 0 or h == 0:
            return None
        
        # Siempre trabajar con la proporción en formato landscape (w >= h) para comparar
        es_vertical = h > w
        if es_vertical:
            w, h = h, w
        
        proporcion_actual = w / h
        
        # Márgenes:
        # - Exacto: ±3 píxeles en la proporción
        # - Con signo: ±15% de la proporción estándar
        mejor_coincidencia = None
        mejor_diferencia = float('inf')
        
        for prop_w, prop_h in self.proporciones_estandar:
            # Normalizar la proporción estándar a landscape
            if prop_h > prop_w:
                prop_w_comp, prop_h_comp = prop_h, prop_w
            else:
                prop_w_comp, prop_h_comp = prop_w, prop_h
            
            proporcion_estandar = prop_w_comp / prop_h_comp
            
            # Calcular diferencia porcentual
            diferencia = abs(proporcion_actual - proporcion_estandar) / proporcion_estandar
            
            if diferencia < mejor_diferencia:
                mejor_diferencia = diferencia
                
                # Determinar el signo
                margen_exacto = 3 / max(w, h)  # 3 píxeles de tolerancia
                margen_amplio = 0.15  # 15% de tolerancia
                
                if diferencia <= margen_exacto:
                    signo = ''
                elif diferencia <= margen_amplio:
                    if proporcion_actual > proporcion_estandar:
                        signo = '+'  # Más alargado
                    else:
                        signo = '-'  # Más cuadrado
                else:
                    continue  # Fuera de margen, ignorar esta proporción
                
                # Usar la proporción original (respetando orientación)
                if es_vertical:
                    mejor_coincidencia = (f"{prop_h}:{prop_w}", signo)
                else:
                    mejor_coincidencia = (f"{prop_w}:{prop_h}", signo)
        
        return mejor_coincidencia
    
    def obtener_dimensiones_actuales(self):
        """Obtiene las dimensiones actuales de la selección o del arrastre"""
        if self.mode == 'new_selection' and self.is_selecting:
            return abs(self.current_pos.x() - self.begin.x()), abs(self.current_pos.y() - self.begin.y())
        elif self.mode == 'resizing' and self.is_selecting and self.resize_anchor is not None:
            return abs(self.current_pos.x() - self.resize_anchor.x()), abs(self.current_pos.y() - self.resize_anchor.y())
        elif not self.selection_rect.isNull():
            return self.selection_rect.width(), self.selection_rect.height()
        return 0, 0

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

        settings = QSettings("kdgdkd", "Captura")
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
            
            # Obtener información de proporción
            proporcion_info = self.obtener_proporcion_info(w_px, h_px)
            
            if proporcion_info:
                proporcion_texto, signo = proporcion_info
                text = f"{w_px} × {h_px}  |  {proporcion_texto}{signo}"
            else:
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
            
            # Si hay signo +/-, mostrarlo en un color diferente para destacar
            if proporcion_info and signo:
                # Dibujar el texto base en blanco
                painter.setPen(QColor(255, 255, 255))
                painter.drawText(bg_rect, Qt.AlignmentFlag.AlignCenter, text)
            else:
                painter.setPen(QColor(255, 255, 255))
                painter.drawText(bg_rect, Qt.AlignmentFlag.AlignCenter, text)

        if show_lupa and not self.current_pos.isNull():
            pen = QPen(QColor(255, 255, 255, 100), 1, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawLine(0, self.current_pos.y(), self.width(), self.current_pos.y())
            painter.drawLine(self.current_pos.x(), 0, self.current_pos.x(), self.height())

            mag_size = self.mag_size
            zoom = self.zoom
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

    def calcular_mcd(self, a, b):
        """Calcula el Máximo Común Divisor usando el algoritmo de Euclides"""
        a, b = abs(a), abs(b)
        while b:
            a, b = b, a % b
        return a
    
    def simplificar_proporcion(self, w, h):
        """Simplifica una proporción a sus términos más pequeños"""
        if w == 0 or h == 0:
            return None
        
        mcd = self.calcular_mcd(w, h)
        w_simplificado = w // mcd
        h_simplificado = h // mcd
        
        return w_simplificado, h_simplificado
    
    def buscar_proporcion_cercana(self, w, h, max_denominador=20):
        """Busca una proporción estándar cercana usando fracciones continuas (con caché)"""
        if w == 0 or h == 0:
            return None
        
        # Verificar caché
        cache_key = (w, h)
        if cache_key in self.proporcion_cache:
            return self.proporcion_cache[cache_key]
            
        # Calcular la proporción exacta simplificada
        proporcion_exacta = self.simplificar_proporcion(w, h)
        if not proporcion_exacta:
            return None
            
        w_exacto, h_exacto = proporcion_exacta
        
        # Si ya es una proporción simple (denominador pequeño), devolverla directamente
        if max(w_exacto, h_exacto) <= max_denominador:
            resultado = f"{w_exacto}:{h_exacto}", True
            self.proporcion_cache[cache_key] = resultado
            return resultado
            
        # Buscar la fracción más cercana con denominador limitado
        objetivo = w / h
        
        mejor_diferencia = float('inf')
        mejor_w = w_exacto
        mejor_h = h_exacto
        
        # Probar denominadores desde 1 hasta max_denominador
        for den in range(1, max_denominador + 1):
            # Calcular el numerador más cercano
            num = round(objetivo * den)
            if num < 1:
                num = 1
            
            diferencia = abs(objetivo - (num / den))
            
            if diferencia < mejor_diferencia:
                mejor_diferencia = diferencia
                mejor_w = num
                mejor_h = den
        
        # Determinar si es una aproximación
        es_exacto = abs(objetivo - (mejor_w / mejor_h)) < 0.01
        
        resultado = f"{mejor_w}:{mejor_h}", es_exacto
        self.proporcion_cache[cache_key] = resultado
        return resultado


    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.current_pos = event.pos()
            
            if not self.selection_rect.isNull():
                handle = self.get_handle_at(self.current_pos)
                if handle:
                    self.mode = 'resizing'
                    self.active_handle = handle
                    # Capturar el vértice opuesto AHORA y mantenerlo fijo durante todo el drag
                    self.resize_anchor = self._anchor_for_handle(handle)
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

    def _get_modifiers_config(self):
        """Devuelve (mod_lock, mod_pr, mod_inv_prop, prop_w, prop_h) leyendo settings."""
        settings = QSettings("kdgdkd", "Captura")
        mod_lock_str = settings.value("mod_lock", "Ctrl")
        mod_pr_str = settings.value("mod_prop", "Shift")
        mod_inv_pr_str = settings.value("mod_inv_prop", "Alt")

        def str_to_mod(s):
            if s == "Shift": return Qt.KeyboardModifier.ShiftModifier
            if s == "Alt": return Qt.KeyboardModifier.AltModifier
            if s == "Ctrl": return Qt.KeyboardModifier.ControlModifier
            return Qt.KeyboardModifier.NoModifier

        mod_lock = str_to_mod(mod_lock_str)
        mod_pr = str_to_mod(mod_pr_str)
        mod_inv_pr = str_to_mod(mod_inv_pr_str)
        prop_w = int(settings.value("prop_w", 9))
        prop_h = int(settings.value("prop_h", 16))
        return mod_lock, mod_pr, mod_inv_pr, prop_w, prop_h

    def _constrain_endpoint(self, anchor, cursor, modifiers):
        """
        Dada un ancla fija y la posición del cursor, devuelve el punto opuesto
        del rectángulo aplicando los modificadores activos.
        """
        mod_lock, mod_pr, mod_inv_pr, prop_w, prop_h = self._get_modifiers_config()

        dx = cursor.x() - anchor.x()
        dy = cursor.y() - anchor.y()

        if dx == 0 and dy == 0:
            return QPoint(cursor)

        sign_x = 1 if dx >= 0 else -1
        sign_y = 1 if dy >= 0 else -1
        abs_dx = abs(dx)
        abs_dy = abs(dy)

        # Bloquear a la proporción mostrada (Ctrl por defecto)
        if modifiers & mod_lock:
            # Obtener la proporción actual mostrada en la UI
            proporcion_info = self.obtener_proporcion_actual()
            
            if proporcion_info:
                proporcion_texto, _ = proporcion_info
                
                # Parsear la proporción objetivo
                partes = proporcion_texto.split(':')
                if len(partes) == 2:
                    target_w = float(partes[0])
                    target_h = float(partes[1])
                    target_ratio = target_w / target_h
                    
                    # El cursor define uno de los lados del rectángulo
                    # Calculamos dos posibles alturas y dos posibles anchos
                    
                    # Opción 1: cursor define el borde horizontal (misma Y, X ajustada por proporción)
                    # Opción 2: cursor define el borde vertical (misma X, Y ajustada por proporción)
                    
                    # Para opción 1: altura = |dy|, ancho = altura * ratio
                    # Para opción 2: ancho = |dx|, altura = ancho / ratio
                    
                    # Elegimos la opción que hace que el rectángulo sea más grande
                    # (el cursor está en el borde que está más lejos del ancla)
                    
                    option1_width = abs_dy * target_ratio
                    option2_height = abs_dx / target_ratio
                    
                    # El cursor define el borde que maximiza el área del rectángulo
                    if option1_width * abs_dy >= abs_dx * option2_height:
                        # El cursor está en el borde horizontal
                        if option1_width >= abs_dx:
                            # El cursor está en la esquina (borde horizontal y vertical derecho)
                            return QPoint(anchor.x() + int(option1_width) * sign_x, cursor.y())
                        else:
                            # El cursor está en el borde vertical
                            return QPoint(cursor.x(), anchor.y() + int(abs_dx / target_ratio) * sign_y)
                    else:
                        # El cursor está en el borde vertical
                        if option2_height >= abs_dy:
                            # El cursor está en la esquina
                            return QPoint(cursor.x(), anchor.y() + int(option2_height) * sign_y)
                        else:
                            # El cursor está en el borde horizontal
                            return QPoint(anchor.x() + int(abs_dy * target_ratio) * sign_x, cursor.y())
            
            # Si no hay proporción mostrada, selección libre
            return QPoint(cursor)
        
        # Bloquear a proporción preferida (Shift por defecto)
        is_inverted = (modifiers & mod_inv_pr)
        is_prop_active = (modifiers & mod_pr) or is_inverted
        
        if is_prop_active and prop_w > 0 and prop_h > 0:
            target_w = prop_h if is_inverted else prop_w
            target_h = prop_w if is_inverted else prop_h
            
            if abs_dx / target_w > abs_dy / target_h:
                h = int(abs_dx * target_h / target_w)
                return QPoint(anchor.x() + dx, anchor.y() + h * sign_y)
            else:
                w = int(abs_dy * target_w / target_h)
                return QPoint(anchor.x() + w * sign_x, anchor.y() + dy)

        return QPoint(cursor)
    
    def obtener_proporcion_actual(self):
        """Obtiene la proporción que se está mostrando actualmente en la UI"""
        if self.selection_rect.isNull():
            return None
            
        w_px = int(self.selection_rect.width() * self.ratio)
        h_px = int(self.selection_rect.height() * self.ratio)
        
        return self.obtener_proporcion_info(w_px, h_px)

    def _anchor_for_handle(self, handle):
        """Vértice opuesto al handle activo (sirve de ancla durante el resize)."""
        r = self.selection_rect
        if handle == 'top_left':
            return r.bottomRight()
        if handle == 'top_right':
            return r.bottomLeft()
        if handle == 'bottom_left':
            return r.topRight()
        if handle == 'bottom_right':
            return r.topLeft()
        return None

    def update_selection(self):
        if not self.is_selecting or self.mode != 'new_selection':
            return

        modifiers = QApplication.keyboardModifiers()
        self.end = self._constrain_endpoint(self.begin, self.current_pos, modifiers)
        self.selection_rect = QRect(self.begin, self.end).normalized()

    def update_resize(self):
        """Recalcula selection_rect mientras se redimensiona, aplicando modificadores."""
        if not self.is_selecting or self.mode != 'resizing' or self.resize_anchor is None:
            return

        modifiers = QApplication.keyboardModifiers()
        new_corner = self._constrain_endpoint(self.resize_anchor, self.current_pos, modifiers)
        self.selection_rect = QRect(self.resize_anchor, new_corner).normalized()

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
                self.update_resize()
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
            self.active_handle = None
            self.resize_anchor = None
            self.update()

    def wheelEvent(self, event):
        angle = event.angleDelta().y()
        modifiers = QApplication.keyboardModifiers()
        
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            if angle > 0:
                self.mag_size = min(400, self.mag_size + 10)
            elif angle < 0:
                self.mag_size = max(60, self.mag_size - 10)
        else:
            if angle > 0:
                self.zoom = min(20, self.zoom + 1)
            elif angle < 0:
                self.zoom = max(1, self.zoom - 1)
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

        # Actualizar geometría cuando se presiona un modificador
        modifiers = QApplication.keyboardModifiers()
        mod_lock, _, _, _, _ = self._get_modifiers_config()
        
        # Si se presionó el modificador de bloqueo, ajustar a la proporción mostrada
        if modifiers & mod_lock and self.is_selecting:
            if self.mode == 'new_selection':
                self.update_selection()
            elif self.mode == 'resizing':
                self.update_resize()
        
        self.update()

    def keyReleaseEvent(self, event):
        # Actualizar geometría cuando se suelta un modificador
        if self.is_selecting:
            if self.mode == 'new_selection':
                self.update_selection()
            elif self.mode == 'resizing':
                self.update_resize()
        self.update()

    def show_export_menu(self, pos):
        self.panel.adjustSize()
        # Intentar ponerlo abajo a la derecha de la selección
        x = self.selection_rect.right() - self.panel.width()
        y = self.selection_rect.bottom() + 10
        
        # Ajustar si se sale por abajo
        if y + self.panel.height() > self.height():
            # Probar arriba de la selección
            y = self.selection_rect.top() - self.panel.height() - 10
            
        # Si aún se sale (por arriba o por abajo), meterlo dentro de los márgenes
        if y < 0:
            y = 10
        if y + self.panel.height() > self.height():
            y = self.height() - self.panel.height() - 10
            
        if x < 0: x = 10
        if x + self.panel.width() > self.width():
            x = self.width() - self.panel.width() - 10
            
        self.panel.move(x, y)
        self.panel.show()

    def on_copy_clicked(self):
        self.btn_copy.setStyleSheet(self.FEEDBACK_STYLE)
        self.copy_to_clipboard()
        QTimer.singleShot(200, self.close)
        
    def on_auto_clicked(self):
        settings = QSettings("kdgdkd", "Captura")
        action = settings.value("auto_action", "Guardar")
        
        if action == "Copiar":
            self.btn_auto.setStyleSheet(self.FEEDBACK_STYLE)
            self.copy_to_clipboard()
            QTimer.singleShot(200, self.close)
            
        elif action == "Guardar":
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
                self.btn_auto.setStyleSheet(self.FEEDBACK_STYLE)
                QTimer.singleShot(200, self.close)
            else:
                print(f"Error al auto-guardar en {path}")
                
        elif action == "Abrir":
            editor_path = settings.value("editor_path", "")
            
            # Verificar si es una URL
            from urllib.parse import urlparse
            parsed = urlparse(editor_path) if editor_path else None
            is_url = parsed and parsed.scheme in ('http', 'https', 'ftp')
            
            if is_url:
                # Si es una URL, copiar al portapapeles y luego abrir el navegador
                import webbrowser
                self.copy_to_clipboard()
                print("Imagen copiada al portapapeles. Abriendo URL...")
                self.btn_auto.setStyleSheet(self.FEEDBACK_STYLE)
                webbrowser.open(editor_path)
                QTimer.singleShot(200, self.close)
                
            elif editor_path and os.path.exists(editor_path):
                # Si es una ruta de archivo válida, guardar temporal y abrir con editor
                fd, temp_path = tempfile.mkstemp(suffix=".png")
                os.close(fd)
                
                if self.get_cropped_pixmap().save(temp_path, format="PNG"):
                    self.btn_auto.setStyleSheet(self.FEEDBACK_STYLE)
                    subprocess.Popen([editor_path, temp_path])
                    QTimer.singleShot(200, self.close)
                else:
                    print("Error al guardar el archivo temporal para abrir la imagen.")
            else:
                # Si no hay editor configurado o la ruta no es válida, usar el diálogo nativo
                fd, temp_path = tempfile.mkstemp(suffix=".png")
                os.close(fd)
                
                if self.get_cropped_pixmap().save(temp_path, format="PNG"):
                    self.btn_auto.setStyleSheet(self.FEEDBACK_STYLE)
                    if os.name == 'nt':
                        subprocess.Popen(['rundll32.exe', 'shell32.dll,OpenAs_RunDLL', temp_path])
                    QTimer.singleShot(200, self.close)
                else:
                    print("Error al guardar el archivo temporal para abrir la imagen.")


    def on_save_clicked(self):
        if self.save_to_file():
            self.btn_save.setStyleSheet(self.FEEDBACK_STYLE)
            QTimer.singleShot(200, self.close)


    def on_open_with_clicked(self):
        settings = QSettings("kdgdkd", "Captura")
        editor_path = settings.value("editor_path", "")
        
        # Verificar si es una URL
        from urllib.parse import urlparse
        parsed = urlparse(editor_path) if editor_path else None
        is_url = parsed and parsed.scheme in ('http', 'https', 'ftp')
        
        if is_url:
            # Si es una URL, copiar al portapapeles y luego abrir el navegador
            import webbrowser
            self.copy_to_clipboard()
            print("Imagen copiada al portapapeles. Abriendo URL...")
            self.btn_open.setStyleSheet(self.FEEDBACK_STYLE)
            webbrowser.open(editor_path)
            QTimer.singleShot(200, self.close)
        else:
            # Comportamiento original para archivos locales
            fd, temp_path = tempfile.mkstemp(suffix=".png")
            os.close(fd)
            
            if self.get_cropped_pixmap().save(temp_path, format="PNG"):
                self.btn_open.setStyleSheet(self.FEEDBACK_STYLE)
                
                if os.name == 'nt':
                    subprocess.Popen(['rundll32.exe', 'shell32.dll,OpenAs_RunDLL', temp_path])
                
                QTimer.singleShot(200, self.close)
            else:
                print("Error al guardar el archivo temporal para abrir la imagen.")

    def get_cropped_pixmap(self):
        physical_rect = QRect(self.selection_rect.topLeft() * self.ratio, 
                              self.selection_rect.size() * self.ratio)
        return self.full_screenshot.copy(physical_rect)

    def copy_to_clipboard(self):
        QApplication.clipboard().setPixmap(self.get_cropped_pixmap())
        print("Copiado al portapapeles.")

    def save_to_file(self):
        settings = QSettings("kdgdkd", "Captura")
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
        if os.name == 'nt':
            import ctypes
            try:
                myappid = 'kdgdkd.captura.1.0' # ID arbitrario para la app
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except Exception:
                pass

        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setWindowIcon(self.get_app_icon())
        
        self.bridge = SignalBridge()
        self.bridge.trigger_capture.connect(self.start_capture)
        self.bridge.trigger_full.connect(self.capture_full_screen)
        
        self.settings_dialog = None
        
        self.setup_tray_icon()
        self.setup_hotkeys()
        
        print("Herramienta iniciada. Usa los atajos (por defecto 'print screen') o el icono en la bandeja.")

    def setup_hotkeys(self):
        keyboard.unhook_all()
        settings = QSettings("kdgdkd", "Captura")
        hk_zone = settings.value("hotkey_zone", "print screen")
        hk_full = settings.value("hotkey_full", "shift+print screen")

        # Si ambos atajos comparten la misma tecla base (ej. "print screen" y
        # "shift+print screen"), los gestionamos con un único hook manual.
        def parse_combo(combo):
            parts = [p.strip().lower() for p in combo.split('+') if p.strip()]
            mods = set(p for p in parts if p in ('ctrl', 'control', 'shift', 'alt', 'win', 'cmd'))
            # normalizamos
            mods = {'ctrl' if m == 'control' else m for m in mods}
            base = next((p for p in parts if p not in ('ctrl', 'control', 'shift', 'alt', 'win', 'cmd')), None)
            return base, mods

        base_zone, mods_zone = parse_combo(hk_zone)
        base_full, mods_full = parse_combo(hk_full)

        if base_zone and base_zone == base_full and mods_zone != mods_full:
            # Conflicto: misma tecla base, distinta combinación de modificadores.
            # Usamos un único hook que decide cuál disparar según el estado de modificadores.
            def on_base_key(event):
                if event.event_type != keyboard.KEY_DOWN:
                    return
                pressed_mods = set()
                if keyboard.is_pressed('shift'): pressed_mods.add('shift')
                if keyboard.is_pressed('ctrl'):  pressed_mods.add('ctrl')
                if keyboard.is_pressed('alt'):   pressed_mods.add('alt')
                if pressed_mods == mods_full:
                    self.bridge.trigger_full.emit()
                elif pressed_mods == mods_zone:
                    self.bridge.trigger_capture.emit()
            try:
                keyboard.on_press_key(base_zone, on_base_key, suppress=True)
            except Exception as e:
                print(f"Advertencia: No se pudo suprimir '{base_zone}': {e}. Se intenta sin supresión.")
                try:
                    keyboard.on_press_key(base_zone, on_base_key)
                except Exception as e2:
                    print(f"Error al registrar hook para '{base_zone}': {e2}")
            return

        # Caso normal: atajos independientes.
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
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_path, "captura.ico")
        
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        else:
            return self.create_placeholder_icon()

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self.get_app_icon(), self.app)
        self.app.setWindowIcon(self.get_app_icon())
        self.tray_icon.setToolTip("Captura")
        
        tray_menu = QMenu()
        capture_action = tray_menu.addAction("Nueva captura")
        capture_action.triggered.connect(self.start_capture)
        
        full_capture_action = tray_menu.addAction("Capturar Pantalla")
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
        if self.settings_dialog is not None:
            self.settings_dialog.activateWindow()
            self.settings_dialog.raise_()
            return
            
        self.settings_dialog = SettingsDialog()
        # Forzamos el icono explícitamente en la ventana del diálogo
        self.settings_dialog.setWindowIcon(self.get_app_icon())
        self.settings_dialog.finished.connect(self._handle_settings_finished)
        self.settings_dialog.show()

    def _handle_settings_finished(self):
        self.setup_hotkeys()
        self.settings_dialog = None

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.start_capture()

    def capture_full_screen(self):
        screen = QApplication.screenAt(QCursor.pos())
        if not screen:
            screen = self.app.primaryScreen()
            
        full_screenshot = screen.grabWindow(0)
        self.overlay = CaptureOverlay(full_screenshot)
        
        # Calculamos el tamaño lógico basado en el ratio de la captura
        ratio = full_screenshot.devicePixelRatio()
        logical_w = int(full_screenshot.width() / ratio)
        logical_h = int(full_screenshot.height() / ratio)
        self.overlay.selection_rect = QRect(0, 0, logical_w, logical_h)
        
        self.overlay.show()
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
