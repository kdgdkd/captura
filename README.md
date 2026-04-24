# captura.py — Herramienta de Capturas de Pantalla

Utilidad ligera en Python que se ejecuta en la bandeja del sistema. Soporta selección de zona, captura de pantalla completa, lupa, atajos configurables y múltiples opciones de exportación.

---

## Instalación

### 1. Crear la carpeta del proyecto

Crea una carpeta en tu equipo donde quieras guardar la herramienta, por ejemplo:

```bash
mkdir captura
cd captura
```

### 2. Descargar los ficheros

En esta página de GitHub, descarga `captura.py` haciendo clic en el fichero y luego en el botón **Download raw file** (icono de descarga, arriba a la derecha del visor de código). Guarda el fichero dentro de la carpeta que acabas de crear.

Si lo prefieres, puedes clonar el repositorio completo directamente:

```bash
git clone https://github.com/tu-usuario/tu-repo.git captura
cd captura
```

### 3. Requisitos previos

- Python 3.8+
- PyQt6
- keyboard

### 4. Instalar dependencias

Con la terminal situada dentro de la carpeta del proyecto:

```bash
pip install PyQt6 keyboard
```

> **Nota (Linux):** La librería `keyboard` requiere privilegios de root o permisos especiales para escuchar atajos globales. Ejecuta con `sudo`, o configura `/etc/udev/rules.d` para dar a tu usuario acceso a `/dev/input`.


---

## Ejecución

Desde dentro de la carpeta del proyecto:

```bash
python captura.py
```

La aplicación arranca en silencio — no aparece ninguna ventana. Busca el icono en la bandeja del sistema (un círculo azul con una "S"). La app se mantiene en segundo plano hasta que la cierras desde el menú de bandeja.

### Icono personalizado (opcional)

Coloca un fichero llamado `captura.ico` en el mismo directorio que `captura.py`. Si no se encuentra, se genera automáticamente un icono azul por defecto.

---

## Atajos por defecto

| Acción | Atajo por defecto |
|---|---|
| Captura de zona | `Impr Pant` |
| Captura de pantalla completa | `Shift + Impr Pant` |

Ambos atajos se pueden cambiar en Configuración (ver más abajo).

---

## Captura de zona — paso a paso

1. Pulsa `Impr Pant` (o úsalo desde el menú de bandeja).
2. La pantalla se oscurece y aparece un cursor en cruz.
3. **Haz clic y arrastra** para dibujar el rectángulo de selección.
4. Suelta el ratón — aparece el panel de exportación cerca de la selección.

### Ajustar la selección después de dibujarla

- **Mover:** haz clic dentro de la selección y arrastra.
- **Redimensionar:** arrastra cualquiera de las cuatro esquinas.
- **Empezar de nuevo:** haz clic fuera de la selección para borrarla y dibujar otra.
- **Cancelar:** pulsa `Esc` o haz clic derecho.

### Teclas modificadoras durante el dibujo

Mantén pulsada una tecla modificadora **mientras arrastras** para restringir la forma:

| Modificador (por defecto) | Efecto |
|---|---|
| `Ctrl` | Fuerza una selección cuadrada (1:1) |
| `Shift` | Bloquea la relación de aspecto configurada (por defecto 16:9) |

Estos modificadores son configurables en Ajustes.

---

## Captura de pantalla completa

Pulsa `Shift + Impr Pant` (o usa el menú de bandeja → *Capturar Pantalla Completa*).

Se captura toda la pantalla principal y el panel de exportación aparece de inmediato — sin necesidad de selección.

---

## Panel de exportación

Tras hacer una selección, aparecen cuatro botones:

| Botón | Atajo de teclado | Acción |
|---|---|---|
| **Copiar** | `Enter` o `C` | Copia la imagen al portapapeles. |
| **Auto** | — | Guarda la imagen automáticamente en la carpeta configurada con nombre de fichero con marca de tiempo (`YYYYMMDD_HHMMSS_captura.png`). |
| **Guardar…** | `G` o `S` | Abre un diálogo Guardar como para elegir ubicación y nombre manualmente. |
| **Cancelar** | `Esc` | Cierra el overlay sin guardar. |

