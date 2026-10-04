#!/usr/bin/env python
"""
Generator symulowanych danych do kursu
„Praktyczna Analiza Danych Eye-Tracking i EEG w Pythonie”.

Uruchomienie (z katalogu głównego repozytorium):

    python skrypty/generuj_dane.py

Skrypt zapisuje w katalogu ``dane/``:

* ``bodziec_plakat.png``            – bodziec do notebooków 01–02 (plakat 1920×1080 px),
* ``et_surowe_uczestnik01.csv``     – surowe próbki eye-trackera (500 Hz) uczestnika U01,
* ``et_fiksacje_grupa.csv``         – raport fiksacji 40 uczestników w dwóch warunkach,
* ``eeg_wyszukiwanie_raw.fif``      – symulowany zapis EEG (32 kanały + 2 EOG + kanał STI),
* ``et_wyszukiwanie_zdarzenia.csv`` – fiksacje i mrugnięcia wykryte przez eye-tracker,
* ``et_wyszukiwanie_triggery.csv``  – znaczniki (triggery) zapisane przez eye-tracker,
* ``et_wyszukiwanie_bodzce.csv``    – położenie elementów na ekranach wyszukiwania.

Wszystkie losowania korzystają ze stałego ziarna (``ZIARNO``), więc kolejne
uruchomienia dają identyczne pliki. Zmiana ziarna daje nowy, równie realistyczny
zestaw danych (np. osobny dla każdej grupy zajęciowej).

Dane są symulowane, ale ich parametry oparto na literaturze, m.in.:
główna sekwencja sakad (Carpenter, 1988), odruch źreniczny (Hoeks i Levelt, 1993),
odpowiedź lambda i P300 w potencjałach wywołanych fiksacją (Dimigen i in., 2011;
Kamienkowski i in., 2012).
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # rysowanie bez okna (działa także na serwerze)
import matplotlib.pyplot as plt  # noqa: E402
import mne  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib import patches  # noqa: E402
from scipy import signal  # noqa: E402

ZIARNO = 2026
KATALOG_DANYCH = Path(__file__).resolve().parents[1] / "dane"

# ---------------------------------------------------------------------------
# Geometria stanowiska badawczego (taka sama we wszystkich notebookach)
# ---------------------------------------------------------------------------
EKRAN_SZER_PX, EKRAN_WYS_PX = 1920, 1080  # rozdzielczość monitora
EKRAN_SZER_CM = 53.1  # szerokość monitora 24" 16:9
ODLEGLOSC_CM = 60.0  # odległość oczu od ekranu
# Ile pikseli przypada na 1 stopień kąta widzenia w centrum ekranu (≈ 37,9 px)
PX_NA_STOPIEN = EKRAN_SZER_PX / EKRAN_SZER_CM * ODLEGLOSC_CM * np.tan(np.deg2rad(1))


def czas_sakady_ms(amplituda_deg):
    """Czas trwania sakady wg „głównej sekwencji” (Carpenter, 1988): D = 2,2·A + 21 ms."""
    return 2.2 * amplituda_deg + 21.0


# ===========================================================================
# CZĘŚĆ 1. Plakat reklamowy (bodziec do notebooków 01–02)
# ===========================================================================

# Obszary zainteresowania (AOI) jako prostokąty (x0, y0, x1, y1) w pikselach ekranu.
# Te same współrzędne są zdefiniowane w notebooku 02.
AOI = {
    "Logo": (80, 60, 300, 320),
    "Hasło": (560, 95, 1800, 235),
    "Twarz": (230, 400, 630, 830),
    "Produkt": (1000, 340, 1420, 830),
    "Cena": (1515, 435, 1865, 785),
    "Przycisk": (760, 890, 1160, 1010),
}

# „Gorące punkty” wewnątrz AOI: (środek x, środek y, rozrzut w px, waga)
GORACE_PUNKTY = {
    "Logo": [(190, 165, 22, 0.8), (190, 290, 16, 0.2)],
    "Twarz": [(365, 590, 16, 0.33), (495, 590, 16, 0.33), (430, 650, 16, 0.12), (430, 718, 18, 0.22)],
    "Produkt": [(1175, 630, 30, 0.45), (1175, 720, 35, 0.25), (1175, 440, 30, 0.30)],
    "Cena": [(1690, 585, 22, 0.75), (1690, 655, 16, 0.25)],
    "Przycisk": [(960, 952, 22, 1.0)],
}

# Względna atrakcyjność AOI w dwóch warunkach eksperymentalnych
WAGI = {
    "swobodne": {"Logo": 0.5, "Hasło": 1.5, "Twarz": 2.2, "Produkt": 1.8,
                 "Cena": 0.9, "Przycisk": 0.8, "tło": 0.5},
    "ocena_ceny": {"Logo": 0.4, "Hasło": 1.0, "Twarz": 1.2, "Produkt": 1.6,
                   "Cena": 2.4, "Przycisk": 1.1, "tło": 0.4},
}
# Mnożniki wag w pierwszych 1,5 s (twarze przyciągają wzrok „oddolnie”,
# a w warunku „ocena_ceny” uczestnicy od razu szukają ceny)
WCZESNE = {
    "swobodne": {"Twarz": 3.5, "Hasło": 1.5},
    "ocena_ceny": {"Twarz": 1.8, "Cena": 2.5},
}
# Średni czas fiksacji [ms] w zależności od AOI
CZAS_FIKSACJI = {
    "swobodne": {"Logo": 230, "Hasło": 215, "Twarz": 290, "Produkt": 270,
                 "Cena": 260, "Przycisk": 245, "tło": 190},
    "ocena_ceny": {"Logo": 230, "Hasło": 215, "Twarz": 270, "Produkt": 280,
                   "Cena": 340, "Przycisk": 250, "tło": 190},
}
# Średnia liczba dodatkowych fiksacji w obrębie jednej wizyty w AOI
DODATKOWE_FIKSACJE = {
    "swobodne": {"Logo": 0.2, "Twarz": 1.0, "Produkt": 0.6, "Cena": 0.4, "Przycisk": 0.2, "tło": 0.0},
    "ocena_ceny": {"Logo": 0.2, "Twarz": 0.7, "Produkt": 0.6, "Cena": 0.9, "Przycisk": 0.3, "tło": 0.0},
}


def gwiazdka(cx, cy, r_zew, r_wew, n_ramion):
    """Wierzchołki wielokąta w kształcie „gwiazdki promocyjnej”."""
    katy = np.linspace(0, 2 * np.pi, 2 * n_ramion, endpoint=False)
    r = np.where(np.arange(2 * n_ramion) % 2 == 0, r_zew, r_wew)
    return np.column_stack([cx + r * np.cos(katy), cy + r * np.sin(katy)])


def rysuj_plakat(sciezka):
    """Rysuje fikcyjny plakat reklamowy „NeuroKawa” w rozdzielczości ekranu."""
    fig = plt.figure(figsize=(EKRAN_SZER_PX / 100, EKRAN_WYS_PX / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, EKRAN_SZER_PX)
    ax.set_ylim(EKRAN_WYS_PX, 0)  # oś y w dół – tak jak współrzędne ekranu
    ax.axis("off")
    braz, ciemny = "#5b3a29", "#3b2418"

    # Tło i dekoracyjny pasek u dołu
    ax.add_patch(patches.Rectangle((0, 0), EKRAN_SZER_PX, EKRAN_WYS_PX, color="#f5efe4"))
    ax.add_patch(patches.Rectangle((0, 1045), EKRAN_SZER_PX, 35, color=braz))

    # Logo
    ax.add_patch(patches.Circle((190, 165), 95, color=braz))
    ax.text(190, 168, "NK", color="white", fontsize=54, fontweight="bold", ha="center", va="center")
    ax.text(190, 290, "NeuroKawa", color=braz, fontsize=22, fontweight="bold", ha="center", va="center")

    # Hasło reklamowe
    ax.text(1180, 165, "Obudź swoje neurony!", color=ciemny, fontsize=64,
            fontweight="bold", ha="center", va="center")

    # Twarz (uproszczona – twarze silnie przyciągają wzrok)
    ax.add_patch(patches.Circle((430, 620), 190, facecolor="#f2c49b", edgecolor="#c98f62", lw=4))
    katy = np.deg2rad(np.linspace(212, 328, 60))  # włosy: „czapka” nad czołem
    ax.add_patch(patches.Polygon(np.column_stack([430 + 200 * np.cos(katy), 625 + 200 * np.sin(katy)]),
                                 color="#4a2c1d"))
    for xo in (365, 495):
        ax.add_patch(patches.Ellipse((xo, 590), 64, 38, facecolor="white", edgecolor=ciemny, lw=3))
        ax.add_patch(patches.Circle((xo + 4, 592), 13, color="#3d6b8f"))
        ax.add_patch(patches.Circle((xo + 4, 592), 6, color="black"))
        ax.plot([xo - 32, xo + 30], [548, 540], color="#4a2c1d", lw=7, solid_capstyle="round")
    ax.plot([430, 415, 438], [610, 662, 666], color="#c98f62", lw=5, solid_capstyle="round")  # nos
    ax.add_patch(patches.Arc((430, 690), 160, 90, theta1=20, theta2=160, color="#a33b2f", lw=7))

    # Produkt – filiżanka kawy na spodku
    ax.add_patch(patches.Ellipse((1175, 795), 420, 56, facecolor="#e8dccb", edgecolor=braz, lw=4))
    ax.add_patch(patches.Arc((1312, 625), 120, 140, theta1=-90, theta2=90, color=braz, lw=16))
    ax.add_patch(patches.FancyBboxPatch((1040, 480), 270, 300, boxstyle="round,pad=0,rounding_size=40",
                                        facecolor="white", edgecolor=braz, lw=6))
    ax.add_patch(patches.Rectangle((1043, 595), 264, 75, color=braz))
    ax.text(1175, 633, "NEURO", color="white", fontsize=30, fontweight="bold", ha="center", va="center")
    ax.add_patch(patches.Ellipse((1175, 482), 270, 52, facecolor="#6f4e37", edgecolor=braz, lw=6))
    for x0 in (1110, 1175, 1240):  # para nad kawą
        yy = np.linspace(445, 360, 60)
        ax.plot(x0 + 12 * np.sin((yy - 360) / 85 * 2 * np.pi), yy, color="#a08c7a", lw=6,
                solid_capstyle="round")

    # Cena – „gwiazdka” promocyjna
    ax.add_patch(patches.Polygon(gwiazdka(1690, 610, 168, 140, 18), color="#d62839"))
    ax.text(1690, 585, "9,99 zł", color="white", fontsize=44, fontweight="bold", ha="center", va="center")
    ax.text(1690, 655, "PROMOCJA", color="white", fontsize=18, fontweight="bold", ha="center", va="center")

    # Przycisk „KUP TERAZ”
    ax.add_patch(patches.FancyBboxPatch((770, 900), 380, 100, boxstyle="round,pad=0,rounding_size=50",
                                        color="#2e7d32"))
    ax.text(960, 952, "KUP TERAZ", color="white", fontsize=36, fontweight="bold", ha="center", va="center")

    fig.savefig(sciezka, dpi=100)
    plt.close(fig)


def w_jakim_aoi(x, y):
    """Zwraca nazwę AOI zawierającego punkt (x, y) albo „tło”."""
    for nazwa, (x0, y0, x1, y1) in AOI.items():
        if x0 <= x <= x1 and y0 <= y <= y1:
            return nazwa
    return "tło"


def losuj_punkt(rng, aoi):
    """Losuje miejsce lądowania fiksacji w obrębie AOI (lub na tle)."""
    if aoi == "tło":
        while True:
            x, y = rng.uniform(40, EKRAN_SZER_PX - 40), rng.uniform(40, EKRAN_WYS_PX - 40)
            if w_jakim_aoi(x, y) == "tło":
                return x, y
    punkty = GORACE_PUNKTY[aoi]
    wagi = np.array([p[3] for p in punkty])
    cx, cy, rozrzut, _ = punkty[rng.choice(len(punkty), p=wagi / wagi.sum())]
    return cx + rng.normal(0, rozrzut), cy + rng.normal(0, rozrzut)


def czytanie_hasla(rng):
    """Sekwencja fiksacji przy czytaniu hasła: od lewej do prawej wzdłuż linii tekstu."""
    x0, y0, x1, y1 = AOI["Hasło"]
    y_srodek = (y0 + y1) / 2
    x = x0 + rng.uniform(40, 160)
    pozycje = []
    for _ in range(rng.integers(3, 7)):
        pozycje.append((x, y_srodek + rng.normal(0, 7)))
        x += rng.normal(195, 40)
        if x > x1 - 40:
            break
    return pozycje


def wybierz_aoi(rng, wagi, warunek, t_ms, historia):
    """Wybiera kolejne AOI (model salientności z hamowaniem powrotu)."""
    nazwy = list(wagi)
    w = np.array([wagi[n] for n in nazwy], dtype=float)
    if t_ms < 1500:
        for nazwa, mnoznik in WCZESNE[warunek].items():
            w[nazwy.index(nazwa)] *= mnoznik
    if historia:  # hamowanie powrotu (ang. inhibition of return)
        w[nazwy.index(historia[-1])] *= 0.15
        for nazwa in historia[-3:-1]:
            w[nazwy.index(nazwa)] *= 0.6
    return nazwy[rng.choice(len(nazwy), p=w / w.sum())]


def symuluj_fiksacje_plakat(rng, warunek, czas_ms=10_000):
    """Symuluje sekwencję fiksacji jednej osoby oglądającej plakat przez ``czas_ms``."""
    wagi = {k: v * rng.lognormal(0, 0.45) for k, v in WAGI[warunek].items()}
    tempo = rng.lognormal(0, 0.12)  # osobnicze tempo (dłuższe/krótsze fiksacje)
    fiksacje = []
    # Fiksacja początkowa w centrum ekranu (wcześniej był tam krzyżyk fiksacyjny)
    x, y = 960 + rng.normal(0, 10), 540 + rng.normal(0, 10)
    t = max(120.0, rng.normal(240, 50))
    fiksacje.append([0.0, t, x, y])
    historia = []
    while t < czas_ms:
        aoi = wybierz_aoi(rng, wagi, warunek, t, historia)
        if aoi == "Hasło":
            pozycje = czytanie_hasla(rng)
        else:
            n = 1 + rng.poisson(DODATKOWE_FIKSACJE[warunek][aoi])
            pozycje = [losuj_punkt(rng, aoi) for _ in range(n)]
        for nx, ny in pozycje:
            amplituda = np.hypot(nx - x, ny - y) / PX_NA_STOPIEN
            t += czas_sakady_ms(amplituda) + rng.normal(0, 2)
            if t >= czas_ms - 40:
                break
            czas = max(80.0, rng.gamma(5, CZAS_FIKSACJI[warunek][aoi] * tempo / 5))
            fiksacje.append([t, min(t + czas, czas_ms), nx, ny])
            t += czas
            x, y = nx, ny
        historia.append(aoi)
    # Zaokrąglamy czasy do 2 ms (rozdzielczość eye-trackera 500 Hz)
    fiksacje = np.array(fiksacje)
    fiksacje[:, :2] = np.round(fiksacje[:, :2] / 2) * 2
    return fiksacje


def symuluj_probki_surowe(rng, fiksacje, fs=500, czas_ms=10_000):
    """Na podstawie listy fiksacji tworzy surowy sygnał eye-trackera (x, y, źrenica)."""
    dt = 1000 / fs
    t = np.arange(0, czas_ms, dt)
    x = np.full(t.size, np.nan)
    y = np.full(t.size, np.nan)

    # 1) Fiksacje: pozycja + powolny dryf oka
    indeksy = []
    for start, koniec, fx, fy in fiksacje:
        m = (t >= start) & (t < koniec)
        n = int(m.sum())
        dryf_x, dryf_y = np.cumsum(rng.normal(0, 0.12, (2, n)), axis=1)
        x[m] = fx + dryf_x - dryf_x.mean()
        y[m] = fy + dryf_y - dryf_y.mean()
        idx = np.flatnonzero(m)
        indeksy.append((idx[0], idx[-1]))

    # 2) Sakady: profil minimalnego szarpnięcia (ang. minimum jerk) + lekka krzywizna
    for (_, kon_a), (pocz_b, _) in zip(indeksy[:-1], indeksy[1:]):
        if pocz_b - kon_a < 2:
            continue
        xs, ys, xe, ye = x[kon_a], y[kon_a], x[pocz_b], y[pocz_b]
        idx = np.arange(kon_a + 1, pocz_b)
        tau = (idx - kon_a) / (pocz_b - kon_a)
        profil = 10 * tau**3 - 15 * tau**4 + 6 * tau**5
        dlugosc = np.hypot(xe - xs, ye - ys)
        nx, ny = -(ye - ys) / dlugosc, (xe - xs) / dlugosc
        krzywizna = rng.normal(0, 0.04) * dlugosc * np.sin(np.pi * tau)
        x[idx] = xs + profil * (xe - xs) + krzywizna * nx
        y[idx] = ys + profil * (ye - ys) + krzywizna * ny

    # 3) Szum pomiarowy eye-trackera (~0,04° RMS)
    x += rng.normal(0, 1.4, t.size)
    y += rng.normal(0, 1.4, t.size)

    # 4) Średnica źrenicy: odruch na jasny bodziec + wolne fluktuacje + szum
    ts = t / 1000
    n_hl, t_max = 10.1, 0.93  # funkcja odpowiedzi źrenicy (Hoeks i Levelt, 1993)
    h = ts**n_hl * np.exp(-n_hl * ts / t_max)
    h /= h.max()
    b, a = signal.butter(2, 0.6 / (fs / 2))
    zapas = 5 * fs  # dłuższy szum i przycięcie brzegów – bez artefaktów filtracji na początku
    wolne = signal.filtfilt(b, a, rng.normal(0, 1, t.size + 2 * zapas))[zapas:-zapas]
    wolne *= 0.05 / wolne.std()
    zrenica = 3.65 - 0.45 * h - 0.20 * (1 - np.exp(-ts / 0.8)) + wolne
    zrenica += rng.normal(0, 0.012, t.size)

    # 5) Mrugnięcia: brak danych + artefakty na brzegach (powieka zasłania źrenicę)
    starty = []
    while len(starty) < 3:
        s = rng.uniform(1200, czas_ms - 900)
        if all(abs(s - s0) > 1800 for s0 in starty):
            starty.append(s)
    for start in sorted(starty):
        dlugosc = rng.uniform(120, 230)
        m = (t >= start - 40) & (t < start)  # zamykanie powieki
        w = (t[m] - (start - 40)) / 40
        zrenica[m] *= 1 - 0.45 * w**2
        y[m] += 170 * w**2
        m = (t >= start + dlugosc) & (t < start + dlugosc + 70)  # otwieranie powieki
        w = 1 - (t[m] - (start + dlugosc)) / 70
        zrenica[m] *= 1 - 0.35 * w**2
        y[m] += 120 * w**2
        m = (t >= start) & (t < start + dlugosc)
        x[m] = y[m] = zrenica[m] = np.nan

    # 6) Krótkie utraty sygnału (np. odblask w okularach)
    for _ in range(4):
        i = rng.integers(100, t.size - 100)
        x[i:i + rng.integers(1, 5)] = np.nan
        y[np.isnan(x)] = np.nan
        zrenica[np.isnan(x)] = np.nan

    zegar_startowy = 1_843_502  # znacznik czasu eye-trackera [ms] w chwili startu nagrania
    return pd.DataFrame({
        "czas_ms": (zegar_startowy + t).astype(int),
        "x_px": np.round(x, 1),
        "y_px": np.round(y, 1),
        "zrenica_mm": np.round(zrenica, 3),
    })


def generuj_dane_plakat(rng):
    rysuj_plakat(KATALOG_DANYCH / "bodziec_plakat.png")

    wiersze = []
    for nr in range(1, 41):
        warunek = "swobodne" if nr <= 20 else "ocena_ceny"
        fiksacje = symuluj_fiksacje_plakat(rng, warunek)
        if nr == 1:
            surowe = symuluj_probki_surowe(rng, fiksacje)
            surowe.to_csv(KATALOG_DANYCH / "et_surowe_uczestnik01.csv", index=False)
        for i, (start, koniec, x, y) in enumerate(fiksacje, start=1):
            wiersze.append({
                "uczestnik": f"U{nr:02d}", "warunek": warunek, "nr_fiksacji": i,
                "start_ms": int(start), "koniec_ms": int(koniec), "czas_trwania_ms": int(koniec - start),
                "x_px": round(float(x), 1), "y_px": round(float(y), 1),
            })
    pd.DataFrame(wiersze).to_csv(KATALOG_DANYCH / "et_fiksacje_grupa.csv", index=False)


# ===========================================================================
# CZĘŚĆ 2. Wyszukiwanie wzrokowe z jednoczesnym zapisem EEG i eye-trackera
# ===========================================================================

FS_EEG = 250.0  # częstotliwość próbkowania EEG [Hz]
N_PROB = 80  # liczba prób (ekranów wyszukiwania)
N_ELEMENTOW = 10  # 1 cel + 9 dystraktorów na każdym ekranie
KODY = {"start_proby": 11, "bodziec": 12, "reakcja": 13}
KOD_TESTOWY = 99  # trigger testowy wysłany, zanim eye-tracker zaczął nagrywać

# Zegary: eye-tracker zaczyna nagrywać później i jego zegar „spieszy się” o 50 ppm
START_ET_S = 3.5  # moment startu nagrania ET (w czasie zegara EEG) [s]
ZEGAR_ET_0 = 2_481_337  # znacznik czasu ET w tym momencie [ms]
DRYF_PPM = 50.0

# Rozkład pola w EEG wywołanego przez ruchy gałek ocznych (dipol rogówkowo-siatkówkowy)
PROPAGACJA_HEOG = {"F7": -0.35, "F8": 0.35, "FC5": -0.18, "FC6": 0.18, "T7": -0.12, "T8": 0.12,
                   "Fp1": -0.12, "Fp2": 0.12, "AF3": -0.08, "AF4": 0.08, "F3": -0.06, "F4": 0.06}
PROPAGACJA_VEOG = {"Fp1": 0.6, "Fp2": 0.6, "AF3": 0.45, "AF4": 0.45, "Fz": 0.25, "F3": 0.22,
                   "F4": 0.22, "F7": 0.18, "F8": 0.18, "FC1": 0.12, "FC2": 0.12, "FC5": 0.08,
                   "FC6": 0.08, "Cz": 0.05}
UV_NA_STOPIEN = 15.0  # amplituda EOG na 1° obrotu oka [µV]


def czas_et_ms(t_s):
    """Przelicza czas zegara EEG [s] na znacznik czasu eye-trackera [ms]."""
    return ZEGAR_ET_0 + (np.asarray(t_s) - START_ET_S) * 1000.0 * (1 + DRYF_PPM * 1e-6)


def rozmiesc_elementy(rng):
    """Losuje położenia elementów (minimalny odstęp 230 px)."""
    punkty = []
    while len(punkty) < N_ELEMENTOW:
        p = rng.uniform([260, 170], [1660, 910])
        if all(np.hypot(*(p - q)) > 230 for q in punkty):
            punkty.append(p)
    return np.array(punkty)


def symuluj_wyszukiwanie(rng):
    """Symuluje przebieg eksperymentu: fiksacje, mrugnięcia, triggery i ekrany."""
    fiksacje, mrugniecia, triggery, ekrany = [], [], [], []
    triggery.append((1.0, KOD_TESTOWY, 0))
    gx, gy = 960.0, 540.0  # bieżąca pozycja wzroku
    start_fiks = START_ET_S + 0.3  # początek fiksacji centralnej przed pierwszą próbą
    t = 6.0
    for proba in range(1, N_PROB + 1):
        t_start = t
        t_bodziec = t_start + rng.uniform(0.5, 0.7)
        triggery += [(t_start, KODY["start_proby"], proba), (t_bodziec, KODY["bodziec"], proba)]

        elementy = rozmiesc_elementy(rng)
        cel = rng.integers(N_ELEMENTOW)
        for i, (ex, ey) in enumerate(elementy):
            ekrany.append({"proba": proba, "element": i + 1, "x_px": round(ex, 1), "y_px": round(ey, 1),
                           "typ": "cel" if i == cel else "dystraktor"})

        # Fiksacja centralna trwa do pierwszej sakady po pojawieniu się ekranu
        t = t_bodziec + rng.uniform(0.18, 0.28)
        fiksacje.append(dict(start=start_fiks, koniec=t, x=gx, y=gy, obiekt="centrum", p300=False))

        # Kolejność przeszukiwania: kilka dystraktorów, potem cel
        n_dystr = min(rng.geometric(0.2) - 1, N_ELEMENTOW - 1)
        pozostale = [i for i in range(N_ELEMENTOW) if i != cel]
        sciezka = []
        for _ in range(n_dystr):
            odl = np.array([np.hypot(*(elementy[i] - (gx, gy))) for i in pozostale])
            p = np.exp(-odl / 350)
            wybrany = pozostale.pop(rng.choice(len(pozostale), p=p / p.sum()))
            sciezka.append(wybrany)
        sciezka.append(cel)

        for nr, element in enumerate(sciezka):
            if rng.random() < 0.12:  # czasem fiksacja na pustym tle pomiędzy elementami
                while True:
                    bx, by = rng.uniform([200, 120], [1720, 960])
                    if np.min(np.hypot(*(elementy - (bx, by)).T)) > 130:
                        break
                t += czas_sakady_ms(np.hypot(bx - gx, by - gy) / PX_NA_STOPIEN) / 1000
                czas = max(0.09, rng.gamma(6, 0.20 / 6))
                fiksacje.append(dict(start=t, koniec=t + czas, x=bx, y=by, obiekt="tło", p300=False))
                t += czas
                gx, gy = bx, by
            ex, ey = elementy[element] + rng.normal(0, 18, 2)
            t += czas_sakady_ms(np.hypot(ex - gx, ey - gy) / PX_NA_STOPIEN) / 1000
            if element == cel:
                czas = max(0.15, rng.gamma(8, 0.42 / 8))
                t_reakcja = t + czas * rng.uniform(0.6, 0.9)
                fiksacje.append(dict(start=t, koniec=t + czas, x=ex, y=ey, obiekt="cel", p300=True))
            else:
                czas = max(0.09, rng.gamma(6, 0.23 / 6))
                fiksacje.append(dict(start=t, koniec=t + czas, x=ex, y=ey, obiekt="dystraktor", p300=False))
            t += czas
            gx, gy = ex, ey
        triggery.append((t_reakcja, KODY["reakcja"], proba))

        if rng.random() < 0.25:  # ponowna fiksacja na celu (już bez P300)
            ex, ey = gx + rng.normal(0, 25), gy + rng.normal(0, 25)
            t += czas_sakady_ms(np.hypot(ex - gx, ey - gy) / PX_NA_STOPIEN) / 1000
            czas = max(0.09, rng.gamma(6, 0.25 / 6))
            fiksacje.append(dict(start=t, koniec=t + czas, x=ex, y=ey, obiekt="cel", p300=False))
            t += czas
            gx, gy = ex, ey

        # Powrót wzroku do środka ekranu w przerwie między próbami (ITI)
        cx, cy = 960 + rng.normal(0, 12), 540 + rng.normal(0, 12)
        t += czas_sakady_ms(np.hypot(cx - gx, cy - gy) / PX_NA_STOPIEN) / 1000
        gx, gy = cx, cy
        start_fiks = t
        t_nastepna = t_reakcja + rng.uniform(1.0, 1.3)
        if rng.random() < 0.6 and start_fiks + 0.15 < t_nastepna - 0.3:  # mrugnięcie w przerwie
            m_start = rng.uniform(start_fiks + 0.15, t_nastepna - 0.3)
            m_koniec = m_start + rng.uniform(0.12, 0.25)
            fiksacje.append(dict(start=start_fiks, koniec=m_start, x=gx, y=gy, obiekt="centrum", p300=False))
            mrugniecia.append(dict(start=m_start, koniec=m_koniec))
            start_fiks = m_koniec
        t = t_nastepna
    fiksacje.append(dict(start=start_fiks, koniec=t, x=gx, y=gy, obiekt="centrum", p300=False))
    return pd.DataFrame(fiksacje), pd.DataFrame(mrugniecia), triggery, pd.DataFrame(ekrany), t + 2.0


def gaussowski_rozklad(pozycje, nazwy, srodek, szerokosc):
    """Gładka topografia (rozkład na skórze głowy) o środku w punkcie ``srodek``."""
    odl = np.linalg.norm(np.array([pozycje[n] for n in nazwy]) - srodek, axis=1)
    return np.exp(-(odl**2) / (2 * szerokosc**2))


def szum_rozowy(rng, n_zrodel, n_probek):
    """Szum o widmie 1/f (typowe tło EEG), znormalizowany do wariancji 1."""
    widmo = np.fft.rfft(rng.normal(size=(n_zrodel, n_probek)), axis=1)
    f = np.fft.rfftfreq(n_probek, 1 / FS_EEG)
    f[0] = f[1]
    x = np.fft.irfft(widmo / np.sqrt(f), n=n_probek, axis=1)
    return x / x.std(axis=1, keepdims=True)


def obwiednia_lognormalna(rng, n_zrodel, n_probek, sigma=0.8, fc=0.5):
    """Wolnozmienna obwiednia amplitudy (rozkład log-normalny).

    Aktywność EEG pojawia się „paczkami” – jej amplituda zmienia się w czasie. Dzięki temu
    źródła tła nie są gaussowskie, a ICA (jak w prawdziwych danych) może je rozdzielić.
    """
    b, a = signal.butter(2, fc / (FS_EEG / 2))
    zapas = int(10 * FS_EEG)
    z = signal.filtfilt(b, a, rng.normal(size=(n_zrodel, n_probek + 2 * zapas)), axis=1)[:, zapas:-zapas]
    return np.exp(sigma * z / z.std(axis=1, keepdims=True))


def dodaj_odpowiedz(sygnal, czasy_s, wzorzec, amplitudy=None):
    """Dodaje kopie ``wzorzec`` (n_probek) zaczynające się w podanych chwilach."""
    if amplitudy is None:
        amplitudy = np.ones(len(czasy_s))
    for t0, a in zip(czasy_s, amplitudy):
        i = int(round(t0 * FS_EEG))
        n = min(len(wzorzec), len(sygnal) - i)
        sygnal[i:i + n] += a * wzorzec[:n]


def generuj_dane_wyszukiwanie(rng):
    fiksacje, mrugniecia, triggery, ekrany, czas_calk = symuluj_wyszukiwanie(rng)
    n = int(np.ceil(czas_calk * FS_EEG))
    czasy = np.arange(n) / FS_EEG

    montaz = mne.channels.make_standard_montage("biosemi32")
    kanaly = montaz.ch_names
    pozycje = montaz.get_positions()["ch_pos"]
    pos = lambda nazwa: np.asarray(pozycje[nazwa])  # noqa: E731
    eeg = np.zeros((len(kanaly), n))

    # --- 1) Tło EEG: przestrzennie skorelowany szum 1/f + rytm alfa + szum czujników
    zrodla = szum_rozowy(rng, 12, n) * obwiednia_lognormalna(rng, 12, n)
    mieszanie = np.column_stack([
        gaussowski_rozklad(pozycje, kanaly, pos(kanaly[i]), 0.05) for i in rng.choice(len(kanaly), 12)
    ])
    tlo = mieszanie @ zrodla
    eeg += 8.0 * tlo / tlo.std(axis=1, keepdims=True)

    # Alfa (~10 Hz), silniejsza przy patrzeniu na krzyżyk niż podczas przeszukiwania ekranu
    b, a = signal.butter(4, [8.5 / (FS_EEG / 2), 11.5 / (FS_EEG / 2)], btype="band")
    alfa = signal.filtfilt(b, a, rng.normal(size=n))
    alfa /= alfa.std()
    obwiednia = np.ones(n)
    kody = {k: v for v, k in KODY.items()}
    t_bodzcow = [t for t, k, _ in triggery if kody.get(k) == "bodziec"]
    t_reakcji = [t for t, k, _ in triggery if kody.get(k) == "reakcja"]
    for t0, t1 in zip(t_bodzcow, t_reakcji):
        obwiednia[(czasy >= t0 + 0.2) & (czasy < t1)] = 0.45
    obwiednia = signal.filtfilt(*signal.butter(2, 2 / (FS_EEG / 2)), obwiednia)
    rozklad_alfa = gaussowski_rozklad(pozycje, kanaly, (pos("Pz") + pos("Oz")) / 2, 0.05)
    eeg += 7.0 * np.outer(rozklad_alfa, alfa * obwiednia)
    eeg += rng.normal(0, 0.8, eeg.shape)

    # --- 2) Odpowiedzi neuronalne
    tw = np.arange(0, 0.8, 1 / FS_EEG)
    gauss = lambda mu, sd: np.exp(-((tw - mu) ** 2) / (2 * sd**2))  # noqa: E731
    lambda_wzorzec = 7.0 * gauss(0.095, 0.017) - 3.5 * gauss(0.17, 0.03)  # odpowiedź lambda
    p300_wzorzec = 6.0 * gauss(0.38, 0.09)  # P300 po rozpoznaniu celu
    vep_wzorzec = 4.0 * gauss(0.10, 0.018) - 5.0 * gauss(0.17, 0.03)  # pojawienie się ekranu

    rozklad_lambda = gaussowski_rozklad(pozycje, kanaly, pos("Oz"), 0.045)
    rozklad_p300 = gaussowski_rozklad(pozycje, kanaly, pos("Pz"), 0.06)

    # Amplituda odpowiedzi lambda rośnie z amplitudą sakady poprzedzającej fiksację
    dx = np.diff(fiksacje["x"].to_numpy(), prepend=fiksacje["x"].iloc[0])
    dy = np.diff(fiksacje["y"].to_numpy(), prepend=fiksacje["y"].iloc[0])
    amp_sakady = np.hypot(dx, dy) / PX_NA_STOPIEN
    na_ekranie = fiksacje["obiekt"].isin(["cel", "dystraktor", "tło"]).to_numpy()
    skala_lambda = np.where(na_ekranie, 1.0, 0.3) * (0.6 + 0.4 * np.clip(amp_sakady / 8, 0, 1.5))
    skala_lambda *= rng.lognormal(0, 0.25, len(fiksacje))
    przebieg = np.zeros(n)
    dodaj_odpowiedz(przebieg, fiksacje["start"], lambda_wzorzec, skala_lambda)
    eeg += np.outer(rozklad_lambda, przebieg)

    przebieg = np.zeros(n)
    t_p300 = fiksacje.loc[fiksacje["p300"], "start"]
    dodaj_odpowiedz(przebieg, t_p300, p300_wzorzec, rng.uniform(0.5, 1.5, len(t_p300)))
    eeg += np.outer(rozklad_p300, przebieg)

    przebieg = np.zeros(n)
    dodaj_odpowiedz(przebieg, t_bodzcow, vep_wzorzec)
    eeg += np.outer(rozklad_lambda, przebieg)

    # --- 3) Artefakty oczne: ruchy gałek ocznych (EOG) i mrugnięcia
    gx = np.interp(czasy, np.ravel(fiksacje[["start", "koniec"]]), np.repeat(fiksacje["x"], 2))
    gy = np.interp(czasy, np.ravel(fiksacje[["start", "koniec"]]), np.repeat(fiksacje["y"], 2))
    heog = UV_NA_STOPIEN * (gx - 960) / PX_NA_STOPIEN  # spojrzenie w prawo -> wartości dodatnie
    veog = UV_NA_STOPIEN * (540 - gy) / PX_NA_STOPIEN  # spojrzenie w górę -> wartości dodatnie
    mrug = np.zeros(n)
    for _, m in mrugniecia.iterrows():
        sel = (czasy >= m["start"] - 0.05) & (czasy < m["koniec"] + 0.1)
        mrug[sel] += 180 * np.hanning(sel.sum())
    veog = veog + mrug
    for nazwa, w in PROPAGACJA_HEOG.items():
        eeg[kanaly.index(nazwa)] += w * heog
    for nazwa, w in PROPAGACJA_VEOG.items():
        eeg[kanaly.index(nazwa)] += w * veog
    eog = np.vstack([heog, veog]) + rng.normal(0, 3.0, (2, n))

    # --- 4) Zakłócenia techniczne: sieć 50 Hz i wolny dryf potencjału elektrod
    eeg += rng.uniform(0.5, 3.0, (len(kanaly), 1)) * np.sin(2 * np.pi * 50 * czasy + rng.uniform(0, 2 * np.pi))
    b, a = signal.butter(1, 0.05 / (FS_EEG / 2))
    dryf = signal.filtfilt(b, a, np.cumsum(rng.normal(0, 1, (len(kanaly), n)), axis=1), axis=1)
    eeg += 15 * dryf / dryf.std(axis=1, keepdims=True)

    # --- 5) Kanał triggerów (impulsy o długości 3 próbek)
    sti = np.zeros(n)
    for t0, kod, _ in triggery:
        i = int(round(t0 * FS_EEG))
        sti[i:i + 3] = kod

    info = mne.create_info(kanaly + ["HEOG", "VEOG", "STI"], FS_EEG,
                           ["eeg"] * len(kanaly) + ["eog", "eog", "stim"])
    raw = mne.io.RawArray(np.vstack([eeg * 1e-6, eog * 1e-6, sti]), info, verbose=False)
    raw.set_montage(montaz)
    raw.info["line_freq"] = 50.0
    raw.info["description"] = "Symulowane dane EEG: wyszukiwanie wzrokowe (kurs ET+EEG)"
    raw.save(KATALOG_DANYCH / "eeg_wyszukiwanie_raw.fif", overwrite=True, verbose=False)

    # --- 6) Pliki eksportowane z eye-trackera (zegar eye-trackera!)
    tr = pd.DataFrame(triggery, columns=["t", "kod", "proba"])
    tr = tr[tr["t"] >= START_ET_S]  # ET nie „widział” triggera testowego
    opisy = {v: k.upper() for k, v in KODY.items()}
    pd.DataFrame({
        "czas_et_ms": np.floor(czas_et_ms(tr["t"] + rng.uniform(0, 0.001, len(tr)))).astype(int),
        "kod": tr["kod"].to_numpy(),
        "opis": tr["kod"].map(opisy).to_numpy(),
    }).to_csv(KATALOG_DANYCH / "et_wyszukiwanie_triggery.csv", index=False)

    starty_prob = np.sort(tr.loc[tr["kod"] == KODY["start_proby"], "t"].to_numpy())
    zdarzenia = pd.concat([
        pd.DataFrame({"typ": "fiksacja", "start": fiksacje["start"], "koniec": fiksacje["koniec"],
                      "x_px": fiksacje["x"] + rng.normal(0, 5, len(fiksacje)),
                      "y_px": fiksacje["y"] + rng.normal(0, 5, len(fiksacje))}),
        pd.DataFrame({"typ": "mrugniecie", "start": mrugniecia["start"], "koniec": mrugniecia["koniec"],
                      "x_px": np.nan, "y_px": np.nan}),
    ]).sort_values("start")
    zdarzenia = zdarzenia[zdarzenia["start"] >= START_ET_S]
    zdarzenia = zdarzenia.assign(
        start_et_ms=np.round(czas_et_ms(zdarzenia["start"])).astype(int),
        koniec_et_ms=np.round(czas_et_ms(zdarzenia["koniec"])).astype(int),
        proba=np.searchsorted(starty_prob, zdarzenia["start"], side="right"),
    )
    zdarzenia["czas_trwania_ms"] = zdarzenia["koniec_et_ms"] - zdarzenia["start_et_ms"]
    zdarzenia = zdarzenia[zdarzenia["proba"] > 0]
    zdarzenia[["typ", "start_et_ms", "koniec_et_ms", "czas_trwania_ms", "x_px", "y_px", "proba"]].round(1).to_csv(
        KATALOG_DANYCH / "et_wyszukiwanie_zdarzenia.csv", index=False)
    ekrany.to_csv(KATALOG_DANYCH / "et_wyszukiwanie_bodzce.csv", index=False)


def main():
    KATALOG_DANYCH.mkdir(exist_ok=True)
    rng_plakat, rng_wyszukiwanie = (np.random.default_rng(s) for s in np.random.SeedSequence(ZIARNO).spawn(2))
    print("Generuję dane eye-trackingowe (plakat)...")
    generuj_dane_plakat(rng_plakat)
    print("Generuję dane EEG + eye-tracking (wyszukiwanie wzrokowe)...")
    generuj_dane_wyszukiwanie(rng_wyszukiwanie)
    print(f"Gotowe! Pliki zapisano w katalogu: {KATALOG_DANYCH}")
    for plik in sorted(KATALOG_DANYCH.iterdir()):
        print(f"  {plik.name:32s} {plik.stat().st_size / 1024:8.0f} kB")


if __name__ == "__main__":
    main()
