"""
MODUŁ: REJESTR ZWIERZĄT

"""
import streamlit as st
import pandas as pd
import crud
from datetime import date
from views.registry_modules import admission, details, editing, adoption

# Funkcja pomocnicza do obliczania wieku
def oblicz_wiek(data_ur):
    if not data_ur:
        return "-"
    try:
        dt = pd.to_datetime(data_ur)
        lata = date.today().year - dt.year
        return f"{lata} lat"
    except:
        return "-"

def render_registry():
    # Inicjalizacja stanu
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = "list"
    if 'active_animal_id' not in st.session_state:
        st.session_state.active_animal_id = None

    # --- ROUTING WIDOKÓW ---
    mode = st.session_state.view_mode

    if mode == "list":
        render_list_view()
    elif mode == "details":
        details.render_details()
    elif mode == "admission":
        admission.render_admission()
    elif mode == "edit":
        editing.render_edit()
    elif mode == "adoption_process":
        adoption.render_adoption()

def render_list_view():
    # --- 1. NAGŁÓWEK ---
    c_back, c_title, c_void = st.columns([1, 6, 1])
    
    with c_back:
        if st.button("⬅️ Wróć", help="Wróć do Kokpitu", use_container_width=False, type="secondary"):
            st.session_state.current_module = "home"
            st.rerun()
            
    with c_title:
        st.markdown("<div class='registry-title'>Rejestr Zwierząt</div>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)

    # --- 2. PASEK NARZĘDZI ---
    c_search, c_add = st.columns([5, 1.5], vertical_alignment="bottom")
    
    with c_search:
        search_query = st.text_input("Szukaj", placeholder="Wpisz imię, rasę lub nr chip...", label_visibility="collapsed")
    
    with c_add:
        if st.session_state.user_role in ["Admin", "Pracownik"]:
            if st.button("➕ Przyjmij", type="primary", use_container_width=True):
                st.session_state.view_mode = "admission"
                st.rerun()
        else:
             st.write("") 

    # --- 3. POBRANIE DANYCH ---
    rola = st.session_state.user_role
    id_uzytkownika = st.session_state.user_id_osoba
    
    if rola == "DT":
        df = crud.pobierz_rejestr_rozszerzony(id_opiekun=id_uzytkownika)
    else:
        df = crud.pobierz_rejestr_rozszerzony()

    if df.empty:
        st.info("Baza jest pusta. Dodaj pierwsze zwierzę.")
        return

    df['Wiek'] = df['DataUrodzenia'].apply(oblicz_wiek)

    # --- 4. FILTRY ZAAWANSOWANE ---
    with st.expander("🔍 Filtry", expanded=False):
        c_f1, c_f2, c_f3, c_f4 = st.columns(4)
        
        with c_f1:
            try: opcje_gat = crud.pobierz_slownik("gatunek")
            except: opcje_gat = ["Pies", "Kot"]
            sel_gatunek = st.multiselect("Gatunek", opcje_gat)
            
        with c_f2:
            try: opcje_stat = crud.pobierz_slownik("status")
            except: opcje_stat = ["Do adopcji", "W trakcie leczenia", "Adoptowany"]
            sel_status = st.multiselect("Status", opcje_stat)

        with c_f3:
            lista_opiekunow = sorted(df['OpiekunNazwa'].dropna().unique().tolist())
            sel_opiekun = st.multiselect("Opiekun (Adopcja)", lista_opiekunow)

        with c_f4:
            lista_nadzorcow = sorted(df['NadzorcaNazwa'].dropna().unique().tolist())
            sel_nadzor = st.multiselect("Nadzór / Wolo.", lista_nadzorcow)

    st.write("") 

    # --- 5. LOGIKA FILTROWANIA ---
    if search_query:
        q = search_query.lower()
        mask = (
            df['Imie'].str.lower().str.contains(q, na=False) |
            df['Rasa'].str.lower().str.contains(q, na=False) |
            df['NrChip'].str.lower().str.contains(q, na=False)
        )
        df = df[mask]
        
    if sel_gatunek: df = df[df['Gatunek'].isin(sel_gatunek)]
    if sel_status: df = df[df['StatusZwierzecia'].isin(sel_status)]
    if sel_opiekun: df = df[df['OpiekunNazwa'].isin(sel_opiekun)]
    if sel_nadzor: df = df[df['NadzorcaNazwa'].isin(sel_nadzor)]

    # --- 6. TABELA ---
    column_cfg = {
        "IDZwierze": None,         
        "DataUrodzenia": None,     
        "NrChip": None,            
        "Imie": st.column_config.TextColumn("Imię", width="medium"),
        "Gatunek": st.column_config.TextColumn("Gatunek", width="small"),
        "Rasa": st.column_config.TextColumn("Rasa", width="medium"),
        "Plec": st.column_config.TextColumn("Płeć", width="small"),
        "Wiek": st.column_config.TextColumn("Wiek", width="small"),
        "StatusZwierzecia": st.column_config.TextColumn("Status", width="medium"),
        "OpiekunNazwa": st.column_config.TextColumn("🏠 Opiekun", width="medium"),
        "NadzorcaNazwa": st.column_config.TextColumn("🩺 Nadzór", width="medium"),
    }
    
    cols_to_show = ["Imie", "Gatunek", "Rasa", "Plec", "Wiek", "StatusZwierzecia", "OpiekunNazwa", "NadzorcaNazwa", "IDZwierze"]
    
    event = st.dataframe(
        df[cols_to_show],
        column_config=column_cfg,
        use_container_width=True,
        hide_index=True,
        height=700, 
        on_select="rerun",
        selection_mode="single-row"
    )

    # --- 7. KLIKNIĘCIE W WIERSZ ---
    if event.selection.rows:
        idx = event.selection.rows[0]
        selected_id = df.iloc[idx]['IDZwierze']
        
        st.session_state.active_animal_id = int(selected_id)
        st.session_state.view_mode = "details"
        st.rerun()