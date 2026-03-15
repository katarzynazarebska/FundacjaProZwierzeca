# crud.py
"""
MODUŁ: CRUD (Create, Read, Update, Delete) 
Odpowiada za logikę biznesową i komunikację z bazą danych.
"""
import pandas as pd
import hashlib
from datetime import date, datetime, timedelta
from sqlalchemy import text, func
from database import SessionLocal
from models import (
    Uzytkownik, Osoba, Zwierze, HistoriaZdarzen, Zalacznik,
    SlownikGatunek, SlownikStatus, SlownikKategoria, KonfiguracjaAlerty
)


# ==============================================================================
# NARZĘDZIA POMOCNICZE
# ==============================================================================

def get_db_session():
    """Tworzy nową sesję do bazy danych."""
    return SessionLocal()

def hash_password(password: str) -> str:
    """Szyfrowanie hasła (SHA256 + Salt)."""
    return hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        b'salt_fundacja', 
        100000
    ).hex()

# ==============================================================================
# 1. UŻYTKOWNICY I LOGOWANIE
# ==============================================================================

def verify_user(login_input, password_input):
    """Weryfikuje logowanie."""
    db = get_db_session()
    try:
        user = db.query(Uzytkownik).filter(Uzytkownik.LoginName == login_input, Uzytkownik.CzyAktywny == True).first()
        if user:
            input_hash = hash_password(password_input)
            if user.HasloHash == input_hash:
                return user.Rola, user.LoginName, user.IDOsoba
        return None, None, None
    finally:
        db.close()

def create_user(login, email, password, role, id_osoba=None):
    """
    Tworzy nowego użytkownika (wersja poprawiona z Hashowaniem hasła).
    """
    db = get_db_session()
    try:
        if db.query(Uzytkownik).filter(Uzytkownik.LoginName == login).first():
            return False, "Login jest już zajęty."

        # Szyfrujemy hasło PRZED zapisaniem do bazy!
        zaszyfrowane_haslo = hash_password(password)

        new_user = Uzytkownik(
            LoginName=login,
            Email=email,
            HasloHash=zaszyfrowane_haslo,
            Rola=role,
            CzyAktywny=True,
            IDOsoba=id_osoba  
        )
        db.add(new_user)
        db.commit()
        return True, "Utworzono konto."
    except Exception as e:
        db.rollback()
        return False, f"Błąd bazy: {e}"
    finally:
        db.close()

# ==============================================================================
# 2. ZWIERZĘTA (LISTING I SZCZEGÓŁY)
# ==============================================================================

def pobierz_liste_zwierzat(id_opiekun_dt=None):
    """Pobiera prostą listę (np. do kafelków na dashboardzie)."""
    db = get_db_session()
    try:
        q = db.query(
            Zwierze.IDZwierze, 
            Zwierze.Imie, 
            Zwierze.Rasa, 
            Zwierze.StatusZwierzecia, 
            Zwierze.Zdjecie,
            Zwierze.IDOpiekun
        ).filter(Zwierze.StatusZwierzecia != 'Za Tęczowym Mostem')

        if id_opiekun_dt:
            q = q.filter(Zwierze.IDOpiekun == id_opiekun_dt)

        df = pd.read_sql(q.statement, db.bind)
        return df
    except Exception as e:
        print(f"Błąd listingu: {e}")
        return pd.DataFrame()
    finally:
        db.close()

