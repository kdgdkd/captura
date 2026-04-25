# captura.py — Screenshot Tool

A lightweight Python screenshot utility that runs in the system tray. Supports region selection, full-screen capture, magnifier, configurable hotkeys, and multiple export options.

---

## Installation

### 1. Create a project folder

Create a folder on your machine where you want to keep the tool, for example:

```bash
mkdir captura
cd captura
```

### 2. Download the files

On this GitHub page, download `captura.py` by clicking the file and then the **Download raw file** button (download icon, top right of the code viewer). Save the file inside the folder you just created.

Alternatively, clone the repository directly:

```bash
git clone https://github.com/your-user/your-repo.git captura
cd captura
```

### 3. Prerequisites

- Python 3.8+
- PyQt6
- keyboard

### 4. Install dependencies

With your terminal inside the project folder:

```bash
pip install PyQt6 keyboard
```

> **Note (Linux):** The `keyboard` library requires root privileges or special permissions to listen to global hotkeys. Run with `sudo`, or configure `/etc/udev/rules.d` to grant your user access to `/dev/input` devices.


---

## Running

From inside the project folder:

```bash
python captura.py
```

The app starts silently — no window appears. Look for the icon in the system tray (a blue circle with an "S"). The app keeps running in the background until you quit it from the tray menu.

### Optional: custom tray icon

Place a file named `captura.ico` in the same directory as `captura.py`. If not found, a default blue icon is generated automatically.

---

## Default Hotkeys

| Action | Default hotkey |
|---|---|
| Region capture | `Print Screen` |
| Full-screen capture | `Shift + Print Screen` |

Both hotkeys can be changed in Settings (see below).

---

## Region Capture — Step by Step

1. Press `Print Screen` (or trigger from tray menu).
2. The screen dims and a crosshair cursor appears.
3. **Click and drag** to draw a selection rectangle.
4. Release the mouse — an export panel appears near the selection.

### Adjusting the selection after drawing

- **Move:** click and drag inside the selection.
- **Resize:** drag any of the four corner handles.
- **Start over:** click outside the selection to clear it and draw again.
- **Cancel:** press `Esc` or right-click.

### Modifier keys during drawing

Hold a modifier key **while dragging** to constrain the shape:

| Modifier (default) | Effect |
|---|---|
| `Ctrl` | Forces a square selection (1:1) |
| `Shift` | Locks the configured aspect ratio (default 16:9) |
| `Alt` | Inverts the aspect ratio (e.g., changes from 16:9 to 9:16) |

These modifiers are configurable in Settings.

---

## Full-Screen Capture

Press `Shift + Print Screen` (or use the tray menu → *Capture Full Screen*).

The entire primary screen is captured and the export panel appears immediately — no selection needed.

---

## Export Panel

After making a selection, four buttons appear:

| Button | Keyboard shortcut | Action |
|---|---|---|
| **Copy** | `Enter` or `C` | Copies the image to the clipboard. |
| **Auto** | — | Saves the image automatically to the configured folder with a timestamp filename (`YYYYMMDD_HHMMSS_captura.png`). |
| **Save…** | `G` or `S` | Opens a Save As dialog to choose the location and filename manually. |
| **Cancel** | `Esc` | Closes the overlay without saving. |

After any action (Copy, Auto, Save), the overlay closes automatically.

---

## Magnifier (Zoom)

While the overlay is open and you are selecting or hovering near a selection edge, a circular magnifier lens (4× zoom) appears near the cursor. It shows a crosshair at its center for precise pixel-level positioning.

- Coordinates (`X: … Y: …`) are displayed above the magnifier.
- The magnifier repositions automatically to avoid overlapping the selection.
- Both the magnifier and coordinates can be disabled in Settings.

---

## Tray Menu

Right-click the tray icon to access:

- **Nueva captura (Zona)** — starts a region capture.
- **Capturar Pantalla Completa** — captures the full screen.
- **Configuración** — opens the settings dialog.
- **Reiniciar** — restarts the process (useful if hotkeys stop working).
- **Salir** — exits the application.

Left-clicking the tray icon also triggers a region capture.

---

## Settings

Open via tray menu → *Configuración*.

| Setting | Description |
|---|---|
| **Atajo Captura Zona** | Hotkey for zone capture. Click *Record* and press the desired combination. |
| **Atajo Pantalla Completa** | Hotkey for full-screen capture. Same recording method. |
| **Forzar Cuadrado (1:1)** | Modifier key to force a square selection (`---`, `Ctrl`, `Shift`, `Alt`). |
| **Forzar preferidas** | Modifier key to lock the aspect ratio. |
| **Invertir preferidas** | Modifier key to invert the locked aspect ratio (e.g., from Landscape to Portrait). |
| **Proporciones preferidas** | Aspect ratio used with the proportional modifier (default: 9:16). Enter any W:H value. |
| **Activar Lupa** | Enables or disables the magnifier. |
| **Mostrar Coordenadas** | Enables or disables X/Y coordinates above the magnifier. |
| **Carpeta Auto-Guardado** | Directory for automatically saved files. Click `...` to browse. |
| **Formato de salida** | `PNG` (lossless) or `JPG`. |
| **Calidad JPG (1-100)** | Compression quality for JPG output. Ignored for PNG. |
| **Iniciar con Windows** | Adds the application to the Windows registry to run automatically on startup (Windows only). |

Click **Save** to apply. Hotkeys are re-registered immediately — no restart required.

Settings are persisted using `QSettings` under the key `kdgdkd/Captura` (location varies by OS: registry on Windows, `~/.config` on Linux, `~/Library/Preferences` on macOS).

---

## File Naming (Auto-Save)

Files saved with the **Auto** button follow this pattern:

```
YYYYMMDD_HHMMSS_captura.png
YYYYMMDD_HHMMSS_captura.jpg
```

Example: `20240315_143022_captura.png`

The target folder is created automatically if it does not exist.

---

## Troubleshooting

**Hotkeys don't work**
- On Linux, run with `sudo` or grant your user input device access.
- If hotkeys stop responding after a settings change, use *Reiniciar* from the tray menu.

**The tray icon doesn't appear**
- Some Linux desktop environments require a system tray extension (e.g., on GNOME, install the *AppIndicator* extension).

**JPG quality setting has no effect**
- Verify the output format is set to `JPG` in Settings. PNG ignores the quality value.

**Auto-save fails silently**
- Check that the configured save directory is writable. The console (if launched from a terminal) will print the error path.