"""
ROUTER MODUŁU: ADMIN
"""
import streamlit as st
from views.admin_modules import dashboard, access_control, people_db, dictionaries, alerts_config
from views import reports

# --- LOKALNY STYL (Tylko nagłówki, reszta dziedziczy z globalnego styles.py) ---
LOCAL_CSS = """
<style>
    /* Nagłówek Admina */
    .admin-title {
        font-size: 2.2em; font-weight: 800; color: #3498db !important; /* Błękitny */
        margin: 0; padding: 0; text-transform: uppercase; letter-spacing: 2px; text-align: center;
    }
    .user-info-top {
        text-align: right; font-size: 0.85em; color: #7f8c8d !important;
        margin-bottom: -15px; font-family: monospace;
    }
</style>
"""

def render_admin():
    st.markdown(LOCAL_CSS, unsafe_allow_html=True)
    
    role = st.session_state.user_role
    mode = st.session_state.admin_mode
    
    if role == "DT": 
        st.error("⛔ BRAK DOSTĘPU")
        if st.button("Wróć"):
            st.session_state.current_module = "home"
            st.rerun()
        st.stop()
        
    tytuly_modulow = {
        "dashboard": "Panel Administracyjny",
        "access": "Dostęp i Konta",
        "users": "Baza Osób",
        "dictionaries": "Słowniki Danych",
        "alerts": "Konfiguracja Alertów",
        "reports": "Raporty Analityczne"
    }
    aktualny_tytul = tytuly_modulow.get(mode, "Panel Administracyjny")

    # NAGŁÓWEK
    c_dummy, c_user = st.columns([8, 2])
    with c_user:
        st.markdown(f"<div class='user-info-top'>Zalogowano jako: {role}</div>", unsafe_allow_html=True)
        
    c_nav, c_title, c_void = st.columns([1.5, 7, 1.5], vertical_alignment="center")
    
    with c_nav:
        if st.button("🏠 Menu", help="Wróć do głównego ekranu", type="secondary", use_container_width=True):
            st.session_state.current_module = "home"
            st.rerun()
            
        if mode != "dashboard":
            if st.button("⬅️ Panel Adm.", help="Wróć do pulpitu admina", type="secondary", use_container_width=True):
                st.session_state.admin_mode = "dashboard"
                st.rerun()
            
    with c_title:
        st.markdown(f"<div class='admin-title'>{aktualny_tytul}</div>", unsafe_allow_html=True)

    st.divider()

    # ROUTING PODMODUŁÓW
    if mode == "dashboard": 
        dashboard.render_dashboard()
    elif mode == "access":
        if role != "Admin": 
            st.error("⛔ Tylko Admin.")
        else: 
            access_control.render_access_control()
    elif mode == "users": 
        people_db.render_people_db()
    elif mode == "dictionaries": 
        dictionaries.render_dictionaries()
    elif mode == "alerts": 
        alerts_config.render_alerts_config()
    elif mode == "reports": 
        reports.render_reports()
    else: 
        st.warning(f"Nieznany tryb: {mode}")