# captura.py — Herramienta de Capturas de Pantalla

Utilidad ligera en Python que se ejecuta en la bandeja del sistema. Soporta selección de zona, captura de pantalla completa, lupa, atajos configurables y múltiples opciones de exportación.

---

## Instalación

### Opción 1: Ejecutable (Recomendado para Windows)

La forma más sencilla y rápida de utilizar la herramienta en Windows es usando el archivo precompilado:

1. Descarga el archivo `captura.exe` (puedes encontrarlo en la carpeta `dist` si lo has compilado, o en las releases del repositorio).
2. Opcionalmente, descarga el archivo `captura.ico` y colócalo en la misma carpeta que el ejecutable para tener el icono original.
3. Haz doble clic en `captura.exe` para iniciar la aplicación.

### Opción 2: Ejecutar desde el código fuente (Python / Multiplataforma)

Si prefieres ejecutar el script directamente o estás en otro sistema operativo (Linux, macOS), sigue estos pasos:

#### 1. Crear la carpeta del proyecto

Crea una carpeta en tu equipo donde quieras guardar la herramienta, por ejemplo:

```bash
mkdir captura
cd captura
```

#### 2. Descargar los ficheros

En esta página de GitHub, descarga `captura.py` dentro de la carpeta que acabas de crear.

Si lo prefieres, puedes clonar el repositorio completo directamente:

```bash
git clone https://github.com/tu-usuario/tu-repo.git captura
cd captura
```

#### 3. Requisitos previos

- Python 3.8+
- PyQt6
- keyboard

#### 4. Instalar dependencias

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

La aplicación arranca en silencio — no aparece ninguna ventana. 



---

## Atajos por defecto

| Acción                       | Atajo por defecto   |
| ---------------------------- | ------------------- |
| Captura de zona              | `Impr Pant`         |
| Captura de pantalla completa | `Shift + Impr Pant` |

Ambos atajos se pueden cambiar en Configuración (ver más abajo).

---

## Captura de zona — paso a paso

1. Pulsa `Impr Pant` (o haz clic izquierdo sobre el icono de bandeja).
2. La pantalla se oscurece y aparece un cursor en cruz.
3. **Haz clic y arrastra** para dibujar el rectángulo de selección.
4. Suelta el ratón — aparece el panel de exportación cerca de la selección.

### Ajustar la selección después de dibujarla

- **Mover:** haz clic dentro de la selección y arrastra. 
- **Redimensionar:** arrastra cualquiera de las cuatro esquinas.
- **Empezar de nuevo:** haz clic fuera de la selección para borrarla y dibujar otra.
- **Cancelar:** pulsa botón X, `Esc` o haz clic derecho.

### Teclas modificadoras durante el dibujo y redimensionado

Mantén pulsada una tecla modificadora **mientras arrastras** para restringir la forma:

