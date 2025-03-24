import os
import json
from pathlib import Path
from backend.core.downloader import descargar_audio

# Configuración inicial
os.environ['PATH'] = r'C:\ffmpeg\bin;' + os.environ['PATH']
HISTORIAL_FILE = 'historial.json'

def cargar_historial():
    """Carga el historial desde el archivo JSON"""
    try:
        with open(HISTORIAL_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def guardar_historial(historial):
    """Guarda el historial en el archivo JSON"""
    with open(HISTORIAL_FILE, 'w') as f:
        json.dump(historial, f, indent=2)

def limpiar_url(url: str) -> str:
    """Elimina parámetros de lista de reproducción"""
    if 'youtu.be/' in url:
        return f"https://youtube.com/watch?v={url.split('youtu.be/')[1].split('?')[0]}"
    return url.split('&')[0] if 'v=' in url else url

def main():
    historial = cargar_historial()
    
    print("🎵 YouTube Music Downloader (Enter para salir)")
    print("---------------------------------------------")
    
    try:
        while True:
            url = input("\nIngresa URL: ").strip()
            if not url:  # Si presiona Enter sin URL
                break
                
            url_limpia = limpiar_url(url)
            
            # Verifica si ya existe en el historial
            if any(item['url'] == url_limpia for item in historial):
                print("⚠ Esta URL ya fue descargada antes")
                continue
                
            try:
                archivo = descargar_audio(url_limpia)
                print(f"✅ Descargado: {archivo.name}")
                
                # Agrega al historial
                historial.append({
                    'url': url_limpia,
                    'nombre': archivo.name,
                    'fecha': datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                
    finally:
        # Esto se ejecutará siempre, incluso al salir con Enter
        guardar_historial(historial)
        print(f"\n💾 Historial guardado con {len(historial)} canciones")

if __name__ == "__main__":
    from datetime import datetime  # Import aquí para evitar circularidad
    main()