import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Han River Pulse Pro", layout="wide")

# --- 2. 안전한 데이터 로드 함수 ---
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

# --- 3. 사이드바 및 업로드 ---
st.sidebar.title("🌊 한강 수질 모니터링")
up_do = st.sidebar.file_uploader("용존산소(DO) 파일 업로드", type=['csv'])
up_ph = st.sidebar.file_uploader("수소이온농도(pH) 파일 업로드", type=['csv'])

if up_do and up_ph:
    df_do = load_data(up_do)
    df_ph = load_data(up_ph)
    
    # 시간 데이터 처리
    df_do['일시'] = pd.to_datetime(df_do['일시'])
    df_ph['일시'] = pd.to_datetime(df_ph['일시'])

    # --- 4. 메인 지도 시각화 (Hover 효과) ---
    st.title("📍 한강 수질 인터랙티브 맵")
    st.markdown("지도 위 포인트에 **마우스를 올리면** 해당 지점의 상세 수치를 확인할 수 있습니다.")

    # 위경도 및 최신 데이터 결합 (노량진/선유 좌표)
    map_data = pd.DataFrame({
        '지점': ['노량진', '선유'],
        'lat': [37.5175, 37.5451],
        'lon': [126.9413, 126.8991],
        '최근_DO': [df_do['노량진'].iloc[-1], df_do['선유'].iloc[-1]],
        '최근_pH': [df_ph['노량진'].iloc[-1], df_ph['선유'].iloc[-1]],
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

    # --- 5. AM/PM 및 시계열 분석 ---
    # 오류가 났던 지점: 들여쓰기를 확실하게 처리함
    for df in [df_do, df_ph]:
        df['Hour'] = df['일시'].dt.hour
        df['AM/PM'] = df['Hour'].apply(lambda x: 'AM (오전)' if x < 12 else 'PM (오후)')

    location = st.sidebar.selectbox("분석 지점 선택", ["노량진", "선유"])
    
    st.subheader(f"📊 {location} 지점 시간대별 변화율")
    c1, c2 = st.columns(2)
    
    with c1:
        avg_do = df_do.groupby('AM/PM')[location].mean().reset_index()
        st.plotly_chart(px.bar(avg_do, x='AM/PM', y=location, title="평균 용존산소(DO)", color='AM/PM', color_discrete_sequence=['#3498db', '#2980b9']), use_container_width=True)
    
    with c2:
        avg_ph = df_ph.groupby('AM/PM')[location].mean().reset_index()
        st.plotly_chart(px.bar(avg_ph, x='AM/PM', y=location, title="평균 수소이온농도(pH)", color='AM/PM', color_discrete_sequence=['#2ecc71', '#27ae60']), use_container_width=True)

    # --- 6. 노량진 vs 선유 비교 표 ---
    st.subheader("🏁 지점별 수질 요약 비교")
    
    summary_data = []
    for loc in ["노량진", "선유"]:
        summary_data.append({
            "지점": loc,
            "평균 DO (mg/L)": round(df_do[loc].mean(), 2),
            "평균 pH": round(df_ph[loc].mean(), 2),
            "최고 DO": df_do[loc].max(),
            "변동성(표준편차)": round(df_do[loc].std(), 2)
        })
    
    st.table(pd.DataFrame(summary_data).set_index("지점"))

    # 자동 인사이트
    if df_do['노량진'].mean() > df_do['선유'].mean():
        st.info("💡 **Insight:** 노량진 지점의 산소 포화도가
