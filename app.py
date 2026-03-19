import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Han River Quality Map", layout="wide")

def load_data(file):
    if file is None: return None
    for enc in ['utf-8', 'cp949', 'euc-kr']:
        try:
            file.seek(0)
            df = pd.read_csv(file, encoding=enc)
            for col in ["노량진", "선유"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            return df
        except: continue
    return None

# --- 2. 사이드바 데이터 업로드 ---
st.sidebar.title("🌊 River Pulse Pro")
up_do = st.sidebar.file_uploader("용존산소(DO) 파일", type=['csv'])
up_ph = st.sidebar.file_uploader("수소이온농도(pH) 파일", type=['csv'])

if up_do and up_ph:
    df_do = load_data(up_do)
    df_ph = load_data(up_ph)
    df_do['일시'] = pd.to_datetime(df_do['일시'])
    df_ph['일시'] = pd.to_datetime(df_ph['일시'])

    # --- 3. 인터랙티브 지도 (Mapbox) ---
    st.title("📍 한강 수질 모니터링 맵")
    st.markdown("지도 위 포인트에 **마우스를 올리면(Hover)** 해당 지점의 최신 정보를 확인할 수 있습니다.")

    # 지점별 좌표 및 최신 데이터 결합
    map_data = pd.DataFrame({
        '지점': ['노량진', '선유'],
        'lat': [37.5175, 37.5451],  # 실제 노량진, 선유 인근 위도
        'lon': [126.9413, 126.8991], # 실제 경도
        '최근 DO': [df_do['노량진'].iloc[-1], df_do['선유'].iloc[-1]],
        '최근 pH': [df_ph['노량진'].iloc[-1], df_ph['선유'].iloc[-1]],
        '평균 DO': [df_do['노량진'].mean(), df_do['선유'].mean()]
    })

    fig_map = px.scatter_mapbox(
        map_data, lat="lat", lon="lon", text="지점", 
        color="최근 DO", size="최근 DO",
        color_continuous_scale=px.colors.cyclical.IceFire, 
        size_max=15, zoom=11,
        hover_name="지점",
        hover_data={"lat": False, "lon": False, "최근 DO": True, "최근 pH": True, "평균 DO": ":.2f"}
    )
    
    # 지도 스타일 설정 (Open Street Map)
    fig_map.update_layout(mapbox_style="open-street-map")
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

    st.divider()

    # --- 4. AM/PM 막대 그래프 ---
    st.subheader("☀️ AM vs 🌙 PM 수질 분석")
    for df in [df_do, df_ph]:
