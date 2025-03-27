import yt_dlp
from pathlib import Path
import subprocess
import os

def descargar_audio(url: str, output_dir: str = "downloads", progress_hook=None) -> Path:
    """Descarga audio con parámetro opcional de directorio y progreso"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'ffmpeg_location': r'C:\ffmpeg\bin\ffmpeg.exe',
        'retries': 3,
        'progress_hooks': [progress_hook] if progress_hook else []
    }

    try:
        subprocess.run(
            [ydl_opts['ffmpeg_location'], '-version'],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
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