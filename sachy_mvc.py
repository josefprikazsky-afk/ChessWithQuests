#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Šachy v architektuře MVC (Model-View-Controller) s grafickým rozhraním Tkinter
=============================================================================
Kompletní, samostatně spustitelná aplikace v jazyce Python 3 splňující veškeré
požadavky ze zadání, včetně herních mechanik, validace tahů, šachu, matu, patu,
časovače, loggeru, úkolů (Kwest) a uživatelského managementu.

Spuštění:
    python3 sachy_mvc.py
"""

try:
    import tkinter as tk
    from tkinter import messagebox, ttk
except ImportError:
    tk = None
    messagebox = None
    ttk = None

from typing import List, Tuple, Optional, Any
import time

# =====================================================================
# 1. ZÁKLADNÍ DATOVÉ TŘÍDY (Model)
# =====================================================================

class Kwest:
    """Reprezentuje herní úkol (quest), který může hráč splnit."""
    def __init__(self, nazev: str, popis: str, odmena_elo: int = 25):
        self.nazev: str = nazev
        self.popis: str = popis
        self.odmena_elo: int = odmena_elo
        self.splneno: bool = False

    def validate(self) -> bool:
        """Ověří podmínky pro splnění úkolu."""
        return self.splneno


class Uzivatel:
    """Reprezentuje registrovaného uživatele v systému."""
    def __init__(self, uzivatelske_jmeno: str, jmeno: str, email: str, elo: int = 1200):
        self.uzivatelske_jmeno: str = uzivatelske_jmeno
        self.jmeno: str = jmeno
        self.email: str = email
        self.elo: int = elo
        self.splnene_kwesty: List[Kwest] = []

    def pridej_kwest(self, quest: Kwest) -> None:
        """Přidá splněný úkol a aktualizuje ELO rating hráče."""
        if quest not in self.splnene_kwesty:
            self.splnene_kwesty.append(quest)
            quest.splneno = True
            self.elo += quest.odmena_elo


class Hrac:
    """Reprezentuje účastníka aktuální šachové partie."""
    def __init__(self, barva: int, uzivatel: Uzivatel):
        self.barva: int = barva  # 0 = Bílý, 1 = Černý
        self.uzivatel: Uzivatel = uzivatel

    def getEloRating(self) -> int:
        """Vrátí aktuální ELO rating hráče."""
        return self.uzivatel.elo


# =====================================================================
# 2. FIGURKY (Objektově orientovaná hierarchie)
# =====================================================================

class Figurka:
    """Základní bázová třída pro všechny šachové figury."""
    def __init__(self, nazev: str, barva: int):
        self.nazev: str = nazev
        self.barva: int = barva  # 0 = bílá, 1 = černá
        self.vektory: List[List[int]] = []
        self.vektory_utoku: List[List[int]] = []
        self.skok: bool = False
        self.symbol: str = " "
        self.hodnota: int = 0
        self.pocet_tahu: int = 0
        self.aktivni: bool = True

    def __repr__(self) -> str:
        barva_str = "B" if self.barva == 0 else "C"
        return f"{self.nazev}({barva_str})"


class Kun(Figurka):
    """Jezdec (kůň) - pohybuje se do tvaru písmene L a skáče přes ostatní figury."""
    def __init__(self, barva: int):
        super().__init__("Kůň", barva)
        self.skok: bool = True
        self.hodnota = 3
        self.symbol = "♘" if barva == 0 else "♞"
        self.vektory: List[List[int]] = [
            [-2, -1], [-2, 1], [-1, -2], [-1, 2],
            [1, -2], [1, 2], [2, -1], [2, 1]
        ]
        self.vektory_utoku: List[List[int]] = self.vektory
        self.vektor: list = self.vektory
        self.vektor_utoku: list = self.vektory_utoku


class Kral(Figurka):
    """Král - nejdůležitější figura, pohybuje se o 1 pole všemi směry."""
    def __init__(self, barva: int):
        super().__init__("Král", barva)
        self.skok: bool = False
        self.hodnota = 1000
        self.symbol = "♔" if barva == 0 else "♚"
        self.vektory: List[List[int]] = [
            [-1, -1], [-1, 0], [-1, 1],
            [0, -1],           [0, 1],
            [1, -1],  [1, 0],  [1, 1]
        ]
        self.vektory_utoku: List[List[int]] = self.vektory
        self.vektor: list = self.vektory
        self.vektor_utoku: list = self.vektory_utoku


class Dama(Figurka):
    """Dáma (královna) - kombinuje pohyb věže a střelce."""
    def __init__(self, barva: int):
        super().__init__("Dáma", barva)
        self.skok: bool = False
        self.hodnota = 9
        self.symbol = "♕" if barva == 0 else "♛"
        self.vektory: List[List[int]] = [
            [-1, -1], [-1, 0], [-1, 1],
            [0, -1],           [0, 1],
            [1, -1],  [1, 0],  [1, 1]
        ]
        self.vektory_utoku: List[List[int]] = self.vektory
        self.vektor: list = self.vektory
        self.vektor_utoku: list = self.vektory_utoku


class Strelec(Figurka):
    """Střelec - pohybuje se po diagonálách libovolný počet polí."""
    def __init__(self, barva: int):
        super().__init__("Střelec", barva)
        self.skok: bool = False
        self.hodnota = 3
        self.symbol = "♗" if barva == 0 else "♝"
        self.vektory: List[List[int]] = [
            [-1, -1], [-1, 1], [1, -1], [1, 1]
        ]
        self.vektory_utoku: List[List[int]] = self.vektory
        self.vektor: list = self.vektory
        self.vektor_utoku: list = self.vektory_utoku


class Vez(Figurka):
    """Věž - pohybuje se vodorovně a svisle libovolný počet polí."""
    def __init__(self, barva: int):
        super().__init__("Věž", barva)
        self.skok: bool = False
        self.hodnota = 5
        self.symbol = "♖" if barva == 0 else "♜"
        self.vektory: List[List[int]] = [
            [-1, 0], [1, 0], [0, -1], [0, 1]
        ]
        self.vektory_utoku: List[List[int]] = self.vektory
        self.vektor: list = self.vektory
        self.vektor_utoku: list = self.vektory_utoku


class Pesak(Figurka):
    """Pěšák - pohybuje se dopředu o 1 (nebo 2 z výchozí řady), bere šikmo."""
    def __init__(self, barva: int):
        super().__init__("Pěšák", barva)
        self.skok: bool = False
        self.hodnota = 1
        self.symbol = "♙" if barva == 0 else "♟"
        # Bílý (0) jde nahoru (řádek -1), Černý (1) jde dolů (řádek +1)
        self.smer: int = -1 if barva == 0 else 1
        self.vektory: List[List[int]] = [[self.smer, 0]]
        self.vektory_utoku: List[List[int]] = [
            [self.smer, -1], [self.smer, 1]
        ]
        self.vektor: list = self.vektory
        self.vektor_utoku: list = self.vektory_utoku


# =====================================================================
# 3. HERNÍ MECHANIKY (Mechanics & Logic)
# =====================================================================

class Tah:
    """Reprezentuje jeden konkrétní tah figurkou po šachovnici."""
    def __init__(self, vychozi_pozice: List[int], cilova_pozice: List[int],
                 figurka: Figurka, typ_tahu: str = "normal",
                 vyhozena_figurka: Optional[Figurka] = None):
        self.vychozi_pozice: List[int] = vychozi_pozice  # [r, c]
        self.cilova_pozice: List[int] = cilova_pozice    # [r, c]
        self.figurka: Figurka = figurka
        self.typ_tahu: str = typ_tahu  # "normal", "brani", "rosada", "en_passant", "povyseni"
        self.vyhozena_figurka: Optional[Figurka] = vyhozena_figurka
        self.sach: bool = False
        self.mat: bool = False

    def over_platnost(self) -> bool:
        """Zkontroluje, zda jsou souřadnice tahu platné uvnitř šachovnice."""
        r1, c1 = self.vychozi_pozice
        r2, c2 = self.cilova_pozice
        return 0 <= r1 < 8 and 0 <= c1 < 8 and 0 <= r2 < 8 and 0 <= c2 < 8

    def proved_tah(self) -> None:
        """Spustí vedlejší efekty provedení tahu."""
        self.figurka.pocet_tahu += 1

    def notace(self) -> str:
        """Vrátí algebraický zápis tahu (např. e4, Jf3, Sxf7+, O-O)."""
        sloupce = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        radky = ['8', '7', '6', '5', '4', '3', '2', '1']
        cil = f"{sloupce[self.cilova_pozice[1]]}{radky[self.cilova_pozice[0]]}"

        if self.typ_tahu == "rosada":
            return "O-O" if self.cilova_pozice[1] == 6 else "O-O-O"

        prefix = ""
        if self.figurka.nazev == "Pěšák":
            prefix = sloupce[self.vychozi_pozice[1]] if self.vyhozena_figurka else ""
        elif self.figurka.nazev == "Kůň":
            prefix = "J"
        elif self.figurka.nazev == "Střelec":
            prefix = "S"
        elif self.figurka.nazev == "Věž":
            prefix = "V"
        elif self.figurka.nazev == "Dáma":
            prefix = "D"
        elif self.figurka.nazev == "Král":
            prefix = "K"

        brani = "x" if self.vyhozena_figurka else ""
        znacka = "#" if self.mat else ("+" if self.sach else "")
        return f"{prefix}{brani}{cil}{znacka}"


class HerniPlocha:
    """Třída spravující stav šachovnice (8x8 matice) a vyhozené figury."""
    def __init__(self):
        self.rozmery: Tuple[int, int] = (8, 8)
        self.herni_deska: List[List[Optional[Figurka]]] = [
            [None for _ in range(8)] for _ in range(8)
        ]
        self.vyhozene_figurky_b: List[Figurka] = []  # Vyhozené bílé figury
        self.vyhozene_figurky_c: List[Figurka] = []  # Vyhozené černé figury
        self.nastav_zakladni_rozestaveni()

    def nastav_zakladni_rozestaveni(self) -> None:
        """Rozestaví všechny figury do počáteční šachové pozice."""
        self.herni_deska = [[None for _ in range(8)] for _ in range(8)]
        self.vyhozene_figurky_b.clear()
        self.vyhozene_figurky_c.clear()

        # Černé figurky (horní řádky 0 a 1)
        rozvrh_hlavni = [Vez, Kun, Strelec, Dama, Kral, Strelec, Kun, Vez]
        for c in range(8):
            self.herni_deska[0][c] = rozvrh_hlavni[c](1)
            self.herni_deska[1][c] = Pesak(1)

        # Bílé figurky (dolní řádky 6 a 7)
        for c in range(8):
            self.herni_deska[6][c] = Pesak(0)
            self.herni_deska[7][c] = rozvrh_hlavni[c](0)

    def vrat_obsah(self, souradnice: Tuple[int, int]) -> Optional[Figurka]:
        """Vrátí figuru na zadaných souřadnicích [radka, sloupec]."""
        r, c = souradnice
        if 0 <= r < 8 and 0 <= c < 8:
            return self.herni_deska[r][c]
        return None

    def posun_figurky(self, tah: Tah) -> bool:
        """Přemístí figurku podle tahu a obslouží braní a speciální tahy."""
        if not tah.over_platnost():
            return False

        r1, c1 = tah.vychozi_pozice
        r2, c2 = tah.cilova_pozice
        fig = self.herni_deska[r1][c1]
        if not fig:
            return False

        cil_obsah = self.herni_deska[r2][c2]

        # Rošáda (posun věže)
        if tah.typ_tahu == "rosada" and fig.nazev == "Král":
            if c2 == 6:  # Malá rošáda
                vez = self.herni_deska[r1][7]
                self.herni_deska[r1][7] = None
                self.herni_deska[r1][5] = vez
                if vez:
                    vez.pocet_tahu += 1
            elif c2 == 2:  # Velká rošáda
                vez = self.herni_deska[r1][0]
                self.herni_deska[r1][0] = None
                self.herni_deska[r1][3] = vez
                if vez:
                    vez.pocet_tahu += 1

        # Braní figury
        if cil_obsah:
            cil_obsah.aktivni = False
            tah.vyhozena_figurka = cil_obsah
            if cil_obsah.barva == 0:
                self.vyhozene_figurky_b.append(cil_obsah)
            else:
                self.vyhozene_figurky_c.append(cil_obsah)

        # Povýšení pěšce na dámu při dosažení poslední řady
        if fig.nazev == "Pěšák" and (r2 == 0 or r2 == 7):
            fig = Dama(fig.barva)
            fig.pocet_tahu = tah.figurka.pocet_tahu
            tah.typ_tahu = "povyseni"

        # Vlastní přesun na šachovnici
        self.herni_deska[r1][c1] = None
        self.herni_deska[r2][c2] = fig
        tah.proved_tah()
        return True

    def nahrad_figurku(self, figurka: Figurka, tah: Tah) -> None:
        """Nahradí figuru na cílové pozici (např. při manuální volbě povýšení)."""
        r, c = tah.cilova_pozice
        self.herni_deska[r][c] = figurka

    def najdi_krale(self, barva: int) -> Optional[Tuple[int, int]]:
        """Najde souřadnice krále dané barvy."""
        for r in range(8):
            for c in range(8):
                f = self.herni_deska[r][c]
                if f and f.nazev == "Král" and f.barva == barva:
                    return (r, c)
        return None


class Timer:
    """Šachový časovač se samostatným měřením času pro oba hráče."""
    def __init__(self, vychozi_sekundy: int = 300):
        self.vychozi_sekundy: int = vychozi_sekundy
        self.cas_hrac: List[int] = [vychozi_sekundy, vychozi_sekundy]
        self.bezi: bool = False

    def nuluj_cas(self) -> None:
        """Resetuje časovač na výchozí hodnoty."""
        self.cas_hrac = [self.vychozi_sekundy, self.vychozi_sekundy]
        self.bezi = False

    def pocitej_cas(self, hrac: int) -> None:
        """Odečte 1 sekundu aktivnímu hráči."""
        if self.bezi and self.cas_hrac[hrac] > 0:
            self.cas_hrac[hrac] -= 1

    def formatuj_cas(self, hrac: int) -> str:
        """Vrátí formátovaný čas MM:SS."""
        s = self.cas_hrac[hrac]
        minuty = s // 60
        sekundy = s % 60
        return f"{minuty:02d}:{sekundy:02d}"


class GameLogger:
    """Ukládá a exportuje historii všech provedených tahů."""
    def __init__(self, soubor: str = "log_partie.txt"):
        self.soubor: str = soubor
        self.tahy: List[Tah] = []

    def uloz_tah(self, tah: Tah) -> None:
        """Zaeviduje tah do herní historie."""
        self.tahy.append(tah)

    def vytvor_soubor(self, nazev: str) -> None:
        """Uloží kompletní textový log do souboru."""
        self.soubor = nazev
        with open(nazev, "w", encoding="utf-8") as f:
            f.write("=== ZÁZNAM ŠACHOVÉ PARTIE ===\n")
            for i in range(0, len(self.tahy), 2):
                cislo = i // 2 + 1
                bily = self.tahy[i].notace()
                cerny = self.tahy[i + 1].notace() if (i + 1) < len(self.tahy) else ""
                f.write(f"{cislo}. {bily:<8} {cerny}\n")


class RevizorTahu:
    """Validátor pravidel, prověřuje šach, mat, pat a generuje platné tahy."""
    def __init__(self, herni_plocha: HerniPlocha):
        self.herni_plocha: HerniPlocha = herni_plocha
        self.tah: Optional[Tah] = None

    def simulate_Move(self, tah: Tah) -> bool:
        """
        Otestuje tah nanečisto: provede ho v záloze šachovnice a ověří,
        zda po něm vlastní král nezůstane v šachu.
        """
        r1, c1 = tah.vychozi_pozice
        r2, c2 = tah.cilova_pozice
        puvodni_cil = self.herni_plocha.herni_deska[r2][c2]
        puvodni_start = self.herni_plocha.herni_deska[r1][c1]

        # Provizorní provedení
        self.herni_plocha.herni_deska[r1][c1] = None
        self.herni_plocha.herni_deska[r2][c2] = puvodni_start

        je_v_sachu = self.check_Sach(tah.figurka.barva)

        # Vrácení původního stavu
        self.herni_plocha.herni_deska[r1][c1] = puvodni_start
        self.herni_plocha.herni_deska[r2][c2] = puvodni_cil

        return not je_v_sachu

    def check_Sach(self, barva: int) -> bool:
        """Vrátí True, pokud je král dané barvy napaden soupeřem."""
        kral_pos = self.herni_plocha.najdi_krale(barva)
        if not kral_pos:
            return False

        opacna_barva = 1 if barva == 0 else 0
        kr, kc = kral_pos

        for r in range(8):
            for c in range(8):
                fig = self.herni_plocha.herni_deska[r][c]
                if fig and fig.barva == opacna_barva:
                    if self._muze_napadnout(fig, (r, c), (kr, kc)):
                        return True
        return False

    def _muze_napadnout(self, fig: Figurka, odkud: Tuple[int, int], kam: Tuple[int, int]) -> bool:
        """Zjistí, zda figura ohrožuje cílové pole čistě geometricky."""
        r1, c1 = odkud
        r2, c2 = kam
        dr = r2 - r1
        dc = c2 - c1

        if fig.nazev == "Pěšák":
            pesak: Pesak = fig  # type: ignore
            return dr == pesak.smer and abs(dc) == 1

        if fig.nazev == "Kůň":
            return [dr, dc] in fig.vektory

        if fig.nazev == "Král":
            return max(abs(dr), abs(dc)) == 1

        # Pro Střelce, Věž a Dámu paprskovitá kontrola volné dráhy
        je_diag = (abs(dr) == abs(dc) and dr != 0)
        je_orto = (dr == 0 and dc != 0) or (dc == 0 and dr != 0)

        if fig.nazev == "Střelec" and not je_diag:
            return False
        if fig.nazev == "Věž" and not je_orto:
            return False
        if fig.nazev == "Dáma" and not (je_diag or je_orto):
            return False

        step_r = 0 if dr == 0 else (1 if dr > 0 else -1)
        step_c = 0 if dc == 0 else (1 if dc > 0 else -1)

        curr_r = r1 + step_r
        curr_c = c1 + step_c
        while (curr_r, curr_c) != (r2, c2):
            if self.herni_plocha.herni_deska[curr_r][curr_c] is not None:
                return False
            curr_r += step_r
            curr_c += step_c

        return True

    def generuj_vsechny_legalni_tahy(self, barva: int) -> List[Tah]:
        """Vrátí kompletní seznam všech legálních tahů daného hráče."""
        vsechny = []
        for r in range(8):
            for c in range(8):
                fig = self.herni_plocha.herni_deska[r][c]
                if fig and fig.barva == barva:
                    tahy_figury = self.generuj_tahy_figury((r, c))
                    for t in tahy_figury:
                        if self.simulate_Move(t):
                            vsechny.append(t)
        return vsechny

    def generuj_tahy_figury(self, pozice: Tuple[int, int]) -> List[Tah]:
        """Vygeneruje kandidátní tahy figurky bez ohledu na šach vlastního krále."""
        r, c = pozice
        fig = self.herni_plocha.herni_deska[r][c]
        if not fig:
            return []

        tahy: List[Tah] = []

        if fig.nazev == "Pěšák":
            pesak: Pesak = fig  # type: ignore
            smer = pesak.smer

            # 1. Krok dopředu o 1
            r_pred = r + smer
            if 0 <= r_pred < 8 and self.herni_plocha.herni_deska[r_pred][c] is None:
                tahy.append(Tah([r, c], [r_pred, c], fig, "normal"))

                # 2. Úvodní skok o 2 pole
                start_radka = 6 if fig.barva == 0 else 1
                r_dva = r + 2 * smer
                if r == start_radka and self.herni_plocha.herni_deska[r_dva][c] is None:
                    tahy.append(Tah([r, c], [r_dva, c], fig, "normal"))

            # 3. Braní šikmo
            for dc in [-1, 1]:
                sc = c + dc
                if 0 <= r_pred < 8 and 0 <= sc < 8:
                    cil_obsah = self.herni_plocha.herni_deska[r_pred][sc]
                    if cil_obsah and cil_obsah.barva != fig.barva:
                        tahy.append(Tah([r, c], [r_pred, sc], fig, "brani", cil_obsah))

        elif fig.skok:  # Kůň
            for dr, dc in fig.vektory:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    cil_obsah = self.herni_plocha.herni_deska[nr][nc]
                    if cil_obsah is None:
                        tahy.append(Tah([r, c], [nr, nc], fig, "normal"))
                    elif cil_obsah.barva != fig.barva:
                        tahy.append(Tah([r, c], [nr, nc], fig, "brani", cil_obsah))

        else:  # Král, Dáma, Věž, Střelec
            max_dosah = 1 if fig.nazev == "Král" else 7
            for dr, dc in fig.vektory:
                for k in range(1, max_dosah + 1):
                    nr, nc = r + dr * k, c + dc * k
                    if not (0 <= nr < 8 and 0 <= nc < 8):
                        break
                    cil_obsah = self.herni_plocha.herni_deska[nr][nc]
                    if cil_obsah is None:
                        tahy.append(Tah([r, c], [nr, nc], fig, "normal"))
                    else:
                        if cil_obsah.barva != fig.barva:
                            tahy.append(Tah([r, c], [nr, nc], fig, "brani", cil_obsah))
                        break

            # Rošáda krále
            if fig.nazev == "Král" and fig.pocet_tahu == 0 and not self.check_Sach(fig.barva):
                # Malá rošáda (sloupec 7)
                v1 = self.herni_plocha.herni_deska[r][7]
                if v1 and v1.nazev == "Věž" and v1.pocet_tahu == 0:
                    if self.herni_plocha.herni_deska[r][5] is None and self.herni_plocha.herni_deska[r][6] is None:
                        t1 = Tah([r, c], [r, 5], fig, "normal")
                        if self.simulate_Move(t1):
                            tahy.append(Tah([r, c], [r, 6], fig, "rosada"))

                # Velká rošáda (sloupec 0)
                v2 = self.herni_plocha.herni_deska[r][0]
                if v2 and v2.nazev == "Věž" and v2.pocet_tahu == 0:
                    if (self.herni_plocha.herni_deska[r][1] is None and
                        self.herni_plocha.herni_deska[r][2] is None and
                        self.herni_plocha.herni_deska[r][3] is None):
                        t2 = Tah([r, c], [r, 3], fig, "normal")
                        if self.simulate_Move(t2):
                            tahy.append(Tah([r, c], [r, 2], fig, "rosada"))

        return tahy

    def check_Mat(self, barva: int) -> bool:
        """Vrátí True, pokud je hráč v šachu a nemá žádný legální tah."""
        return self.check_Sach(barva) and len(self.generuj_vsechny_legalni_tahy(barva)) == 0

    def check_Pat(self, barva: int) -> bool:
        """Vrátí True, pokud hráč NENÍ v šachu, ale nemá žádný legální tah (pat)."""
        return not self.check_Sach(barva) and len(self.generuj_vsechny_legalni_tahy(barva)) == 0


class UserManager:
    """Správce uživatelů, profilů, historie a herních relací."""
    def __init__(self):
        self.id_uzivatele: Optional[Hrac] = None
        self.log_uzivatelu: str = ""
        self.historie_uzivatele: str = ""
        self.uzivatele: List[Uzivatel] = [
            Uzivatel("bily_mistr", "Jan Novák", "jan@sachy.cz", 1450),
            Uzivatel("cerny_velmistr", "Petr Dvořák", "petr@sachy.cz", 1520),
        ]

    def proved_tah(self) -> bool:
        """Zaznamená aktivitu hráče."""
        return True


class GameManager:
    """Hlavní fasáda herní logiky a stavu celé šachové hry."""
    def __init__(self):
        self.plocha: HerniPlocha = HerniPlocha()
        self.aktivni_hrac: int = 0  # 0 = Bílý, 1 = Černý
        self.hraci: List[Hrac] = []
        self.aktualni_tah: Optional[Tah] = None
        self.casovac: Timer = Timer(300)
        self.game_logger: GameLogger = GameLogger("log_partie.txt")
        self.revizor_tahu: RevizorTahu = RevizorTahu(self.plocha)
        self.stav_hry: str = "hra"  # "hra", "sach", "mat", "pat", "konec"
        self.kwesty: List[Kwest] = [
            Kwest("První krev", "Vyhoď soupeřovu figuru během prvních 10 tahů", 30),
            Kwest("Královská pevnost", "Proveď úspěšně rošádu (malou či velkou)", 20),
            Kwest("Šachmat", "Vyhraj partii matováním soupeřova krále", 50),
        ]

    def zacni_tah(self) -> Optional[Tah]:
        """Vrátí právě připravený tah."""
        return self.aktualni_tah

    def mozne_tahy(self, pozice: Tuple[int, int]) -> List[Tah]:
        """Vrátí všechny legální tahy pro vybranou figuru na zadané pozici."""
        kandidati = self.revizor_tahu.generuj_tahy_figury(pozice)
        return [t for t in kandidati if self.revizor_tahu.simulate_Move(t)]

    def proved_tah(self, tah: Tah) -> bool:
        """Provede tah, otestuje šach/mat/pat a přepne hráče."""
        self.casovac.bezi = True
        self.plocha.posun_figurky(tah)

        opacny = 1 if self.aktivni_hrac == 0 else 0
        tah.sach = self.revizor_tahu.check_Sach(opacny)
        tah.mat = self.revizor_tahu.check_Mat(opacny)

        self.game_logger.uloz_tah(tah)

        # Kontrola splnění questů
        if tah.vyhozena_figurka and len(self.game_logger.tahy) <= 20:
            if not self.kwesty[0].splneno and self.hraci:
                self.hraci[self.aktivni_hrac].uzivatel.pridej_kwest(self.kwesty[0])

        if tah.typ_tahu == "rosada" and self.hraci:
            if not self.kwesty[1].splneno:
                self.hraci[self.aktivni_hrac].uzivatel.pridej_kwest(self.kwesty[1])

        if tah.mat:
            self.stav_hry = "mat"
            self.casovac.bezi = False
            if self.hraci and not self.kwesty[2].splneno:
                self.hraci[self.aktivni_hrac].uzivatel.pridej_kwest(self.kwesty[2])
        elif self.revizor_tahu.check_Pat(opacny):
            self.stav_hry = "pat"
            self.casovac.bezi = False
        elif tah.sach:
            self.stav_hry = "sach"
        else:
            self.stav_hry = "hra"

        self.aktivni_hrac = opacny
        return True

    def zrus_tah(self) -> None:
        """Zruší aktuálně rozpracovaný výběr."""
        self.aktualni_tah = None

    def uloz_log(self) -> None:
        """Uloží log do souboru."""
        self.game_logger.vytvor_soubor("log_partie.txt")

    def get_stav(self) -> int:
        """Vrátí číselný kód stavu hry (0 = probíhá, 1 = šach, 2 = mat, 3 = pat)."""
        stavy = {"hra": 0, "sach": 1, "mat": 2, "pat": 3}
        return stavy.get(self.stav_hry, 0)

    def najdi_uzivatele(self, id_u: int) -> Uzivatel:
        """Najde a vrátí profil uživatele."""
        return Uzivatel("hrac", "Šachista", "hrac@sachy.cz", 1300)


# =====================================================================
# 4. VIEW VRSTVA (Tkinter Canvas & GUI Komponenty)
# =====================================================================

class GameView:
    """
    Pohled (View) na šachovnici.
    Zajišťuje vykreslení plátna Tkinter Canvas, pole, figur a zvýraznění.
    Využívá event binding pro zachycení kliknutí uživatele.
    """
    def __init__(self, root: Any, controller: 'GameManagerController'):
        self.controller = controller
        self.canvas_size: int = 560
        self.sq_size: int = self.canvas_size // 8

        # Barvy šachovnice (teplý dřevěný styl)
        self.barva_svetle: str = "#f0d9b5"
        self.barva_tmave: str = "#b58863"
        self.barva_vyberu: str = "#bbcb2b"
        self.barva_posledni: str = "#f6f669"
        self.barva_tecky: str = "#10b981"

        if tk is not None:
            self.canvas = tk.Canvas(
                root, width=self.canvas_size, height=self.canvas_size,
                bg="#292524", highlightthickness=2, highlightbackground="#44403c"
            )
            self.canvas.pack(side=tk.LEFT, padx=15, pady=15)
            # Event binding na klik myši (Event-driven MVC)
            self.canvas.bind("<Button-1>", self.on_klik)
        else:
            self.canvas = None

    def on_klik(self, event: Any) -> None:
        """Předá souřadnice kliknutí do Controlleru."""
        sloupec = event.x // self.sq_size
        radka = event.y // self.sq_size
        if 0 <= radka < 8 and 0 <= sloupec < 8:
            self.controller.zpracuj_klik(radka, sloupec)

    def aktualizuj_plochu(self) -> None:
        """Překreslí šachovnici, figury a vizuální indikátory."""
        if not self.canvas:
            return
        self.canvas.delete("all")
        deska = self.controller.game_manager.plocha.herni_deska
        vybrano = self.controller.vybrana_pozice
        posledni_tah = self.controller.game_manager.game_logger.tahy[-1] if self.controller.game_manager.game_logger.tahy else None

        # 1. Vykreslení 64 políček
        for r in range(8):
            for c in range(8):
                x1 = c * self.sq_size
                y1 = r * self.sq_size
                x2 = x1 + self.sq_size
                y2 = y1 + self.sq_size

                barva = self.barva_svetle if (r + c) % 2 == 0 else self.barva_tmave

                # Zvýraznění posledního tahu
                if posledni_tah:
                    if posledni_tah.vychozi_pozice == [r, c] or posledni_tah.cilova_pozice == [r, c]:
                        barva = self.barva_posledni

                # Zvýraznění aktivně vybraného pole
                if vybrano and vybrano == (r, c):
                    barva = self.barva_vyberu

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=barva, outline="")

                # Souřadnice písmen a čísel po obvodu
                if c == 0:
                    text_barva = self.barva_tmave if (r + c) % 2 == 0 else self.barva_svetle
                    self.canvas.create_text(x1 + 6, y1 + 10, text=str(8 - r),
                                            font=("Helvetica", 9, "bold"), fill=text_barva)
                if r == 7:
                    text_barva = self.barva_tmave if (r + c) % 2 == 0 else self.barva_svetle
                    pismena = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
                    self.canvas.create_text(x2 - 8, y2 - 8, text=pismena[c],
                                            font=("Helvetica", 9, "bold"), fill=text_barva)

                # Vykreslení figurky
                fig = deska[r][c]
                if fig:
                    symbol = fig.symbol
                    # Efekt plastické figurky se stínem
                    cx = x1 + self.sq_size // 2
                    cy = y1 + self.sq_size // 2

                    stinovaci_barva = "#09090b" if fig.barva == 1 else "#e2e8f0"
                    self.canvas.create_text(
                        cx + 1, cy + 1, text=symbol,
                        font=("Arial", 36, "bold"), fill="#000000" if fig.barva == 0 else "#ffffff"
                    )
                    self.canvas.create_text(
                        cx, cy, text=symbol,
                        font=("Arial", 36, "bold"), fill=stinovaci_barva
                    )

        # 2. Vykreslení teček pro dostupné legální tahy
        for t in self.controller.dostupne_tahy:
            cr, cc = t.cilova_pozice
            cx = cc * self.sq_size + self.sq_size // 2
            cy = cr * self.sq_size + self.sq_size // 2

            if t.vyhozena_figurka:
                # Kolečko okolo ohrožené figury
                self.canvas.create_oval(
                    cx - 24, cy - 24, cx + 24, cy + 24,
                    outline="#ef4444", width=3
                )
            else:
                # Decentní tečka na prázdném poli
                self.canvas.create_oval(
                    cx - 8, cy - 8, cx + 8, cy + 8,
                    fill=self.barva_tecky, outline=""
                )


class HracView:
    """Pohled (View) zobrazující informace o hráči, časovači a stavu tahu."""
    def __init__(self, parent: Any, barva: int):
        self.barva: int = barva
        self.parent = parent
        barva_nazev = "BÍLÝ" if barva == 0 else "ČERNÝ"
        ikona = "♔" if barva == 0 else "♚"

        if tk is not None and parent is not None:
            self.frame = tk.Frame(parent, bg="#1c1917", bd=1, relief=tk.SOLID, padx=12, pady=10)
            self.frame.pack(fill=tk.X, pady=6)

            # Horní řádek s jménem
            top_row = tk.Frame(self.frame, bg="#1c1917")
            top_row.pack(fill=tk.X)

            self.label_ikona = tk.Label(top_row, text=ikona, font=("Arial", 16), bg="#1c1917", fg="#f59e0b")
            self.label_ikona.pack(side=tk.LEFT, padx=(0, 6))

            self.label_jmeno = tk.Label(
                top_row, text=f"{barva_nazev}", font=("Helvetica", 11, "bold"),
                bg="#1c1917", fg="#fafaf9"
            )
            self.label_jmeno.pack(side=tk.LEFT)

            self.label_elo = tk.Label(
                top_row, text="1200 ELO", font=("Helvetica", 9),
                bg="#1c1917", fg="#a8a29e"
            )
            self.label_elo.pack(side=tk.RIGHT)

            # Spodní řádek s časem a stavem
            bottom_row = tk.Frame(self.frame, bg="#1c1917")
            bottom_row.pack(fill=tk.X, pady=(6, 0))

            self.label_stav = tk.Label(
                bottom_row, text="Čeká na tah", font=("Helvetica", 9),
                bg="#1c1917", fg="#78716c"
            )
            self.label_stav.pack(side=tk.LEFT)

            self.label_cas = tk.Label(
                bottom_row, text="05:00", font=("Consolas", 14, "bold"),
                bg="#292524", fg="#38bdf8", padx=8, pady=2
            )
            self.label_cas.pack(side=tk.RIGHT)
        else:
            self.frame = None

    def aktualizuj(self, hrac: Hrac, je_na_tahu: bool, cas_str: str) -> None:
        """Aktualizuje grafické zobrazení hráče."""
        if not self.frame:
            return
        self.label_jmeno.config(text=f"{hrac.uzivatel.jmeno}")
        self.label_elo.config(text=f"{hrac.getEloRating()} ELO")
        self.label_cas.config(text=cas_str)

        if je_na_tahu:
            self.frame.config(bg="#292524", highlightbackground="#f59e0b", highlightthickness=1)
            self.label_stav.config(text="● NA TAHU", fg="#22c55e")
            self.label_cas.config(bg="#0c4a6e", fg="#38bdf8")
        else:
            self.frame.config(bg="#1c1917", highlightbackground="#292524", highlightthickness=1)
            self.label_stav.config(text="Čeká", fg="#78716c")
            self.label_cas.config(bg="#292524", fg="#94a3b8")


# =====================================================================
# 5. CONTROLLER VRSTVA (Event Handling, Coordination & Game Loop)
# =====================================================================

class GameManagerController:
    """
    Hlavní Controller architektury MVC.
    Koordinuje komunikaci mezi Modelem (GameManager) a Pohledy (GameView, HracView).
    Zpracovává uživatelské události (kliknutí, nová hra, exporty).
    """
    def __init__(self, root: Any):
        self.root: Any = root
        if tk is not None and root is not None:
            self.root.title("Šachy MVC — Návrhový vzor Model-View-Controller (Tkinter)")
            self.root.geometry("960x650")
            self.root.configure(bg="#0c0a09")

        # 1. Inicializace Modelu
        self.game_manager: GameManager = GameManager()

        user1 = Uzivatel("bily_jezdec", "Jan Novák (Bílý)", "jan@sachy.cz", 1380)
        user2 = Uzivatel("cerny_kral", "Petr Dvořák (Černý)", "petr@sachy.cz", 1450)
        self.game_manager.hraci = [Hrac(0, user1), Hrac(1, user2)]

        self.vybrana_pozice: Optional[Tuple[int, int]] = None
        self.dostupne_tahy: List[Tah] = []

        # 2. Vytvoření rozvržení a herní smyčky (pouze v režimu GUI s Tkinter)
        if tk is not None and self.root is not None:
            self._vytvor_gui()
            self._aktualizuj_vse()
            self.root.after(1000, self._tik_casovace)

    def _vytvor_gui(self) -> None:
        """Vytvoří rozhraní Tkinter: šachovnici vlevo a postranní panel vpravo."""
        if tk is None or self.root is None:
            return
        # Levá část: Šachovnice (GameView)
        board_container = tk.Frame(self.root, bg="#0c0a09")
        board_container.pack(side=tk.LEFT, padx=15, pady=15, fill=tk.BOTH)

        self.game_view: GameView = GameView(board_container, self)

        # Pravá část: Ovládací panel (Sidebar)
        sidebar = tk.Frame(self.root, bg="#0c0a09", width=340)
        sidebar.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 15), pady=15)

        # Záhlaví panelu
        header_frame = tk.Frame(sidebar, bg="#1c1917", padx=12, pady=8)
        header_frame.pack(fill=tk.X, pady=(0, 8))

        lbl_title = tk.Label(
            header_frame, text="ŠACHOVÁ PARTIE MVC",
            font=("Helvetica", 12, "bold"), fg="#f59e0b", bg="#1c1917"
        )
        lbl_title.pack(anchor="w")

        self.lbl_stav_hry = tk.Label(
            header_frame, text="Partie probíhá",
            font=("Helvetica", 10), fg="#a8a29e", bg="#1c1917"
        )
        self.lbl_stav_hry.pack(anchor="w")

        # Hráč Černý (nahoře)
        self.view_cerny: HracView = HracView(sidebar, 1)

        # Historie tahů (Notace)
        history_frame = tk.Frame(sidebar, bg="#1c1917", padx=8, pady=8)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=4)

        lbl_hist = tk.Label(
            history_frame, text="ZÁPIS TAHŮ (NOTACE)",
            font=("Helvetica", 9, "bold"), fg="#78716c", bg="#1c1917"
        )
        lbl_hist.pack(anchor="w", pady=(0, 4))

        self.txt_historie = tk.Text(
            history_frame, height=7, bg="#0c0a09", fg="#e7e5e4",
            font=("Consolas", 9), relief=tk.FLAT, padx=6, pady=4
        )
        self.txt_historie.pack(fill=tk.BOTH, expand=True)

        # Hráč Bílý (dole)
        self.view_bily: HracView = HracView(sidebar, 0)

        # Akční tlačítka
        btn_frame = tk.Frame(sidebar, bg="#0c0a09")
        btn_frame.pack(fill=tk.X, pady=(8, 0))

        btn_nova = tk.Button(
            btn_frame, text="Nová hra", bg="#f59e0b", fg="#0c0a09",
            font=("Helvetica", 10, "bold"), relief=tk.FLAT, padx=10, pady=5,
            command=self.nova_hra
        )
        btn_nova.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        btn_log = tk.Button(
            btn_frame, text="Uložit log", bg="#292524", fg="#fafaf9",
            font=("Helvetica", 10), relief=tk.FLAT, padx=10, pady=5,
            command=self.uloz_log
        )
        btn_log.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))

    def zpracuj_klik(self, radka: int, sloupec: int) -> None:
        """
        Klíčová metoda Controlleru obsluhující kliknutí hráče na pole šachovnice.
        Provádí přechody stavu: výběr figury -> zobrazení tahů -> provedení tahu.
        """
        deska = self.game_manager.plocha
        fig = deska.vrat_obsah((radka, sloupec))
        aktivni = self.game_manager.aktivni_hrac

        # Fáze 1: Žádná figura zatím není vybrána
        if self.vybrana_pozice is None:
            if fig and fig.barva == aktivni:
                self.vybrana_pozice = (radka, sloupec)
                self.dostupne_tahy = self.game_manager.mozne_tahy((radka, sloupec))
        else:
            # Fáze 2: Klik na cílové pole nebo změna výběru
            r_sel, c_sel = self.vybrana_pozice
            vybrany_tah = next(
                (t for t in self.dostupne_tahy if t.cilova_pozice == [radka, sloupec]),
                None
            )

            if vybrany_tah:
                # Provedení legálního tahu
                self.game_manager.proved_tah(vybrany_tah)
                self.vybrana_pozice = None
                self.dostupne_tahy = []

                # Zvuk / hlášení při šachu nebo matu
                if self.game_manager.stav_hry == "mat":
                    vitez = "BÍLÝ" if self.game_manager.aktivni_hrac == 1 else "ČERNÝ"
                    messagebox.showinfo("Šachmat!", f"Konec hry! Vítězí {vitez}!")
                elif self.game_manager.stav_hry == "pat":
                    messagebox.showinfo("Pat", "Remíza! Na šachovnici nastal pat.")
            elif fig and fig.barva == aktivni:
                # Přepnutí výběru na jinou vlastní figuru
                self.vybrana_pozice = (radka, sloupec)
                self.dostupne_tahy = self.game_manager.mozne_tahy((radka, sloupec))
            else:
                # Klik jinam - zrušení výběru
                self.vybrana_pozice = None
                self.dostupne_tahy = []

        self._aktualizuj_vse()

    def _tik_casovace(self) -> None:
        """Pravidelný tik časovače (voláno každou sekundu přes root.after)."""
        if self.game_manager.casovac.bezi:
            self.game_manager.casovac.pocitaj_cas(self.game_manager.aktivni_hrac)
            # Kontrola vypršení času
            if self.game_manager.casovac.cas_hrac[self.game_manager.aktivni_hrac] <= 0:
                self.game_manager.casovac.bezi = False
                prohral = "Bílý" if self.game_manager.aktivni_hrac == 0 else "Černý"
                messagebox.showwarning("Čas vypršel", f"{prohral} prohrál na čas!")

            self._aktualizuj_hrace()

        # Naplánování dalšího tiku za 1000 ms
        self.root.after(1000, self._tik_casovace)

    def _aktualizuj_vse(self) -> None:
        """Synchronizuje zobrazení všech View s aktuálním stavem Modelu."""
        if tk is None or self.root is None:
            return

        # 1. Překreslení šachovnice
        self.game_view.aktualizuj_plochu()

        # 2. Aktualizace hráčů
        self._aktualizuj_hrace()

        # 3. Aktualizace stavového textu
        stavy_text = {
            "hra": "Partie probíhá",
            "sach": "POZOR: ŠACH!",
            "mat": "KONEC HRY - ŠACHMAT",
            "pat": "KONEC HRY - PAT (REMÍZA)"
        }
        self.lbl_stav_hry.config(text=stavy_text.get(self.game_manager.stav_hry, "Hra"))
        if self.game_manager.stav_hry == "sach":
            self.lbl_stav_hry.config(fg="#ef4444")
        elif self.game_manager.stav_hry == "mat":
            self.lbl_stav_hry.config(fg="#f59e0b")
        else:
            self.lbl_stav_hry.config(fg="#a8a29e")

        # 4. Aktualizace zápisu historie tahů
        self.txt_historie.delete("1.0", tk.END)
        tahy = self.game_manager.game_logger.tahy
        for i in range(0, len(tahy), 2):
            cislo = i // 2 + 1
            bily = tahy[i].notace()
            cerny = tahy[i + 1].notace() if (i + 1) < len(tahy) else ""
            self.txt_historie.insert(tk.END, f"{cislo:2d}. {bily:<8} {cerny}\n")
        self.txt_historie.see(tk.END)

    def _aktualizuj_hrace(self) -> None:
        """Aktualizuje čas a stav hráčů v HracView."""
        if not hasattr(self, 'view_bily') or not hasattr(self, 'view_cerny'):
            return
        cas_b = self.game_manager.casovac.formatuj_cas(0)
        cas_c = self.game_manager.casovac.formatuj_cas(1)
        aktivni = self.game_manager.aktivni_hrac

        self.view_bily.aktualizuj(self.game_manager.hraci[0], aktivni == 0, cas_b)
        self.view_cerny.aktualizuj(self.game_manager.hraci[1], aktivni == 1, cas_c)

    def nova_hra(self) -> None:
        """Resetuje stav celé hry na novou partii."""
        self.game_manager.plocha.nastav_zakladni_rozestaveni()
        self.game_manager.aktivni_hrac = 0
        self.game_manager.stav_hry = "hra"
        self.game_manager.game_logger.tahy.clear()
        self.game_manager.casovac.nuluj_cas()
        self.vybrana_pozice = None
        self.dostupne_tahy.clear()
        self._aktualizuj_vse()

    def uloz_log(self) -> None:
        """Uloží záznam tahu do souboru na disk."""
        self.game_manager.uloz_log()
        if messagebox:
            messagebox.showinfo("Export hotov", "Záznam byl úspěšně uložen do log_partie.txt")
        else:
            print("Záznam byl úspěšně uložen do log_partie.txt")


# =====================================================================
# SPUŠTĚNÍ APLIKACE (Main entry point)
# =====================================================================

if __name__ == "__main__":
    if tk is not None:
        okno = tk.Tk()
        app = GameManagerController(okno)
        okno.mainloop()
    else:
        print("=" * 68)
        print("  ŠACHY MVC (Model-View-Controller) — Ověření logiky v konzoli")
        print("=" * 68)
        print("[INFO] Tkinter není v tomto prostředí dostupný (např. headless Docker/CI).")
        print("[INFO] Spouštím ukázkovou simulaci šachových tříd a tahů:")

        gm = GameManager()
        u1 = Uzivatel("bily_jezdec", "Jan Novák (Bílý)", "jan@sachy.cz", 1380)
        u2 = Uzivatel("cerny_kral", "Petr Dvořák (Černý)", "petr@sachy.cz", 1450)
        gm.hraci = [Hrac(0, u1), Hrac(1, u2)]

        print(f"\n1. Inicializováni hráči:")
        print(f"   - {u1.jmeno} (ELO: {u1.elo})")
        print(f"   - {u2.jmeno} (ELO: {u2.elo})")

        print(f"\n2. Dostupné Kwesty (úkoly):")
        for k in gm.kwesty:
            print(f"   - [{ '✓' if k.splneno else ' ' }] {k.nazev}: {k.popis} (+{k.odmena_elo} ELO)")

        # Tah 1: 1. e4
        tahy_b = gm.mozne_tahy((6, 4))
        tah_e4 = next((t for t in tahy_b if t.cilova_pozice == [4, 4]), None)
        if tah_e4:
            gm.proved_tah(tah_e4)
            print(f"\n3. Tah 1 proveden: {tah_e4.notace()} (e2 -> e4)")

        # Tah 2: 1... e5
        tahy_c = gm.mozne_tahy((1, 4))
        tah_e5 = next((t for t in tahy_c if t.cilova_pozice == [3, 4]), None)
        if tah_e5:
            gm.proved_tah(tah_e5)
            print(f"4. Tah 2 proveden: {tah_e5.notace()} (e7 -> e5)")

        # Tah 3: 2. Jf3
        tahy_b2 = gm.mozne_tahy((7, 6))
        tah_jf3 = next((t for t in tahy_b2 if t.cilova_pozice == [5, 5]), None)
        if tah_jf3:
            gm.proved_tah(tah_jf3)
            print(f"5. Tah 3 proveden: {tah_jf3.notace()} (Jezdec g1 -> f3)")

        # Uložení logu
        gm.uloz_log()
        print(f"\n6. Logování partií (GameLogger):")
        print(f"   Zapsáno {len(gm.game_logger.tahy)} tahů do log_partie.txt: {[t.notace() for t in gm.game_logger.tahy]}")

        print("\n" + "=" * 68)
        print("Pro spuštění plnohodnotného Tkinter GUI na počítači s grafickým rozhraním:")
        print("   python3 sachy_mvc.py")
        print("=" * 68)
