import streamlit as st
import asyncio
import os
import tempfile
import glob
import shutil
from fpdf import FPDF
from main import run_pipeline

st.set_page_config(
    page_title="Secure Audio-Vision Assistant by redshark-pl",
    page_icon="🔐",
    layout="wide"
)

st.markdown("""
<style>
/* === DARK BACKGROUND === */
.stApp {
    background: linear-gradient(135deg, #0d0d1a 0%, #1a0a2e 50%, #0d0d1a 100%);
    color: #e0e0ff;
}

/* === SIDEBAR === */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #13002b 0%, #1e0a3c 100%);
    border-right: 1px solid #7c3aed44;
}
[data-testid="stSidebar"] * { color: #c4b5fd !important; }

/* === GŁÓWNY TYTUŁ === */
h1 { 
    background: linear-gradient(90deg, #818cf8, #c084fc, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5rem !important;
    font-weight: 800 !important;
}

/* === NAGŁÓWKI SEKCJI === */
h2, h3 { color: #c084fc !important; }

/* === TEKST PODSTAWOWY === */
p, label, .stMarkdown { color: #cbd5e1 !important; }

/* === POLE TEKSTOWE INPUT === */
.stTextInput input {
    background: #1e1b4b !important;
    border: 1px solid #4f46e5 !important;
    border-radius: 8px !important;
    color: #e0e7ff !important;
    padding: 10px 14px !important;
}
.stTextInput input:focus {
    border-color: #818cf8 !important;
    box-shadow: 0 0 0 3px #818cf833 !important;
}

/* === PRZYCISK GŁÓWNY (Rozpocznij Analizę) === */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px 28px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 20px #7c3aed44 !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #6366f1, #9333ea) !important;
    box-shadow: 0 6px 28px #9333ea66 !important;
    transform: translateY(-1px) !important;
}

/* === PRZYCISK DOWNLOAD PDF === */
.stDownloadButton > button {
    background: linear-gradient(135deg, #0ea5e9, #38bdf8) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 16px #0ea5e944 !important;
}

/* === RADIO BUTTONS === */
.stRadio label { color: #a5b4fc !important; }
.stRadio [data-testid="stMarkdownContainer"] p { color: #a5b4fc !important; }

/* === SUCCESS BOX === */
.stSuccess { 
    background: #052e16 !important; 
    border-left: 4px solid #22c55e !important;
    color: #86efac !important;
}

/* === ERROR BOX === */
.stError { 
    background: #2d0000 !important; 
    border-left: 4px solid #ef4444 !important;
    color: #fca5a5 !important;
}

/* === EXPANDER === */
.streamlit-expanderHeader {
    background: #1e1b4b !important;
    border: 1px solid #4f46e544 !important;
    border-radius: 8px !important;
    color: #a5b4fc !important;
}
.streamlit-expanderContent {
    background: #13102d !important;
    border: 1px solid #4f46e533 !important;
    color: #cbd5e1 !important;
}

/* === SEKCJA RAPORTU === */
[data-testid="stMarkdown"] h1,
[data-testid="stMarkdown"] h2,
[data-testid="stMarkdown"] h3 {
    color: #c084fc !important;
}

/* === SPINNER === */
.stSpinner > div { border-top-color: #818cf8 !important; }

/* === SEPARATOR === */
hr { border-color: #4f46e533 !important; }

/* === FILE UPLOADER === */
.stFileUploader {
    background: #1e1b4b !important;
    border: 2px dashed #4f46e5 !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

if "pipeline_logs" not in st.session_state:
    st.session_state["pipeline_logs"] = []

st.markdown("<h1>Secure Audio-Vision Assistant <span style='font-weight: normal !important; font-size: 0.6em;'>by redshark-pl</span></h1>", unsafe_allow_html=True)
st.markdown("Aplikacja do bezpiecznej analizy multimediów. Główne funkcje: **Bezpieczna transkrypcja audio, wydobywanie tekstu ze zdjęć (OCR) oraz bezwzględna cenzura PII**.")

st.sidebar.header("Ustawienia modelu")
selected_model = st.sidebar.selectbox(
    "Wybierz model LLM:", 
    [
        "gemini-3.5-flash",       # Free tier — wysoki limit RPD
        "gemini-3.1-flash-lite",  # Free tier — wysoki limit RPD
        "gemini-2.5-flash",       # Popularny — niski limit RPD
        "gemini-2.5-pro",         # Premium — niski limit RPD
        "gemini-2.0-flash",       # Legacy — niski limit RPD
    ]
)

st.sidebar.header("Wybór wejścia")
input_mode = st.sidebar.radio("Jakie dane chcesz przeanalizować?", ["Podaj link YouTube", "Wgraj plik (Audio/Obraz/Dokument)"])

input_path = None
temp_file_to_delete = None
enable_redaction = True  # domyślnie włączona

if input_mode == "Podaj link YouTube":
    yt_link = st.text_input("Link do filmu na YouTube:")
    if yt_link:
        input_path = yt_link

    # Radio z wyborem cenzury — ZAWSZE widoczne w trybie YouTube
    redaction_choice = st.radio(
        "Czy chcesz włączyć cenzurę danych wrażliwych (PII)?",
        [
            "Tak — cenzuruj (spotkanie biznesowe, dane klientów)",
            "Nie — zachowaj oryginalne nazwy (film, serial, podcast)",
        ],
        index=0,
    )
    enable_redaction = redaction_choice.startswith("Tak")
else:
    uploaded_file = st.file_uploader("Przeciągnij lub wybierz plik", type=["mp3", "wav", "m4a", "mp4", "mkv", "png", "jpg", "jpeg", "pdf", "docx", "txt"])
    if uploaded_file is not None:
        # Tymczasowe zapisanie pliku, by węzeł Router mógł go odczytać po ścieżce
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        input_path = temp_file_path
        temp_file_to_delete = temp_file_path

    # Radio z wyborem cenzury — ZAWSZE widoczne w trybie pliku
    redaction_choice = st.radio(
        "Czy chcesz włączyć cenzurę danych wrażliwych (PII)?",
        [
            "Tak — cenzuruj (spotkanie biznesowe, dane klientów)",
            "Nie — zachowaj oryginalne nazwy (film, serial, podcast)",
        ],
        index=0,
    )
    enable_redaction = redaction_choice.startswith("Tak")


def generate_pdf(text: str) -> bytes:
    """Generuje PDF z treścią raportu z pełną obsługą polskich znaków UTF-8."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Systemowa czcionka Arial — pełne UTF-8 z polskimi znakami
    pdf.add_font("Arial", fname=r"C:\Windows\Fonts\arial.ttf")
    pdf.set_font("Arial", size=11)

    pdf.multi_cell(0, 6, text)

    # output() w fpdf2 zwraca bytearray — konwertujemy na bytes dla st.download_button
    return bytes(pdf.output())


def cleanup_temp_audio():
    """Usuwa foldery yt_audio_* z Temp jeśli jeszcze istnieją"""
    temp_dir = os.environ.get("TEMP", os.path.join(os.path.expanduser("~"), 
                                                     "AppData", "Local", "Temp"))
    for folder in glob.glob(os.path.join(temp_dir, "yt_audio_*")):
        try:
            shutil.rmtree(folder)
        except Exception:
            pass


if st.button("Rozpocznij Analizę", type="primary"):
    if not input_path:
        st.warning("Proszę podać link lub wgrać plik przed rozpoczęciem analizy.")
    elif not os.path.exists("mcp_server.py"):
        st.error(
            "🔴 Nie znaleziono pliku mcp_server.py w katalogu projektu!\n\n"
            "Upewnij się, że uruchamiasz aplikację z głównego katalogu projektu."
        )
    else:
        # Inicjalizacja stanu na nowe uruchomienie
        st.session_state["pipeline_logs"] = []
        st.session_state.pop("final_summary", None)
        st.session_state.pop("analysis_done", None)
        st.session_state.pop("last_error", None)
        st.session_state["stop_requested"] = False

        cancel_placeholder = st.empty()
        log_placeholder = st.empty()

        def ui_log(msg):
            st.session_state["pipeline_logs"].append(msg)
            log_placeholder.markdown(
                "```\n" + "\n".join(st.session_state["pipeline_logs"]) + "\n```"
            )
            # Pokazujemy przycisk przerwania tylko, gdy napotkano błąd rate limit
            if "429" in msg or "rate limit" in msg.lower():
                if cancel_placeholder.button("🔴 Przerwij proces i czekanie na API", key=f"cancel_{len(st.session_state['pipeline_logs'])}", type="primary"):
                    st.session_state["stop_requested"] = True
                    st.stop() # Zatrzymuje skrypt Streamlit i uruchamia bloki finally
            else:
                cancel_placeholder.empty()

        with st.spinner("Agenty pracują (Router -> Redactor -> Summarizer)..."):
            try:
                # Wykonanie asynchronicznej logiki grafu z main.py w pętli Streamlita
                result = asyncio.run(run_pipeline(
                    input_path, 
                    enable_redaction=enable_redaction, 
                    log_callback=ui_log, 
                    model_name=selected_model
                ))

                # Zapisz wyniki do session_state
                st.session_state["final_summary"] = result.get("final_summary", "Brak podsumowania.")
                st.session_state["analysis_done"] = True

                # Jeśli sukces: logi znikają z ekranu
                log_placeholder.empty()
                st.success("Analiza zakończona pomyślnie!")

            except Exception as e:
                st.session_state["last_error"] = str(e)
                st.error(f"Wystąpił błąd podczas przetwarzania: {e}")

            finally:
                # Sprzątanie po uploadzie
                if temp_file_to_delete and os.path.exists(temp_file_to_delete):
                    try:
                        os.remove(temp_file_to_delete)
                    except Exception:
                        pass
                
                cleanup_temp_audio()

# Wyświetlanie raportu z session_state — przeżywa rerender po "Pobierz PDF"
if st.session_state.get("analysis_done"):
    st.subheader("Ostateczny Raport Analityczny")
    st.markdown(st.session_state["final_summary"])

    # Przycisk pobierania raportu jako PDF
    st.download_button(
        label="📄 Pobierz raport jako PDF",
        data=generate_pdf(st.session_state["final_summary"]),
        file_name="raport_analityczny.pdf",
        mime="application/pdf",
    )

# Jeśli błąd i nie zakończono sukcesem — zachowaj logi widoczne na ekranie
if st.session_state.get("last_error") and not st.session_state.get("analysis_done"):
    st.subheader("Dziennik zdarzeń (Logi błędu)")
    st.markdown("```\n" + "\n".join(st.session_state.get("pipeline_logs", [])) + "\n```")
    st.error(f"Analiza przerwana: {st.session_state['last_error']}")
