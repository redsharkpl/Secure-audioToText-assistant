# -*- coding: utf-8 -*-
import os
import sys
from typing import Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import google.genai as genai

# Absolutne ścieżki — krytyczne dla poprawnego uruchomienia podprocesu MCP
_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MCP_SERVER_PATH = os.path.join(_PROJECT_DIR, "mcp_server.py")
_PYTHON_EXECUTABLE = sys.executable  # Zawsze wskazuje na interpreter z aktywnego .venv

async def call_mcp_tool(tool_name: str, **kwargs):
    """Pomocnicza funkcja do komunikacji z lokalnym serwerem MCP za pomocą standardowych wejść/wyjść."""
    server_params = StdioServerParameters(
        command=_PYTHON_EXECUTABLE,   # .venv\Scripts\python.exe — ma wszystkie zależności
        args=[_MCP_SERVER_PATH],      # Absolutna ścieżka do mcp_server.py
    )
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=kwargs)
                # Zwracanie tekstu z narzędzia MCP (zazwyczaj znajduje się w pierwszym bloku text)
                return result.content[0].text
    except* Exception as eg:
        # ExceptionGroup z TaskGroup — wypisz każdy błąd z grupy czytelnie
        errors = "\n  ".join(str(e) for e in eg.exceptions)
        error_msg = (
            f"[MCP ERROR] Nie można uruchomić serwera MCP.\n"
            f"  Interpreter: {_PYTHON_EXECUTABLE}\n"
            f"  Serwer:      {_MCP_SERVER_PATH}\n"
            f"  Narzędzie:   {tool_name}\n"
            f"  Błędy z TaskGroup:\n  {errors}"
        )
        print(error_msg)
        raise RuntimeError(error_msg) from eg

async def router_node(input_path: str, log_callback=None, model_name: str = "gemini-2.0-flash") -> Dict[str, Any]:
    def _log(msg):
        print(msg)
        if log_callback:
            log_callback(msg)

    _log(f"\n[ROUTER] Analizowanie wejscia: {input_path}")
    
    ext = os.path.splitext(input_path.lower())[1]
    raw_text = ""
    
    # 1. ŚCIEŻKA AUDIO / YOUTUBE (MCP)
    if input_path.startswith("http") or ext in [".mp3", ".wav", ".mp4", ".mkv", ".m4a"]:
        _log("[ROUTER] Wykryto Audio/Wideo. Laczenie z lokalnym serwerem MCP...")
        file_path = input_path
        
        if input_path.startswith("http"):
            _log(f"[ROUTER] -> MCP: Pobieranie z YouTube ({input_path})")
            file_path = await call_mcp_tool("download_youtube_audio", url=input_path)
            _log(f"[ROUTER] Zapisano plik jako: {file_path}")
            
        _log("[ROUTER] -> MCP: Uruchamianie Whisper (z wykrywaniem GPU)")
        raw_text = await call_mcp_tool("transcribe_local_audio", file_path=file_path)
        
    elif ext in [".png", ".jpg", ".jpeg", ".webp"]:
        import re
        _log(f"[ROUTER] Wykryto Obraz. OCR via Gemini (model: {model_name})...")
        client = genai.Client()
        prompt = "Odczytaj i przepisz bardzo dokładnie cały tekst z tego zdjęcia, w tym pismo odręczne"
        _log("[ROUTER] Wysylanie pliku do analizy Gemini...")
        
        try:
            uploaded_file = client.files.upload(file=input_path)
            response = client.models.generate_content(
                model=model_name,
                contents=[uploaded_file, prompt])
            extracted_text = response.text
        except Exception as e:
            _log(f"[ROUTER] Błąd podczas OCR: {e}")
            extracted_text = None
            
        if not extracted_text:
            extracted_text = "[BŁĄD API: Model nie zwrócił tekstu. Prawdopodobnie osiągnięto limit zapytań (Rate Limit). Zmień model na inny.]"
            
        raw_text = re.sub(r'```(?:markdown)?', '', extracted_text)
        
    # 3. ŚCIEŻKA DOKUMENTY (Natywnie)
    elif ext in [".pdf", ".docx", ".txt"]:
        _log("[ROUTER] Wykryto Dokument.")
        if ext == ".txt":
            _log("[ROUTER] Odczytywanie pliku tekstowego...")
            with open(input_path, "r", encoding="utf-8") as f:
                raw_text = f.read()
        elif ext == ".pdf":
            _log("[ROUTER] Odczyt PDF za pomocą PyMuPDF...")
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(input_path)
                pages_text = []
                for page_num, page in enumerate(doc, start=1):
                    page_text = page.get_text("text")
                    if page_text.strip():
                        pages_text.append(f"--- Strona {page_num} ---\n{page_text}")
                doc.close()
                raw_text = "\n\n".join(pages_text)
                if not raw_text.strip():
                    raw_text = "[PDF nie zawiera tekstu — dokument może być skanem/obrazem. Spróbuj OCR.]"
                _log(f"[ROUTER] Wydobyto tekst z {len(pages_text)} stron PDF.")
            except Exception as e:
                _log(f"[ROUTER] BLAD odczytu PDF: {e}")
                raw_text = f"[Błąd odczytu PDF: {e}]"
        elif ext == ".docx":
            _log("[ROUTER] Odczyt DOCX za pomocą python-docx...")
            try:
                from docx import Document
                doc = Document(input_path)
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                raw_text = "\n".join(paragraphs)
                if not raw_text.strip():
                    raw_text = "[Dokument DOCX jest pusty lub nie zawiera tekstu.]"
                _log(f"[ROUTER] Wydobyto {len(paragraphs)} akapitów z DOCX.")
            except Exception as e:
                _log(f"[ROUTER] BLAD odczytu DOCX: {e}")
                raw_text = f"[Błąd odczytu DOCX: {e}]"
            
    else:
        _log("[ROUTER] OSTRZEZENIE: Nieznany format pliku.")
        raw_text = "Nieznany format pliku."

    _log(f"[ROUTER] Wyciagnieto {len(raw_text)} znakow. Przekazywanie do wezla Redactor.")
    return {"raw_text": raw_text}