def pobierz_rejestr_rozszerzony(id_opiekun=None):
    """
    Pobiera listę zwierząt wraz z IMIONAMI opiekunów (JOIN).
    Jeśli podano id_opiekun (dla roli DT), filtruje wyniki tylko dla tej osoby.
    """
    db = get_db_session()
    try:
        sql = """
            SELECT 
                z.IDZwierze, 
                z.Imie, 
                z.Gatunek, 
                z.Rasa, 
                z.Plec, 
                z.StatusZwierzecia, 
                z.DataUrodzenia,
                z.NrChip,
                (o1.Imie || ' ' || o1.Nazwisko) AS OpiekunNazwa,
                (o2.Imie || ' ' || o2.Nazwisko) AS NadzorcaNazwa
            FROM ZWIERZE z
            LEFT JOIN OSOBA o1 ON z.IDOpiekun = o1.IDOsoba
            LEFT JOIN OSOBA o2 ON z.IDNadzor = o2.IDOsoba
        """
        
        # Jeśli funkcja dostała ID (czyli to Dom Tymczasowy), dodajemy filtr WHERE
        if id_opiekun is not None:
            sql += " WHERE z.IDOpiekun = :id_op"
            
        sql += " ORDER BY z.IDZwierze DESC"
        
        query = text(sql)
        params = {"id_op": id_opiekun} if id_opiekun is not None else {}
        
        df = pd.read_sql(query, db.bind, params=params)
        return df
    finally:
        db.close()

def pobierz_szczegoly_zwierzecia(id_zwierze):
    """Pobiera pełny obiekt zwierzęcia."""
    db = get_db_session()
    try:
        zwierze = db.query(Zwierze).filter(Zwierze.IDZwierze == id_zwierze).first()
        return zwierze
    finally:
        db.close()

def dodaj_nowe_zwierze(imie, gatunek, rasa, plec, status, id_nadzorca=None, id_opiekun=None, nr_chip=None, zrodlo=None, data_przyjecia=None, data_urodzenia=None, opis=None, czy_olx=False, czy_www=False, zdjecie_blob=None):
    """
    Rejestruje nowe zwierzę z PEŁNYM zestawem danych.
    """
    db = get_db_session()
    try:
        if not data_przyjecia:
            data_przyjecia = date.today()

        nowe = Zwierze(
            Imie=imie,
            Gatunek=gatunek,
            Rasa=rasa,
            Plec=plec,
            StatusZwierzecia=status,
            IDNadzor=id_nadzorca,
            IDOpiekun=id_opiekun,
            NrChip=nr_chip,
            ZrodloFinansowania=zrodlo,
            DataPrzyjecia=data_przyjecia,
            DataUrodzenia=data_urodzenia,
            Opis=opis,
            CzyOgloszenieOLX=czy_olx,
            CzyOgloszenieWWW=czy_www,
            Zdjecie=zdjecie_blob
        )
        db.add(nowe)
        db.commit()
        return nowe.IDZwierze
    except Exception as e:
        db.rollback()
        print(f"Błąd dodawania zwierzęcia: {e}")
        return None
    finally:
        db.close()

# ==============================================================================
# 3. EDYCJA DANYCH
# ==============================================================================

def aktualizuj_dane_podstawowe(id_zwierze, dane_dict):
    """Aktualizuje podstawowe pola."""
    db = get_db_session()
    try:
        zwierze = db.query(Zwierze).filter(Zwierze.IDZwierze == id_zwierze).first()
        if not zwierze:
            return False

        for key, value in dane_dict.items():
            if hasattr(zwierze, key):
                setattr(zwierze, key, value)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()

def aktualizuj_zdjecie(id_zwierze, bytes_data):
    """Zapisuje BLOB zdjęcia."""
    db = get_db_session()
    try:
        db.query(Zwierze).filter(Zwierze.IDZwierze == id_zwierze).update({Zwierze.Zdjecie: bytes_data})
        db.commit()
    finally:
        db.close()

def adoptuj_zwierze(id_zwierze, id_nowy_wlasciciel):
    """Finalizacja adopcji."""
    db = get_db_session()
    try:
        zwierze = db.query(Zwierze).filter(Zwierze.IDZwierze == id_zwierze).first()
        if zwierze:
            zwierze.StatusZwierzecia = 'Adoptowany'
            zwierze.IDOpiekun = id_nowy_wlasciciel
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()

# ==============================================================================
# 4. MEDYCYNA I HISTORIA
# ==============================================================================

