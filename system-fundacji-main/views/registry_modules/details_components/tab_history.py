"""
KOMPONENT KARTY: ZAKŁADKA 'HISTORIA'

"""
import streamlit as st
import crud
import pandas as pd

def skroc_tekst(tekst, limit=80):
    if not isinstance(tekst, str):
        return ""
    if len(tekst) > limit:
        return tekst[:limit] + "..."
    return tekst

def render_tab(id_zwierze):
    
    # --- 1. DODAWANIE NOWEGO WPISU ---
    with st.expander("➕ Dodaj nowe zdarzenie", expanded=False):
        with st.form("nowy_wpis_form", clear_on_submit=True):
            c_kat, c_plik = st.columns([1, 1])
            
            with c_kat:
                try:
                    kat_opcje = crud.pobierz_slownik("kategoria")
                except:
                    kat_opcje = ["Weterynaria", "Behawiorysta", "Administracja", "Inne"]
                kategoria = st.selectbox("Kategoria", kat_opcje)
            
            with c_plik:
                pliki = st.file_uploader("Załączniki (Zdjęcia, PDF)", accept_multiple_files=True)

            opis = st.text_area("Opis zdarzenia", height=100)
            submitted = st.form_submit_button("Zapisz wpis", type="primary")
            
            if submitted:
                if not opis:
                    st.error("Opis jest wymagany.")
                else:
                    # Fallback ID usera
                    current_user_id = st.session_state.get('user_id', 1)
                    
                    # 1. Tworzymy wpis
                    id_historia = crud.dodaj_wpis_historii(id_zwierze, current_user_id, kategoria, opis)
                    
                    if id_historia:
                        # 2. Dodajemy załączniki 
                        sukces_pliki = 0
                        if pliki:
                            for p in pliki:
                                ok, msg = crud.dodaj_zalacznik(id_historia, p)
                                if ok:
                                    sukces_pliki += 1
                                else:
                                    st.error(f"Błąd pliku {p.name}: {msg}")
                        
                        st.success(f"Dodano wpis. Załączników: {sukces_pliki}")
                        st.rerun()
                    else:
                        st.error("Błąd zapisu do bazy.")

    st.divider()

    # --- 2. FILTRY I TABELA ---
    df = crud.pobierz_historie(id_zwierze)
    
    if df.empty:
        st.info("Brak wpisów w historii.")
        return

    # PANEL FILTRÓW
    c_filter_1, c_filter_2 = st.columns([1, 2])
    with c_filter_1:
        dostepne_kategorie = df['Kategoria'].unique().tolist()
        wybrane_kategorie = st.multiselect("Filtruj kategorię", dostepne_kategorie, placeholder="Wszystkie")
    with c_filter_2:
        szukana_f = st.text_input("Szukaj w opisie", placeholder="Np. szczepienie...", label_visibility="visible")

    # LOGIKA FILTROWANIA
    df_filtered = df.copy()
    if wybrane_kategorie:
        df_filtered = df_filtered[df_filtered['Kategoria'].isin(wybrane_kategorie)]
    if szukana_f:
        df_filtered = df_filtered[df_filtered['Opis'].str.contains(szukana_f, case=False, na=False)]

    st.caption(f"Wyświetlono: {len(df_filtered)} wpisów")

    df_display = df_filtered.copy()
    df_display['Podgląd Opisu'] = df_display['Opis'].apply(lambda x: skroc_tekst(x, 90))
    
    column_cfg = {
        "IDHistoria": None,
        "Opis": None,
        "Podgląd Opisu": st.column_config.TextColumn("Opis zdarzenia", width="large"),
        "DataZdarzenia": st.column_config.DateColumn("Data", format="DD.MM.YYYY", width="small"),
        "Kategoria": st.column_config.TextColumn("Kategoria", width="medium"),
        "Autor": st.column_config.TextColumn("Autor", width="small"),
    }
    cols = ["DataZdarzenia", "Kategoria", "Podgląd Opisu", "Autor"]

    # TABELA
    event = st.dataframe(
        df_display[cols],
        column_config=column_cfg,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    # --- 3. SZCZEGÓŁY WPISU + ZAŁĄCZNIKI ---
    if event.selection.rows:
        idx = event.selection.rows[0]
        
        row = df_filtered.iloc[idx]
        
        try:
            id_historia = int(row['IDHistoria'])
        except:
            id_historia = row['IDHistoria']
            
        pelny_opis = row['Opis']
        data_zd = row['DataZdarzenia']
        kategoria = row['Kategoria']
        autor = row['Autor']
        
        st.write("")
        st.markdown("---")
        st.markdown(f"#### 🔎 Szczegóły wpisu z dnia {data_zd}")
        
        with st.container(border=True):
            c1, c2 = st.columns([1, 4])
            with c1:
                st.caption("Kategoria / Autor")
                st.markdown(f"**{kategoria}**")
                st.markdown(f"👤 {autor}")
            with c2:
                st.caption("Pełna treść:")
                st.write(pelny_opis)
            
            # --- ZAŁĄCZNIKI ---
            st.divider()
            
            pliki_df = crud.pobierz_liste_zalacznikow(id_historia)
            
            if not pliki_df.empty:
                st.markdown(f"**📎 Załączniki ({len(pliki_df)}):**")
                
                cols_files = st.columns(3)
                for index, file_row in pliki_df.iterrows():
                    wynik = crud.pobierz_plik_content(file_row['ID_Zalacznik'])
                    
                    if wynik:
                        nazwa, content, typ = wynik
                        with cols_files[index % 3]:
                            st.download_button(
                                label=f"⬇️ {nazwa}",
                                data=content,
                                file_name=nazwa,
                                mime=typ,
                                key=f"dl_{file_row['ID_Zalacznik']}",
                                use_container_width=True
                            )
            else:
                st.caption("Brak załączników dla tego wpisu.")