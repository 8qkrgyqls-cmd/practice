import streamlit as st
import pandas as pd
import plotly.express as px

# --- 페이지 설정 ---
st.set_page_config(page_title="River Pulse | 수질 모니터링", layout="wide")

# --- 스타일링 (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 상단 타이틀 ---
st.title("🌊 River Pulse: 한강 수질 분석 대시보드")
st.info("왼쪽 사이드바에서 '용존산소.csv'와 '수소이온농도.csv' 파일을 업로드해주세요.")

# --- 사이드바: 파일 업로드 ---
st.sidebar.header("📁 데이터 업로드")
uploaded_do = st.sidebar.file_uploader("용존산소.csv 업로드", type=['csv'])
uploaded_ph = st.sidebar.file_uploader("수소이온농도.csv 업로드", type=['csv'])

# --- 데이터 처리 로직 ---
if uploaded_do and uploaded_ph:
    try:
        # 데이터 읽기
        df_do = pd.read_csv(uploaded_do)
        df_ph = pd.read_csv(uploaded_ph)
        
        # 날짜 변환 (에러 방지용)
        df_do['일시'] = pd.to_datetime(df_do['일시'])
        df_ph['일시'] = pd.to_datetime(df_ph['일시'])

        # --- 사이드바 필터 ---
        st.sidebar.divider()
        st.sidebar.header("📍 필터 설정")
        location = st.sidebar.selectbox("분석 지점 선택", ["노량진", "선유"])
        
        min_date = df_do['일시'].min().date()
        max_date = df_do['일시'].max().date()
        
        date_range = st.sidebar.date_input("조회 기간", [min_date, max_date])

        # 기간 필터링
        mask = (df_do['일시'].dt.date >= date_range[0]) & (df_do['일시'].dt.date <= date_range[1])
        f_do = df_do.loc[mask]
        f_ph = df_ph.loc[mask]

        # --- 메인 화면: Metric ---
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("평균 DO (mg/L)", round(f_do[location].mean(), 2))
        with col2:
            st.metric("평균 pH", round(f_ph[location].mean(), 2))
        with col3:
            status = "🔴 주의" if f_do[location].mean() < 5 else "🟢 양호"
            st.metric("수질 상태", status)

        # --- 시각화 ---
        st.divider()
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader(f"📈 {location} 용존산소 추이")
            fig1 = px.area(f_do, x='일시', y=location, color_discrete_sequence=['#00a8ff'])
            st.plotly_chart(fig1, use_container_width=True)

        with c2:
            st.subheader(f"📉 {location} pH 농도 추이")
            fig2 = px.line(f_ph, x='일시', y=location, color_discrete_sequence=['#4cd137'])
            st.plotly_chart(fig2, use_container_width=True)

        # --- 지점 비교 (박스플롯) ---
        st.subheader("📊 지점별 수질 데이터 분포 비교")
        compare_df = f_do.melt(id_vars='일시', var_name='지점', value_name='DO')
        fig3 = px.box(compare_df, x='지점', y='DO', color='지점', points="all")
        st.plotly_chart(fig3, use_container_width=True)

    except Exception as e:
        st.error(f"데이터 처리 중 오류가 발생했습니다: {e}")
        st.warning("CSV 파일의 컬럼명이 '일시', '노량진', '선유'로 되어 있는지 확인해주세요.")
else:
    st.warning("분석을 시작하려면 파일을 업로드해주세요.")
    # 포트폴리오 느낌을 위해 샘플 이미지나 설명을 넣을 수 있습니다.
    st.image("https://images.unsplash.com/photo-1502737224383-ed3a350700ae?auto=format&fit=crop&w=1000&q=80", caption="River Water Quality Analysis System")
