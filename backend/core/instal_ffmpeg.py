import os
import urllib.request
import subprocess
import shutil

# Ruta base del proyecto (carpeta backend/core)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# URLs y rutas internas del proyecto
FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z"

DOWNLOAD_PATH = os.path.join(BASE_DIR, "ffmpeg-download.7z")
INSTALL_DIR = os.path.join(BASE_DIR, "ffmpeg")
WINRAR_PATH = r"C:\Program Files\WinRAR\WinRAR.exe"


def run(cmd):
    """Ejecuta un comando en el sistema"""
    return subprocess.run(cmd, shell=True)


def main():
    print("=== Instalador Automático de FFmpeg ===")

    # 1) Verificar WinRAR
    if not os.path.exists(WINRAR_PATH):
        print("❌ No se encontró WinRAR en:")
        print(WINRAR_PATH)
        print("\nIndica la ruta correcta si lo tienes en otra carpeta.")
        return

    print("✓ WinRAR encontrado.")

    # 2) Descargar FFmpeg
    print("Descargando FFmpeg...")
    urllib.request.urlretrieve(FFMPEG_URL, DOWNLOAD_PATH)
    print("✓ Descarga completada.")

    # 3) Limpiar instalación previa si existe
    if os.path.exists(INSTALL_DIR):
        shutil.rmtree(INSTALL_DIR)

    os.makedirs(INSTALL_DIR, exist_ok=True)

    # 4) Extraer con WinRAR
    print("Extrayendo FFmpeg con WinRAR...")
    run(f'"{WINRAR_PATH}" x -y "{DOWNLOAD_PATH}" "{INSTALL_DIR}\\"')
    print("✓ FFmpeg extraído.")

    # 5) Detectar carpeta interna genérica y reorganizar
    print("Organizando archivos...")
    content = os.listdir(INSTALL_DIR)
    for folder in content:
        full_path = os.path.join(INSTALL_DIR, folder)
        if os.path.isdir(full_path) and "ffmpeg" in folder.lower():
            for item in os.listdir(full_path):
                shutil.move(os.path.join(full_path, item), INSTALL_DIR)
            shutil.rmtree(full_path)
            break

    bin_dir = os.path.join(INSTALL_DIR, "bin")

    # 6) Agregar FFmpeg al PATH
    print("Agregando FFmpeg al PATH del sistema...")
    os.system(f'setx /M PATH "%PATH%;{bin_dir}"')

    # 7) Eliminar archivo descargado
    if os.path.exists(DOWNLOAD_PATH):
        os.remove(DOWNLOAD_PATH)
        print("✓ Archivo temporal de descarga eliminado")

    # Mensajes finales
    print("\n==========================================")
    print("✓ FFmpeg instalado exitosamente")
    print("✓ Agregado al PATH del sistema")
    print("👉 Cierra y vuelve a abrir CMD para que funcione")
    print("==========================================")

    
if __name__ == "__main__":
    main()
