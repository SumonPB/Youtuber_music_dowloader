import yt_dlp
from pathlib import Path
import subprocess
import os


def descargar_audio(url: str, output_dir: str = "downloads", progress_hook=None) -> Path:
    """Descarga audio desde YouTube y lo convierte a MP3."""

    # Ruta FFmpeg relativa al archivo actual
    ffmpeg_path = Path(__file__).parent / "ffmpeg" / "bin" / "ffmpeg.exe"

    # Opciones básicas
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }
        ],
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,

        # 🔥 FFmpeg totalmente PORTABLE
        'ffmpeg_location': str(ffmpeg_path),

        'retries': 3,
        'progress_hooks': [progress_hook] if progress_hook else [],
        'ignoreerrors': True,
        'allow_unplayable_formats': True,
    }

    try:
        # Verifica que FFmpeg existe
        subprocess.run(
            [str(ffmpeg_path), '-version'],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Crear carpeta de salida si no existe
        os.makedirs(output_dir, exist_ok=True)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        return Path(filename).with_suffix('.mp3')

    except Exception as e:
        print(f"❌ Error al descargar {url}: {str(e)}")
        raise


def obtener_info_video(url: str) -> dict:
    """Obtiene información del video sin descargarlo"""

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    return {
        'titulo': info.get('title', 'Sin título'),
        'url': url,
        'duracion': info.get('duration', 0)
    }
