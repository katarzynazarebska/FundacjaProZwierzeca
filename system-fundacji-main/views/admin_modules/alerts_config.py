"""
PODMODUŁ ADMINA: ALERTÓW

"""
import streamlit as st
import crud
import pandas as pd

def render_alerts_config():
    
    with st.container(border=True):
        st.info("Zdefiniuj, po ilu dniach system ma oznaczać szczepienia/badania jako przeterminowane (czerwone).")
    
        # 1. Pobranie danych
        try:
            df_config = crud.pobierz_konfiguracje_alertow()
        except AttributeError:
            st.error("Błąd funkcji CRUD.")
            return

        if df_config.empty:
            st.warning("Brak konfiguracji. Uruchom setup.")
            return

        # 2. Edycja
        edited_df = st.data_editor(
            df_config,
            column_config={
                "KodPola": st.column_config.TextColumn("System ID", disabled=True),
                "Etykieta": st.column_config.TextColumn("Nazwa Wyświetlana"),
                "DniWaznosci": st.column_config.NumberColumn("Ważność (dni)", min_value=0, max_value=3650, format="%d dni"),
                "CzyAktywny": st.column_config.CheckboxColumn("Włączony?")
            },
            hide_index=True,
            use_container_width=True,
            key="alerts_editor_final"
        )

        st.write("")
        # 3. Zapis 
        if st.button("💾 Zapisz Konfigurację", type="primary", use_container_width=True):
            if crud.zapisz_konfiguracje_alertow(edited_df):
                st.success("Zaktualizowano ustawienia alertów!")
                st.rerun()
            else:
                st.error("Błąd zapisu.")