Tras cualquier acción (Copiar, Auto, Guardar), el overlay se cierra automáticamente.

---

## Lupa (Zoom)

Mientras el overlay está abierto y estás seleccionando o pasando el cursor cerca del borde de una selección, aparece una lupa circular (zoom 4×) cerca del cursor. Muestra una cruz en su centro para un posicionamiento preciso a nivel de píxel.

- Las coordenadas (`X: … Y: …`) se muestran encima de la lupa.
- La lupa se reposiciona automáticamente para no solaparse con la selección.
- Tanto la lupa como las coordenadas se pueden desactivar en Configuración.

---

## Menú de bandeja

Haz clic derecho sobre el icono de la bandeja para acceder a:

- **Nueva captura (Zona)** — inicia una captura de zona.
- **Capturar Pantalla Completa** — captura la pantalla completa.
- **Configuración** — abre el diálogo de ajustes.
- **Reiniciar** — reinicia el proceso (útil si los atajos dejan de funcionar).
- **Salir** — cierra la aplicación.

Hacer clic izquierdo sobre el icono de bandeja también activa la captura de zona.

---

## Configuración

Accede desde el menú de bandeja → *Configuración*.

| Ajuste | Descripción |
|---|---|
| **Atajo Captura Zona** | Atajo para la captura de zona. Haz clic en *Grabar* y pulsa la combinación deseada. |
| **Atajo Pantalla Completa** | Atajo para la captura completa. Mismo método de grabación. |
| **Modificador Cuadrado (1:1)** | Tecla modificadora para forzar selección cuadrada (`Control` / `Shift` / `Alt`). |
| **Modificador Proporciones** | Tecla modificadora para bloquear la relación de aspecto. |
| **Proporciones preferidas** | Relación de aspecto usada con el modificador proporcional (por defecto: 16:9). Introduce cualquier valor W:H. |
| **Activar Lupa (Zoom)** | Activa o desactiva la lupa. |
| **Mostrar Coordenadas** | Activa o desactiva las coordenadas X/Y sobre la lupa. |
| **Carpeta Auto-Guardado** | Directorio para los ficheros guardados automáticamente. Haz clic en `...` para explorar. |
| **Formato de salida** | `PNG` (sin pérdida) o `JPG`. |
| **Calidad JPG (1-100)** | Calidad de compresión para la salida JPG. Se ignora para PNG. |

Haz clic en **Guardar** para aplicar. Los atajos se reregistran de inmediato — no hace falta reiniciar.

La configuración se persiste mediante `QSettings` bajo la clave `MiEmpresa/Capturador` (ubicación según SO: registro en Windows, `~/.config` en Linux, `~/Library/Preferences` en macOS).

---

## Nomenclatura de ficheros (auto-guardado)

Los ficheros guardados con el botón **Auto** siguen este patrón:

```
YYYYMMDD_HHMMSS_captura.png
YYYYMMDD_HHMMSS_captura.jpg
```

Ejemplo: `20240315_143022_captura.png`

La carpeta destino se crea automáticamente si no existe.

---

## Solución de problemas

**Los atajos no funcionan**
- En Linux, ejecuta con `sudo` o concede a tu usuario acceso a los dispositivos de entrada.
- Si los atajos dejan de responder tras un cambio de configuración, usa *Reiniciar* desde el menú de bandeja.

**El icono de bandeja no aparece**
- Algunos entornos de escritorio Linux requieren una extensión de bandeja del sistema (p. ej., en GNOME instala la extensión *AppIndicator*).

**El ajuste de calidad JPG no tiene efecto**
- Verifica que el formato de salida esté configurado como `JPG` en Ajustes. PNG ignora el valor de calidad.

**El auto-guardado falla sin avisar**
- Comprueba que el directorio de guardado configurado tenga permisos de escritura. La consola (si lanzaste desde un terminal) mostrará la ruta del error.