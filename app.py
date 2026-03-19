import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Han River Pulse Pro", layout="wide")

# --- 2. 데이터 로드 함수 ---
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
        except:
            continue
    return None

# --- 3. 사이드바 ---
st.sidebar.title("🌊 한강 수질 분석")
up_do = st.sidebar.file_uploader("용존산소(DO) 파일 업로드", type=['csv'])
up_ph = st.sidebar.file_uploader("수소이온농도(pH) 파일 업로드", type=['csv'])

if up_do and up_ph:
    df_do = load_data(up_do)
    df_ph = load_data(up_ph)
    
    df_do['일시'] = pd.to_datetime(df_do['일시'])
    df_ph['일시'] = pd.to_datetime(df_ph['일시'])

    # --- 4. 한강 인터랙티브 지도 (Hover) ---
    st.title("📍 한강 수질 실시간 모니터링 맵")
    
    map_data = pd.DataFrame({
        '지점': ['노량진', '선유'],
        'lat': [37.5175, 37.5451],
        'lon': [126.9413, 126.8991],
        '최근_DO': [df_do['노량진'].dropna().iloc[-1], df_do['선유'].dropna().iloc[-1]],
        '최근_pH': [df_ph['노량진'].dropna().iloc[-1], df_ph['선유'].dropna().iloc[-1]],
    })

    fig_map = px.scatter_mapbox(
        map_data, lat="lat", lon="lon", 
        color="최근_DO", size="최근_DO",
        color_continuous_scale=px.colors.sequential.Blues,
        hover_name="지점",
        hover_data={"lat": False, "lon": False, "최근_DO": True, "최근_pH": True},
        zoom=11, height=400
    )
    fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

    st.divider()

    # --- 5. AM/PM 시간대별 분석 ---
    for df in [df_do, df_ph]:
        df['AM/PM'] = df['일시'].dt.hour.apply(lambda x: '오전(AM)' if x < 12 else '오후(PM)')

    location = st.sidebar.selectbox("분석 지점 선택", ["노량진", "선유"])
    
    st.subheader(f"📊 {location} 지점 시간대별 통계")
    c1, c2 = st.columns(2)
    
    with c1:
        avg_do = df_do.groupby('AM/PM')[location].mean().reset_index()
        st.plotly_chart(px.bar(avg_do, x='AM/PM', y=location, title="평균 용존산소", color='AM/PM'), use_container_width=True)
    
    with c2:
        avg_ph = df_ph.groupby('AM/PM')[location].mean().reset_index()
        st.plotly_chart(px.bar(avg_ph, x='AM/PM', y=location, title="평균 수소이온농도", color='AM/PM'), use_container_width=True)

    # --- 6. 노량진 vs 선유 비교표 및 인사이트 ---
