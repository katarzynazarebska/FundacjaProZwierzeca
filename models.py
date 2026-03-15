# models.py
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, LargeBinary, Text
from sqlalchemy.orm import relationship
from datetime import date
from database import Base

# ==============================================================================
# 1. OSOBA (Dane personalne)
# ==============================================================================
class Osoba(Base):
    __tablename__ = 'OSOBA'

    IDOsoba = Column(Integer, primary_key=True, index=True)
    Imie = Column(String(50), nullable=False)
    Nazwisko = Column(String(50), nullable=False)
    Telefon = Column(String(20))
    Email = Column(String(100))
    
    # Adres
    AdresMiasto = Column(String(50))
    AdresUlica = Column(String(100))
    AdresNrLokalu = Column(String(20))
    AdresKodPocztowy = Column(String(10))
    
    DataRejestracji = Column(Date, default=date.today)

    # Relacje
    Uzytkownik = relationship("Uzytkownik", back_populates="Osoba", uselist=False)
    ZwierzetaPodOpieka = relationship("Zwierze", foreign_keys="[Zwierze.IDOpiekun]", back_populates="Opiekun")
    ZwierzetaNadzorowane = relationship("Zwierze", foreign_keys="[Zwierze.IDNadzor]", back_populates="Nadzorca")

# ==============================================================================
# 2. UZYTKOWNIK (Logowanie)
# ==============================================================================
class Uzytkownik(Base):
    __tablename__ = 'UZYTKOWNIK'

    IDUser = Column(Integer, primary_key=True, index=True)
    LoginName = Column(String(50), unique=True, nullable=False)
    Email = Column(String(100), nullable=False)
    HasloHash = Column(String(255), nullable=False)
    Rola = Column(String(20), nullable=False)
    CzyAktywny = Column(Boolean, default=True)
    ResetToken = Column(String(100), nullable=True)

    IDOsoba = Column(Integer, ForeignKey('OSOBA.IDOsoba'))
    
    Osoba = relationship("Osoba", back_populates="Uzytkownik")
    HistoriaDzialan = relationship("HistoriaZdarzen", back_populates="User")

# ==============================================================================
# 3. ZWIERZE (Zintegrowane z profilem medycznym)
# ==============================================================================
class Zwierze(Base):
    __tablename__ = 'ZWIERZE'

    IDZwierze = Column(Integer, primary_key=True, index=True)
    # --- Dane podstawowe ---
    Imie = Column(String(50), nullable=False)
    Gatunek = Column(String(50)) 
    Rasa = Column(String(50))
    Plec = Column(String(20))
    DataUrodzenia = Column(Date)
    DataPrzyjecia = Column(Date, default=date.today)
    StatusZwierzecia = Column(String(50)) 
    NrChip = Column(String(50))
    Opis = Column(Text)
    Zdjecie = Column(LargeBinary)
    ZrodloFinansowania = Column(String(100))

    # --- Pola Ogłoszeniowe ---
    CzyOgloszenieOLX = Column(Boolean, default=False)
    CzyOgloszenieWWW = Column(Boolean, default=False)

    # --- Profil Medyczny ---
    DataKastracji = Column(Date, nullable=True) 
    SzczepienieWscieklizna = Column(Date)
    SzczepienieZakazne = Column(Date)
    Odrobaczenie = Column(Date)
    OchronaKleszczeDo = Column(Date)
    OpisZdrowia = Column(Text)

    # --- Klucze obce ---
    IDOpiekun = Column(Integer, ForeignKey('OSOBA.IDOsoba'), nullable=True) 
    IDNadzor = Column(Integer, ForeignKey('OSOBA.IDOsoba'), nullable=True)  

    # --- Relacje ---
    Opiekun = relationship("Osoba", foreign_keys=[IDOpiekun], back_populates="ZwierzetaPodOpieka")
    Nadzorca = relationship("Osoba", foreign_keys=[IDNadzor], back_populates="ZwierzetaNadzorowane")
    
    # ProfilMedyczny
    Historia = relationship("HistoriaZdarzen", back_populates="Zwierze", cascade="all, delete-orphan")

# ==============================================================================
# 4. HISTORIA ZDARZEŃ
# ==============================================================================
class HistoriaZdarzen(Base):
    __tablename__ = 'HISTORIA_ZDARZEN'

    IDHistoria = Column(Integer, primary_key=True, index=True)
    IDZwierze = Column(Integer, ForeignKey('ZWIERZE.IDZwierze'), nullable=False)
    IDUser = Column(Integer, ForeignKey('UZYTKOWNIK.IDUser'))
    
    DataZdarzenia = Column(Date, default=date.today)
    Kategoria = Column(String(50))
    Opis = Column(Text)

    Zwierze = relationship("Zwierze", back_populates="Historia")
    User = relationship("Uzytkownik", back_populates="HistoriaDzialan")
    Zalaczniki = relationship("Zalacznik", back_populates="Historia", cascade="all, delete-orphan")

# ==============================================================================
# 5. ZAŁĄCZNIKI
# ==============================================================================
class Zalacznik(Base):
    __tablename__ = 'ZALACZNIKI'

    IDZalacznik = Column(Integer, primary_key=True)
    IDHistoria = Column(Integer, ForeignKey('HISTORIA_ZDARZEN.IDHistoria'), nullable=False)
    
    NazwaPliku = Column(String(255))
    TypPliku = Column(String(50))
    DaneBLOB = Column(LargeBinary)
    DataDodania = Column(Date, default=date.today)

    Historia = relationship("HistoriaZdarzen", back_populates="Zalaczniki")

# ==============================================================================
# 6. SŁOWNIKI I KONFIGURACJA
# ==============================================================================
class SlownikGatunek(Base):
    __tablename__ = 'SLOWNIK_GATUNEK'
    Wartosc = Column(String(50), primary_key=True)

class SlownikStatus(Base):
    __tablename__ = 'SLOWNIK_STATUS'
    Wartosc = Column(String(50), primary_key=True)

class SlownikKategoria(Base):
    __tablename__ = 'SLOWNIK_KATEGORIA'
    Wartosc = Column(String(50), primary_key=True)

class KonfiguracjaAlerty(Base):
    __tablename__ = 'KONFIGURACJA_ALERTY'
    KodPola = Column(String(50), primary_key=True)
    Etykieta = Column(String(100))
    DniWaznosci = Column(Integer)
    CzyAktywny = Column(Boolean, default=True)