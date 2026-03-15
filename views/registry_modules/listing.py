"""
MODUŁ REJESTRU: LISTA ZWIERZĄT

"""
import streamlit as st
import crud
import pandas as pd

def render_list():
    role = st.session_state.user_role
    
    # 1. Pobieranie słowników 
    gatunki = crud.pobierz_slownik('gatunek')
    statusy = crud.pobierz_slownik('status')

    # 2. Pasek akcji 
    c_filt, c_act = st.columns([4, 1])
    
    with c_act:
        if role in ["Admin", "Wolontariusz"]:
             if st.button("➕ Przyjmij", type="primary", use_container_width=True):
                st.session_state.view_mode = "admission"
                st.rerun()
        else:
             st.write("") 

    # 3. Filtry UI
    with c_filt:
        c1, c2, c3 = st.columns(3)
        with c1: 
            f_gat = st.multiselect("Gatunek", gatunki, default=[])
        with c2: 
            f_stat = st.multiselect("Status", statusy, default=[])
        with c3: 
            f_txt = st.text_input("Szukaj (Imię/Rasa)")

    # 4. Pobieranie danych z bazy
    id_dla_dt = None
    if role == "DT":
        id_dla_dt = st.session_state.user_id_osoba
    
    df = crud.pobierz_liste_zwierzat(id_opiekun_dt=id_dla_dt)

    if df.empty:
        if role == "DT":
            st.info("Nie masz przypisanych żadnych zwierząt.")
        else:
            st.info("Brak zwierząt w bazie.")
        return

    # 5. Logika Filtrowania
    if f_gat:
        df = df[df['Gatunek'].isin(f_gat)] 
    
    
    if f_stat:
        df = df[df['StatusZwierzecia'].isin(f_stat)]
        
    if f_txt:
        mask = df['Imie'].str.contains(f_txt, case=False, na=False) | \
               df['Rasa'].str.contains(f_txt, case=False, na=False)
        df = df[mask]

    # 6. Przygotowanie danych do wyświetlenia
    df['Foto'] = df['Zdjecie'].apply(lambda x: "📸" if x else "❌")

    df_display = df[['IDZwierze', 'Foto', 'Imie', 'Rasa', 'StatusZwierzecia']].copy()
    
    # 7. Wyświetlanie interaktywnej tabeli
    st.markdown("### Lista Podopiecznych")
    
    event = st.dataframe(
        df_display,
        column_config={
            "IDZwierze": st.column_config.NumberColumn("ID", width="small"),
            "Foto": st.column_config.TextColumn("Zdjęcie", width="small"),
            "Imie": st.column_config.TextColumn("Imię", width="medium"),
            "Rasa": st.column_config.TextColumn("Rasa/Typ", width="medium"),
            "StatusZwierzecia": st.column_config.TextColumn("Status", width="medium"),
        },
        on_select="rerun",
        selection_mode="single-row",
        hide_index=True,
        use_container_width=True
    )

    if len(event.selection.rows) > 0:
        selected_index = event.selection.rows[0]
        wybrane_id = df_display.iloc[selected_index]["IDZwierze"]
        
        st.session_state.active_animal_id = int(wybrane_id)
        st.session_state.view_mode = "details"
        st.rerun()