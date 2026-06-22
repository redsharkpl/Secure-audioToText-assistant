import subprocess
import sys
import os

def main():
    print("Rozpoczynanie skanowania bezpieczeństwa Semgrep (szukanie wycieków sekretów)...")
    try:
        # Uruchamiamy semgrep ze statyczną analizą na podstawie .semgrep.yaml
        # Flaga --error sprawia, że Semgrep zwraca błąd (exit code 1) jeśli znajdzie reguły
        result = subprocess.run(["uv", "run", "semgrep", "scan", "--config", ".semgrep.yaml", "--error"], check=False)
        
        if result.returncode != 0:
            print("\n[BŁĄD BEZPIECZEŃSTWA] Skanowanie wykryło twardo zakodowane sekrety (API Keys) w kodzie!")
            print("Zatrzymaj proces (np. commit) i niezwłocznie przenieś klucze do pliku .env!")
            sys.exit(1)
            
        print("\n[SUKCES] Brak wykrytych sekretów w kodzie. Repozytorium jest bezpieczne.")
        sys.exit(0)
    except FileNotFoundError:
        print("[BŁĄD] Nie znaleziono narzędzia uv/semgrep. Upewnij się, że jest zainstalowane.")
        sys.exit(1)

if __name__ == "__main__":
    main()
