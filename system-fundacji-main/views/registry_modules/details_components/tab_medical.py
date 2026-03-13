"""
KOMPONENT KARTY: ZAKŁADKA 'ZDROWIE'

"""
import streamlit as st
import pandas as pd
from datetime import date

def render_tab(r):
    # 1. SZCZEPIENIA
    st.markdown("##### 🛡️ Szczepienia")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        
        with c1:
            wsciek = r.get('SzczepienieWscieklizna')
            st.caption("Wścieklizna (Data ostatniego):")
            if wsciek:
                dni = (date.today() - wsciek).days
                if dni > 365:
                    st.markdown(f"🔴 **{wsciek}** (Nieważne!)")
                else:
                    st.markdown(f"🟢 **{wsciek}**")
            else:
                st.markdown("⚪ Brak danych")

        with c2:
            zakazne = r.get('SzczepienieZakazne')
            st.caption("Choroby zakaźne (Data ostatniego):")
            if zakazne:
                st.markdown(f"**{zakazne}**")
            else:
                st.markdown("⚪ Brak danych")

    st.write("")

    # 2. OCHRONA PRZECIW KLESZCZOM
    st.markdown("##### 🕷️ Ochrona p/kleszczom")
    with st.container(border=True):
        kleszcze = r.get('OchronaKleszczeDo')
        st.caption("Ważne do:")
        if kleszcze:
            if kleszcze < date.today():
                st.markdown(f"🔴 **{kleszcze}** (Wygasło)")
            else:
                st.markdown(f"🟢 **{kleszcze}**")
        else:
            st.markdown("⚪ Brak danych")

    st.write("")

    # 3. ODROBACZANIE
    st.markdown("##### 💊 Odrobaczanie")
    with st.container(border=True):
        odrobaczanie = r.get('Odrobaczenie') 
        st.caption("Data ostatniego zabiegu:")
        if odrobaczanie:
            st.markdown(f"**{odrobaczanie}**")
        else:
            st.markdown("⚪ Brak danych")

    st.write("")

    # 4. KASTRACJA / STERYLIZACJA
    st.markdown("##### ✂️ Kastracja / Sterylizacja")
    with st.container(border=True):
        data_kast = r.get('DataKastracji')
        st.caption("Data zabiegu:")
        if data_kast:
            st.success(f"✅ Wykonano: **{data_kast}**")
        else:
            st.markdown("⚪ Nie wykonano / Brak daty")

    st.write("")
    st.divider()

    # 5. DODATKOWY OPIS ZDROWIA 
    st.markdown("##### 📝 Opis / Notatki Medyczne")
    
    # POPRAWKA NAZWY:
    opis_med = r.get('OpisZdrowia') 
    
    if opis_med:
        with st.container(border=True):
            st.write(opis_med)
    else:
        st.caption("Brak szczegółowego opisu medycznego.")