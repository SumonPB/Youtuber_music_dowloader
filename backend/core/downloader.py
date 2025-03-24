import yt_dlp
import os
from typing import Optional

def descargar_mp3(url: str, nombre_archivo: str, carpeta_descargas: str = "downloads") -> Optional[str]:
    """Descarga audio en MP3 con mejor manejo de errores"""
    try:
        os.makedirs(carpeta_descargas, exist_ok=True)
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{carpeta_descargas}/{nombre_archivo}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        return f"{carpeta_descargas}/{nombre_archivo}.mp3"
    except Exception as e:
        print(f"❌ Error al descargar {nombre_archivo}: {str(e)}")
        return None