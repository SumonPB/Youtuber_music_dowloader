# YouTube Music Downloader PRO 🎵

![App Screenshot](screenshot.png)

Aplicación para descargar audio desde YouTube con interfaz intuitiva.

## Características ✨
- 🎶 Monitoreo automático de reproducción en navegador
- 📁 Selección de carpeta personalizada
- 🎧 Calidad de audio configurable (64-320kbps)
- 📊 Barra de progreso en tiempo real
- 📚 Historial de descargas en JSON
- 🎨 Temas oscuro/claro

## Requisitos 💻
```bash
Python 3.8+
yt-dlp >= 2023.11.16
customtkinter >= 5.2.1
selenium >= 4.10.0
FFmpeg (incluido en Windows)
```

## Instalación ⚙️
Clonar repositorio:

```bash
git clone https://github.com/tu-usuario/youtube-music-downloader.git
cd youtube-music-downloader
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Uso Básico 🚀
```bash
python main.py
```

Seleccionar carpeta destino (opcional)

Iniciar monitor con "▶ Iniciar Monitor"

Reproducir música en navegador

Las canciones aparecerán automáticamente

Usar "⬇ Descargar Todo" para guardar

## Configuración ⚙️
Editar backend/core/config.ini:

```ini
[settings]
default_folder = ~/Music
default_quality = 320  # 64|128|192|256|320
theme = dark  # dark|light|system
```

## ⚠️ Descargo de Responsabilidad
Este software es para uso personal/educativo:

✅ Solo descarga contenido con derechos de uso

⚖️ Respeta Términos de YouTube

🚫 No redistribuyas contenido descargado

El desarrollador no asume responsabilidad por el mal uso.

## Capturas 📸
| Interfaz Principal | Progreso de Descarga |
|--------------------|---------------------|
| Main UI | Progress |

## Licencia 📜
MIT License - Ver LICENSE

Última actualización: 25/11/2023
