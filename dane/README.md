# Dane do zajęć

Wszystkie pliki w tym katalogu to **dane symulowane**, wygenerowane skryptem [`skrypty/generuj_dane.py`](../skrypty/generuj_dane.py). Mają typowe właściwości prawdziwych nagrań, a ponieważ znamy parametry symulacji, możemy sprawdzić, czy metody analizy odtwarzają „prawdę”.

Notebooki 03 i 04 korzystają dodatkowo z prawdziwego zestawu **`mne.datasets.sample`** (MEG + EEG), który pobiera się automatycznie do `~/mne_data` (skrypt [`skrypty/pobierz_dane_eeg.py`](../skrypty/pobierz_dane_eeg.py)).

## Stanowisko badawcze (wspólne dla wszystkich danych ET)

| parametr | wartość |
|---|---|
| rozdzielczość monitora | 1920 × 1080 px, punkt (0, 0) to **lewy górny** róg ekranu |
| fizyczny rozmiar ekranu | 53,1 × 29,9 cm (24″, 16:9) |
| odległość oczu od ekranu | 60 cm |
| 1° kąta widzenia (środek ekranu) | ≈ 37,9 px |

## Notebooki 01–02: oglądanie plakatu reklamowego

**`bodziec_plakat.png`** – bodziec: fikcyjny plakat kawy „NeuroKawa” (1920 × 1080 px, wyświetlany na całym ekranie przez 10 s). Obszary zainteresowania (AOI) jako prostokąty `(x0, y0, x1, y1)` w pikselach:

| AOI | x0 | y0 | x1 | y1 |
|---|---|---|---|---|
| Logo | 80 | 60 | 300 | 320 |
| Hasło | 560 | 95 | 1800 | 235 |
| Twarz | 230 | 400 | 630 | 830 |
| Produkt | 1000 | 340 | 1420 | 830 |
| Cena | 1515 | 435 | 1865 | 785 |
| Przycisk | 760 | 890 | 1160 | 1010 |

**`et_surowe_uczestnik01.csv`** – surowe próbki eye-trackera jednej osoby (500 Hz, 10 s, 5000 wierszy):

| kolumna | opis |
|---|---|
| `czas_ms` | znacznik czasu eye-trackera [ms], liczony od włączenia urządzenia (co 2 ms) |
| `x_px`, `y_px` | położenie wzroku na ekranie [px] |
| `zrenica_mm` | średnica źrenicy [mm] |

Puste pola (`NaN`) oznaczają brak danych: 3 mrugnięcia (120–230 ms) i 4 krótkie utraty sygnału (2–8 ms). Pierwsza próbka odpowiada pojawieniu się plakatu.

**`et_fiksacje_grupa.csv`** – raport fiksacji 40 osób (jeden wiersz = jedna fiksacja):

| kolumna | opis |
|---|---|
| `uczestnik` | identyfikator osoby: `U01`–`U40` |
| `warunek` | `swobodne` (U01–U20, swobodne oglądanie) lub `ocena_ceny` (U21–U40, instrukcja: „Oceń, czy produkt jest tani”) |
| `nr_fiksacji` | numer kolejny fiksacji danej osoby |
| `start_ms`, `koniec_ms` | początek i koniec fiksacji [ms] od pojawienia się bodźca |
| `czas_trwania_ms` | czas trwania fiksacji [ms] |
| `x_px`, `y_px` | położenie fiksacji [px] |

Fiksacje osoby `U01` to dokładnie te fiksacje, z których wygenerowano surowe próbki w `et_surowe_uczestnik01.csv` – w notebooku 01 służą jako „prawda” do oceny algorytmu I-VT.

## Notebook 05: wyszukiwanie wzrokowe z jednoczesnym zapisem EEG i ET

Paradygmat: 80 prób. Każda próba to krzyżyk fiksacyjny (0,5–0,7 s), następnie ekran z 10 elementami (1 cel „T”, 9 dystraktorów „L”), który znika po naciśnięciu przycisku, i przerwa ok. 1–1,3 s. Badany swobodnie porusza oczami.

**`eeg_wyszukiwanie_raw.fif`** – zapis EEG w formacie MNE (ok. 289 s, 250 Hz, jednostki: V):

* 32 kanały EEG w układzie BioSemi 32 (nazwy systemu 10–20: `Fp1`, `AF3`, …, `Fz`, `Cz`) z zapisanymi położeniami elektrod,
* `HEOG`, `VEOG` – kanały EOG (ruchy oczu w poziomie i w pionie),
* `STI` – kanał triggerów: `11` początek próby, `12` pojawienie się ekranu wyszukiwania, `13` reakcja, `99` trigger testowy (tylko w EEG – wysłany przed startem eye-trackera).

