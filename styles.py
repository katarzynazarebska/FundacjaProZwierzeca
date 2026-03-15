# styles.py
import streamlit as st

def apply_custom_css():
    MAIN_COLOR = "#3498db" 
    TEXT_COLOR = "#2c3e50" 
    BG_GRADIENT = "linear-gradient(180deg, #f4f7f6 0%, #e0eaf5 100%)" 
    
    st.markdown(f"""
        <style>
        /* Czcionka */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
        html, body, [class*="css"] {{ font-family: 'Poppins', sans-serif; }}
        
        /* Ukrycie Sidebara */
        [data-testid="stSidebar"] {{ display: none; }}
        
        .stApp {{
            background: {BG_GRADIENT} !important;
            background-attachment: fixed !important;
        }}
        [data-testid="stHeader"] {{ background-color: transparent !important; }}
        
        /* WYMUSZENIE CIEMNEGO TEKSTU WSZĘDZIE */
        .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp span, .stApp label, .stMarkdown, .stText {{
            color: {TEXT_COLOR} !important;
        }}

        /* POLA WPROWADZANIA I FILTRY MULTISELECT */
        .stTextInput input, .stSelectbox div[data-baseweb="select"], .stMultiSelect div[data-baseweb="select"] {{
            color: #000000 !important;
            background-color: #ffffff !important;
            border: 1px solid #dcdde1 !important;
            border-radius: 6px;
        }}
        span[data-baseweb="tag"] {{
            background-color: {MAIN_COLOR} !important;
            color: white !important;
            border-radius: 4px;
        }}

        /* PRZYCISKI PRIMARY */
        .stButton > button[kind="primary"],
        [data-testid="stFormSubmitButton"] > button {{
            background-color: {MAIN_COLOR} !important; 
            border-color: {MAIN_COLOR} !important;
            color: white !important; 
            font-weight: 600 !important; 
            border-radius: 8px !important;
            box-shadow: 0 4px 6px rgba(52,152,219,0.3) !important; 
            transition: all 0.3s ease !important;
        }}
        .stButton > button[kind="primary"] p,
        [data-testid="stFormSubmitButton"] > button p {{
            color: white !important; 
        }}
        .stButton > button[kind="primary"]:hover,
        [data-testid="stFormSubmitButton"] > button:hover {{
            background-color: #2980b9 !important; 
            border-color: #2980b9 !important;
            transform: translateY(-2px);
        }}
        
        /* PRZYCISKI SECONDARY */
        .stButton > button[kind="secondary"] {{
            background-color: #ffffff !important; 
            border: 2px solid {MAIN_COLOR} !important;
            color: {MAIN_COLOR} !important; 
            font-weight: 600 !important; 
            border-radius: 8px !important;
        }}
        .stButton > button[kind="secondary"] p {{
            color: {MAIN_COLOR} !important; 
        }}
        .stButton > button[kind="secondary"]:hover {{
            background-color: #eaf2f8 !important; 
            border-color: #2980b9 !important;
            color: #2980b9 !important;
        }}
        
        /* KONTENERY  */
        [data-testid="stVerticalBlockBorderWrapper"] > div {{
            background-color: #ffffff !important;
            border: 1px solid #f1f2f6 !important;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.04);
            padding: 20px;
        }}

        /* TABELA  */
        [data-testid="stDataFrame"] {{
            background-color: #ffffff !important;
            border: 1px solid #f1f2f6 !important;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.04);
            padding: 0px !important; /* Usuwamy padding żeby tabela nie wyjeżdżała */
            overflow: hidden !important; /* Przycinamy ramki */
        }}

        /* Kafelki statystyk */
        .stat-card-light {{
            background-color: #ffffff; border: 1px solid #ecf0f1; border-radius: 8px;
            padding: 15px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            border-bottom: 4px solid;
        }}
        .stat-val {{ font-size: 28px; font-weight: bold; color: {MAIN_COLOR}; }}
        .stat-label {{ font-size: 13px; color: #7f8c8d !important; text-transform: uppercase; letter-spacing: 1px; }}
        .blue-b {{ border-bottom-color: #3498db; }}
        .green-b {{ border-bottom-color: #2ecc71; }}
        .purple-b {{ border-bottom-color: #9b59b6; }}
        .orange-b {{ border-bottom-color: #e67e22; }}
        
        /* Tytuły specyficzne */
        .fundacja-title, .admin-title, .registry-title {{ font-size: 2.2em; font-weight: 800; color: {MAIN_COLOR} !important; text-align: center; margin: 0; padding: 0; }}
        .fundacja-subtitle {{ text-align: center; color: #7f8c8d !important; font-size: 1.1em; margin-bottom: 20px; }}
        .user-text, .user-info-top {{ text-align: right; font-size: 0.85em; color: #7f8c8d !important; }}
        </style>
    """, unsafe_allow_html=True)