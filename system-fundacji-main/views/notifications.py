"""
WIDOK: CENTRUM POWIADOMIEŃ

"""
import streamlit as st
import crud
import pandas as pd

def render_notifications():
    st.title("🔔 Centrum Powiadomień")
    
    # Przycisk powrotu
    if st.button("⬅️ Wróć do Kokpitu"):
        st.session_state.current_module = "home"
        st.rerun()
        
    st.divider()
    
    # 1. Pobranie danych z logiki biznesowej
    lista_alertow = crud.pobierz_alerty_medyczne(
        rola_usera=st.session_state.user_role,
        id_osoba=st.session_state.get('user_id_osoba')
    )
    
    if not lista_alertow:
        st.balloons()
        st.success("Wszystko w porządku! Żaden podopieczny nie ma zaległych szczepień ani odrobaczeń.")
        return

    st.warning(f"⚠️ Znaleziono {len(lista_alertow)} zadań wymagających uwagi.")
    
    # 2. Wyświetlanie jako tabela z akcjami
    for alert in lista_alertow:
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 4, 2])
            
            with c1:
                st.write("🐕" if "Szczepienie" in alert['komunikat'] else "💊")
                
            with c2:
                st.markdown(f"**{alert['imie']}** (Chip: {alert['chip'] or 'Brak'})")
                st.error(alert['komunikat'])
                
            with c3:
                if st.button("Idź do karty ➡️", key=f"alert_{alert['id']}_{alert['komunikat']}"):
                    st.session_state.current_module = "registry"
                    st.session_state.view_mode = "details"
                    st.session_state.active_animal_id = alert['id']
                    st.rerun()