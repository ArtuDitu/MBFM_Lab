# Praktyczna Analiza Danych Eye-Tracking i EEG w Pythonie

[![Otwórz w GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ArtuDitu/MBFM_Lab?quickstart=1)

Materiały do zajęć praktycznych z analizy danych okulograficznych (*eye-tracking*, ET) i elektroencefalograficznych (EEG). Całość działa **w przeglądarce** dzięki GitHub Codespaces – nie musisz niczego instalować na swoim komputerze. Dostajesz gotowe środowisko z Pythonem, VS Code, Jupyterem i wszystkimi potrzebnymi bibliotekami (MNE-Python, PyPREP, MNE-BIDS, NumPy, pandas, SciPy, Matplotlib, seaborn, Plotly, scikit-learn).

**Czego się nauczysz?**

* oczyszczać surowe dane z eye-trackera i wykrywać fiksacje oraz sakady,
* wizualizować ruchy oczu (ścieżki wzroku, mapy cieplne) i analizować obszary zainteresowania (AOI),
* przetwarzać sygnał EEG: filtrować, wykrywać złe kanały, usuwać artefakty metodą ICA,
* liczyć potencjały wywołane (ERP) i analizować oscylacje w dziedzinie czas–częstotliwość,
* łączyć oba rodzaje danych i liczyć potencjały wywołane fiksacją (FRP).

---

## 🚀 Szybki start: uruchomienie w przeglądarce (GitHub Codespaces)

1. **Zaloguj się na [github.com](https://github.com)** (lub załóż bezpłatne konto). Jako student możesz dołączyć do [GitHub Education](https://education.github.com/students) – dostaniesz m.in. większy darmowy limit Codespaces.
2. **Otwórz stronę tego repozytorium** (link od prowadzącego).
3. Kliknij zielony przycisk **`<> Code`** nad listą plików.
4. Przejdź na zakładkę **Codespaces**.
5. Kliknij **Create codespace on main**.

   > Możesz też po prostu kliknąć niebieski przycisk **Open in GitHub Codespaces** na górze tej strony.

6. **Poczekaj na przygotowanie środowiska.** Przy pierwszym uruchomieniu trwa to ok. 3–5 minut: GitHub buduje kontener i instaluje pakiety. Kolejne uruchomienia zajmują kilkanaście sekund.
7. W przeglądarce otworzy się **VS Code**. W panelu terminala zobaczysz, że w tle pobiera się zestaw danych EEG (ok. 1,6 GB). Nie czekaj na koniec – zacznij od notebooków 01 i 02, które go nie potrzebują.
8. W panelu plików po lewej otwórz `notebooks/01_et_preprocessing.ipynb`.
9. **Wybierz jądro (kernel):** kliknij **Select Kernel** w prawym górnym rogu notebooka → **Python Environments…** → **Python 3.10** (`/usr/local/bin/python`).
10. **Uruchamiaj komórki** po kolei klawiszami **Shift + Enter** albo wszystkie naraz przyciskiem **Run All**.

### Powrót do pracy na kolejnych zajęciach

**Nie twórz za każdym razem nowego codespace'a** – Twoje zmiany zostają w tym, który już masz. Wejdź na [github.com/codespaces](https://github.com/codespaces) i kliknij swój codespace albo ponownie użyj przycisku **Open in GitHub Codespaces** (zaproponuje wznowienie istniejącego środowiska).

---

## 💻 Praca w lokalnym VS Code połączonym z Codespace

Jeśli wolisz pracować w VS Code zainstalowanym na swoim komputerze (szybszy edytor, własne skróty klawiszowe), możesz połączyć go z codespace'em. **Obliczenia nadal wykonują się w chmurze**, więc nie musisz instalować Pythona ani bibliotek.

1. Zainstaluj [Visual Studio Code](https://code.visualstudio.com/).
2. W VS Code otwórz panel rozszerzeń (**Ctrl + Shift + X**, na macOS **Cmd + Shift + X**), wyszukaj **GitHub Codespaces** i zainstaluj je.
3. Zaloguj się do GitHuba: kliknij ikonę konta w lewym dolnym rogu → **Sign in with GitHub** i potwierdź w przeglądarce.
4. Połącz się z codespace'em w jeden z trzech sposobów:
   * **Z przeglądarki:** w otwartym codespace kliknij menu **☰** (lewy górny róg) → **Open in VS Code Desktop**.
   * **Z VS Code:** naciśnij **F1** (lub **Ctrl + Shift + P**) → wpisz **Codespaces: Connect to Codespace** → wybierz swój codespace.
   * **Ze strony** [github.com/codespaces](https://github.com/codespaces): przy swoim codespace kliknij **…** → **Open in** → **Visual Studio Code**.
5. Gdy w lewym dolnym rogu VS Code pojawi się napis **Codespaces: …**, jesteś połączony. Rozszerzenia Python i Jupyter zainstalują się automatycznie po stronie codespace'a.

<details>
<summary><b>Praca w pełni lokalna (bez Codespaces) – dla zaawansowanych</b></summary>

* **Z kontenerem:** zainstaluj Docker oraz rozszerzenie *Dev Containers*, sklonuj repozytorium i wybierz **Dev Containers: Reopen in Container**. Konfiguracja jest w `.devcontainer/devcontainer.json`.
* **Bez kontenera:** potrzebujesz Pythona 3.10. W katalogu repozytorium:

  ```bash
  python3.10 -m venv .venv
  source .venv/bin/activate          # Windows: .venv\Scripts\activate
  pip install -r requirements.txt
  python skrypty/pobierz_dane_eeg.py  # zestaw danych EEG (ok. 1,6 GB)
  jupyter lab
  ```

</details>

---

## 📓 Notebooki

Notebooki najlepiej przerabiać po kolei. Każdy kończy się podsumowaniem, **pięcioma zadaniami powtórkowymi** i literaturą. Zadania nie wprowadzają nowych metod – powtarzają kroki z notebooka – i każde kończy się jednym wynikiem do oddania: liczbą w podanym formacie albo jedną figurą.

| Notebook | Temat | Dane | Czas |
|---|---|---|---|
| [`01_et_preprocessing.ipynb`](notebooks/01_et_preprocessing.ipynb) | Wstępne przetwarzanie danych eye-trackingowych | symulowane | ok. 90 min |
| [`02_et_wizualizacje.ipynb`](notebooks/02_et_wizualizacje.ipynb) | Ścieżki wzroku, mapy cieplne i analiza AOI | symulowane | ok. 90 min |
| [`03_eeg_preprocessing.ipynb`](notebooks/03_eeg_preprocessing.ipynb) | Wstępne przetwarzanie EEG w MNE-Python | `mne.datasets.sample` | ok. 90–120 min |
| [`04_eeg_erp_i_spektrum.ipynb`](notebooks/04_eeg_erp_i_spektrum.ipynb) | Potencjały wywołane i analiza czas–częstotliwość | `mne.datasets.sample` | ok. 90 min |
| [`05_laczenie_et_eeg.ipynb`](notebooks/05_laczenie_et_eeg.ipynb) | Łączenie ET i EEG: potencjały wywołane fiksacją (FRP) | symulowane | ok. 90–120 min |

**01 · Wstępne przetwarzanie danych ET.** Wczytujemy surowe próbki z eye-trackera (czas, współrzędne X i Y, średnica źrenicy), sprawdzamy jakość nagrania, usuwamy mrugnięcia razem z artefaktami na ich brzegach i interpolujemy brakujące dane. Po wygładzeniu sygnału (filtr Savitzky'ego–Golaya) liczymy prędkość kątową i implementujemy krok po kroku algorytm **I-VT**, który dzieli zapis na fiksacje i sakady. Wynik weryfikujemy główną sekwencją sakad, analizą wrażliwości na próg i porównaniem z „prawdą” z symulacji.

**02 · Wizualizacje i AOI.** Na danych 40 osób oglądających plakat reklamowy rysujemy **ścieżki wzroku** (także interaktywne, w Plotly) i **mapy cieplne** oparte na estymacji jądrowej gęstości (KDE), m.in. porównując wpływ szerokości jądra. Następnie definiujemy obszary zainteresowania (AOI) i liczymy **Time to First Fixation (TTFF)**, **Dwell Time**, liczbę fiksacji i wizyt, a na koniec testem statystycznym sprawdzamy, jak zadanie zmienia sposób oglądania (efekt Yarbusa).

**03 · Wstępne przetwarzanie EEG.** Pracujemy z obiektem `mne.io.Raw` na danych z zestawu `mne.datasets.sample`. Wykrywamy złe kanały biblioteką **PyPREP** i interpolujemy je, stosujemy filtr sieciowy (**50 Hz** w Polsce, 60 Hz w USA – skąd pochodzą dane) i pasmowoprzepustowy **1–40 Hz**, przechodzimy na **referencję do średniej** i usuwamy mrugnięcia oraz artefakty mięśniowe metodą **ICA**. Dla chętnych: zapis danych w standardzie **BIDS** (MNE-BIDS).

**04 · ERP i analiza widmowa.** Wycinamy epoki wokół bodźców wzrokowych (`mne.Epochs`), liczymy **potencjały wywołane** i rysujemy je z zacienionym **błędem standardowym**. Mapy topograficzne (`plot_topomap`) pokazują, że wczesne komponenty (P1, N1) są silniejsze nad półkulą przeciwną do pola widzenia, w którym pojawił się bodziec. Na koniec wykonujemy **analizę czas–częstotliwość falkami Morleta** (`tfr_morlet`): moc i spójność fazy między próbami (ITC).

**05 · Łączenie ET i EEG.** Synchronizujemy zegary eye-trackera i wzmacniacza EEG na podstawie wspólnych triggerów (z korektą dryfu zegarów), przenosimy fiksacje i mrugnięcia do zapisu EEG i klasyfikujemy fiksacje jako fiksacje na celu lub na dystraktorze w zadaniu wyszukiwania wzrokowego. Po usunięciu artefaktów ocznych liczymy **potencjały wywołane fiksacją (FRP)**: odpowiedź lambda i P300. Porównujemy cele z dystraktorami (mapy topograficzne, test t, test permutacyjny oparty na klastrach) i omawiamy typowe pułapki analizy FRP.

> Notebook 04 korzysta z danych oczyszczonych w notebooku 03 (`wyniki/03_sample_eeg_oczyszczone_raw.fif`). Jeśli ich nie ma, użyje wersji zapasowej z zestawu `sample`.

---

## 🗂️ Struktura repozytorium

```
.
├── .devcontainer/
│   └── devcontainer.json      # konfiguracja środowiska Codespaces (Python 3.10 + pakiety + rozszerzenia)
├── dane/                      # dane symulowane (opis kolumn: dane/README.md)
├── notebooks/                 # 5 notebooków z zajęć
├── skrypty/
│   ├── generuj_dane.py        # generator danych symulowanych (dla prowadzących)
│   └── pobierz_dane_eeg.py    # pobranie zestawu mne.datasets.sample
├── wyniki/                    # tu notebooki zapisują wyniki (tworzony automatycznie, nie trafia do repozytorium)
├── requirements.txt           # lista pakietów Python z wersjami
└── README.md
```

## 📊 Dane

* **Dane symulowane** (notebooki 01, 02 i 05) są w katalogu `dane/`. Mają realistyczne właściwości (szum, mrugnięcia, dryf zegarów, artefakty oczne), a ponieważ zostały wygenerowane, znamy „prawdę” i możemy sprawdzić, czy nasze metody ją odtwarzają. Opis plików i kolumn: [`dane/README.md`](dane/README.md).
* **Zestaw `sample` z MNE-Python** (notebooki 03 i 04) to prawdziwy zapis MEG/EEG ([opis zestawu](https://mne.tools/stable/documentation/datasets.html#sample)). Pobiera się automatycznie do katalogu `~/mne_data` (ok. 1,6 GB do pobrania, ok. 2,7 GB na dysku).

## 💾 Jak nie stracić swojej pracy?

* Pliki w codespace **zostają zapisane** po jego zatrzymaniu – po wznowieniu wszystko będzie na miejscu.
* Nieużywany codespace **zatrzymuje się sam** po 30 minutach bezczynności, a po dłuższym czasie nieużywania (domyślnie 30 dni) jest **usuwany**.
* Aby zachować rozwiązania na stałe, zapisz je na GitHubie: panel **Source Control** (ikona rozgałęzienia po lewej) → wpisz opis → **Commit** → **Sync Changes**. Jeśli nie masz uprawnień do tego repozytorium, VS Code zaproponuje utworzenie **forka** (własnej kopii) – zgódź się. Możesz też pobrać pojedyncze pliki: prawy przycisk myszy na pliku → **Download…**

## ⏱️ Limity GitHub Codespaces

Konta osobiste mają miesięczny bezpłatny limit czasu pracy i miejsca na dysku. Obecnie jest to:

* **GitHub Free:** 120 „godzin rdzeniowych” (czyli ok. **60 godzin** pracy na maszynie 2-rdzeniowej) i 15 GB-miesięcy miejsca,
* **GitHub Pro** (dostępny też w pakiecie GitHub Education): 180 godzin rdzeniowych (ok. 90 godzin) i 20 GB-miesięcy.

Aktualne wartości sprawdzisz w [dokumentacji GitHub](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces). Aby oszczędzać limit:

* po zajęciach zatrzymaj codespace: [github.com/codespaces](https://github.com/codespaces) → **…** → **Stop codespace**,
* usuń codespace'y, których już nie potrzebujesz (**…** → **Delete**),
* wybieraj maszynę 2-rdzeniową – w zupełności wystarcza na tych zajęciach.

## 🛠️ Rozwiązywanie problemów

| Problem | Rozwiązanie |
|---|---|
| Notebook nie widzi jądra albo pyta o kernel | **Select Kernel** → **Python Environments…** → **Python 3.10** (`/usr/local/bin/python`). |
| `ModuleNotFoundError: No module named ...` | W terminalu (**Ctrl + `**): `pip install --user -r requirements.txt`, potem **Restart** jądra. |
| Notebook 03 długo pobiera dane albo pobieranie się nie powiodło | W terminalu: `python skrypty/pobierz_dane_eeg.py`, a po zakończeniu uruchom notebook ponownie. |
| Jądro się „wywróciło” (*kernel died*) albo działa bardzo wolno | Zamknij nieużywane notebooki (każdy zajmuje pamięć), zrestartuj jądro i uruchom komórki od początku. |
| Wykresy Plotly się nie wyświetlają | Upewnij się, że rozszerzenie Jupyter jest włączone, i przeładuj okno (**F1** → **Developer: Reload Window**). |
| Coś „zepsułem” w notebooku | Przywróć oryginał: prawy przycisk na pliku w panelu **Source Control** → **Discard Changes**. |


## 📚 Literatura podstawowa

* Holmqvist, K., Nyström, M., Andersson, R., Dewhurst, R., Jarodzka, H., i van de Weijer, J. (2011). *Eye tracking: A comprehensive guide to methods and measures*. Oxford University Press.
* Luck, S. J. (2014). *An introduction to the event-related potential technique* (wyd. 2). MIT Press.
* Cohen, M. X. (2014). *Analyzing neural time series data: Theory and practice*. MIT Press.
* Gramfort, A., i in. (2013). MEG and EEG data analysis with MNE-Python. *Frontiers in Neuroscience, 7*, 267.
* Dimigen, O., Sommer, W., Hohlfeld, A., Jacobs, A. M., i Kliegl, R. (2011). Coregistration of eye movements and EEG in natural reading: Analyses and review. *Journal of Experimental Psychology: General, 140*(4), 552–572.
* Dokumentacja MNE-Python: <https://mne.tools>

## Licencja

Kod i materiały udostępniono na licencji MIT (zob. [LICENSE](LICENSE)). Zestaw danych `sample` jest rozpowszechniany przez projekt MNE-Python na jego własnych warunkach.
