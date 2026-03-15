import streamlit as st
import pandas as pd
import crud
from sqlalchemy import text
from datetime import date, timedelta
import plotly.express as px

FUNDACJA_COLORS = ['#3498db', '#2ecc71', '#9b59b6', '#e67e22', '#f1c40f', '#1abc9c']

def apply_light_transparent_layout(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',  
        font=dict(color='#2c3e50', size=14), 
        margin=dict(t=30, b=20, l=20, r=20),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)', zeroline=False),
        legend=dict(font=dict(color='#2c3e50'), bgcolor='rgba(0,0,0,0)')
    )
    return fig

def render_reports():
    st.title("📊 Raporty Analityczne")
    st.markdown("Generowanie zaawansowanych zestawień na podstawie rzeczywistych danych fundacji.")
    
    if st.button("⬅️ Wróć", type="secondary"):
        st.session_state.current_module = "home"
        st.rerun()
        
    st.divider()

    def wybierz_okres(klucz_prefix):
        typ_okresu = st.radio("Wybór okresu:", ["Cały rok", "Własny zakres dat"], horizontal=True, key=f"{klucz_prefix}_radio")
        if typ_okresu == "Cały rok":
            rok = st.selectbox("Wybierz rok:", range(date.today().year, 2019, -1), key=f"{klucz_prefix}_rok")
            return date(rok, 1, 1), date(rok, 12, 31)
        else:
            c_od, c_do = st.columns(2)
            return c_od.date_input("Data od", date.today().replace(month=1, day=1), key=f"{klucz_prefix}_od"), c_do.date_input("Data do", date.today(), key=f"{klucz_prefix}_do")

    tab1, tab2, tab3 = st.tabs(["🔄 Analiza Przepływu", "💰 Źródła Finansowania", "💉 Zestawienie Medyczne"])
    db = crud.get_db_session()

    # RAPORT 1
    with tab1:
        st.subheader("Analiza Losów Zwierząt (Kohorta)")
        start_przeplyw, end_przeplyw = wybierz_okres("przeplyw")
        gatunek_filter = st.radio("Wybierz gatunek do analizy:", ["Wszystkie", "Pies", "Kot"], horizontal=True)

        if start_przeplyw <= end_przeplyw:
            query = text("""
                SELECT Gatunek, COUNT(IDZwierze) as Przyjete,
                       SUM(CASE WHEN StatusZwierzecia = 'Adoptowany' THEN 1 ELSE 0 END) as Adoptowane,
                       SUM(CASE WHEN StatusZwierzecia = 'Dom Tymczasowy' THEN 1 ELSE 0 END) as W_DT,
                       SUM(CASE WHEN StatusZwierzecia = 'Za Tęczowym Mostem' THEN 1 ELSE 0 END) as Zmarle
                FROM ZWIERZE WHERE DataPrzyjecia >= :start AND DataPrzyjecia <= :end GROUP BY Gatunek
            """)
            df_wynik = pd.read_sql(query, db.bind, params={"start": start_przeplyw, "end": end_przeplyw})

            if not df_wynik.empty:
                if gatunek_filter != "Wszystkie": df_wynik = df_wynik[df_wynik['Gatunek'] == gatunek_filter]
                p = int(df_wynik['Przyjete'].sum()); a = int(df_wynik['Adoptowane'].sum())
                dt = int(df_wynik['W_DT'].sum()); z = int(df_wynik['Zmarle'].sum()); s = p - (a + dt + z)

                c1, c2, c3, c4 = st.columns(4)
                with c1: st.markdown(f"<div class='stat-card-light blue-b'><div class='stat-val'>{p}</div><div class='stat-label'>Suma Przyjęć</div></div>", unsafe_allow_html=True)
                with c2: st.markdown(f"<div class='stat-card-light green-b'><div class='stat-val'>{a}</div><div class='stat-label'>Suma Adopcji</div></div>", unsafe_allow_html=True)
                with c3: st.markdown(f"<div class='stat-card-light purple-b'><div class='stat-val'>{dt}</div><div class='stat-label'>Obecnie w DT</div></div>", unsafe_allow_html=True)
                with c4: st.markdown(f"<div class='stat-card-light orange-b'><div class='stat-val'>{s}</div><div class='stat-label'>Pozostało w Fundacji</div></div>", unsafe_allow_html=True)

                c_chart, c_table = st.columns([3, 2], vertical_alignment="center")
                with c_chart:
                    df_plot = pd.DataFrame({'Status': ['Adoptowane', 'W DT', 'Za Tęczowym Mostem', 'W Schronisku'], 'Liczba': [a, dt, z, s]})
                    df_plot = df_plot[df_plot['Liczba'] > 0]
                    if not df_plot.empty:
                        fig_bar = px.bar(df_plot, x='Status', y='Liczba', text='Liczba', color='Status', color_discrete_sequence=FUNDACJA_COLORS)
                        fig_bar = apply_light_transparent_layout(fig_bar)
                        fig_bar.update_layout(showlegend=False, xaxis_title="", yaxis_title="Ilość zwierząt")
                        fig_bar.update_traces(textposition='outside')
                        st.plotly_chart(fig_bar, use_container_width=True, theme=None)
                with c_table:
                    st.dataframe(df_wynik, use_container_width=True, hide_index=True)
                    st.download_button("📥 Pobierz", data=df_wynik.to_csv(index=False).encode('utf-8'), file_name="przeplyw.csv", mime="text/csv")

    # RAPORT 2
    with tab2:
        st.subheader("Struktura Źródeł Finansowania")
        df_finanse = pd.read_sql(text("SELECT ZrodloFinansowania, COUNT(IDZwierze) as Liczba FROM ZWIERZE WHERE StatusZwierzecia NOT IN ('Adoptowany', 'Za Tęczowym Mostem') AND ZrodloFinansowania IS NOT NULL AND ZrodloFinansowania != '' GROUP BY ZrodloFinansowania"), db.bind)
        if not df_finanse.empty:
            c_chart, c_table = st.columns([3, 2], vertical_alignment="center")
            with c_chart:
                fig_donut = px.pie(df_finanse, values='Liczba', names='ZrodloFinansowania', hole=0.45, color_discrete_sequence=FUNDACJA_COLORS)
                fig_donut = apply_light_transparent_layout(fig_donut)
                fig_donut.update_traces(textposition='inside', textinfo='percent+label')
                fig_donut.update_layout(showlegend=False)
                st.plotly_chart(fig_donut, use_container_width=True, theme=None)
            with c_table:
                st.dataframe(df_finanse, use_container_width=True, hide_index=True)

    # RAPORT 3
    with tab3:
        st.subheader("Zestawienie Działań Medycznych")
        start_med, end_med = wybierz_okres("med")
        if start_med <= end_med:
            df_med = pd.read_sql(text("SELECT Kategoria, COUNT(IDHistoria) as Liczba FROM HISTORIA_ZDARZEN WHERE Kategoria IN ('Wizyta Weterynaryjna', 'Szczepienie', 'Zabieg', 'Behawiorysta') AND DataZdarzenia >= :s AND DataZdarzenia <= :e GROUP BY Kategoria"), db.bind, params={"s": start_med, "e": end_med})
            if not df_med.empty:
                c1, c2 = st.columns([2, 1])
                with c1:
                    fig_m = px.bar(df_med, x="Kategoria", y="Liczba", text="Liczba", color="Kategoria", color_discrete_sequence=FUNDACJA_COLORS)
                    fig_m = apply_light_transparent_layout(fig_m)
                    fig_m.update_layout(showlegend=False, xaxis_title="", yaxis_title="Ilość")
                    fig_m.update_traces(textposition='outside')
                    st.plotly_chart(fig_m, use_container_width=True, theme=None)
                with c2:
                    st.dataframe(df_med, use_container_width=True, hide_index=True)

    db.close()