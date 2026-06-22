# -*- coding: utf-8 -*-
import asyncio
import os
import google.genai as genai
from google.genai import types
from typing import Dict, Any
from agents.retry_helper import call_gemini_with_retry
from utils.helpers import is_rate_limit_error

async def summarizer_node(clean_text: str, log_callback=None, model_name: str = "gemini-2.0-flash") -> Dict[str, Any]:
    def _log(msg):
        print(msg)
        if log_callback:
            log_callback(msg)

    _log("\n[SUMMARIZER] Otrzymano bezpieczny tekst. Inicjalizacja architektury Proportional Density...")
    
    if not clean_text or clean_text.strip() == "":
        _log("[SUMMARIZER] Tekst po cenzurze jest pusty. Zwracanie pustego podsumowania.")
        return {"final_summary": "Brak danych do podsumowania."}

    # Sprawdz czy tekst z redactora to komunikat bledu — nie wysylaj go do LLM
    if clean_text.startswith("[BLAD CENZURY]"):
        _log("[SUMMARIZER] Tekst wejsciowy to komunikat bledu z Redactora. Pomijanie generowania raportu.")
        return {"final_summary": "[BLAD PIPELINE] Nie mozna wygenerowac raportu — etap cenzury zakonczyl sie bledem. Sprobuj ponownie za chwile."}

    # Wczytywanie pliku SKILL.md jako tzw. Grounding / System Prompt
    # Upewniamy sie, ze sciezka trafia w skills/summarizer/SKILL.md
    base_dir = os.path.dirname(os.path.dirname(__file__))
    skill_path = os.path.join(base_dir, "skills", "summarizer", "SKILL.md")
    
    try:
        with open(skill_path, "r", encoding="utf-8") as f:
            skill_content = f.read()
            # Zastapienie polskich znakow na ASCII aby uniknac bledu w naglowkach HTTP
            skill_content = skill_content.encode("ascii", errors="replace").decode("ascii")
    except Exception as e:
        _log(f"[SUMMARIZER] BLAD podczas ladowania regul SKILL.md: {e}")
        skill_content = "Przygotuj rzetelny i kompleksowy raport analityczny."

    def get_gemini_model(model_name: str, sys_instr: str = None):
        import os
        if model_name.startswith("gemini-1.5"):
            # Stary SDK — obsługuje v1
            import google.generativeai as genai_old
            genai_old.configure(api_key=os.getenv("GEMINI_API_KEY"))
            if sys_instr:
                return genai_old.GenerativeModel(model_name, system_instruction=sys_instr), "old"
            return genai_old.GenerativeModel(model_name), "old"
        else:
            # Nowy SDK — gemini-2.0, gemini-2.5
            from google import genai as genai_new
            client = genai_new.Client(api_key=os.getenv("GEMINI_API_KEY"))
            return client, "new"

    client_or_model, sdk_type = get_gemini_model(model_name, skill_content)
    
    prompt = f"Oto przefiltrowany tekst do analizy i podsumowania:\n\n<TEXT>\n{clean_text}\n</TEXT>"
    
    try:
        _log("[SUMMARIZER] Weryfikacja regul i generowanie KOMPLEKSOWEGO RAPORTU ANALITYCZNEGO...")
        final_summary = await call_gemini_with_retry(
            client_or_model=client_or_model,
            model=model_name,
            sdk_type=sdk_type,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=skill_content,
                temperature=0.2  # Niska temperatura minimalizuje halucynacje i ulatwia trzymanie sie formatu
            ),
            max_retries=5,
            label="SUMMARIZER",
            log_callback=log_callback,
        )
    except Exception as e:
        is_rate_limit = is_rate_limit_error(e)
        if is_rate_limit:
            _log(f"[SUMMARIZER] Błąd rate limit (429). Oczekiwanie 60 sekund z odliczaniem...")
            import streamlit as st
            for i in range(60, 0, -1):
                if st.session_state.get("stop_requested", False):
                    raise InterruptedError("Użytkownik zatrzymał proces")
                if log_callback:
                    log_callback(f"[CZEKAM] Rate limit — wznowienie za {i}s...")
                await asyncio.sleep(1)
            
            _log("[SUMMARIZER] Ponawianie próby (ostatnia szansa)...")
            try:
                final_summary = await call_gemini_with_retry(
                    client_or_model=client_or_model,
                    model=model_name,
                    sdk_type=sdk_type,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=skill_content,
                        temperature=0.2
                    ),
                    max_retries=1,
                    label="SUMMARIZER",
                    log_callback=log_callback,
                )
            except Exception as e2:
                _log(f"[SUMMARIZER] BLAD API podczas generowania podsumowania (po ostatniej probie): {e2}")
                final_summary = "[BLAD SUMMARIZERA] System wstrzymal tworzenie raportu z powodu bledu silnika LLM. Sprobuj ponownie za kilka minut."
        else:
            _log(f"[SUMMARIZER] BLAD API podczas generowania podsumowania (po retry): {e}")
            final_summary = "[BLAD SUMMARIZERA] System wstrzymal tworzenie raportu z powodu bledu silnika LLM. Sprobuj ponownie za kilka minut."

    _log(f"[SUMMARIZER] Sukces! Wygenerowano raport o dlugosci {len(final_summary)} znakow.")
    return {"final_summary": final_summary}