def dodaj_wpis_historii(id_zwierze, id_user, kategoria, opis):
    """Dodaje zdarzenie do historii."""
    db = get_db_session()
    try:
        wpis = HistoriaZdarzen(
            IDZwierze=id_zwierze,
            IDUser=id_user,
            Kategoria=kategoria,
            Opis=opis,
            DataZdarzenia=date.today()
        )
        db.add(wpis)
        db.commit()
        return wpis.IDHistoria
    except Exception as e:
        db.rollback()
        return None
    finally:
        db.close()

def pobierz_historie(id_zwierze):
    """Pobiera historię jako DataFrame."""
    db = get_db_session()
    try:
        q = db.query(
            HistoriaZdarzen.IDHistoria,
            HistoriaZdarzen.DataZdarzenia,
            HistoriaZdarzen.Kategoria,
            HistoriaZdarzen.Opis,
            Uzytkownik.LoginName.label("Autor")
        ).join(Uzytkownik, HistoriaZdarzen.IDUser == Uzytkownik.IDUser)\
         .filter(HistoriaZdarzen.IDZwierze == id_zwierze)\
         .order_by(HistoriaZdarzen.DataZdarzenia.desc())
        
        df = pd.read_sql(q.statement, db.bind)
        return df
    finally:
        db.close()

# ==============================================================================
# 5. OSOBY
# ==============================================================================

def pobierz_wszystkie_osoby():
    """Zwraca DataFrame wszystkich osób wraz ze szczegółami kontaktowymi."""
    db = get_db_session()
    try:
        q = db.query(Osoba.IDOsoba, Osoba.Imie, Osoba.Nazwisko, Osoba.Telefon, 
                     Osoba.Email, Osoba.AdresMiasto, Osoba.AdresUlica, 
                     Osoba.AdresNrLokalu, Osoba.AdresKodPocztowy)
        df = pd.read_sql(q.statement, db.bind)
        if not df.empty:
            df['Display'] = df['Imie'] + " " + df['Nazwisko'] + " (" + df['AdresMiasto'].fillna('-') + ")"
        return df
    finally:
        db.close()

def aktualizuj_osobe(id_osoba, imie, nazwisko, telefon, email, miasto, ulica, lokal, kod):
    """Zapisuje zmienione dane Osoby w bazie."""
    db = get_db_session()
    try:
        osoba = db.query(Osoba).filter(Osoba.IDOsoba == id_osoba).first()
        if not osoba:
            return False, "Nie znaleziono osoby w bazie."
        
        osoba.Imie = imie
        osoba.Nazwisko = nazwisko
        osoba.Telefon = telefon
        osoba.Email = email
        osoba.AdresMiasto = miasto
        osoba.AdresUlica = ulica
        osoba.AdresNrLokalu = lokal
        osoba.AdresKodPocztowy = kod
        
        db.commit()
        return True, "Zaktualizowano dane osoby."
    except Exception as e:
        db.rollback()
        return False, f"Błąd bazy: {e}"
    finally:
        db.close()

def anonimizuj_osobe(id_osoba):
    """
    Zgodność z RODO: Prawo do bycia zapomnianym.
    Nadpisuje dane wrażliwe Osoby i blokuje powiązane konto Użytkownika,
    zachowując jednocześnie spójność relacji w bazie danych (np. adopcje).
    """
    db = get_db_session()
    try:
        # 1. Anonimizacja danych osobowych
        osoba = db.query(Osoba).filter(Osoba.IDOsoba == id_osoba).first()
        if not osoba:
            return False, "Nie znaleziono osoby w bazie."
        
        osoba.Imie = "Anonim"
        osoba.Nazwisko = "(RODO)"
        osoba.Telefon = "-"
        osoba.Email = "-"
        osoba.AdresMiasto = "Zanonimizowano"
        osoba.AdresUlica = "Zanonimizowano"
        osoba.AdresNrLokalu = "-"
        osoba.AdresKodPocztowy = "-"

        # 2. Deaktywacja i anonimizacja powiązanego konta dostępowego
        user = db.query(Uzytkownik).filter(Uzytkownik.IDOsoba == id_osoba).first()
        if user:
            user.LoginName = f"usuniety_rodo_{id_osoba}"
            user.Email = "-"
            user.CzyAktywny = False
            user.HasloHash = "USUNIETO"

        db.commit()
        return True, "Dane zostały pomyślnie zanonimizowane."
    except Exception as e:
        db.rollback()
        return False, f"Błąd bazy danych: {e}"
    finally:
        db.close()

