"""
MODUŁ ADMINA: ZARZĄDZANIE DOSTĘPEM

"""
import streamlit as st
import crud
import time

def render_access_control():
    if st.session_state.user_role != "Admin":
        st.error("Brak uprawnień.")
        return

    try:
        df_ludzie = crud.pobierz_wszystkie_osoby()
        mapa_ludzi = {"- Nie powiązano -": None}
        if not df_ludzie.empty:
            for _, row in df_ludzie.iterrows():
                label = f"{row['Imie']} {row['Nazwisko']} (ID: {row['IDOsoba']})"
                mapa_ludzi[label] = row['IDOsoba']
        lista_opcji_ludzi = list(mapa_ludzi.keys())
    except:
        lista_opcji_ludzi = ["- Błąd pobierania danych -"]
        mapa_ludzi = {}

    t1, t2 = st.tabs(["👥 Lista Kont", "➕ Utwórz Nowe Konto"])
    
    # --- TAB 1: LISTA ---
    with t1:
        users = crud.pobierz_wszystkich_uzytkownikow()
        
        if not users.empty:
            st.dataframe(
                users,
                column_config={
                    "LoginName": "Login",
                    "CzyAktywny": st.column_config.CheckboxColumn("Aktywny?", disabled=True),
                    "ID_User": st.column_config.NumberColumn("ID", disabled=True) 
                },
                hide_index=True,
                use_container_width=True
            )
            
            st.write("")
            st.markdown("##### ⚡ Panel Akcji")
            
            with st.container(border=True):
                lista_loginow = users['LoginName'].tolist()
                wybrany_login = st.selectbox("Wybierz użytkownika do edycji", lista_loginow)
                
                if wybrany_login:
                    user_row = users[users['LoginName'] == wybrany_login].iloc[0]
                    try: user_id = int(user_row['ID_User'])
                    except: user_id = int(user_row.get('IDUser', 0))
                    
                    is_active = int(user_row['CzyAktywny'])
                    
                    st.subheader("🔐 Zmiana Hasła")
                    c_pass_input, c_pass_btn = st.columns([3, 1], vertical_alignment="bottom")
                    with c_pass_input:
                        new_pass_manual = st.text_input("Wpisz nowe hasło", type="password", key="reset_pass", placeholder="Minimum 5 znaków...")
                    with c_pass_btn:
                        if st.button("🔄 Zmień hasło", use_container_width=True):
                            if new_pass_manual:
                                crud.zmien_haslo_uzytkownika(wybrany_login, new_pass_manual)
                                st.success("Hasło zmienione.")
                            else:
                                st.warning("Podaj hasło.")

                    st.divider()

                    c_status, c_delete = st.columns(2)
                    with c_status:
                        st.markdown("**Status Konta**")
                        st.caption(f"Obecnie: {'Aktywne' if is_active else 'Zablokowane'}")
                        btn_label = "🚫 Zablokuj Konto" if is_active else "✅ Odblokuj Konto"
                        if st.button(btn_label, use_container_width=True, type="secondary"):
                            crud.zmien_status_uzytkownika(user_id, is_active)
                            st.success("Status zmieniony.")
                            time.sleep(0.5)
                            st.rerun()     
                    with c_delete:
                        st.markdown("**Usunięcie Konta**")
                        st.caption("Operacja nieodwracalna.")
                        if st.button("🗑️ Usuń trwale", type="primary", use_container_width=True):
                            crud.usun_uzytkownika(user_id)
                            st.warning(f"Usunięto konto: {wybrany_login}")
                            time.sleep(1)
                            st.rerun()
        else:
            st.info("Brak użytkowników.")
            
    # --- TAB 2: TWORZENIE ---
    with t2:
        with st.container(border=True):
            st.subheader("Formularz Rejestracji")
            
            with st.form("new_user_form", clear_on_submit=True):
                wybrana_osoba_str = st.selectbox("Powiązana Osoba *", lista_opcji_ludzi)
                
                c1, c2 = st.columns(2)
                with c1:
                    new_login = st.text_input("Login *")
                    new_email = st.text_input("E-mail")
                with c2:
                    new_pass = st.text_input("Hasło *", type="password")
                    new_role = st.selectbox("Rola", ["Admin", "Pracownik", "Wolontariusz", "DT"])
                
                st.write("")
                
                if st.form_submit_button("➕ Utwórz konto", type="primary", use_container_width=True):
                    if new_login and new_pass and wybrana_osoba_str:
                        id_osoby_do_zapisu = mapa_ludzi.get(wybrana_osoba_str)
                        
                        if not id_osoby_do_zapisu:
                            st.error("Musisz wybrać osobę z listy.")
                        else:
                            ok, msg = crud.create_user(new_login, new_email, new_pass, new_role, id_osoba=id_osoby_do_zapisu)
                            if ok:
                                st.success(f"Utworzono konto dla: {new_login}")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(msg)
                    else:
                        st.warning("Wypełnij wymagane pola (Osoba, Login, Hasło).")