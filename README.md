# Organizador de Descargas

Una herramienta sencilla y potente para mantener tu carpeta de descargas limpia y organizada automáticamente.

## ✨ Características

- **Categorización Automática**: Mueve tus archivos a carpetas específicas:
    - `IMAGENES`: Imágenes (.png, .jpg, .webp, etc.)
    - `DOCUMENTOS`: Documentos (.pdf, .docx, .xlsx, .txt, etc.)
    - `OTROS`: Todo lo demás.
- **Renombrado de Imágenes**: Las fotos en `IMAGENES` se renombran automáticamente al formato `IMG_YYYYMMDD_HHMMSS` basado en su fecha de creación.
- **Manejo de Archivos Comprimidos**:
    - Detecta archivos `.zip`, `.rar`, `.7z`, `.tar`, `.gz`.
    - Crea una carpeta con el nombre del archivo dentro de `OTROS`.
    - Descomprime el contenido dentro de esa carpeta.
    - Elimina el archivo comprimido original para ahorrar espacio.
- **Auto-Corrección**: Si la app encuentra un archivo en la carpeta equivocada (ej. un PDF en Imágenes), lo mueve a su lugar correcto.
- **Interfaz Intuitiva**: Incluye una barra de progreso y notificaciones de éxito o error.
- **Logs de Error**: Genera un archivo `organizer_log.txt` en el escritorio en caso de fallos.

## 🛠️ Requisitos del Sistema

### Para usuarios (Ejecutable)
- **Extracción de RAR/7z**: Se requiere tener instalado **WinRAR** o **7-Zip** en el sistema para que la aplicación pueda procesar estos formatos propietarios.

### Para desarrolladores (Código fuente)
- Python 3.x
- Librerías necesarias:
  ```bash
  pip install pillow patool pyinstaller
  ```

## 🚀 Uso

1. Ejecuta `OrganizadorDescargas.exe` desde tu escritorio.
2. Haz clic en el botón **Organizar**.
3. ¡Listo! Tus archivos estarán clasificados en segundos.

## 🔧 Construcción del Ejecutable

Si deseas volver a generar el ejecutable desde el código fuente, utiliza:

```bash
pyinstaller --onefile --noconsole --icon=app_icon.ico --hidden-import patoolib --name="OrganizadorDescargas" organizer.py
```


