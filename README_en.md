# captura.py — Screenshot Tool

Lightweight Python utility that runs in the system tray. Supports area selection, full-screen capture, magnifier, configurable shortcuts, and multiple export options.

---

## Installation

### Option 1: Executable (Recommended for Windows)

The easiest and fastest way to use the tool on Windows is with the precompiled file:

1. Download the `captura.exe` file (you can find it in the `dist` folder if you've compiled it, or in the repository releases).
2. Optionally, download the `captura.ico` file and place it in the same folder as the executable to get the original icon.
3. Double-click `captura.exe` to start the application.

### Option 2: Run from source code (Python / Cross-platform)

If you prefer to run the script directly or are on another operating system (Linux, macOS), follow these steps:

#### 1. Create the project folder

Create a folder on your machine where you want to store the tool, for example:

```bash
mkdir captura
cd captura
```

#### 2. Download the files

On this GitHub page, download `captura.py` into the folder you just created.

If you prefer, you can clone the entire repository directly:

```bash
git clone https://github.com/tu-usuario/tu-repo.git captura
cd captura
```

#### 3. Prerequisites

- Python 3.8+
- PyQt6
- keyboard

#### 4. Install dependencies

From a terminal inside the project folder:

```bash
pip install PyQt6 keyboard
```

> **Note (Linux):** The `keyboard` library requires root privileges or special permissions to listen for global shortcuts. Run with `sudo`, or configure `/etc/udev/rules.d` to grant your user access to `/dev/input`.

---

## Running

From inside the project folder:

```bash
python captura.py
```

The application starts silently — no window appears.

---

## Default Shortcuts

| Action            | Default shortcut     |
| ----------------- | -------------------- |
| Area capture      | `Print Screen`       |
| Full-screen capture | `Shift + Print Screen` |

Both shortcuts can be changed in Settings (see below).

---

## Area Capture — step by step

1. Press `Print Screen` (or left-click the tray icon).
2. The screen darkens and a cross cursor appears.
3. **Click and drag** to draw the selection rectangle.
4. Release the mouse — the export panel appears near the selection.

### Adjusting the selection after drawing it

- **Move:** click inside the selection and drag.
- **Resize:** drag any of the four corners.
- **Start over:** click outside the selection to clear it and draw a new one.
- **Cancel:** press the X button, `Esc`, or right-click.

### Modifier keys while drawing and resizing

Hold down a modifier key **while dragging** to constrain the shape:

| Modifier (default) | Effect                                                                                                                                                                                                                  |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Ctrl`             | Locks the selection to the **proportion currently displayed** in the interface indicator. If the current selection has a 16:9+ proportion, the rectangle is forced to maintain exactly the 16:9 proportion.              |
| `Shift`            | Locks the selection to the **preferred aspect ratio** configured in Settings (default: 9:16).                                                                                                                            |
| `Alt`              | **Inverts** the preferred aspect ratio (by default, switches from 9:16 to 16:9).                                                                                                                                        |

These modifiers are configurable in Settings. You can assign `Ctrl`, `Shift`, `Alt`, or `---` (disabled) to each function.

---

## Full-Screen Capture

Press `Shift + Print Screen` (or use the tray menu → *Capturar Pantalla*).

The screen where the mouse cursor is located is captured (multi-monitor support). The export panel appears immediately with the entire screen already selected.

---

## Proportion Indicator During Selection

While drawing or resizing a selection, a label with proportion information is displayed:

```
1920 × 1080  |  16:9
```

This label appears near the selection (normally above, or below if there is no room). The application compares the current proportion against a list of 12 predefined standard proportions:

- **Square:** 1:1
- **Landscape:** 4:3, 3:2, 16:9, 16:10, 21:9, 3:1
- **Portrait:** 9:16, 1:3, 3:4, 2:3
- **Other:** 5:4

The indicator adds a sign to show the deviation:

| Sign      | Meaning                                                                      |
| --------- | ---------------------------------------------------------------------------- |
| *(no sign)* | The proportion matches **exactly** (±3 pixels tolerance) the standard one. |
| `+`       | The rectangle is **more elongated** than the nearest standard proportion.    |
| `-`       | The rectangle is **more square** than the nearest standard proportion.       |

If the proportion does not resemble any of the 12 standards (deviation >15%), only the pixel dimensions are shown without the proportion label.

---

## Export Panel

After making a selection (or after a full-screen capture), up to five buttons appear:

| Button     | Keyboard shortcut | Action                                                                                                                                              |
| ---------- | ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Auto**   | —                 | Executes the action configured in Settings (Save, Copy, or Open). If the action is set to `---`, this button is not shown.                         |
| **Copy**   | `Enter` or `C`    | Copies the image to the clipboard.                                                                                                                  |
| **Save…**  | `G` or `S`        | Opens a Save As dialog to choose location and name manually.                                                                                        |
| **Open**   | —                 | Opens the image with the application or URL configured in Settings ("Abrir con" field). If nothing is configured, opens the Windows "Open with…" dialog. |
| **Cancel** | `Esc`             | Closes the overlay without saving.                                                                                                                  |

Keyboard shortcuts (`Enter`, `C`, `G`, `S`) only work when the export panel is visible.

### Detailed Auto Button Behavior

The Auto button's action depends on the value configured in Settings → Auto → **Acción 'Auto'**:

- **Guardar (Save):** Saves the image automatically in the configured folder with a timestamped filename (`YYYYMMDD_HHMMSS_captura.png` or `.jpg`).
- **Copiar (Copy):** Copies the image to the clipboard (same behavior as the Copy button).
- **Abrir (Open):** Opens the image with the application or URL configured in "Abrir con". If the path is a URL (http/https/ftp), it first copies the image to the clipboard and then opens the URL in the browser. If it's an executable file path, it saves the capture to a temporary file and opens it with that executable. If nothing is configured or the path is invalid, it opens the Windows "Open with…" dialog.

---

## Magnifier (Zoom)

While the overlay is open and you are selecting or hovering the cursor near the edge of a selection, a circular magnifier appears near the cursor.

- **Zoom Adjustment:** Scroll the **mouse wheel** up/down to increase or decrease the zoom level of the image inside the magnifier (between 1x and 20x).
- **Size Adjustment:** Scroll the **mouse wheel while holding the `Ctrl` key** (the physical system Ctrl, not the configurable modifier) to increase or decrease the magnifier diameter (between 60px and 400px, in 10px increments).
- Zoom and size adjustments made during a capture are kept until you close the overlay. Default values can be set in Settings.
- Both the magnifier and coordinates can be disabled in Settings.

---

## Tray Menu

Right-click the tray icon to access:

- **Nueva captura** — starts an area capture.
- **Capturar Pantalla** — captures the full screen (the screen where the cursor is at that moment).
- **Configuración** — opens the settings dialog. If already open, the window is brought to the front.
- **Reiniciar** — completely restarts the process (useful if shortcuts stop working).
- **Salir** — closes the application.

Left-clicking the tray icon also triggers an area capture.

---

## Settings

Access via the tray menu → *Configuración*.

The settings dialog is organized into four sections.

### Section: Shortcuts

| Setting                       | Description                                                                                                                                                                                                                        |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Capturar Zona**             | Shortcut for area capture. Click *Grabar* and press the desired combination.                                                                                                                                                       |
| **Capturar Pantalla**         | Shortcut for full-screen capture. Same recording method.                                                                                                                                                                           |
| **Bloquear proporción**       | Modifier key to lock the selection to the proportion currently displayed on screen (default: `Ctrl`). Options: `---`, `Ctrl`, `Shift`, `Alt`.                                                                                      |
| **Forzar preferidas**         | Modifier key to lock the preferred aspect ratio configured below (default: `Shift`). Options: `---`, `Ctrl`, `Shift`, `Alt`.                                                                                                       |
| **Invertir preferidas**       | Modifier key to invert the locked aspect ratio (default: `Alt`). For example, if the preferred proportion is 9:16, pressing this modifier forces 16:9. Options: `---`, `Ctrl`, `Shift`, `Alt`.                                     |
| **Proporciones preferidas**   | Aspect ratio used with the "Forzar preferidas" and "Invertir preferidas" modifiers (default: 9:16). Expressed as two numeric fields `W : H`. Range: 1–9999 for each value.                                                          |

### Section: Magnifier

| Setting                   | Description                                                 |
| ------------------------- | ----------------------------------------------------------- |
| **Activar Lupa**          | Fully enables or disables the magnifier and guide lines.    |
| **Zoom**                  | Initial zoom level for the magnifier (1x – 20x).            |
| **Tamaño**                | Initial diameter in pixels of the magnifier (60px – 400px, step of 10px). |
| **Mostrar coordenadas**   | Enables or disables X/Y coordinates on the magnifier.       |

### Section: Auto

| Setting            | Description                                                                                                                                                                                               |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Acción 'Auto'**  | Determines what the Auto button in the export panel does: `Guardar` (Save), `Abrir` (Open), `Copiar` (Copy), or `---` (disables the button, it won't appear in the panel).                                |
| **Guardar en**     | Directory for automatically saved files (only used when "Acción 'Auto'" = `Guardar`). Click `...` to browse folders. This field is disabled if the Auto action is not Save.                               |
| **Abrir con**      | Path to an executable (.exe) or a URL (https://...) for opening captures. This field is disabled if the Auto action is not Open.                                                                         |
|                    | - The `...` button lets you browse for an executable on the file system.                                                                                                                                  |
|                    | - The `📋` button pastes a URL from the clipboard, validating that it is http/https/ftp. If the clipboard text is not a valid URL, a warning is shown.                                                     |
|                    | - When saving the settings, the path is validated to be an existing file, an absolute path, or a valid URL. If not, a warning is shown and the settings are not saved.                                    |

### Section: General

| Setting                     | Description                                                                                                                   |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **Iniciar con Windows**     | Adds or removes the `CapturaKdgdkd` entry in the Windows registry so the application starts automatically on login.           |
| **Formato de salida**       | `PNG` (lossless) or `JPG`. Affects both auto-save and the Save As dialog.                                                      |
| **Calidad JPG**             | Compression quality for JPG output (1–100). Automatically disabled when the selected format is PNG.                            |

Settings are persisted via `QSettings` under the key `kdgdkd/Captura` (location depends on OS: registry on Windows, `~/.config` on Linux, `~/Library/Preferences` on macOS).

---

## Multi-Monitor Support

The application captures the screen where the mouse cursor is located at the moment the capture is started (for both area capture and full-screen capture), using `QApplication.screenAt(QCursor.pos())`. If for some reason the screen cannot be determined, the primary screen is used.

Captures correctly handle the `devicePixelRatio` (DPI scaling) of each screen.
