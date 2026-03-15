"""
WIDOK: KOKPIT
"""
import streamlit as st
import crud

def render_home():
    try:
        alerty = crud.pobierz_alerty_medyczne(
            rola_usera=st.session_state.user_role,
            id_osoba=st.session_state.get('user_id_osoba')
        )
        liczba = len(alerty)
    except:
        liczba = 0

    c_left, c_center, c_right = st.columns([1, 6, 2.5])

    # DZWONECZEK
    with c_left:
        lbl = f"🔔 {liczba}" if liczba > 0 else "🔔"
        btn_type = "primary" if liczba > 0 else "secondary"
        if st.button(lbl, type=btn_type, use_container_width=False, help="Powiadomienia"):
            st.session_state.current_module = "notifications"
            st.rerun()

    # TYTUŁY
    with c_center:
        st.markdown("<div class='fundacja-title'>Fundacja Przyjaciele Palucha</div>", unsafe_allow_html=True)
        st.markdown("<div class='fundacja-subtitle'>Panel Zarządzania Schroniskiem</div>", unsafe_allow_html=True)

    # UŻYTKOWNIK
    with c_right:
        role_pl = st.session_state.user_role.upper()
        cr_text, cr_btn = st.columns([2, 1])
        with cr_text:
             st.markdown(f"<div class='user-text'>Zalogowany:<br><b>{st.session_state.user_name}</b> <span style='color:#3498db'>({role_pl})</span></div>", unsafe_allow_html=True)
        with cr_btn:
            if st.button("Wyloguj", type="secondary", use_container_width=False):
                st.session_state.logged_in = False
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # WYSZUKIWARKA
    with st.container(border=True):
        c_search, c_btn = st.columns([7, 1])
        with c_search:
            query = st.text_input("Szukaj", placeholder="🔍 Wpisz imię psa lub numer chip...", label_visibility="collapsed")
        with c_btn:
            if st.button("SZUKAJ", type="primary", use_container_width=True):
                if query:
                    st.session_state.current_module = "registry"
                    st.session_state.view_mode = "list"
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_main, col_quick = st.columns([3, 1], vertical_alignment="bottom")

    with col_main:
        # REJESTR
        with st.container(border=True):
            ci, ct, ca = st.columns([0.3, 3, 1])
            with ci: st.markdown("## 🐾")
            with ct: 
                st.subheader("Rejestr Zwierząt")
                st.caption("Baza podopiecznych, edycja kartotek, historia leczenia.")
            with ca: 
                st.write("") 
                if st.button("Otwórz", key="btn_reg", use_container_width=True, type="primary"):
                    st.session_state.current_module = "registry"
                    st.session_state.view_mode = "list"
                    st.rerun()

        st.write("")

        # ADMINISTRACJA
        is_admin = (st.session_state.user_role == "Admin")
        with st.container(border=True):
            ci, ct, ca = st.columns([0.3, 3, 1])
            with ci: st.markdown("## ⚙️" if is_admin else "## 🔒")
            with ct:
                st.subheader("Administracja")
                st.caption("Użytkownicy, Słowniki, Baza Osób, Alerty." if is_admin else "Tylko dla Administratora.")
            with ca:
                st.write("")
                if st.button("Otwórz", key="btn_adm", disabled=not is_admin, use_container_width=True, type="primary"):
                    st.session_state.current_module = "admin"
                    st.session_state.admin_mode = "dashboard"
                    st.rerun()

    with col_quick:
        st.markdown("##### ⚡ Szybkie Akcje")
        
        rola = st.session_state.user_role
        
        if rola in ["Admin", "Pracownik"]:
            with st.container(border=True):
                st.write("**Nowy pies?**")
                st.caption("Utwórz nową kartę.")
                if st.button("➕ Przyjmij", type="primary", use_container_width=True):
                    st.session_state.current_module = "registry"
                    st.session_state.view_mode = "admission"
                    st.rerun()
                    
            with st.container(border=True):
                st.write("**Analityka**")
                st.caption("Wykresy i statystyki.")
                if st.button("📊 Raporty", type="primary", use_container_width=True):
                    st.session_state.current_module = "reports"
                    st.rerun()
        else:
            st.info("Brak przypisanych szybkich akcji dla Twojej roli.")
        
        if liczba > 0:
             st.markdown(f"<div style='text-align:center; color:#e74c3c; font-size:12px; margin-top:5px;'>⚠️ Zaległości: {liczba}</div>", unsafe_allow_html=True)
             
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # STATYSTYKI
    if st.session_state.user_role in ["Admin", "Pracownik"]:
        st.divider()
        stats = crud.get_dashboard_stats()
        c_s1, c_s2, c_s3, c_s4 = st.columns(4)

        with c_s1: st.markdown(f"<div class='stat-card-light blue-b'><div class='stat-val'>{stats['w_fundacji']}</div><div class='stat-label'>Zwierzęta w fundacji</div></div>", unsafe_allow_html=True)
        with c_s2: st.markdown(f"<div class='stat-card-light green-b'><div class='stat-val'>{stats['aktywni_wolo']}</div><div class='stat-label'>Aktywni Wolontariusze</div></div>", unsafe_allow_html=True)
        with c_s3: st.markdown(f"<div class='stat-card-light purple-b'><div class='stat-val'>{stats['aktywne_dt']}</div><div class='stat-label'>Aktywne DT</div></div>", unsafe_allow_html=True)
        with c_s4: st.markdown(f"<div class='stat-card-light orange-b'><div class='stat-val'>{stats['adopcje_miesiac']}</div><div class='stat-label'>Adopcje (Miesiąc)</div></div>", unsafe_allow_html=True)