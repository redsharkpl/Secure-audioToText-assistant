# Secure Audio-Vision Assistant 🛡️🎙️

[🇪🇺 Read in English](#English-version) | [🇵🇱 Czytaj po polsku](#wersja-polska)

---

## 🇪🇺 English Version

Enterprise-grade, multimodal business assistant built on the latest **Google ADK 2.0** framework (scaffolded with `agents-cli`). The application automates transcription, document analysis, and structured insight extraction from audio-visual materials, with an absolute focus on corporate data privacy (**Data Privacy**) and codebase security (**Codebase Security**).

### 📂 Project Structure

```text
Secure-audioToText-assistant/
├── agents/                  # Core DAG logic nodes
│   ├── router_agent.py      # Input unification (YT, Audio, OCR)
│   ├── redactor_agent.py    # Zero-temperature Sanitary Filter (PII & Prompt Injection)
│   └── summarizer_agent.py  # Analytical engine using Proportional Density
├── skills/                  # Agent skills and groundings
│   └── summarizer/SKILL.md  # Core business rules for the Summarizer
├── main.py                  # Main ADK DAG Workflow definition
├── mcp_server.py            # Local Model Context Protocol server (Whisper & yt-dlp)
├── ui.py                    # Streamlit web dashboard
├── pyproject.toml           # uv dependency management
├── Makefile                 # Task automation scripts
└── .semgrep.yaml            # Static application security testing rules

---

🏗️ System Architecture (DAG Workflow)
The system is designed as a Directed Acyclic Graph (DAG) orchestrated by the Google ADK engine:

1. Multimodal Router: Supports YouTube links, local audio files, and Native Vision OCR for images/PDF documents.

2. Sanitary Filter (Redactor): Detects and masks Personally Identifiable Information (PII) and neutralizes Prompt Injection attacks.

3. Advanced Summarizer: Utilizes Agent Skills architecture based on Grounding techniques to generate structured business reports with a mandatory Markdown table for Action Items.

---

🔒 Security Core
- PII Anonymization: Unconditional replacement of sensitive data with [MASKED_PII].

- Prompt Injection Shield: Isolation of user text within hard <TEXT> XML tags.

- Local MCP Server: Speech transcription is processed 100% locally via Whisper (NVIDIA CUDA accelerated).

- Codebase Security: Integration with Semgrep and Git pre-commit hooks to block hardcoded API keys.

---

🚀 Quick Start & Installation
Ensure you have uv (Astral package manager) installed.

1. Clone the repository:
   git clone <your-repo-link>
   cd Secure-audioToText-assistant

2.Environment Variables: Create a .env file in the root directory:
   GEMINI_API_KEY=Your_Gemini_API_Key

3. Start the application in terminal:
- macOS / Linux / Windows (with make):
   make run-ui

- Windows (without make):
   uv run streamlit run ui.py

4. Stop the application in terminal:
   Ctrl+C in the terminal where the application is running.

---

🛠️ Project Management & CommandsWe use a Makefile to simplify long commands. If you don't have make, you can run the equivalent underlying commands:

> **Windows users:** Install `make` via `winget install GnuWin32.Make`
> or use the equivalent commands from the table below:

| Automation Shortcut    | Underlying Terminal Command                     | Functional Description                                        |
|------------------------|-------------------------------------------------|---------------------------------------------------------------|
| `make run-ui`          | `uv run streamlit run ui.py`                    | Launches the Streamlit Web Dashboard                          |
| `make check-security`  | `uv run semgrep scan --config .semgrep.yaml`    | Executes local static code security validation                |
| `make clean`           | `rm -rf __pycache__ .pytest_cache`              | Purges Python cache and temp files                            |
| *(agents-cli)*         | `agents-cli deploy`                             | Deploys the built agent to the Agent Runtime                  |
| *(agents-cli)*         | `agents-cli publish gemini-enterprise`          | Registers the deployed agent to Gemini Enterprise             |
| *(agents-cli)*         | `agents-cli scaffold enhance`                   | Automatically injects CI/CD pipelines & Terraform infra       |
| *(agents-cli)*         | `agents-cli infra cicd`                         | Triggers one-command setup of production CI/CD pipelines      |
| *(agents-cli)*         | `agents-cli scaffold upgrade`                   | Upgrades core framework files while preserving customizations |

###Made by redshark-pl

-------------------------------------
-------------------------------------

## 🇵🇱 Wersja polska

Enterprise-grade, multimodalny asystent biznesowy zbudowany w oparciu o najnowszy framework Google ADK 2.0 (wygenerowany przy użyciu agents-cli). Aplikacja automatyzuje proces transkrypcji, analizy dokumentów oraz wyciągania ustrukturyzowanych wniosków z materiałów audio-wizualnych, kładąc bezwzględny nacisk na prywatność danych korporacyjnych (Data Privacy) oraz bezpieczeństwo bazy kodowej (Codebase Security).

📂 Struktura Projektu

Secure-audioToText-assistant/
├── agents/                  # Główne węzły logiczne DAG
│   ├── router_agent.py      # Unifikacja wejścia (YT, Audio, OCR)
│   ├── redactor_agent.py    # Filtr sanitarny (cenzura PII i ochrona Prompt Injection)
│   └── summarizer_agent.py  # Silnik analityczny (Proportional Density)
├── skills/                  # Umiejętności i reguły agentów
│   └── summarizer/SKILL.md  # Instrukcje biznesowe dla Summarizera
├── main.py                  # Definicja przepływu grafu (Workflow) w ADK
├── mcp_server.py            # Lokalny serwer narzędziowy (Whisper i yt-dlp)
├── ui.py                    # Interfejs graficzny Streamlit (Dashboard)
├── pyproject.toml           # Zarządzanie zależnościami przez uv
├── Makefile                 # Automatyzacja poleceń
└── .semgrep.yaml            # Reguły skanera bezpieczeństwa kodu

---

🏗️ Architektura Systemu (Graf DAG)
System to Skierowany Graf Acykliczny (DAG) sterowany silnikiem Google ADK:

1. Wielokanałowy Router: Obsługuje linki YouTube, lokalne pliki dźwiękowe oraz natywne optyczne rozpoznawanie znaków (Vision OCR) dla PDF i zdjęć.

2. Filtr Sanitarny (Redactor): Wykrywa i maskuje dane wrażliwe (PII) oraz neutralizuje złośliwe komendy sterujące (Prompt Injection).

3. Zaawansowany Summarizer: Wykorzystuje architekturę Agent Skills i reguły Proportional Density do generowania ustrukturyzowanych raportów wraz z tabelą Action Items.

---

🔒 Funkcje Bezpieczeństwa
- Anonimizacja PII: Zastępowanie danych wrażliwych znacznikami [MASKOWANE_PII].

- Prompt Injection Shield: Izolacja tekstu użytkownika wewnątrz twardych tagów XML <TEXT>.

- Lokalny Serwer MCP: Transkrypcja odbywa się w 100% lokalnie (akceleracja NVIDIA CUDA), chroniąc nagrania przed wyciekiem.

- Codebase Security: Integracja ze skanerem Semgrep oraz blokadami Git chroniącymi przed wyciekiem kluczy API.

---

🚀 Wymagania i Instalacja
- Przed uruchomieniem upewnij się, że posiadasz zainstalowane:

- uv: Nowoczesny i szybki menedżer środowisk wirtualnych Pythona.

- google-agents-cli: Narzędzie instalowane globalnie komendą uv tool install google-agents-cli

- Google Cloud SDK: Skonfigurowane środowisko do zarządzania infrastrukturą GCP.

---

🚀 Szybki start i instalacja
Upewnij się, że posiadasz nowoczesny menedżer pakietów uv.

1. Sklonuj repozytorium:
   git clone <twój-link-do-repozytorium>
   cd Secure-audioToText-assistant

2. Zmienne środowiskowe: Utwórz plik .env w głównym katalogu projektu:
   GEMINI_API_KEY=Twój_Klucz_API_Gemini

3. Uruchomienie aplikacji w terminalu:
   - macOS / Linux / Windows (z zainstalowanym make):
      make run-ui
   - Windows (bez narzędzia make):
      .\.venv\Scripts\python -m streamlit run ui.py

4. Zatrzymanie aplikacji w terminalu:
   - **Naciśnij** Ctrl + C w oknie terminala, w którym działa aplikacja (skrót uniwersalny dla wszystkich systemów operacyjnych).

---

🛠️ Zarządzanie i AutomatyzacjaDla wygody długie komendy systemowe zostały zaszyte w pliku Makefile. Jeśli nie posiadasz narzędzia make, możesz używać pełnych poleceń:

| Komenda (Make)      | Pełne polecenie                            | Opis                                           |
| ------------------- | ------------------------------------------ | ---------------------------------------------- |
| make run-ui         | uv run streamlit run ui.py                 | Uruchamia interfejs Streamlit                  |
| make check-security | uv run semgrep scan --config .semgrep.yaml | Skanowanie kodu pod kątem bezpieczeństwa       |
| make clean          | rm -rf __pycache__ .pytest_cache           | Usuwa cache Pythona                            |
| (komenda CLI)       | agents-cli deploy                          | Wdraża agenta do Agent Runtime                 |
| (komenda CLI)       | agents-cli publish gemini-enterprise       | Rejestruje agenta w Gemini Enterprise          |
| (komenda CLI)       | agents-cli scaffold enhance                | Dodaje potoki CI/CD i infrastrukturę Terraform |
| (komenda CLI)       | agents-cli infra cicd                      | Konfiguruje architekturę CI/CD                 |
| (komenda CLI)       | agents-cli scaffold upgrade                | Aktualizuje framework z zachowaniem zmian      |

Uwaga: Projekt jest w pełni kompatybilny z narzędziem agents-cli. Wdrożenie do chmury Google Cloud można przeprowadzić standardowymi komendami agents-cli deploy oraz agents-cli scaffold enhance.

### Stworzone przez redshark-pl
