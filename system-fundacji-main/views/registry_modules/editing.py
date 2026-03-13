"""
MODUŁ REJESTRU: EDYCJA

"""
import streamlit as st
import crud
from datetime import date

# --- STYL LOKALNY ---
LOCAL_CSS = """
<style>
    /* Nagłówek - wyśrodkowany, dopasowany do jasnego motywu */
    .edit-header {
        text-align: center;
        font-size: 2.5em;
        font-weight: 800;
        color: #3498db !important; /* Fundacyjny błękit */
        margin-bottom: 5px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
"""

def render_edit():
    st.markdown(LOCAL_CSS, unsafe_allow_html=True)

    # 1. Weryfikacja ID
    try:
        id_zw = int(st.session_state.active_animal_id)
    except:
        st.error("Błąd ID.")
        if st.button("Wróć"):
            st.session_state.view_mode = "list"
            st.rerun()
        st.stop()

    # 2. Pobranie danych
    zwierze = crud.pobierz_szczegoly_zwierzecia(id_zw)
    if not zwierze:
        st.error("Nie znaleziono zwierzęcia.")
        return

    # 3. Słowniki
    try: gatunki = crud.pobierz_slownik("gatunek")
    except: gatunki = ["Pies", "Kot"]

    try: statusy = crud.pobierz_slownik("status")
    except: statusy = ["Do adopcji", "Kwarantanna", "Adoptowany"]

    try:
        df_osoby = crud.pobierz_wszystkie_osoby()
        mapa_osob = {row['IDOsoba']: f"{row['Imie']} {row['Nazwisko']}" for _, row in df_osoby.iterrows()}
        opcje_osob_ids = [None] + list(mapa_osob.keys())
    except:
        mapa_osob = {}
        opcje_osob_ids = [None]

    def format_func_osoba(id_os):
        if id_os is None: return "- brak / nie wybrano -"
        return mapa_osob.get(id_os, f"ID: {id_os}")

    # --- POCZĄTEK FORMULARZA ---
    with st.form("edit_form", border=False):
        
        # === GÓRNA BELKA (Anuluj | Tytuł | Zapisz) ===
        c_back, c_title, c_save = st.columns([1, 6, 1.5], vertical_alignment="center")
        
        with c_back:
            # Przycisk Anuluj (jako submit secondary)
            if st.form_submit_button("⬅️ Anuluj", type="secondary", use_container_width=True):
                st.session_state.view_mode = "details"
                st.rerun()
                
        with c_title:
            st.markdown(f"<div class='edit-header'>✏️ Edycja: {zwierze.Imie}</div>", unsafe_allow_html=True)
            
        with c_save:
            # PRZYCISK ZAPISU
            is_saved = st.form_submit_button("💾 Zapisz", type="primary", use_container_width=True)

        st.divider()

        # === TREŚĆ FORMULARZA (Zakładki) ===
        tab_base, tab_med = st.tabs(["📝 Dane Podstawowe", "🏥 Dane Medyczne"])
        
        # -- Zakładka 1: Dane Podstawowe --
        with tab_base:
            c1, c2 = st.columns(2)
            with c1:
                new_imie = st.text_input("Imię", value=zwierze.Imie)
                new_gatunek = st.selectbox("Gatunek", gatunki, index=gatunki.index(zwierze.Gatunek) if zwierze.Gatunek in gatunki else 0)
                new_rasa = st.text_input("Rasa", value=zwierze.Rasa or "")
                plec_idx = 0
                if zwierze.Plec == "Samica": plec_idx = 1
                new_plec = st.radio("Płeć", ["Samiec", "Samica"], index=plec_idx, horizontal=True)

            with c2:
                new_chip = st.text_input("Nr Chip", value=zwierze.NrChip or "")
                new_status = st.selectbox("Status", statusy, index=statusy.index(zwierze.StatusZwierzecia) if zwierze.StatusZwierzecia in statusy else 0)
                new_data_ur = st.date_input("Data Urodzenia", value=zwierze.DataUrodzenia)
                new_data_przyjecia = st.date_input("Data Przyjęcia", value=zwierze.DataPrzyjecia)

            st.markdown("##### Ludzie i Organizacja")
            with st.container(border=True):
                col_ppl1, col_ppl2 = st.columns(2)
                with col_ppl1:
                    current_nadzor_idx = 0
                    if zwierze.IDNadzor in opcje_osob_ids:
                        current_nadzor_idx = opcje_osob_ids.index(zwierze.IDNadzor)
                    new_nadzor = st.selectbox("Nadzór (Wolontariusz)", opcje_osob_ids, format_func=format_func_osoba, index=current_nadzor_idx)
                    new_zrodlo = st.text_input("Źródło Finansowania", value=zwierze.ZrodloFinansowania or "")

                with col_ppl2:
                    current_opiekun_idx = 0
                    if zwierze.IDOpiekun in opcje_osob_ids:
                        current_opiekun_idx = opcje_osob_ids.index(zwierze.IDOpiekun)
                    new_opiekun = st.selectbox("Opiekun / Dom Tymczasowy", opcje_osob_ids, format_func=format_func_osoba, index=current_opiekun_idx)
            
            st.write("")
            c_check1, c_check2 = st.columns(2)
            with c_check1:
                new_olx = st.checkbox("Ogłoszenie OLX", value=bool(zwierze.CzyOgloszenieOLX))
            with c_check2:
                new_www = st.checkbox("Ogłoszenie WWW", value=bool(zwierze.CzyOgloszenieWWW))

            st.markdown("##### 📝 Opis")
            new_opis = st.text_area("Opis ogólny", value=zwierze.Opis or "", height=100)
            
            st.markdown("##### 📷 Zdjęcie profilowe")
            uploaded_photo = st.file_uploader("Zmień zdjęcie (zastąpi obecne)", type=['png', 'jpg', 'jpeg'])

        # -- Zakładka 2: Dane Medyczne --
        with tab_med:
            m1, m2 = st.columns(2)
            with m1:
                new_wsciek = st.date_input("Szczepienie Wścieklizna", value=zwierze.SzczepienieWscieklizna)
                new_zakazne = st.date_input("Szczepienie Zakaźne", value=zwierze.SzczepienieZakazne)
                
                val_odrob = getattr(zwierze, "Odrobaczenie", None)
                new_odrob = st.date_input("Odrobaczanie", value=val_odrob)
            
            with m2:
                new_kastracja = st.date_input("Kastracja / Sterylizacja", value=zwierze.DataKastracji)
                new_kleszcze = st.date_input("Ochrona p/kleszczom (Ważne do)", value=zwierze.OchronaKleszczeDo)

            st.write("")
            val_opis_zdrowia = getattr(zwierze, "OpisZdrowia", "")
            new_opis_med = st.text_area("Opis / Notatki Medyczne", value=val_opis_zdrowia or "", height=150)

    # --- LOGIKA ZAPISU ---
    if is_saved:
        dane_update = {
            "Imie": new_imie,
            "Gatunek": new_gatunek,
            "Rasa": new_rasa,
            "Plec": new_plec,
            "NrChip": new_chip,
            "StatusZwierzecia": new_status,
            "DataUrodzenia": new_data_ur,
            "DataPrzyjecia": new_data_przyjecia,
            "CzyOgloszenieOLX": new_olx,
            "CzyOgloszenieWWW": new_www,
            "Opis": new_opis,
            "IDNadzor": new_nadzor,
            "IDOpiekun": new_opiekun,
            "ZrodloFinansowania": new_zrodlo,
            "SzczepienieWscieklizna": new_wsciek,
            "SzczepienieZakazne": new_zakazne,
            "Odrobaczenie": new_odrob,
            "DataKastracji": new_kastracja,
            "OchronaKleszczeDo": new_kleszcze,
            "OpisZdrowia": new_opis_med 
        }

        if uploaded_photo:
            bytes_data = uploaded_photo.getvalue()
            crud.aktualizuj_zdjecie(id_zw, bytes_data)

        sukces = crud.aktualizuj_dane_podstawowe(id_zw, dane_update)
        
        if sukces:
            st.success("Zapisano zmiany!")
            st.session_state.view_mode = "details"
            st.rerun()
        else:
            st.error("Wystąpił błąd podczas zapisu.")