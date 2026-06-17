from enum import Enum

class Barva(Enum):
    BILY = 1
    CERNY = 2

class TypFigurky(Enum):
    PESAK = 1
    VEZ = 2
    KUN = 3
    STRELEC = 4
    DAMA = 5
    KRAL = 6

class StavHry(Enum):
    HRA = 1
    SACH = 2
    MAT = 3
    PAT = 4
    REMIZA = 5

class TypTahu(Enum):
    NORMALNI = 1
    BRANI = 2
    ROSADA = 3
    EN_PASSANT = 4
    PROMOCE = 5

class Pozice:
    def __init__(self, radka: int, sloupec: int):
        self.radka: int = radka
        self.sloupec: int = sloupec

class Figurka:
    def __init__(self, typ: TypFigurky, barva: Barva, pozice: Pozice):
        self.typ: TypFigurky = typ
        self.barva: Barva = barva
        self.pozice: Pozice = pozice
        self.pocetTahu: int = 0
        self.aktivni: bool = True

    def hodnota(self) -> int: ...
    def symbol(self) -> str: ...

class HerniPlocha:
    def __init__(self):
        self.rozmer: int = 8
        self.pole: list[list[Figurka | None]] = [[None] * 8 for _ in range(8)]
        self.figurky: list[Figurka] = []

    def figurkaNa(self, pozice: Pozice) -> Figurka | None: ...
    def jeValidniPozice(self, pozice: Pozice) -> bool: ... 
    def nastavFigurku(self, figurka: Figurka, pozice: Pozice) -> None: ...
    def odeberFigurku(self, pozice: Pozice) -> None: ...
    def najdiKrale(self, barva: Barva) -> Figurka | None: ...
    def kopie(self) -> "HerniPlocha": ...

class Tah:
    def __init__(self, figurka: Figurka, zPozice: Pozice, naPozici: Pozice):
        self.figurka: Figurka = figurka
        self.zPozice: Pozice = zPozice
        self.naPozici: Pozice = naPozici
        self.figurkaBrana: Figurka | None = None
        self.typTahu: TypTahu = TypTahu.NORMALNI
        self.sach: bool = False
        self.mat: bool = False

class RevizorTahu:
    def __init__(self, plocha: HerniPlocha):
        self.plocha: HerniPlocha = plocha

    def jePlatny(self, tah: Tah) -> bool: ...
    def overSach(self, barva: Barva) -> bool: ...
    def overMat(self, barva: Barva) -> bool: ...
    def overPat(self, barva: Barva) -> bool: ...
    def overRemizu(self) -> bool: ...
    def getMozneTahy(self, figurka: Figurka) -> list[Tah]: ...
    def getVsechnyMozneTahy(self, barva: Barva) -> list[Tah]: ...

class Timer:
    def __init__(self, pocatecniCas: float = 600.0, inkrement: float = 0.0):
        self.casBily: float = pocatecniCas
        self.casCerny: float = pocatecniCas
        self.inkrement: float = inkrement
        self.bezi: bool = False
        self.aktivni: Barva | None = None

    def start(self) -> None: ...
    def stop(self) -> None: ...
    def prepniHrace(self) -> None: ...
    def getZbylyCas(self, barva: Barva) -> float: ...

class GameLogger:
    def __init__(self):
        self.zaznamy: list[str] = []
        self.kolobeh: int = 1

    def logTah(self, tah: Tah) -> None: ...
    def logZprava(self, zprava: str) -> None: ...
    def ulozDoSouboru(self, cesta: str) -> None: ...

class GameManager:
    def __init__(self, casNaHrace: float = 600.0, inkrement: float = 0.0):
        self.plocha: HerniPlocha = HerniPlocha()
        self.revizor: RevizorTahu = RevizorTahu(self.plocha)
        self.timer: Timer = Timer(casNaHrace, inkrement)
        self.logger: GameLogger = GameLogger()
        self.seznamTahu: list[Tah] = []
        self.aktualniHrac: Barva = Barva.BILY
        self.stavHry: StavHry = StavHry.HRA
        self.historiePozic: list[str] = []
        self.bezi: bool = False

    def startHry(self) -> None: ...
    def provedTah(self, tah: Tah) -> bool: ...
    def zmenHrace(self) -> None: ...
    def getAktualniHrac(self) -> Barva: ...
    def konecHry(self, vysledek: str) -> None: ...
    def vratZpet(self) -> bool: ...
    def getHistorieTahu(self) -> list[Tah]: ...