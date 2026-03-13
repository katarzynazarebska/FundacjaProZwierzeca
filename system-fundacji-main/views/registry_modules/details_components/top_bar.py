"""
KOMPONENT KARTY: NAGŁÓWEK

"""
import streamlit as st

def render_top_bar(r, id_zw):
    c_back, c_title, c_actions = st.columns([1, 5, 3], vertical_alignment="center")
    
    with c_back:
        if st.button("⬅️", help="Wróć do listy", type="secondary", use_container_width=False):
            st.session_state.view_mode = "list"
            st.rerun()

    with c_title:
        imie = r.get('Imie', 'BEZ IMIENIA').upper()
        st.markdown(f"<div class='animal-title'>{imie}</div>", unsafe_allow_html=True)

    with c_actions:
        ca1, ca2 = st.columns([1, 1])
        
        status = r.get('StatusZwierzecia')
        
        with ca1:
            # Przycisk ADOPTUJ 
            if status not in ["Adoptowany", "Za Tęczowym Mostem"]:
                if st.button("🏠 Adoptuj", help="Rozpocznij proces adopcji", use_container_width=True):
                    st.session_state.view_mode = "adoption_process"
                    st.rerun()
            else:
                pass

        with ca2:
            # Przycisk EDYTUJ
            if st.button("✏️ Edytuj", help="Edytuj dane", type="secondary", use_container_width=True):
                 st.session_state.view_mode = "edit"
                 st.rerun()
             
    st.divider()