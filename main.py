import os
import subprocess
from pathlib import Path

from frontend.gui import YouTubeDownloaderApp


def ensure_ffmpeg_installed():
    """Verifica si FFmpeg existe dentro del proyecto. Si no, lo instala."""
    root = Path(__file__).parent
    ffmpeg_path = root / "backend" / "core" / "ffmpeg" / "bin" / "ffmpeg.exe"

    # Si existe y funciona → perfecto
    if ffmpeg_path.exists():
        try:
            subprocess.run(
                [str(ffmpeg_path), "-version"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("✓ FFmpeg detectado correctamente.\n")
            return
        except:
            print("⚠ FFmpeg encontrado pero da error, reinstalando...\n")

    print("❌ FFmpeg no encontrado, instalando...\n")

    installer = root / "backend" / "core" / "instal_ffmpeg.py"

    result = subprocess.run(
        ["python", str(installer)],
        cwd=root
    )

    if result.returncode != 0:
        print("❌ No se pudo instalar FFmpeg")
        exit(1)

    print("✓ FFmpeg instalado con éxito.\n")


if __name__ == "__main__":
    print("""
===========================================
ADVERTENCIA: Solo para uso personal legítimo
===========================================
""")

    ensure_ffmpeg_installed()

    app = YouTubeDownloaderApp()
    app.mainloop()
