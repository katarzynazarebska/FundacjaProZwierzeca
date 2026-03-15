"""
MODUŁ REJESTRU: PRZYJĘCIE ZWIERZĘCIA

"""
import streamlit as st
import crud
from datetime import date

# --- STYL LOKALNY ---
LOCAL_CSS = """
<style>
    .admission-title {
        text-align: center;
        font-size: 2.2em;
        font-weight: 800;
        color: #3498db !important; /* Fundacyjny błękit */
        margin-bottom: 20px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
</style>
"""

def render_admission():
    st.markdown(LOCAL_CSS, unsafe_allow_html=True)

    # --- NAGŁÓWEK ---
    c_back, c_title, c_void = st.columns([1, 6, 1])
    with c_back:
        if st.button("⬅️ Anuluj", help="Wróć do listy", type="secondary", use_container_width=False):
            st.session_state.view_mode = "list"
            st.rerun()
    with c_title:
        st.markdown("<div class='admission-title'>Nowe Przyjęcie</div>", unsafe_allow_html=True)

    # --- SŁOWNIKI ---
    try: gatunki = crud.pobierz_slownik("gatunek")
    except: gatunki = ["Pies", "Kot"]

    try:
        statusy = crud.pobierz_slownik("status")
        default_status_idx = 0
        if "Kwarantanna" in statusy:
            default_status_idx = statusy.index("Kwarantanna")
    except: 
        statusy = ["Kwarantanna", "Do adopcji", "W trakcie leczenia"]
        default_status_idx = 0

    try:
        df_osoby = crud.pobierz_wszystkie_osoby()
        mapa_osob = {"- wybierz -": None}
        if not df_osoby.empty:
            for _, row in df_osoby.iterrows():
                mapa_osob[row['Display']] = row['IDOsoba']
        lista_osob = list(mapa_osob.keys())
    except:
        lista_osob = ["- błąd pobierania -"]
        mapa_osob = {}

    # --- FORMULARZ ---
    with st.form("admission_form", clear_on_submit=False):
        
        # 1. DANE PODSTAWOWE
        st.markdown("##### 📄 Dane Podstawowe")
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                imie = st.text_input("Imię")
                gatunek = st.selectbox("Gatunek", gatunki)
                rasa = st.text_input("Rasa", placeholder="np. Mieszaniec, Owczarek...")
                plec = st.selectbox("Płeć", ["Samiec", "Samica"])
            with c2:
                nr_chip = st.text_input("Nr Chip")
                status = st.selectbox("Status początkowy", statusy, index=default_status_idx)
                cd1, cd2 = st.columns(2)
                with cd1: data_przyjecia = st.date_input("Data przyjęcia", value=date.today())
                with cd2: data_urodzenia = st.date_input("Data urodzenia (przybliżona)", value=None)

        st.write("") 

        # 2. LUDZIE I ORGANIZACJA
        st.markdown("##### 👥 Ludzie i Organizacja")
        with st.container(border=True):
            c3, c4 = st.columns(2)
            with c3:
                sel_nadzor = st.selectbox("Nadzór (Wolontariusz)", lista_osob)
                zrodlo = st.text_input("Źródło finansowania", placeholder="np. Miasto, Fundacja...")
            with c4:
                sel_opiekun = st.selectbox("Opiekun / Dom Tymczasowy", lista_osob)
                st.write("Status ogłoszeń:")
                co1, co2 = st.columns(2)
                with co1: czy_olx = st.checkbox("Ogłoszenie OLX")
                with co2: czy_www = st.checkbox("Ogłoszenie WWW")

        st.write("") 
        
        # 3. OPIS I MEDIA
        st.markdown("##### 📝 Opis i Media")
        with st.container(border=True):
            opis = st.text_area("Opis zwierzęcia / Charakter", height=100)
            zdjecie = st.file_uploader("Zdjęcie profilowe", type=['jpg', 'png', 'jpeg'])

        st.write("")

        # 4. DANE MEDYCZNE (STARTOWE)
        st.markdown("##### 💉 Dane Medyczne (Startowe)")
        with st.container(border=True):
            m1, m2 = st.columns(2)
            with m1:
                szczep_wsciek = st.date_input("Szczepienie Wścieklizna", value=None)
                szczep_zakazne = st.date_input("Szczepienie Zakaźne", value=None)
                odrobaczenie = st.date_input("Odrobaczanie", value=None)
            
            with m2:
                kastracja = st.date_input("Kastracja / Sterylizacja", value=None)
                kleszcze = st.date_input("Ochrona p/kleszczom (Ważne do)", value=None)

        st.write("")
        submit_btn = st.form_submit_button("💾 Zapisz i Utwórz Kartę", type="primary", use_container_width=True)

        if submit_btn:
            if not imie:
                st.error("Imię jest wymagane!")
            else:
                id_nadzor = mapa_osob.get(sel_nadzor)
                id_opiekun = mapa_osob.get(sel_opiekun)

                zdjecie_blob = None
                if zdjecie:
                    zdjecie_blob = zdjecie.getvalue()

                new_id = crud.dodaj_nowe_zwierze(
                    imie=imie,
                    gatunek=gatunek,
                    rasa=rasa,
                    plec=plec,
                    status=status,
                    id_nadzorca=id_nadzor,
                    id_opiekun=id_opiekun,
                    nr_chip=nr_chip,
                    zrodlo=zrodlo,
                    data_przyjecia=data_przyjecia,
                    data_urodzenia=data_urodzenia,
                    opis=opis,
                    czy_olx=czy_olx,
                    czy_www=czy_www,
                    zdjecie_blob=zdjecie_blob
                )

                if new_id:
                    med_updates = {}
                    if szczep_wsciek: med_updates['SzczepienieWscieklizna'] = szczep_wsciek
                    if szczep_zakazne: med_updates['SzczepienieZakazne'] = szczep_zakazne
                    if odrobaczenie: med_updates['Odrobaczenie'] = odrobaczenie
                    if kastracja: med_updates['DataKastracji'] = kastracja
                    if kleszcze: med_updates['OchronaKleszczeDo'] = kleszcze
                    
                    if med_updates:
                        crud.aktualizuj_dane_podstawowe(new_id, med_updates)
                    
                    st.success(f"Zwierzę {imie} zostało przyjęte!")
                    st.session_state.active_animal_id = new_id
                    st.session_state.view_mode = "details"
                    st.rerun()
                else:
                    st.error("Wystąpił błąd podczas zapisu do bazy.")