# ==============================================================================
# 6. SŁOWNIKI
# ==============================================================================

def get_dictionary(nazwa_modelu):
    return pobierz_slownik(nazwa_modelu)

def pobierz_slownik(nazwa_modelu):
    """Pobiera wartości ze słownika."""
    db = get_db_session()
    model_map = {
        'gatunek': SlownikGatunek,
        'status': SlownikStatus,
        'kategoria': SlownikKategoria,
        'SLOWNIK_GATUNKI': SlownikGatunek,    
        'SLOWNIK_STATUSY': SlownikStatus,
        'SLOWNIK_KATEGORIE': SlownikKategoria
    }
    
    try:
        model = model_map.get(nazwa_modelu)
        if not model: return []
        
        wyniki = db.query(model.Wartosc).all()
        return [w[0] for w in wyniki]
    finally:
        db.close()

def delete_dict_value(typ, wartosc): usun_wartosc_slownika(typ, wartosc)
def add_dict_value(typ, wartosc): dodaj_wartosc_slownika(typ, wartosc)

# ==============================================================================
# 7. POWIADOMIENIA I ALERTY
# ==============================================================================

def pobierz_alerty_medyczne(rola_usera="Admin", id_osoba=None):
    """Generuje alerty medyczne i operacyjne. Wersja pancerna na konflikty typów dat."""
    db = get_db_session()
    alerty = []
    dzis = date.today()
    try:
        reguly = db.query(KonfiguracjaAlerty).filter(KonfiguracjaAlerty.CzyAktywny == True).all()

        query = db.query(Zwierze).filter(
            Zwierze.StatusZwierzecia.notin_(['Adoptowany', 'Za Tęczowym Mostem'])
        )

        if rola_usera != "Admin" and id_osoba is not None:
            query = query.filter(Zwierze.IDNadzor == id_osoba)

        zwierzeta = query.all()

        for zwierzak in zwierzeta:
            try:
                data_przyj = zwierzak.DataPrzyjecia
                if isinstance(data_przyj, datetime):
                    data_przyj = data_przyj.date()
                elif isinstance(data_przyj, str):
                    data_przyj = datetime.strptime(data_przyj.split(' ')[0], '%Y-%m-%d').date()
                
                if data_przyj:
                    dni_w_fundacji = (dzis - data_przyj).days
                else:
                    dni_w_fundacji = 0

                # ------------------------------------------------------------------
                # A. ALERTY OPERACYJNE
                # ------------------------------------------------------------------
                if zwierzak.StatusZwierzecia == 'Kwarantanna' and dni_w_fundacji >= 14:
                    alerty.append({
                        "id": zwierzak.IDZwierze, "imie": zwierzak.Imie, "chip": zwierzak.NrChip,
                        "komunikat": f"🟢 Koniec kwarantanny! Zwierzę jest w fundacji już {dni_w_fundacji} dni."
                    })

                if not zwierzak.NrChip and dni_w_fundacji >= 3:
                    alerty.append({
                        "id": zwierzak.IDZwierze, "imie": zwierzak.Imie, "chip": "BRAK",
                        "komunikat": f"⚠️ Brak CHIP! Zwierzę przebywa w fundacji od {dni_w_fundacji} dni."
                    })

                if not zwierzak.IDNadzor:
                    alerty.append({
                        "id": zwierzak.IDZwierze, "imie": zwierzak.Imie, "chip": zwierzak.NrChip,
                        "komunikat": f"🙋‍♀️ Brak Wolontariusza! Nikt nie sprawuje nadzoru nad tym zwierzęciem."
                    })

                # ------------------------------------------------------------------
                # B. ALERTY MEDYCZNE
                # ------------------------------------------------------------------
                if not reguly: continue

                for regula in reguly:
                    pole = regula.KodPola
                    limit_dni = int(regula.DniWaznosci)
                    etykieta = regula.Etykieta
                    data_baza = getattr(zwierzak, pole, None)
                    
                    if not data_baza: 
                        alerty.append({
                            "id": zwierzak.IDZwierze, "imie": zwierzak.Imie, "chip": zwierzak.NrChip,
                            "komunikat": f"⚠️ {etykieta}: Brak jakiejkolwiek wpisanej daty!"
                        })
                        continue 

                    if isinstance(data_baza, datetime):
                        data_baza = data_baza.date()
                    elif isinstance(data_baza, str):
                        data_baza = datetime.strptime(data_baza.split(' ')[0], '%Y-%m-%d').date()

                    if pole == 'OchronaKleszczeDo':
                        dni_do_konca = (data_baza - dzis).days
                        if dni_do_konca < 0:
                            alerty.append({
                                "id": zwierzak.IDZwierze, "imie": zwierzak.Imie, "chip": zwierzak.NrChip,
                                "komunikat": f"🔴 {etykieta}: Wygasła {abs(dni_do_konca)} dni temu! ({data_baza})"
                            })
                        elif dni_do_konca <= 14:
                            alerty.append({
                                "id": zwierzak.IDZwierze, "imie": zwierzak.Imie, "chip": zwierzak.NrChip,
                                "komunikat": f"🟡 {etykieta}: Wygasa za {dni_do_konca} dni ({data_baza})."
                            })
                    else:
                        data_waznosci = data_baza + timedelta(days=limit_dni)
                        dni_do_konca = (data_waznosci - dzis).days

                        if dni_do_konca < 0:
                            alerty.append({
                                "id": zwierzak.IDZwierze, "imie": zwierzak.Imie, "chip": zwierzak.NrChip,
                                "komunikat": f"🔴 {etykieta}: Przeterminowane o {abs(dni_do_konca)} dni! (Ważne do {data_waznosci})"
                            })
                        elif dni_do_konca <= 14:
                            alerty.append({
                                "id": zwierzak.IDZwierze, "imie": zwierzak.Imie, "chip": zwierzak.NrChip,
                                "komunikat": f"🟡 {etykieta}: Kończy się za {dni_do_konca} dni! (Ważne do {data_waznosci})"
                            })
            except Exception as e:
                print(f"Błąd analizy alertów dla {zwierzak.IDZwierze}: {e}")
                continue

        return alerty
    except Exception as e:
        print(f"Globalny błąd alertów: {e}")
        return []
    finally:
        db.close()