| Modificador (por defecto) | Efecto                                                                                                                                                                                                                         |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Ctrl`                    | Bloquea la selección a la **proporción que se está mostrando actualmente** en el indicador de la interfaz. Si la selección actual tiene proporción 16:9+, se fuerza que el rectángulo mantenga exactamente la proporción 16:9. |
| `Shift`                   | Bloquea la selección a la **relación de aspecto preferida** configurada en Ajustes (por defecto: 9:16).                                                                                                                        |
| `Alt`                     | **Invierte** la relación de aspecto preferida (por defecto, pasa de 9:16 a 16:9).                                                                                                                                              |

Estos modificadores son configurables en Ajustes. Puedes asignar `Ctrl`, `Shift`, `Alt` o `---` (desactivado) a cada función. 

---

## Captura de pantalla completa

Pulsa `Shift + Impr Pant` (o usa el menú de bandeja → *Capturar Pantalla*).

Se captura la pantalla donde se encuentra el cursor del ratón (soporte multi-monitor). El panel de exportación aparece de inmediato con la pantalla completa ya seleccionada.

---

## Indicador de proporción durante la selección

Mientras dibujas o redimensionas una selección, se muestra una etiqueta con información de la proporción:

```
1920 × 1080  |  16:9
```

Esta etiqueta aparece cerca de la selección (normalmente encima, o debajo si no cabe). La aplicación compara la proporción actual con una lista de 12 proporciones estándar predefinidas:

- **Cuadradas:** 1:1
- **Horizontales (landscape):** 4:3, 3:2, 16:9, 16:10, 21:9, 3:1
- **Verticales (portrait):** 9:16, 1:3, 3:4, 2:3
- **Otras:** 5:4

El indicador añade un signo para mostrar la desviación:

| Signo         | Significado                                                                        |
| ------------- | ---------------------------------------------------------------------------------- |
| *(sin signo)* | La proporción coincide **exactamente** (±3 píxeles de tolerancia) con la estándar. |
| `+`           | El rectángulo es **más alargado** que la proporción estándar más cercana.          |
| `-`           | El rectángulo es **más cuadrado** que la proporción estándar más cercana.          |

Si la proporción no se parece a ninguna de las 12 estándar (desviación >15%), solo se muestran las dimensiones en píxeles sin la etiqueta de proporción.

---

## Panel de exportación

Tras hacer una selección (o tras una captura de pantalla completa), aparecen hasta cinco botones:

| Botón        | Atajo de teclado | Acción                                                                                                                                                  |
| ------------ | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Auto**     | —                | Ejecuta la acción configurada en Ajustes (Guardar, Copiar o Abrir). Si la acción está configurada como `---`, este botón no se muestra.                 |
| **Copiar**   | `Enter` o `C`    | Copia la imagen al portapapeles.                                                                                                                        |
| **Guardar…** | `G` o `S`        | Abre un diálogo Guardar como para elegir ubicación y nombre manualmente.                                                                                |
| **Abrir**    | —                | Abre la imagen con la aplicación o URL configurada en Ajustes (campo "Abrir con"). Si no hay nada configurado, abre el diálogo "Abrir con…" de Windows. |
| **Cancelar** | `Esc`            | Cierra el overlay sin guardar.                                                                                                                          |

Los atajos de teclado (`Enter`, `C`, `G`, `S`) solo funcionan cuando el panel de exportación está visible.

### Comportamiento detallado del botón Auto

La acción del botón Auto depende del valor configurado en Ajustes → Auto → **Acción 'Auto'**:

- **Guardar:** Guarda la imagen automáticamente en la carpeta configurada con nombre de fichero con marca de tiempo (`YYYYMMDD_HHMMSS_captura.png` o `.jpg`).
- **Copiar:** Copia la imagen al portapapeles (mismo comportamiento que el botón Copiar).
- **Abrir:** Abre la imagen con la aplicación o URL configurada en "Abrir con". Si la ruta es una URL (http/https/ftp), primero copia la imagen al portapapeles y luego abre la URL en el navegador. Si es una ruta de archivo ejecutable, guarda la captura en un archivo temporal y la abre con dicho ejecutable. Si no hay nada configurado o la ruta no es válida, abre el diálogo "Abrir con…" de Windows.

### 

---

## Lupa (Zoom)

Mientras el overlay está abierto y estás seleccionando o pasando el cursor cerca del borde de una selección, aparece una lupa circular cerca del cursor. 



- **Ajuste de Zoom:** Gira la **rueda del ratón** hacia arriba/abajo para aumentar o reducir el nivel de zoom de la imagen dentro de la lupa (entre 1x y 20x).
- **Ajuste de Tamaño:** Gira la **rueda del ratón manteniendo pulsada la tecla `Ctrl`** (el Ctrl físico del sistema, no el modificador configurable) para aumentar o reducir el diámetro de la lupa (entre 60px y 400px, en incrementos de 10px).
- Los ajustes de zoom y tamaño que realices durante una captura se mantendrán hasta que cierres el overlay. Los valores por defecto se pueden definir en Configuración.
- Tanto la lupa como las coordenadas se pueden desactivar en Configuración.

---

## Menú de bandeja

Haz clic derecho sobre el icono de la bandeja para acceder a:

- **Nueva captura** — inicia una captura de zona.
- **Capturar Pantalla** — captura la pantalla completa (la pantalla donde está el cursor en ese momento).
- **Configuración** — abre el diálogo de ajustes. Si ya está abierto, la ventana se trae al frente.
- **Reiniciar** — reinicia el proceso completamente (útil si los atajos dejan de funcionar).
- **Salir** — cierra la aplicación.

Hacer clic izquierdo sobre el icono de bandeja también activa la captura de zona.

---

## Configuración

Accede desde el menú de bandeja → *Configuración*.

El diálogo de configuración se organiza en cuatro secciones.

### Sección: Atajos

| Ajuste                      | Descripción                                                                                                                                                                                                                  |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Capturar Zona**           | Atajo para la captura de zona. Haz clic en *Grabar* y pulsa la combinación deseada.                                                                                                                                          |
| **Capturar Pantalla**       | Atajo para la captura completa. Mismo método de grabación.                                                                                                                                                                   |
| **Bloquear proporción**     | Tecla modificadora para bloquear la selección a la proporción que se está mostrando actualmente en pantalla (por defecto: `Ctrl`). Opciones: `---`, `Ctrl`, `Shift`, `Alt`.                                                  |
| **Forzar preferidas**       | Tecla modificadora para bloquear la relación de aspecto preferida configurada abajo (por defecto: `Shift`). Opciones: `---`, `Ctrl`, `Shift`, `Alt`.                                                                         |
| **Invertir preferidas**     | Tecla modificadora para invertir la relación de aspecto bloqueada (por defecto: `Alt`). Por ejemplo, si la proporción preferida es 9:16, al pulsar este modificador se fuerza 16:9. Opciones: `---`, `Ctrl`, `Shift`, `Alt`. |
| **Proporciones preferidas** | Relación de aspecto usada con los modificadores "Forzar preferidas" e "Invertir preferidas" (por defecto: 9:16). Se expresan como dos campos numéricos `W : H`. Rango: 1–9999 para cada valor.                               |



### Sección: Lupa

| Ajuste                  | Descripción                                                          |
| ----------------------- | -------------------------------------------------------------------- |
| **Activar Lupa**        | Activa o desactiva completamente la lupa y las líneas guía.          |
| **Zoom**                | Nivel de aumento inicial para la lupa (1x – 20x).                    |
| **Tamaño**              | Diámetro inicial en píxeles de la lupa (60px – 400px, paso de 10px). |
| **Mostrar coordenadas** | Activa o desactiva las coordenadas X/Y sobre la lupa.                |

### Sección: Auto

| Ajuste            | Descripción                                                                                                                                                                                                 |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Acción 'Auto'** | Determina qué hace el botón Auto del panel de exportación: `Guardar`, `Abrir`, `Copiar`, o `---` (desactiva el botón, no se muestra en el panel).                                                           |
| **Guardar en**    | Directorio para los ficheros guardados automáticamente (solo se usa cuando "Acción 'Auto'" = `Guardar`). Haz clic en `...` para explorar carpetas. Este campo se desactiva si la acción Auto no es Guardar. |
| **Abrir con**     | Ruta de un ejecutable (.exe) o una URL (https://...) para abrir las capturas. Este campo se desactiva si la acción Auto no es Abrir.                                                                        |
|                   | - El botón `...` permite buscar un ejecutable en el sistema de archivos.                                                                                                                                    |
|                   | - El botón `📋` pega una URL desde el portapapeles, validando que sea http/https/ftp. Si el texto del portapapeles no es una URL válida, muestra un aviso.                                                  |
|                   | - Al guardar la configuración, se valida que la ruta sea un archivo existente, una ruta absoluta, o una URL válida. Si no, se muestra un aviso y no se guarda.                                              |

### Sección: General

| Ajuste                  | Descripción                                                                                                                               |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Iniciar con Windows** | Añade o elimina la entrada `CapturaKdgdkd` en el registro de Windows para que la aplicación se ejecute automáticamente al iniciar sesión. |
| **Formato de salida**   | `PNG` (sin pérdida) o `JPG`. Afecta tanto al auto-guardado como al diálogo Guardar como.                                                  |
| **Calidad JPG**         | Calidad de compresión para la salida JPG (1–100). Se desactiva automáticamente cuando el formato seleccionado es PNG.                     |

La configuración se persiste mediante `QSettings` bajo la clave `kdgdkd/Captura` (ubicación según SO: registro en Windows, `~/.config` en Linux, `~/Library/Preferences` en macOS).



---

## Soporte multi-monitor

La aplicación captura la pantalla donde se encuentra el cursor del ratón en el momento de iniciar la captura (tanto para captura de zona como para pantalla completa), usando `QApplication.screenAt(QCursor.pos())`. Si por alguna razón no se puede determinar la pantalla, se usa la pantalla principal.

Las capturas manejan correctamente el `devicePixelRatio` (escalado DPI) de cada pantalla.

---



- 