**`et_wyszukiwanie_triggery.csv`** – te same triggery zapisane przez eye-tracker:

| kolumna | opis |
|---|---|
| `czas_et_ms` | znacznik czasu eye-trackera [ms] |
| `kod` | kod triggera (`11`, `12`, `13`) |
| `opis` | `START_PROBY`, `BODZIEC`, `REAKCJA` |

**`et_wyszukiwanie_zdarzenia.csv`** – zdarzenia wykryte przez eye-tracker (557 fiksacji i 44 mrugnięcia):

| kolumna | opis |
|---|---|
| `typ` | `fiksacja` lub `mrugniecie` |
| `start_et_ms`, `koniec_et_ms` | początek i koniec zdarzenia w zegarze eye-trackera [ms] |
| `czas_trwania_ms` | czas trwania [ms] |
| `x_px`, `y_px` | średnie położenie fiksacji [px] (puste dla mrugnięć) |
| `proba` | numer próby (1–80), do której eye-tracker przypisał zdarzenie |

**`et_wyszukiwanie_bodzce.csv`** – położenie elementów na każdym ekranie (80 prób × 10 elementów):

| kolumna | opis |
|---|---|
| `proba` | numer próby |
| `element` | numer elementu (1–10) |
| `x_px`, `y_px` | środek elementu [px] |
| `typ` | `cel` lub `dystraktor` |

## Parametry symulacji („prawda”) – dla prowadzących

<details>
<summary>Rozwiń</summary>

**Eye-tracking (notebooki 01–02)**

* Czas trwania sakad zgodny z główną sekwencją D = 2,2·A + 21 ms (Carpenter, 1988); profil prędkości minimalnego szarpnięcia (*minimum jerk*) z lekką krzywizną toru.
* Szum pomiarowy położenia: σ = 1,4 px (ok. 0,04°) plus powolny dryf oka w trakcie fiksacji.
* Mrugnięcia z artefaktami brzegowymi: przez 40 ms przed luką i 70 ms po niej pozorny spadek średnicy źrenicy i przesunięcie pozycji Y.
* Źrenica: odruch na jasny bodziec według funkcji odpowiedzi źrenicy (Hoeks i Levelt, 1993) – maksymalne zwężenie ok. 0,45 mm po ok. 0,9 s – oraz trwałe zwężenie 0,2 mm i wolne fluktuacje.
* Wybór kolejnych AOI: model salientności z hamowaniem powrotu (*inhibition of return*). Twarze przyciągają wzrok szczególnie w pierwszych 1,5 s, a w warunku `ocena_ceny` wzrasta atrakcyjność ceny. Hasło jest „czytane” serią fiksacji od lewej do prawej.

**EEG + ET (notebook 05)**

* **Odpowiedź lambda** po każdej fiksacji: +7 µV przy 95 ms i −3,5 µV przy 170 ms, rozkład potyliczny (środek w Oz). Amplituda rośnie z amplitudą poprzedzającej sakady i jest mniejsza dla fiksacji na pustym ekranie.
* **P300** tylko po **pierwszej** fiksacji na celu: +6 µV przy 380 ms (σ = 90 ms), rozkład ciemieniowy (środek w Pz), zmienna amplituda między próbami.
* Odpowiedź wzrokowa na pojawienie się ekranu (P1/N1, potylicznie).
* Artefakty oczne: dipol rogówkowo-siatkówkowy 15 µV/° w HEOG/VEOG z propagacją do elektrod czołowych; mrugnięcia o amplitudzie ok. 180 µV w VEOG.
* Tło EEG: przestrzennie skorelowany szum 1/f z log-normalną obwiednią amplitudy, rytm alfa (ok. 10 Hz, potylicznie, słabszy podczas przeszukiwania ekranu), szum czujników, zakłócenia sieci 50 Hz i wolny dryf potencjału.
* Zegary: eye-tracker zaczyna nagrywać 3,5 s po EEG, a jego zegar „spieszy się” o **50 ppm**. Triggery w eye-trackerze mają opóźnienie 0–1 ms i rozdzielczość 1 ms.
* Fiksacje na celu trwają dłużej (średnio ok. 420 ms) niż na dystraktorach (ok. 230 ms), jak w prawdziwych badaniach wyszukiwania wzrokowego.

Ponowne wygenerowanie danych: `python skrypty/generuj_dane.py`. Ziarno generatora (`ZIARNO`) ustalono na stałe, więc pliki są za każdym razem identyczne. Zmiana ziarna daje nowy zestaw danych.

</details>
