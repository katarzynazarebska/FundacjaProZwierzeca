"""
MODUŁ ADMINA: BAZA OSÓB

"""
import streamlit as st
import crud
import pandas as pd
import time

def render_people_db():
    role = st.session_state.user_role
    
    # Konfiguracja zakładek
    tabs_names = ["📋 Lista Osób"]
    if role in ["Admin", "Pracownik"]:
        tabs_names.extend(["➕ Dodaj Osobę", "✏️ Edytuj Osobę"])
        
    if len(tabs_names) > 1:
        tabs = st.tabs(tabs_names)
        tab_view = tabs[0]
        tab_add = tabs[1]
        tab_edit = tabs[2] if len(tabs) > 2 else None
    else:
        tab_view = st.tabs(tabs_names)[0]
        tab_add = None
        tab_edit = None
    
    df_os = crud.pobierz_wszystkie_osoby()
    
    # --- ZAKŁADKA 1: LISTA I RODO ---
    with tab_view:
         if not df_os.empty:
             df_view = df_os.drop(columns=['Display', 'AdresUlica', 'AdresNrLokalu', 'AdresKodPocztowy'], errors='ignore')
             st.dataframe(
                 df_view, 
                 use_container_width=True,
                 hide_index=True,
                 column_config={
                     "IDOsoba": st.column_config.NumberColumn("ID", width="small"),
                     "Imie": "Imię",
                     "Nazwisko": "Nazwisko",
                     "Telefon": "Tel",
                     "Email": "E-mail",
                     "AdresMiasto": "Miasto"
                 }
             )
             
             # ===== PANEL RODO =====
             if role == "Admin":
                 st.write("")
                 st.markdown("##### 🛡️ Panel Prawny (RODO)")
                 with st.container(border=True):
                     st.warning("**Prawo do bycia zapomnianym**\n\nOperacja jest **nieodwracalna**.")
                     lista_rodo = {f"{r['Imie']} {r['Nazwisko']} (ID: {r['IDOsoba']})": r['IDOsoba'] for i, r in df_os.iterrows() if r['Nazwisko'] != "(RODO)"}
                     
                     if lista_rodo:
                         c_sel, c_btn = st.columns([3, 1], vertical_alignment="bottom")
                         with c_sel:
                             wybor = st.selectbox("Wybierz osobę do anonimizacji", list(lista_rodo.keys()))
                         with c_btn:
                             if st.button("🗑️ Anonimizuj", type="primary", use_container_width=True):
                                 id_os = lista_rodo[wybor]
                                 ok, msg = crud.anonimizuj_osobe(id_os)
                                 if ok:
                                     st.success(msg)
                                     time.sleep(1.5)
                                     st.rerun()
                                 else:
                                     st.error(msg)
                     else:
                         st.info("Brak aktywnych osób do anonimizacji.")
         else:
             st.info("Baza osób jest pusta.")
             
    # --- ZAKŁADKA 2: DODAWANIE ---
    if tab_add:
        with tab_add:
             with st.container(border=True):
                 st.markdown("##### Nowy Kontakt")
                 with st.form("add_os_form", clear_on_submit=True):
                     st.caption("Dane Kontaktowe")
                     c1, c2 = st.columns(2)
                     with c1:
                         im = st.text_input("Imię *")
                         tel = st.text_input("Telefon")
                     with c2:
                         nz = st.text_input("Nazwisko *")
                         em = st.text_input("E-mail")
                     
                     st.divider()
                     st.caption("Dane Adresowe")
                     a1, a2 = st.columns(2)
                     with a1:
                         mi = st.text_input("Miasto")
                         ul = st.text_input("Ulica")
                     with a2:
                         kod = st.text_input("Kod pocztowy")
                         lok = st.text_input("Nr lokalu/domu")
                     
                     st.write("")
                     if st.form_submit_button("💾 Zapisz w bazie", type="primary", use_container_width=True):
                         if im and nz:
                             ok, msg = crud.dodaj_osobe(im, nz, tel, em, mi, ul, lok, kod)
                             if ok:
                                st.success(f"Dodano osobę: {im} {nz}")
                                time.sleep(1)
                                st.rerun()
                             else:
                                st.error(f"Błąd: {msg}")
                         else:
                             st.warning("Pola oznaczone gwiazdką (*) są wymagane.")

    # --- ZAKŁADKA 3: EDYCJA ---
    if tab_edit:
        with tab_edit:
            if df_os.empty:
                st.info("Brak osób w bazie do edycji.")
            else:
                lista_edycji = {f"{r['Imie']} {r['Nazwisko']} (ID: {r['IDOsoba']})": r for i, r in df_os.iterrows() if r['Nazwisko'] != "(RODO)"}
                
                if not lista_edycji:
                    st.info("Brak osób do edycji (wszyscy zanonimizowani).")
                else:
                    st.markdown("##### Edycja Kontaktu")
                    wybor_edycja = st.selectbox("Wybierz osobę do edycji", list(lista_edycji.keys()), key="sel_edycja")
                    dane = lista_edycji[wybor_edycja]

                    def clean_val(val):
                        return "" if pd.isna(val) else str(val)

                    with st.form("edit_os_form"):
                        st.caption("Dane Kontaktowe")
                        e1, e2 = st.columns(2)
                        with e1:
                            e_im = st.text_input("Imię *", value=clean_val(dane.get('Imie')))
                            e_tel = st.text_input("Telefon", value=clean_val(dane.get('Telefon')))
                        with e2:
                            e_nz = st.text_input("Nazwisko *", value=clean_val(dane.get('Nazwisko')))
                            e_em = st.text_input("E-mail", value=clean_val(dane.get('Email')))
                            
                        st.divider()
                        st.caption("Dane Adresowe")
                        ea1, ea2 = st.columns(2)
                        with ea1:
                            e_mi = st.text_input("Miasto", value=clean_val(dane.get('AdresMiasto')))
                            e_ul = st.text_input("Ulica", value=clean_val(dane.get('AdresUlica')))
                        with ea2:
                            e_kod = st.text_input("Kod pocztowy", value=clean_val(dane.get('AdresKodPocztowy')))
                            e_lok = st.text_input("Nr lokalu/domu", value=clean_val(dane.get('AdresNrLokalu')))
                            
                        st.write("")
                        if st.form_submit_button("💾 Zapisz Zmiany", type="primary", use_container_width=True):
                            if e_im and e_nz:
                                ok, msg = crud.aktualizuj_osobe(dane['IDOsoba'], e_im, e_nz, e_tel, e_em, e_mi, e_ul, e_lok, e_kod)
                                if ok:
                                    st.success("Zaktualizowano dane!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"Błąd: {msg}")
                            else:
                                st.warning("Imię i Nazwisko są wymagane.")