# ==============================================================================
# 8. ZAŁĄCZNIKI I HISTORIA
# ==============================================================================

def usun_wpis_historii(id_historia):
    """Usuwa zdarzenie i kaskadowo jego załączniki."""
    db = get_db_session()
    try:
        wpis = db.query(HistoriaZdarzen).filter(HistoriaZdarzen.IDHistoria == id_historia).first()
        if wpis:
            db.delete(wpis)
            db.commit()
            return True, "Usunięto wpis."
        return False, "Nie znaleziono wpisu."
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()

def pobierz_liste_zalacznikow(id_historia):
    """Pobiera listę plików."""
    db = get_db_session()
    try:
        from sqlalchemy.orm import defer
        pliki = db.query(Zalacznik).filter(Zalacznik.IDHistoria == id_historia).all()
        data = []
        for p in pliki:
            rozmiar = len(p.DaneBLOB) if p.DaneBLOB else 0
            data.append({
                "ID_Zalacznik": p.IDZalacznik,
                "NazwaPliku": p.NazwaPliku,
                "TypPliku": p.TypPliku,
                "RozmiarBajt": rozmiar
            })
        return pd.DataFrame(data)
    finally:
        db.close()
        
def pobierz_zalaczniki(id_historia): return pobierz_liste_zalacznikow(id_historia)

