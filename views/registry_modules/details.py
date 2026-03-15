"""
MODUŁ REJESTRU: SZCZEGÓŁY (LAYOUT)

"""
import streamlit as st
import crud
from views.registry_modules.details_components import side_panel, top_bar, tab_info, tab_medical, tab_history

# --- LOKALNE STYLE KOMPONENTÓW (TYLKO DLA WIDOKU SZCZEGÓŁÓW) ---
LOCAL_CSS = """
<style>
    /* 1. TYTUŁ ZWIERZĘCIA */
    .animal-title {
        text-align: center;
        text-transform: uppercase;
        font-size: 3.5em; 
        font-weight: 900;
        letter-spacing: 3px;
        color: #3498db !important; /* Fundacyjny błękit */
        margin: 0; padding: 0;
        line-height: 1.1;
    }

    /* 2. RAMKA ZDJĘCIA (Jasna, nowoczesna) */
    .profile-photo {
        border: 4px solid #ffffff;
        border-radius: 8px; 
        padding: 0;
        margin-bottom: 15px;
        background-color: transparent;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); /* Delikatny cień */
    }
    
    /* 3. MIKRO-KARTY (INFO TILES) - WERSJA JASNA */
    .info-tile {
        background-color: #ffffff;
        border-left: 4px solid #3498db; /* Błękitny akcent z lewej */
        border-radius: 6px;
        padding: 10px 15px;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid #f1f2f6;
    }
    .info-label {
        font-size: 11px;
        color: #7f8c8d;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 2px;
    }
    .info-value {
        font-size: 15px;
        color: #2c3e50;
        font-weight: 600;
    }
</style>
"""

def render_details():
    st.markdown(LOCAL_CSS, unsafe_allow_html=True)

    # 1. Weryfikacja ID
    try:
        id_zw = int(st.session_state.active_animal_id)
    except:
        st.error("Błąd: Brak ID zwierzęcia.")
        st.button("Wróć", on_click=lambda: st.session_state.update(view_mode="list"))
        st.stop()
        
    # 2. Pobieranie danych
    zwierze_obj = crud.pobierz_szczegoly_zwierzecia(id_zw)
    if not zwierze_obj: 
        st.error("Nie znaleziono zwierzęcia.")
        return
    
    r = {k: v for k, v in vars(zwierze_obj).items() if not k.startswith('_')}
    r['ID_Zwierze'] = zwierze_obj.IDZwierze 

    top_bar.render_top_bar(r, id_zw)

    col_left, col_right = st.columns([1.5, 3.5])

    with col_left:
        side_panel.render_side_panel(r)

    with col_right:
        t1, t2, t3 = st.tabs(["📄 Dane", "💉 Zdrowie", "📜 Historia"])
        with t1: tab_info.render_tab(r)
        with t2: tab_medical.render_tab(r)
        with t3: tab_history.render_tab(id_zw)