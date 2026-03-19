import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

# --- 1. 페이지 설정 및 테마 ---
st.set_page_config(page_title="Han River Water Quality AI", layout="wide")
st.markdown("""
    <style>
    .reportview-container { background: #f5f7f9; }
    .main-header { font-size: 45px; font-weight: 800; color: #1E3A8A; margin-bottom: 20px; }
    .metric-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# --- 2. 데이터 처리 함수 ---
def load_data(file):
    if file is None: return None
    for enc in ['utf-8', 'cp949', 'euc-kr']:
        try:
            file.seek(0)
            df = pd.read_csv(file, encoding=enc)
            for col in ["노량진", "선유"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            return df.dropna(subset=['일시'])
        except: continue
    return None

# --- 3. 사이드바 ---
st.sidebar.markdown("<h2 style='color: #1E3A8A;'>🌊 Data Control</h2>", unsafe_allow_html=True)
up_do = st.sidebar.file_uploader("용존산소(DO) 데이터", type=['csv'])
up_ph = st.sidebar.file_uploader("수소이온농도(pH) 데이터", type=['csv'])

if up_do and up_ph:
    df_do = load_data(up_do)
    df_ph = load_data(up_ph)
    df_do['일시'] = pd.to_datetime(df_do['일시'])
    df_ph['일시'] = pd.to_datetime(df_ph['일시'])

    # --- 메인 타이틀 ---
    st.markdown("<div class='main-header'>River Quality Insight Engine</div>", unsafe_allow_html=True)
    
    # --- [섹션 1] 실시간 수질 지도 및 알람 ---
    st.subheader("📍 Real-time Monitoring Map")
    col_map, col_alert = st.columns([2, 1])
    
    with col_map:
        map_data = pd.DataFrame({
            '지점': ['노량진', '선유'],
            'lat': [37.5175, 37.5451], 'lon': [126.9413, 126.8991],
            '최근_DO': [df_do['노량진'].dropna().iloc[-1], df_do['선유'].dropna().iloc[-1]]
        })
        fig_map = px.scatter_mapbox(map_data, lat="lat", lon="lon", color="최근_DO", size="최근_DO",
                                    color_continuous_scale="Viridis", zoom=10.5, height=350)
        fig_map.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map,
