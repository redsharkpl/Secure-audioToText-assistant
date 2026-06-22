# -*- coding: utf-8 -*-
"""Retry helper z exponential backoff dla wywolań Gemini API.

Obsługuje błędy 429 RESOURCE_EXHAUSTED (przekroczenie limitu) poprzez
automatyczne ponawianie z rosnącym opóźnieniem.
"""
import asyncio
import re


async def call_gemini_with_retry(
    client_or_model,
    model: str,
    contents,
    config,
    sdk_type: str = "new",
    max_retries: int = 5,
    base_delay: float = 2.0,
    label: str = "GEMINI",
    log_callback=None,
) -> str:
    """Wywołuje Gemini API z automatycznym retry przy błędach 429.

    Args:
        client_or_model: Instancja genai.Client() dla nowego SDK lub GenerativeModel dla starego
        model: Nazwa modelu (np. 'gemini-2.5-flash')
        contents: Treść zapytania
        config: GenerateContentConfig
        sdk_type: "new" lub "old"
        max_retries: Maksymalna liczba prób (domyślnie 5)
        base_delay: Bazowe opóźnienie w sekundach (domyślnie 2s)
        label: Etykieta do logów (np. 'REDACTOR', 'SUMMARIZER')
        log_callback: Opcjonalna funkcja callback do logowania w UI

    Returns:
        Tekst odpowiedzi z API

    Raises:
        Exception: Jeśli wszystkie próby się nie powiodą
    """
    import streamlit as st

    def _log(msg):
        print(msg)
        if log_callback:
            log_callback(msg)

    last_exception = None

    for attempt in range(1, max_retries + 1):
        try:
            if sdk_type == "old":
                import google.generativeai as genai_old
                temperature = config.temperature if hasattr(config, 'temperature') else 0.0
                gen_config = genai_old.types.GenerationConfig(temperature=temperature)
                # old sdk expects just the string or list of parts
                response = client_or_model.generate_content(
                    contents=contents,
                    generation_config=gen_config
                )
                return response.text.strip()
            else:
                response = client_or_model.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config,
                )
                return response.text.strip()
        except Exception as e:
            last_exception = e
            error_str = str(e)

            # Sprawdz czy to błąd 429 (rate limit) — jedyny typ do retry
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                # Sprobuj wyciagnac sugerowany czas oczekiwania z bledu API
                retry_delay = _extract_retry_delay(error_str)
                if retry_delay is None:
                    # Exponential backoff: 2s, 4s, 8s, 16s, 32s
                    retry_delay = base_delay * (2 ** (attempt - 1))

                if attempt < max_retries:
                    _log(
                        f"[{label}] Blad 429 (rate limit) - proba {attempt}/{max_retries}. "
                        f"Oczekiwanie {retry_delay:.1f}s przed ponowna proba..."
                    )
                    delay_int = int(retry_delay)
                    for i in range(delay_int, 0, -1):
                        if st.session_state.get("stop_requested", False):
                            raise InterruptedError("Użytkownik zatrzymał proces")
                        await asyncio.sleep(1)
                    if retry_delay - delay_int > 0:
                        await asyncio.sleep(retry_delay - delay_int)
                else:
                    _log(
                        f"[{label}] Blad 429 - wyczerpano wszystkie {max_retries} prob."
                    )
                    raise
            else:
                # Inny błąd — nie ponawiamy, rzucamy od razu
                _log(f"[{label}] Blad API (nie-429): {e}")
                raise

    # Nie powinno tu dotrzeć, ale na wszelki wypadek
    raise last_exception


def _extract_retry_delay(error_str: str) -> float | None:
    """Wyciąga sugerowany czas retry z komunikatu błędu Gemini API.

    Szuka wzorców typu 'retry in 993.848812ms' lub 'retryDelay: 1s'.
    """
    # Wzorzec: "retry in XXXms" lub "retry in X.XXXs"
    match = re.search(r"retry in ([\d.]+)(ms|s)", error_str, re.IGNORECASE)
    if match:
        value = float(match.group(1))
        unit = match.group(2).lower()
        if unit == "ms":
            return max(value / 1000.0, 1.0)  # minimum 1s
        else:
            return max(value, 1.0)

    # Wzorzec: "retryDelay': 'Xs'" 
    match = re.search(r"retryDelay['\"]?:\s*['\"]?(\d+)s", error_str)
    if match:
        return max(float(match.group(1)), 1.0)

    return None
