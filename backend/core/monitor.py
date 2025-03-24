from typing import Optional, Dict
import yt_dlp

def obtener_url_actual() -> Optional[str]:
    """Obtiene la URL de YouTube desde input"""
    url = input("Ingresa la URL de YouTube (o 'salir' para terminar): ")
    return url if url.lower() != "salir" else None

def obtener_info_cancion(url: str) -> Dict[str, str]:
    """Obtiene información de la canción con manejo de errores"""
    ydl_opts = {
        'quiet': True,
        'extract_flat': False,  # Cambiado a False para obtener metadatos completos
        'force_generic_extractor': True  # Para manejar mejor URLs especiales
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # Extraer título o usar un valor por defecto
            titulo = info.get('title', f"video_sin_titulo_{info['id']}")
            return {"name": titulo, "url": url}
    except Exception as e:
        print(f"⚠ Error al procesar {url}: {str(e)}")
        return {"name": "error_al_obtener_titulo", "url": url}