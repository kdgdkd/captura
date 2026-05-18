"""
Centralized theme system for Captura.
Supports Auto (system detection), Light, and Dark themes.
"""
import winreg
from enum import Enum
from typing import Optional
from PyQt6.QtGui import QColor


class Theme(Enum):
    AUTO = "auto"
    LIGHT = "light"
    DARK = "dark"


class ColorPalette:
    """Base palette – all colour tokens that vary between themes."""
    # Panel / main UI background
    panel_bg: str = ""
    panel_border: str = ""

    # Toolbar buttons (copy, save, open)
    btn_bg: str = ""
    btn_border: str = ""
    btn_text: str = ""
    btn_hover_bg: str = ""
    btn_hover_border: str = ""
    btn_hover_text: str = ""
    btn_pressed_bg: str = ""
    btn_pressed_border: str = ""
    btn_pressed_text: str = ""

    # Cancel button (different hover colour)
    cancel_btn_bg: str = ""
    cancel_btn_border: str = ""
    cancel_btn_text: str = ""
    cancel_btn_hover_bg: str = ""
    cancel_btn_hover_text: str = ""
    cancel_btn_pressed_bg: str = ""
    cancel_btn_pressed_text: str = ""

    # Feedback flash when a button action completes
    feedback_btn_bg: str = ""
    feedback_btn_border: str = ""

    # Hotkey recording button
    recording_btn_bg: str = ""
    recording_btn_text: str = ""

    # SVG icon fill colours (normal / hover)
    icon_light: str = ""
    icon_dark: str = ""

    # Settings conflict indicator
    conflict_text: str = ""
    conflict_border: str = ""
    conflict_bg: str = ""

    # ---- paintEvent colours ----

    # Semi-transparent overlay that dims the screen
    overlay_dim: QColor = QColor(0, 0, 0, 120)
    # Selection rectangle border
    selection_border: QColor = QColor(255, 255, 255)
    # Corner handle fill
    selection_handle: str = "#0078d7"
    # Dimension label (width x height) background / text
    dimension_label_bg: QColor = QColor(0, 0, 0, 180)
    dimension_label_text: QColor = QColor(255, 255, 255)
    # Modifier chips during drag
    modifier_chip_blocker: QColor = QColor(0, 120, 215, 200)
    modifier_chip_inverted: QColor = QColor(160, 80, 200, 200)
    modifier_chip_forced: QColor = QColor(0, 160, 80, 200)
    chip_text: QColor = QColor(255, 255, 255)
    # Crosshair lines
    crosshair_lines: QColor = QColor(255, 255, 255, 100)
    # Coordinate label background / text
    coord_text_bg: QColor = QColor(0, 0, 0, 150)
    coord_text: QColor = QColor(255, 255, 255)
    # Magnifier crosshair (inner)
    magnifier_crosshair: QColor = QColor(128, 128, 128, 180)
    magnifier_border: str = "white"

    # Tray / placeholder icon
    placeholder_bg: str = "#0078d7"
    placeholder_text: str = "white"


class DarkPalette(ColorPalette):
    panel_bg = "#2b2b2b"
    panel_border = "#1a1a1a"

    btn_bg = "#3a3a3a"
    btn_border = "#555555"
    btn_text = "#ffffff"
    btn_hover_bg = "#e0e0e0"
    btn_hover_border = "#cccccc"
    btn_hover_text = "#1a1a1a"
    btn_pressed_bg = "#c0c0c0"
    btn_pressed_border = "#aaaaaa"
    btn_pressed_text = "#1a1a1a"

    cancel_btn_bg = "#3a3a3a"
    cancel_btn_border = "#555555"
    cancel_btn_text = "#ffffff"
    cancel_btn_hover_bg = "#FF8C00"
    cancel_btn_hover_text = "#1a1a1a"
    cancel_btn_pressed_bg = "#E07000"
    cancel_btn_pressed_text = "#1a1a1a"

    feedback_btn_bg = "#e0e0e0"
    feedback_btn_border = "#cccccc"

    recording_btn_bg = "#ff4444"
    recording_btn_text = "white"

    icon_light = "#ffffff"
    icon_dark = "#1a1a1a"

    conflict_text = "#ff6b6b"
    conflict_border = "#ff6b6b"
    conflict_bg = "#3a2020"


class LightPalette(ColorPalette):
    panel_bg = "#f0f0f0"
    panel_border = "#cccccc"

    btn_bg = "#ffffff"
    btn_border = "#bbbbbb"
    btn_text = "#1a1a1a"
    btn_hover_bg = "#0078d7"
    btn_hover_border = "#005a9e"
    btn_hover_text = "#ffffff"
    btn_pressed_bg = "#005a9e"
    btn_pressed_border = "#004578"
    btn_pressed_text = "#ffffff"

    cancel_btn_bg = "#ffffff"
    cancel_btn_border = "#bbbbbb"
    cancel_btn_text = "#1a1a1a"
    cancel_btn_hover_bg = "#FF8C00"
    cancel_btn_hover_text = "#ffffff"
    cancel_btn_pressed_bg = "#E07000"
    cancel_btn_pressed_text = "#ffffff"

    feedback_btn_bg = "#0078d7"
    feedback_btn_border = "#005a9e"

    recording_btn_bg = "#ff4444"
    recording_btn_text = "white"

    icon_light = "#1a1a1a"
    icon_dark = "#ffffff"

    conflict_text = "#cc0000"
    conflict_border = "#cc0000"
    conflict_bg = "#ffe0e0"

    overlay_dim = QColor(0, 0, 0, 80)
    selection_border = QColor(0, 0, 0)
    dimension_label_bg = QColor(255, 255, 255, 200)
    dimension_label_text = QColor(0, 0, 0)
    crosshair_lines = QColor(128, 128, 128, 100)
    coord_text_bg = QColor(255, 255, 255, 200)
    coord_text = QColor(0, 0, 0)
    magnifier_border = "black"


