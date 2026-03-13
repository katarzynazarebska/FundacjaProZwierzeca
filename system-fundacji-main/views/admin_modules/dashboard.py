"""
MODUŁ ADMINA: DASHBOARD (PULPIT)

"""
import streamlit as st

def render_dashboard():
    role = st.session_state.user_role

    c1, c2 = st.columns(2)
    
    # --- KAFELETEK 1: DOSTĘP ---
    with c1:
        with st.container(border=True):
            st.subheader("🔐 Dostęp i Konta")
            st.markdown("Zarządzanie użytkownikami, hasłami i blokadami kont.")
            st.write("") 
            
            if role == "Admin":
                if st.button("Zarządzaj Dostępem", use_container_width=True): 
                    st.session_state.admin_mode = "access"
                    st.rerun()
            else:
                st.button("⛔ Brak uprawnień", disabled=True, use_container_width=True)
            
    # --- KAFELETEK 2: BAZA OSÓB ---
    with c2:
        with st.container(border=True):
            st.subheader("👥 Baza Osób")
            st.markdown("Wspólna baza: Domy Tymczasowe, Adoptujący, Wolontariusze.")
            st.write("")
            
            if st.button("Otwórz Bazę Osób", use_container_width=True): 
                st.session_state.admin_mode = "users"
                st.rerun()
            
    st.write("") 
    
    c3, c4 = st.columns(2)
    
    # --- KAFELETEK 3: SŁOWNIKI ---
    with c3:
        with st.container(border=True):
            st.subheader("📚 Słowniki")
            st.markdown("Definicje: Gatunki, Statusy, Kategorie zdarzeń.")
            st.write("")
            
            if st.button("Edytuj Słowniki", use_container_width=True): 
                st.session_state.admin_mode = "dictionaries"
                st.rerun()

    # --- KAFELETEK 4: POWIADOMIENIA ---
    with c4:
        with st.container(border=True):
            st.subheader("🔔 Alerty")
            st.markdown("Konfiguracja terminów ważności szczepień i badań.")
            st.write("")
            
            if st.button("Konfiguruj Alerty", use_container_width=True): 
                st.session_state.admin_mode = "alerts"
                st.rerun()