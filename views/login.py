"""
WIDOK: LOGOWANIE I RESET HASŁA
"""
import streamlit as st
import time
import crud
try:
    from services import email_service
except ImportError:
    class email_service:
        @staticmethod
        def wyslij_email_resetu(email, kod):
            return True, f"Kod (SYMULACJA): {kod}"

def render_login():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<h1 style='text-align: center; color: #3498db !important;'>🔐 System Fundacji</h1>", unsafe_allow_html=True)
        st.container(border=True)
        
        if 'login_mode' not in st.session_state:
            st.session_state.login_mode = "login"

        # ======================================================
        # TRYB 1: STANDARDOWE LOGOWANIE
        # ======================================================
        if st.session_state.login_mode == "login":
            st.subheader("Zaloguj się")
            with st.form("login_form"):
                email = st.text_input("Login", autocomplete="username") 
                passwd = st.text_input("Hasło", type="password", autocomplete="current-password")
                submitted = st.form_submit_button("Wejdź", type="primary", use_container_width=True)
                
                if submitted:
                    role, name, id_osoba = crud.verify_user(email, passwd)
                    
                    if role: 
                        st.session_state.logged_in = True
                        st.session_state.user_name = name
                        st.session_state.user_role = role
                        st.session_state.user_email = email
                        st.session_state.user_id_osoba = id_osoba 
                        
                        st.success(f"Witaj {name}!")
                        time.sleep(0.5)
                        st.rerun()
                    else: 
                        st.error("Błędny login lub hasło.")

            st.write("")
            if st.button("Nie pamiętam hasła ❓", use_container_width=True):
                st.session_state.login_mode = "forgot_request"
                st.rerun()

        # ======================================================
        # TRYB 2: RESET - KROK 1 
        # ======================================================
        elif st.session_state.login_mode == "forgot_request":
            st.subheader("Reset hasła (Krok 1/2)")
            st.info("Podaj login. Wygenerujemy kod weryfikacyjny.")
            
            email_reset = st.text_input("Twój Login")
            
            c_b1, c_b2 = st.columns(2)
            with c_b1:
                if st.button("⬅️ Wróć"):
                    st.session_state.login_mode = "login"
                    st.rerun()
            with c_b2:
                if st.button("Wyślij kod 📩", type="primary"):
                    try:
                        ok, wynik = crud.inicjuj_reset_hasla(email_reset)
                        
                        if ok:
                            sent_ok, msg = email_service.wyslij_email_resetu(email_reset, wynik)
                            if sent_ok:
                                st.session_state.reset_email = email_reset
                                st.session_state.login_mode = "forgot_verify"
                                st.success(msg) 
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error(msg)
                        else:
                            st.error(wynik)
                    except AttributeError:
                        st.error("Funkcja resetu hasła jest w trakcie migracji na nowy system bazy danych.")

        # ======================================================
        # TRYB 3: RESET - KROK 2 
        # ======================================================
        elif st.session_state.login_mode == "forgot_verify":
            st.subheader("Reset hasła (Krok 2/2)")
            st.info(f"Wpisz kod dla: **{st.session_state.get('reset_email', '')}**")
            
            with st.form("reset_final"):
                kod = st.text_input("Kod weryfikacyjny")
                new_pass = st.text_input("Nowe hasło", type="password")
                new_pass2 = st.text_input("Powtórz nowe hasło", type="password")
                
                if st.form_submit_button("Zmień hasło 💾", type="primary"):
                    if new_pass != new_pass2:
                        st.error("Hasła nie są identyczne!")
                    elif len(new_pass) < 4:
                        st.error("Hasło jest za krótkie (min. 4 znaki).")
                    else:
                        try:
                            email_u = st.session_state.get('reset_email')
                            ok, msg = crud.finalizuj_reset_hasla(email_u, kod, new_pass)
                            
                            if ok:
                                st.balloons()
                                st.success("Hasło zmienione pomyślnie!")
                                time.sleep(3)
                                st.session_state.login_mode = "login"
                                st.rerun()
                            else:
                                st.error(msg)
                        except AttributeError:
                             st.error("Błąd migracji bazy danych.")
            
            if st.button("Anuluj"):
                st.session_state.login_mode = "login"
                st.rerun()