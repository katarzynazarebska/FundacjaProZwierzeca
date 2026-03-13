import random
from datetime import date, timedelta
from faker import Faker
from werkzeug.security import generate_password_hash
from database import SessionLocal
import models as m

fake = Faker('pl_PL')

def seed_realistic_data():
    db = SessionLocal()
    print("--- ROZPOCZYNAM GENEROWANIE REALISTYCZNYCH DANYCH ---")

    # ==========================================
    # 1. PULE REALISTYCZNYCH DANYCH
    # ==========================================
    psie_imiona = ["Burek", "Luna", "Reksio", "Azor", "Bella", "Maks", "Daisy", "Rocky", "Kapsel", "Pusia", "Ares", "Sonia", "Tofik", "Fiona", "Ciapek", "Fąfel", "Kulka"]
    rasy = ["Mieszaniec", "Owczarek Niemiecki", "Labrador", "Jamnik", "Kundelek", "Amstaff", "Golden Retriever", "Terier"]
    zrodla_finansowania = ["Środki Fundacji", "Darczyńca prywatny", "Zbiórka publiczna"]
    
    opisy_zdrowia = [
        "Zdrowy, pełen energii, bez widocznych problemów.",
        "Alergia pokarmowa (drób) - wymaga karmy hipoalergicznej (np. z jagnięciną).",
        "Brak lewego oka w wyniku starego urazu. Radzi sobie świetnie, nie wymaga leczenia.",
        "Padaczka - przyjmuje leki (Luminal) 2x dziennie. Przy regularnym dawkowaniu brak ataków.",
        "Starszy pies, zwyrodnienie stawów. Wymaga suplementacji (np. ArthroFos) i unikania schodów.",
        "Głuchy od urodzenia. Reaguje na gesty rąk i silne wibracje podłoża.",
        "Delikatne szmery w sercu, wymaga kontroli kardiologicznej za 6 miesięcy."
    ]

    notatki_wolontariusza = [
        "Na spacerze bardzo ciągnie na smyczy, ekscytuje się na widok innych psów.",
        "Uwielbia węszyć, zrobiliśmy dzisiaj długi spacer po lesie.",
        "Bardzo przyjazny w stosunku do dzieci, dawał się głaskać przez siatkę.",
        "Trochę wycofany w boksie, ale po wyjściu na trawę od razu się otwiera."
    ]

    notatki_behawiorysta = [
        "Pies wykazuje lęk separacyjny. Zalecono wprowadzanie klatki kenelowej i trening odwrażliwiania.",
        "Obrona zasobów przy jedzeniu - zalecono karmienie z ręki i wymianę na lepsze smaczki.",
        "Reaktywność smyczowa na inne psy. Ćwiczyliśmy dzisiaj mijanki z dużej odległości."
    ]

    # ==========================================
    # 2. GENEROWANIE OSÓB I KONT
    # ==========================================
    print("Generuję 10 osób (Pracownicy, Wolontariusze, Adoptujący)...")
    
    role = ["Pracownik", "Pracownik", "Wolontariusz", "Wolontariusz", "Wolontariusz", "Brak", "Brak", "Brak", "Brak", "Brak"]
    id_personelu = []   # Do nadzorowania
    id_adoptujacych = [] # Na opiekunów
    id_uzytkownikow = [] # Autorzy wpisów w historii

    for rola in role:
        osoba = m.Osoba(
            Imie=fake.first_name(),
            Nazwisko=fake.last_name(),
            Telefon=fake.phone_number().replace(" ", "")[:15],
            Email=fake.unique.email()[:100],
            AdresMiasto=fake.city()[:50],
            AdresUlica=fake.street_name()[:100],
            AdresNrLokalu=str(random.randint(1, 150)) if random.choice([True, False]) else None,
            AdresKodPocztowy=fake.postcode()[:10],
            DataRejestracji=fake.date_between(start_date='-2y', end_date='today')
        )
        db.add(osoba)
        db.commit()
        db.refresh(osoba)

        if rola != "Brak":
            id_personelu.append(osoba.IDOsoba)
            login = f"{osoba.Imie[0].lower()}{osoba.Nazwisko.lower()}"
            login = login.replace('ą','a').replace('ć','c').replace('ę','e').replace('ł','l').replace('ń','n').replace('ó','o').replace('ś','s').replace('ź','z').replace('ż','z')
            
            uzytkownik = m.Uzytkownik(
                LoginName=login + str(random.randint(1,99)),
                Email=osoba.Email,
                HasloHash=generate_password_hash("haslo123"),
                Rola=rola,
                CzyAktywny=True,
                IDOsoba=osoba.IDOsoba
            )
            db.add(uzytkownik)
            db.commit()
            db.refresh(uzytkownik)
            id_uzytkownikow.append(uzytkownik.IDUser)
        else:
            id_adoptujacych.append(osoba.IDOsoba)

    # ==========================================
    # 3. GENEROWANIE 15 PSÓW
    # ==========================================
    print("Generuję 15 psów...")
    statusy = ["Za Tęczowym Mostem"] * 2 + ["Adoptowany"] * 4 + ["Do adopcji", "Do adopcji", "W trakcie leczenia", "Kwarantanna", "Dom Tymczasowy", "Do adopcji", "W trakcie leczenia", "Do adopcji", "Do adopcji"]
    
    for i, status in enumerate(statusy):
        data_przyjecia = fake.date_between(start_date='-1y', end_date='-1m')
        data_urodzenia = data_przyjecia - timedelta(days=random.randint(300, 4000))
        
        nadzorca = random.choice(id_personelu) if id_personelu else None
        opiekun = random.choice(id_adoptujacych) if status in ["Adoptowany", "Dom Tymczasowy"] and id_adoptujacych else None

        imie_psa = psie_imiona[i % len(psie_imiona)] 

        zwierze = m.Zwierze(
            Imie=imie_psa,
            Gatunek="Pies",
            Rasa=random.choice(rasy),
            Plec=random.choice(["Samiec", "Samica"]),
            DataUrodzenia=data_urodzenia,
            DataPrzyjecia=data_przyjecia,
            StatusZwierzecia=status,
            NrChip=f"6160939{random.randint(10000000, 99999999)}",
            Opis=f"{imie_psa} to wspaniały pies, który trafił do fundacji z interwencji. Szukamy dla niego kochającego i cierpliwego domu.",
            ZrodloFinansowania=random.choice(zrodla_finansowania),
            CzyOgloszenieOLX=random.choice([True, False]),
            CzyOgloszenieWWW=True,
            DataKastracji=data_przyjecia + timedelta(days=14) if random.choice([True, False]) else None,
            SzczepienieWscieklizna=data_przyjecia + timedelta(days=365), 
            OpisZdrowia=random.choice(opisy_zdrowia),
            IDNadzor=nadzorca,
            IDOpiekun=opiekun
        )
        db.add(zwierze)
        db.commit()
        db.refresh(zwierze)

        # ==========================================
        # 4. GENEROWANIE 5 ZDARZEŃ W HISTORII
        # ==========================================
        for d in range(5):
            autor = random.choice(id_uzytkownikow) if id_uzytkownikow else None
            data_zdarzenia = data_przyjecia + timedelta(days=random.randint(1, 30))
            
            kategoria = random.choice(["Wizyta Weterynaryjna", "Szczepienie", "Zabieg", "Behawiorysta", "Notatka Wolontariusza"])
            
            if kategoria == "Szczepienie":
                opis = random.choice(["Podano szczepionkę przeciwko wściekliźnie (Nobivac).", "Szczepienie na choroby zakaźne (Eurican). Pies zniósł dobrze."])
            elif kategoria == "Zabieg":
                opis = random.choice(["Zabieg kastracji. Przebieg bez powikłań, pies wybudza się prawidłowo.", "Usunięcie kamienia nazębnego w znieczuleniu ogólnym.", "Zeszycie rany na łapie. Założono 3 szwy."])
            elif kategoria == "Behawiorysta":
                opis = random.choice(notatki_behawiorysta)
            elif kategoria == "Notatka Wolontariusza":
                opis = random.choice(notatki_wolontariusza)
            else: 
                opis = random.choice(["Wizyta kontrolna. Osłuchowo w porządku, waga w normie.", "Odrobaczenie tabletką Drontal Plus.", "Pies dostał preparat Bravecto na kleszcze (ważny 3 miesiące)."])

            if status == "Adoptowany" and d == 4:
                kategoria = "Adopcja"
                opis = "Podpisano umowę adopcyjną. Pies pojechał do nowego domu! Powodzenia!"
                data_zdarzenia = date.today() - timedelta(days=random.randint(1, 10))

            zdarzenie = m.HistoriaZdarzen(
                IDZwierze=zwierze.IDZwierze,
                IDUser=autor,
                DataZdarzenia=data_zdarzenia,
                Kategoria=kategoria,
                Opis=opis
            )
            db.add(zdarzenie)

    db.commit()
    db.close()
    print("--- ZAKOŃCZONO SUKCESEM! DANE SĄ GOTOWE DO OBRONY PROJEKTU. ---")
    print("Konta do testów mają format loginu: pierwsza_litera_imienia + nazwisko + liczba (np. jkowalski12).")
    print("Hasło dla każdego wygenerowanego konta to: haslo123")

if __name__ == "__main__":
    seed_realistic_data()