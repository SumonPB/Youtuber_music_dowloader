import json
import os
from typing import List, Dict

def cargar_historial() -> List[Dict[str, str]]:
    """Carga el archivo JSON de historial si existe, sino retorna una lista vacía."""
    ruta_json = os.path.join(os.path.dirname(__file__), "../data/historial.json")
    if os.path.exists(ruta_json):
        with open(ruta_json, "r") as f:
            return json.load(f)
    return []

def guardar_historial(historial: List[Dict[str, str]]) -> None:
    """Guarda la lista de canciones en el archivo JSON."""
    ruta_json = os.path.join(os.path.dirname(__file__), "../data/historial.json")
    with open(ruta_json, "w") as f:
        json.dump(historial, f, indent=4)

def es_url_nueva(url: str, historial: List[Dict[str, str]], lista_actual: List[Dict[str, str]]) -> bool:
    """Verifica si la URL no está en el historial ni en la lista actual."""
    return not any(
        cancion["url"] == url
        for cancion in historial + lista_actual
    )
