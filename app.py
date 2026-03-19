import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Han River Water Quality Pro", layout="wide")

# --- 2. 데이터 로드 함수 (인코딩 자동 대응) ---
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
        except:
            continue
    return None

# --- 3. 사이드바 구성 ---
st.sidebar.title("🌊 River Insight Control")
up_do = st.sidebar.file_uploader("용존산소(DO) 데이터 (CSV)", type=['csv'])
up_ph = st.sidebar.file_uploader("수소이온농도(pH) 데이터 (CSV)", type=['csv'])

if up_do and up_ph:
    df_do = load_data(up_do)
    df_ph = load_data(up_ph)
    
    # 시간 데이터 변환
    df_do['일시'] = pd.to_datetime(df_do['일시'])
    df_ph['일시'] = pd.to_datetime(df_ph['일시'])

    st.title("🚀 한강 수질 데이터 사이언스 대시보드")
    st.markdown("공공 데이터를 기반으로 한 지점별 수질 특성 및 통계 분석 리포트입니다.")

    # --- 4. 섹션 1: 인터랙티브 지도 (Hover 기능) ---
    st.subheader("📍 지점별 실시간 수질 위치 정보")
    
    # 최신 데이터 추출
    map_data = pd.DataFrame({
        '지점': ['노량진', '선유'],
        'lat': [37.5175, 37.5451],
        'lon': [126.9413, 126.8991],
        '최근_DO': [df_do['노량진'].dropna().iloc[-1], df_do['선유'].dropna().iloc[-1]],
        '최근_pH': [df_ph['노량진'].dropna().iloc[-1], df_ph['선유'].dropna().iloc[-1]]
    })

    fig_map = px.scatter_mapbox(
        map_data, lat="lat", lon="lon", 
        color="최근_DO", size="최근_DO",
        color_continuous_scale="Viridis",
        hover_name="지점",
        hover_data={"lat": False, "lon": False, "최근_DO": True, "최근_pH": True},
        zoom=10.5, height=400
    )
    fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

    st.divider
