#!/usr/bin/env python
"""
Pobiera zestaw danych „sample” z MNE-Python (ok. 1,6 GB), używany w notebookach 03 i 04.

W GitHub Codespaces skrypt uruchamia się automatycznie po utworzeniu środowiska.
Można go też uruchomić ręcznie (np. gdy pobieranie zostało przerwane):

    python skrypty/pobierz_dane_eeg.py

Dane trafiają do katalogu ~/mne_data. Jeśli zestaw jest już pobrany, skrypt kończy się natychmiast.
"""

import sys
import time


def main():
    try:
        import mne
    except ImportError:
        print("Nie znaleziono pakietu MNE. Najpierw zainstaluj pakiety: pip install --user -r requirements.txt")
        return 1

    print("Pobieram zestaw danych EEG „sample” z MNE-Python (ok. 1,6 GB) – to może potrwać kilka minut.")
    print("W tym czasie możesz pracować z notebookami 01 i 02 (eye-tracking).")
    start = time.time()
    try:
        sciezka = mne.datasets.sample.data_path()
    except Exception as blad:  # np. brak połączenia z serwerem
        print(f"\nNie udało się pobrać danych: {blad}")
        print("Spróbuj ponownie później poleceniem: python skrypty/pobierz_dane_eeg.py")
        return 1

    print(f"\nGotowe ({time.time() - start:.0f} s). Dane EEG są w katalogu: {sciezka}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
