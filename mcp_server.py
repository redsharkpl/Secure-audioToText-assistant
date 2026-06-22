import os
import shutil
import tempfile
import torch
import whisper
import yt_dlp
from mcp.server.fastmcp import FastMCP

# Inicjalizacja serwera FastMCP
mcp = FastMCP("AudioToTextServer")

@mcp.tool()
def download_youtube_audio(url: str) -> str:
    """
    Pobiera audio z podanego linku YouTube do izolowanego folderu tymczasowego
    i zwraca ścieżkę do pliku.
    Każde pobranie dostaje własny folder (mkdtemp), co eliminuje WinError 32.
    """
    try:
        # Izolowany folder tymczasowy — yt-dlp ma ekskluzywny dostęp
        tmpdir = tempfile.mkdtemp(prefix="yt_audio_")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(tmpdir, '%(id)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            'noprogress': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_id = info.get('id', 'unknown')

            # Szukaj pliku mp3 w izolowanym folderze
            file_path = os.path.join(tmpdir, f"{file_id}.mp3")
            if os.path.exists(file_path):
                return file_path

            # Fallback dla innych potencjalnych rozszerzeń po procesowaniu
            for ext in ['m4a', 'wav', 'webm', 'ogg']:
                possible_path = os.path.join(tmpdir, f"{file_id}.{ext}")
                if os.path.exists(possible_path):
                    return possible_path

            return "Błąd: Zakończono pobieranie, ale nie można odnaleźć pliku audio na dysku."

    except Exception as e:
        return f"Błąd podczas pobierania audio z YouTube: {str(e)}"

@mcp.tool()
def transcribe_local_audio(file_path: str) -> str:
    """
    Transkrybuje audio z podanej ścieżki pliku na dysku, używając modelu Whisper ('base').
    Dynamicznie wykrywa wsparcie dla sprzętu.
    """
    try:
        if not os.path.exists(file_path):
            return f"Błąd: Plik nie istnieje pod ścieżką: {file_path}"
            
        # BARDZO WAŻNE: Dynamiczne wykrywanie sprzętu (GPU vs CPU)
        if torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"
            
        # Ładowanie modelu Whisper w zadeklarowanym rozmiarze "base" i na odpowiednim urządzeniu
        model = whisper.load_model("base", device=device)
        
        # Rozpoczęcie transkrypcji
        result = model.transcribe(file_path)
        transcribed_text = result.get("text", "")

        # Czyszczenie plików tymczasowych po transkrypcji
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            # Usuń folder tymczasowy jeśli pusty
            parent = os.path.dirname(file_path)
            if os.path.isdir(parent) and not os.listdir(parent):
                shutil.rmtree(parent)
        except Exception:
            pass  # Nie blokuj wyniku jeśli cleanup się nie uda

        return transcribed_text

    except Exception as e:
        return f"Błąd podczas transkrypcji pliku audio: {str(e)}"

if __name__ == "__main__":
    # Uruchomienie serwera MCP (standard IO)
    mcp.run()
