import yt_dlp
from pathlib import Path
import subprocess

def descargar_audio(url: str) -> Path:
    """Descarga SOLO el video de la URL, ignorando listas"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'noplaylist': True,  # Bloquea descarga de listas
        'quiet': False,
        'no_warnings': False,
        'ffmpeg_location': r'C:\ffmpeg\bin\ffmpeg.exe'
    }

    try:
        # Verificación FFmpeg
        subprocess.run([ydl_opts['ffmpeg_location'], '-version'], check=True)
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if 'entries' in info:  # Por si acaso
                info = info['entries'][0]
            return Path(ydl.prepare_filename(info)).with_suffix('.mp3')
            
    except Exception as e:
        print(f"❌ Error descargando {url}: {str(e)}")
        raise