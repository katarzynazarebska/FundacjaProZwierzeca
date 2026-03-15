"""
KOMPONENT KARTY: ZAKŁADKA 'DANE'

"""
import streamlit as st
import pandas as pd

def render_tab(r):
    st.subheader("📋 Metryczka")
    
    # Dane do wyświetlenia w układzie 2-kolumnowym
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown(f"**🐾 Gatunek:** {r.get('Gatunek', '-')}")
        st.markdown(f"**🐕 Rasa:** {r.get('Rasa', '-')}")
        st.markdown(f"**⚧ Płeć:** {r.get('Plec', '-')}")
        st.markdown(f"**📟 Nr Chip:** {r.get('NrChip', 'Brak')}")

    with c2:
        st.markdown(f"**🎂 Data Urodzenia:** {r.get('DataUrodzenia', '-')}")
        st.markdown(f"**📅 Data Przyjęcia:** {r.get('DataPrzyjecia', '-')}")
        
        # Status z kolorem
        status = r.get('StatusZwierzecia', 'Nieznany')
        if status == "Adoptowany":
            st.success(f"**Status:** {status}")
        elif status in ["W trakcie leczenia", "Kwarantanna"]:
            st.warning(f"**Status:** {status}")
        else:
            st.info(f"**Status:** {status}")

    st.divider()
    
    st.subheader("📝 Opis / Notatki")
    opis = r.get('Opis')
    if opis:
        st.write(opis)
    else:
        st.caption("Brak dodatkowego opisu.")