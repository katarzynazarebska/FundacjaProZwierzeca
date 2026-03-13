"""
KOMPONENT: SZCZEGÓŁY ZDARZENIA
"""
import streamlit as st
import crud
import time
import pandas as pd

def render_event_details(event_id):
    c_nav, c_del = st.columns([6, 2])
    with c_nav:
        if st.button("⬅️ Wróć do listy"):
            st.session_state.active_history_event_id = None
            st.rerun()
    with c_del:
        if st.button("🗑️ Usuń wpis", type="primary"):
            crud.usun_wpis_historii(event_id)
            st.session_state.active_history_event_id = None
            st.rerun()

    st.divider()
    
    # Załączniki
    st.subheader("📎 Załączniki")
    df_files = crud.pobierz_liste_zalacznikow(event_id)
    
    if not df_files.empty:
        for _, f in df_files.iterrows():
            c1, c2, c3 = st.columns([0.5, 4, 1.5])
            c1.write("📄")
            c2.write(f"**{f['NazwaPliku']}** ({f['RozmiarBajt']/1024:.1f} KB)")
            
            with c3:
                content = crud.pobierz_plik_content(f['ID_Zalacznik'])
                if content:
                    st.download_button("⬇️", content[1], file_name=content[0], mime=content[2], key=f"dl_{f['ID_Zalacznik']}")
                    
                if st.button("🗑️", key=f"del_{f['ID_Zalacznik']}"):
                    crud.usun_zalacznik(f['ID_Zalacznik'])
                    st.rerun()
    else:
        st.caption("Brak załączników.")

    st.divider()
    st.write("Dodaj plik:")
    upl = st.file_uploader("", accept_multiple_files=True, key="new_files")
    if st.button("Wyślij"):
        for u in upl:
            crud.dodaj_zalacznik(event_id, u)
        st.rerun()