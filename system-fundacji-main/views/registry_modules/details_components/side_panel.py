"""
KOMPONENT KARTY: PANEL BOCZNY

"""
import streamlit as st
import crud

def render_side_panel(r):
    # 1. ZDJĘCIE
    photo_data = r.get('Zdjecie')
    
    st.markdown('<div class="profile-photo">', unsafe_allow_html=True)
    if photo_data:
        st.image(photo_data, use_container_width=True)
    else:
        st.image("https://place.dog/400/400", caption="Brak zdjęcia", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. DANE ORGANIZACYJNE
    
    id_nadzor = r.get('IDNadzor')
    id_opiekun = r.get('IDOpiekun')
    nazwa_nadzor = "-"
    nazwa_opiekun = "-"

    try:
        df_ludzie = crud.get_all_people()
        if not df_ludzie.empty:
            mapa_ludzi = {row['IDOsoba']: f"{row['Imie']} {row['Nazwisko']}" for _, row in df_ludzie.iterrows()}
            if id_nadzor: nazwa_nadzor = mapa_ludzi.get(id_nadzor, f"ID: {id_nadzor}")
            if id_opiekun: nazwa_opiekun = mapa_ludzi.get(id_opiekun, f"ID: {id_opiekun}")
    except: pass

    # --- RENDEROWANIE MIKRO-KART HTML ---
    
    # Karta 1: Nadzór
    st.markdown(f"""
    <div class="info-tile">
        <div class="info-label">Osoba Nadzorująca</div>
        <div class="info-value">🩺 {nazwa_nadzor}</div>
    </div>
    """, unsafe_allow_html=True)

    # Karta 2: Opiekun
    st.markdown(f"""
    <div class="info-tile">
        <div class="info-label">Opiekun / DT</div>
        <div class="info-value">🏠 {nazwa_opiekun}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Karta 3: Finansowanie
    zrodlo = r.get('ZrodloFinansowania', '-')
    st.markdown(f"""
    <div class="info-tile" style="border-left-color: #2ecc71;">
        <div class="info-label">Finansowanie</div>
        <div class="info-value">💰 {zrodlo}</div>
    </div>
    """, unsafe_allow_html=True)

    # Karta 4: Ogłoszenia (Pionowo)
    olx = r.get('CzyOgloszenieOLX', False)
    www = r.get('CzyOgloszenieWWW', False)
    
    c_olx = "#2ecc71" if olx else "#7f8c8d"
    c_www = "#2ecc71" if www else "#7f8c8d"
    t_olx = "AKTYWNE" if olx else "BRAK"
    t_www = "AKTYWNE" if www else "BRAK"

    st.markdown(f"""
    <div class="info-tile" style="border-left-color: #9b59b6;">
        <div style="margin-bottom: 8px;">
            <div class="info-label">OLX</div>
            <div class="info-value" style="color: {c_olx}; font-size: 13px;">● {t_olx}</div>
        </div>
        <div>
            <div class="info-label">WWW</div>
            <div class="info-value" style="color: {c_www}; font-size: 13px;">● {t_www}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)