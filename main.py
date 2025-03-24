from backend.core.monitor import obtener_url_actual, obtener_info_cancion
from backend.core.utils import cargar_historial, guardar_historial, es_url_nueva
from backend.core.downloader import descargar_mp3

def main():
    historial = cargar_historial()
    lista_actual = []
    
    while True:
        url = obtener_url_actual()
        if not url:
            break
        
        if es_url_nueva(url, historial, lista_actual):
            cancion = obtener_info_cancion(url)
            lista_actual.append(cancion)
            historial.append(cancion)
            print(f"Canción añadida: {cancion['name']}")
    
    # Guardar historial al finalizar
    guardar_historial(historial)
    
    # Descargar todas las canciones (simulación)
    for cancion in lista_actual:
        descargar_mp3(cancion["url"], cancion["name"])

if __name__ == "__main__":
    main()