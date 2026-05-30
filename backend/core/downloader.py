import yt_dlp
from pathlib import Path
import subprocess
import traceback
import os


def descargar_audio(
    url: str,
    output_dir: str = "downloads",
    progress_hook=None,
    debug: bool = True
) -> Path:

    ffmpeg_path = Path(__file__).parent / "ffmpeg" / "bin" / "ffmpeg.exe"

    if not ffmpeg_path.exists():
        raise FileNotFoundError(
            f"No se encontró FFmpeg en:\n{ffmpeg_path}"
        )

    ydl_opts = {
        "format": "bestaudio/best",
        "sleep_interval": 2,
        "max_sleep_interval": 5,
        "extractor_args": {
            "youtube": {
                "player_client": ["android"]
            }
        },

        "outtmpl": os.path.join(
            output_dir,
            "%(title)s.%(ext)s"
        ),

        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",
        }],

        "ffmpeg_location": str(ffmpeg_path),

        "noplaylist": True,
        "retries": 5,
        "fragment_retries": 5,
        "socket_timeout": 30,

        "quiet": not debug,
        "no_warnings": not debug,

        "ignoreerrors": False,

        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/148.0.0.0 Safari/537.36"
            )
        }
    }

    if progress_hook:
        ydl_opts["progress_hooks"] = [progress_hook]

    try:

        subprocess.run(
            [str(ffmpeg_path), "-version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        os.makedirs(output_dir, exist_ok=True)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            print("\n========== DESCARGA ==========")
            print("URL:", url)

            info = ydl.extract_info(
                url,
                download=True
            )

            print("Tipo info:", type(info))

            if info is None:
                raise RuntimeError(
                    "yt-dlp devolvió None"
                )

            print("Título:", info.get("title"))

            filename = ydl.prepare_filename(info)

            print("Archivo original:", filename)

            mp3_file = Path(filename).with_suffix(".mp3")

            print("MP3 esperado:", mp3_file)

            if not mp3_file.exists():
                print(
                    "ADVERTENCIA: El mp3 aún no existe."
                )

            print("==============================\n")

            return mp3_file

    except Exception as e:

        print("\n========== ERROR ==========")
        traceback.print_exc()
        print("===========================\n")

        print(f"❌ Error al descargar:")
        print(f"URL: {url}")
        print(f"Motivo: {e}\n")

        raise


def obtener_info_video(url: str) -> dict:

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "noplaylist": True,
        "ignoreerrors": False,

        "extractor_args": {
            "youtube": {
                "player_client": ["android"]
            }
        }
    }

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

            print("\n========== DEBUG INFO ==========")
            print("Tipo:", type(info))

            if isinstance(info, dict):
                print("Claves:", list(info.keys())[:20])

            else:
                print("Contenido:", info)

            print("================================\n")

        if info is None:
            raise RuntimeError(
                "yt-dlp devolvió None"
            )

        return {
            "titulo": info.get("title", "Sin título"),
            "url": url,
            "duracion": info.get("duration", 0)
        }

    except Exception as e:

        traceback.print_exc()

        print("\n========== ERROR INFO ==========")
        print(f"URL: {url}")
        print(f"Motivo: {e}")
        print("================================\n")

        return {
            "titulo": "Video no disponible",
            "url": url,
            "duracion": 0
        }


if __name__ == "__main__":

    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    print(obtener_info_video(test_url))

    descargar_audio(
        test_url,
        debug=True
    )