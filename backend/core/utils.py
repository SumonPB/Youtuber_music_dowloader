import json
from pathlib import Path

def cargar_historial():
    try:
        with open('historial.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def guardar_historial(data):
    with open('historial.json', 'w') as f:
        json.dump(data, f, indent=2)

def es_url_nueva(url, historial, lista_actual):
    return not any(item['url'] == url for item in historial + lista_actual)