# ---------------------------------------------------------------------------
# Palette resolution
# ---------------------------------------------------------------------------

def _detect_windows_theme() -> Theme:
    """Query Windows registry for the current app theme preference."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            0, winreg.KEY_READ,
        )
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return Theme.LIGHT if value == 1 else Theme.DARK
    except (FileNotFoundError, OSError):
        return Theme.DARK


def _palette_for(theme: Theme) -> ColorPalette:
    if theme == Theme.LIGHT:
        return LightPalette()
    return DarkPalette()


class ThemeManager:
    """Singleton that holds the current theme preference and resolves the
    active palette on demand.

    Usage::

        ThemeManager.instance().set_theme("auto")   # or "light" / "dark"
        p = ThemeManager.instance().palette          # -> ColorPalette
    """

    _instance: Optional["ThemeManager"] = None

    def __init__(self):
        self._theme_setting: str = "auto"
        self._cached: Optional[ColorPalette] = None

    @classmethod
    def instance(cls) -> "ThemeManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_theme(self, theme_str: str):
        """Set the raw preference string and invalidate the cache."""
        self._theme_setting = theme_str
        self._cached = None

    @property
    def palette(self) -> ColorPalette:
        """Resolve (with caching) and return the active palette."""
        if self._cached is None:
            self._cached = self._resolve()
        return self._cached

    @property
    def resolved_theme(self) -> Theme:
        """The actually-active theme after auto-detection."""
        if self._cached is None:
            self._cached = self._resolve()
        if isinstance(self._cached, LightPalette):
            return Theme.LIGHT
        return Theme.DARK

    def _resolve(self) -> ColorPalette:
        if self._theme_setting == "light":
            return LightPalette()
        if self._theme_setting == "dark":
            return DarkPalette()
        # auto
        return _palette_for(_detect_windows_theme())


# ---------------------------------------------------------------------------
# QSS generators – build stylesheets from a palette instance
# ---------------------------------------------------------------------------

def panel_qss(p: ColorPalette) -> str:
    """Main capture-bar panel + its tool buttons."""
    return f"""
        QWidget {{
            background-color: {p.panel_bg};
            border: 1px solid {p.panel_border};
            border-radius: 6px;
        }}
        QPushButton {{
            min-width: 30px;
            min-height: 30px;
            max-width: 30px;
            max-height: 30px;
            padding: 4px;
            border: 1px solid {p.btn_border};
            background-color: {p.btn_bg};
            border-radius: 4px;
            color: {p.btn_text};
        }}
        QPushButton:hover {{
            background-color: {p.btn_hover_bg};
            border: 1px solid {p.btn_hover_border};
            color: {p.btn_hover_text};
        }}
        QPushButton:pressed {{
            background-color: {p.btn_pressed_bg};
            border: 1px solid {p.btn_pressed_border};
            color: {p.btn_pressed_text};
        }}
    """


def cancel_btn_qss(p: ColorPalette) -> str:
    """Cancel button (orange hover, different from normal toolbar buttons)."""
    return f"""
        QPushButton {{
            min-width: 30px;
            min-height: 30px;
            max-width: 30px;
            max-height: 30px;
            padding: 4px;
            border: 1px solid {p.cancel_btn_border};
            background-color: {p.cancel_btn_bg};
            border-radius: 4px;
            color: {p.cancel_btn_text};
        }}
        QPushButton:hover {{
            background-color: {p.cancel_btn_hover_bg};
            color: {p.cancel_btn_hover_text};
        }}
        QPushButton:pressed {{
            background-color: {p.cancel_btn_pressed_bg};
            color: {p.cancel_btn_pressed_text};
        }}
    """


def feedback_qss(p: ColorPalette) -> str:
    """Brief flash style when a button action completes."""
    return f"""
        QPushButton {{
            min-width: 30px;
            min-height: 30px;
            max-width: 30px;
            max-height: 30px;
            padding: 4px;
            background-color: {p.feedback_btn_bg};
            border: 1px solid {p.feedback_btn_border};
            border-radius: 4px;
        }}
    """


def conflict_qss(p: ColorPalette) -> str:
    """Red conflict indicator for modifier combos in settings."""
    return f"""
        QComboBox {{
            color: {p.conflict_text};
            border: 1px solid {p.conflict_border};
            background-color: {p.conflict_bg};
        }}
        QComboBox QAbstractItemView {{
            color: {p.conflict_text};
        }}
    """