def pobierz_plik_content(id_zalacznik):
    """Pobiera content pliku."""
    db = get_db_session()
    try:
        plik = db.query(Zalacznik).filter(Zalacznik.IDZalacznik == id_zalacznik).first()
        if plik:
            return plik.NazwaPliku, plik.DaneBLOB, plik.TypPliku
        return None
    finally:
        db.close()

def dodaj_zalacznik(id_historia, uploaded_file):
    """Zapisuje plik."""
    db = get_db_session()
    try:
        bytes_data = uploaded_file.getvalue()
        nowy = Zalacznik(
            IDHistoria=id_historia,
            NazwaPliku=uploaded_file.name,
            TypPliku=uploaded_file.type,
            DaneBLOB=bytes_data
        )
        db.add(nowy)
        db.commit()
        return True, "Dodano plik"
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()

def usun_zalacznik(id_zalacznik):
    """Usuwa plik."""
    db = get_db_session()
    try:
        plik = db.query(Zalacznik).filter(Zalacznik.IDZalacznik == id_zalacznik).first()
        if plik:
            db.delete(plik)
            db.commit()
    finally:
        db.close()

# ==============================================================================
# 9. ADMINISTRACJA
# ==============================================================================

# Userzy
def pobierz_wszystkich_uzytkownikow():
    db = get_db_session()
    try:
        q = db.query(Uzytkownik.IDUser, Uzytkownik.LoginName, Uzytkownik.Email, Uzytkownik.Rola, Uzytkownik.CzyAktywny)
        df = pd.read_sql(q.statement, db.bind)
        df.rename(columns={'IDUser': 'ID_User'}, inplace=True)
        return df
    finally:
        db.close()

def get_all_users(): return pobierz_wszystkich_uzytkownikow()
def get_all_people(): return pobierz_wszystkie_osoby()
def add_person(*args): return dodaj_osobe(*args)
def delete_user(uid): usun_uzytkownika(uid)
def toggle_user_status(uid, status): zmien_status_uzytkownika(uid, status)
def change_user_password(login, pwd): zmien_haslo_uzytkownika(login, pwd)

def zmien_status_uzytkownika(id_user, obecny_status):
    db = get_db_session()
    try:
        nowy_status = not bool(obecny_status)
        db.query(Uzytkownik).filter(Uzytkownik.IDUser == id_user).update({Uzytkownik.CzyAktywny: nowy_status})
        db.commit()
    finally:
        db.close()

def zmien_haslo_uzytkownika(login, nowe_haslo_plain):
    db = get_db_session()
    try:
        nowy_hash = hash_password(nowe_haslo_plain)
        db.query(Uzytkownik).filter(Uzytkownik.LoginName == login).update({Uzytkownik.HasloHash: nowy_hash})
        db.commit()
    finally:
        db.close()

def usun_uzytkownika(id_user):
    db = get_db_session()
    try:
        db.query(Uzytkownik).filter(Uzytkownik.IDUser == id_user).delete()
        db.commit()
    finally:
        db.close()

# Słowniki
def dodaj_wartosc_slownika(typ_slownika, wartosc):
    db = get_db_session()
    model_map = {
        'gatunek': SlownikGatunek, 'SLOWNIK_GATUNKI': SlownikGatunek,
        'status': SlownikStatus, 'SLOWNIK_STATUSY': SlownikStatus,
        'kategoria': SlownikKategoria, 'SLOWNIK_KATEGORIE': SlownikKategoria
    }
    try:
        Model = model_map.get(typ_slownika)
        if Model:
            db.add(Model(Wartosc=wartosc))
            db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

def usun_wartosc_slownika(typ_slownika, wartosc):
    db = get_db_session()
    model_map = {
        'gatunek': SlownikGatunek, 'SLOWNIK_GATUNKI': SlownikGatunek,
        'status': SlownikStatus, 'SLOWNIK_STATUSY': SlownikStatus,
        'kategoria': SlownikKategoria, 'SLOWNIK_KATEGORIE': SlownikKategoria
    }
    try:
        Model = model_map.get(typ_slownika)
        if Model:
            db.query(Model).filter(Model.Wartosc == wartosc).delete()
            db.commit()
    finally:
        db.close()

