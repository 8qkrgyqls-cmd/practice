import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Han River Water Quality AI", layout="wide")

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
            return df.dropna(subset=['일시'])
        except: continue
    return None

# --- 3. 사이드바 제어 ---
st.sidebar.title("🌊 데이터 컨트롤")
up_do = st.sidebar.file_uploader("용존산소(DO) 데이터", type=['csv'])
up_ph = st.sidebar.file_uploader("수소이온농도(pH) 데이터", type=['csv'])

if up_do and up_ph:
    df_do = load_data(up_do)
    df_ph = load_data(up_ph)
    df_do['일시'] = pd.to_datetime(df_do['일시'])
    df_ph['일시'] = pd.to_datetime(df_ph['일시'])

    # --- [상단] 헤더 ---
    st.title("🚀 River Quality Insight Engine")
    st.caption("한강 노량진/선유 지점 수질 데이터 분석 포트폴리오")
    st.divider()

    # --- [섹션 1] 주요 지표 (Metrics) ---
    loc_select = st.sidebar.selectbox("분석 대상 지점", ["노량진", "선유"])
    
    m1, m2, m3 = st.columns(3)
    latest_do = df_do[loc_select].dropna().iloc[-1]
    latest_ph = df_ph[loc_select].dropna().iloc[-1]
    
    m1.metric(f"{loc_select} 최근 DO", f"{latest_do:.2f} mg/L")
    m2.metric(f"{loc_select} 최근 pH", f"{latest_ph:.2f}")
    m3.metric("데이터 상태", "정상 (Good)")
    st.divider()

    # --- [섹션 2] 지도 및 시계열 차트 ---
    st.subheader("📍 지점별 실시간 위치 및 추이")
    c1, c2 = st.columns([1, 1])
    
    with c1:
        # 지도 생성
        map_data = pd.DataFrame({
            '지점': ['노량진', '선유'],
            'lat': [37.5175, 37.5451], 'lon': [126.9413, 126.8991],
            '최근_DO': [df_do['노량진'].dropna().iloc[-1], df_do['선유'].dropna().iloc[-1]]
        })
        fig_map = px.scatter_mapbox(map_data, lat="lat", lon="lon", color="최근_DO", size="최근_DO",
                                    hover_name="지점", zoom=10.5, height=400)
        fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)

    with c2:
        # 시계열 차트 생성 (fig_trend 정의)
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=df_do['일시'], y=df_do[loc_select], name="DO", line=dict(color='#3498db')))
        fig_trend.add_trace(go.Scatter(x=df_ph['일시'], y=df_ph[loc_select], name="pH", yaxis="y2", line=dict(color='#2ecc71')))
        fig_trend.update_layout(
            title=f"{loc_select} 통합 지표 추이",
            yaxis=dict(title="DO (mg/L)"),
            yaxis2=dict(title="pH", overlaying="y", side="right"),
            height=400, margin={"t":50,"b":0}
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    
    st.divider()

    # --- [섹션 3] AM/PM 및 통계 분석 ---
    st.subheader("🧪 데이터 사이언스 분석 (AM/PM & T-Test)")
    
    # AM/PM 변수 생성
    df_do['AM/PM'] = df_do['일시'].dt.hour.apply(lambda x: '오전(AM)' if x < 12 else '오후(PM)')
    avg_do = df_do.groupby('AM/PM')[loc_select].mean().reset_index()
    
    # T-Test 계산
    t_stat, p_val = stats.ttest_ind(df_do['노량진'].dropna(), df_do['선유'].dropna())
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(px.bar(avg_do, x='AM/PM', y=loc_select, title="주야간 평균 DO 비교"), use_container_width=True)
    with col_b:
        st.write("📊 **통계적 유의성 검정 결과**")
        st.info(f"노량진 vs 선유 DO 데이터의 P-value: **{p_val:.4f}**")
        if p_val < 0.05:
            st.success("💡 결과: 두 지점 간의 수질 차이는 통계적으로 매우 유의미합니다.")
        else:
            st.warning("💡 결과: 두 지점은 통계적으로 유의미한 수질 차이가 없습니다.")

    st.divider()

    # --- [섹션 4] 리포트 다운로드 ---
    csv = df_do.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 전체 분석 데이터 다운로드 (CSV)", data=csv, file_name="HanRiver_Quality_Report.csv")

else:
    st.warning("👈 왼쪽 사이드바에서 '용존산소'와 '수소이온농도' CSV 파일을 업로드해주세요.")
    st.image("https://images.unsplash.com/photo-1502933691298-84fc14542831?auto=format&fit=crop&w=1200&q=80")