# Alerty Config (Admin)
def pobierz_konfiguracje_alertow():
    db = get_db_session()
    try:
        # --- AUTO-SETUP BAZY DANYCH ---
        if db.query(KonfiguracjaAlerty).count() == 0:
            domyslne_reguly = [
                KonfiguracjaAlerty(KodPola="SzczepienieWscieklizna", Etykieta="Wścieklizna", DniWaznosci=365, CzyAktywny=True),
                KonfiguracjaAlerty(KodPola="SzczepienieZakazne", Etykieta="Choroby zakaźne", DniWaznosci=365, CzyAktywny=True),
                KonfiguracjaAlerty(KodPola="Odrobaczenie", Etykieta="Odrobaczanie", DniWaznosci=90, CzyAktywny=True),
                KonfiguracjaAlerty(KodPola="OchronaKleszczeDo", Etykieta="Ochrona na kleszcze", DniWaznosci=0, CzyAktywny=True)
            ]
            db.add_all(domyslne_reguly)
            db.commit()
        # ------------------------------
        
        q = db.query(KonfiguracjaAlerty)
        df = pd.read_sql(q.statement, db.bind)
        return df
    finally:
        db.close()

def zapisz_konfiguracje_alertow(edited_df):
    db = get_db_session()
    try:
        for index, row in edited_df.iterrows():
            db.query(KonfiguracjaAlerty).filter(KonfiguracjaAlerty.KodPola == row['KodPola']).update({
                KonfiguracjaAlerty.Etykieta: row['Etykieta'],
                KonfiguracjaAlerty.DniWaznosci: row['DniWaznosci'],
                KonfiguracjaAlerty.CzyAktywny: bool(row['CzyAktywny'])
            })
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Błąd zapisu alertów: {e}")
        return False
    finally:
        db.close()


# ==============================================================================
# 10. STATYSTYKI DASHBOARDU
# ==============================================================================

def get_dashboard_stats():
    """
    Pobiera zagregowane statystyki do wyświetlenia na Dashboardzie.
    Zwraca słownik z policzonymi wartościami.
    """
    db = get_db_session()
    try:
        today = date.today()
        thirty_days_ago = today - timedelta(days=30)

        # 1. Zwierzęta w fundacji (wykluczamy Adoptowane i Za Tęczowym Mostem)
        w_fundacji = db.query(Zwierze).filter(
            Zwierze.StatusZwierzecia.notin_(['Adoptowany', 'Za Tęczowym Mostem'])
        ).count()

        # 2. Aktywni wolontariusze
        aktywni_wolo = db.query(Uzytkownik).filter(
            Uzytkownik.Rola == 'Wolontariusz',
            Uzytkownik.CzyAktywny == True
        ).count()

        # 3. Aktywne domy tymczasowe (unikalna liczba osób będących opiekunami zwierząt w DT)
        aktywne_dt = db.query(func.count(func.distinct(Zwierze.IDOpiekun))).filter(
            Zwierze.StatusZwierzecia == 'Dom Tymczasowy'
        ).scalar() or 0

        # 4. Adopcje w ostatnim miesiącu (Zdarzenia z kategorii 'Adopcja')
        adopcje_miesiac = db.query(HistoriaZdarzen).filter(
            HistoriaZdarzen.Kategoria == 'Adopcja',
            HistoriaZdarzen.DataZdarzenia >= thirty_days_ago
        ).count()

        return {
            "w_fundacji": w_fundacji,
            "aktywni_wolo": aktywni_wolo,
            "aktywne_dt": aktywne_dt,
            "adopcje_miesiac": adopcje_miesiac
        }
    except Exception as e:
        print(f"Błąd pobierania statystyk: {e}")
        return {
            "w_fundacji": 0, "aktywni_wolo": 0, "aktywne_dt": 0, "adopcje_miesiac": 0
        }
    finally:
        db.close()