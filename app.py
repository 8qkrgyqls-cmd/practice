import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="2026 방역 전략 대시보드", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터셋 (보고서 부록 기반)
@st.cache_data
def load_data():
    data = [
        ["서울", "인플루엔자", 18.5, 12.2, 42.0, 68.5, "스마트 공조"],
        ["경기", "RSV", 34.2, 22.8, 22.5, 45.0, "클린 에듀케이션"],
        ["인천", "노로바이러스", 15.8, 9.5, 12.0, 35.5, "워터-세이프"],
        ["강원", "COVID-19", 24.2, 15.1, 50.4, 82.5, "모빌리티 보건소"],
        ["전라", "노로바이러스", 14.5, 8.8, 13.2, 32.4, "미생물 이력제"]
    ]
    return pd.DataFrame(data, columns=['지역', '바이러스', '발병률_24', '발병률_25', '면역율_24', '면역율_25', '핵심정책'])

df = load_data()

# 3. 타이틀 섹션
st.title("📊 2024-2025 국가 방역 성과 분석")
st.info("데이터 기반 능동형 방역 시스템의 실효성을 정량적으로 평가한 결과입니다. [cite: 11, 12]")

# 4. [모양 변경 1] 지표 카드 (Metrics Cards)
st.subheader("📌 전국 주요 성과 지표")
m1, m2, m3, m4 = st.columns(4)
m1.metric("발병률 감소 (전국)", "12.82%", "-34.1% [cite: 22]")
m2.metric("면역율 상승 (전국)", "62.40%", "+74.3% [cite: 23]")
m3.metric("중증 감소 상관관계", "r = -0.85", "매우 강함 [cite: 25]")
m4.metric("경제적 편익", "4,700억", "자본 투자 효과 [cite: 122]")

st.markdown("---")

# 5. [모양 변경 2] 지역별 성과 카드 (Expandable Cards)
st.subheader("🗺️ 권역별 심층 성과 요약")
cols = st.columns(3)

regions = df['지역'].tolist()
for i, region in enumerate(regions):
    row = df[df['지역'] == region].iloc[0]
    with cols[i % 3]:
        with st.expander(f"📍 {region} 권역 성과 보기", expanded=True):
            st.write(f"**핵심 정책:** {row['핵심정책']}")
            
            # 발병률 변화 시각화 (진척도 바 형태)
            st.write(f"발병률 감소: {row['발병률_24']}% → {row['발병률_25']}%")
            st.progress(int((row['발병률_25'] / row['발병률_24']) * 100))
            
            # 면역율 변화
            st.write(f"면역율 상승: {row['면역율_24']}% → {row['면역율_25']}%")
            st.caption(f"주요 성과: {row['핵심정책']}")

st.markdown("---")

# 6. [모양 변경 3] 인터랙티브 비교 차트
st.subheader("📈 정책 시행 전후 데이터 비교")
chart_type = st.radio("데이터 선택", ["발병률 추이", "면역율 추이"], horizontal=True)

if chart_type == "발병률 추이":
    fig = px.line(df, x="지역", y=["발병률_24", "발병률_25"], markers=True, title="2024 vs 2025 발병률 변화")
else:
    fig = px.line(df, x="지역", y=["면역율_24", "면역율_25"], markers=True, title="2024 vs 2025 면역율 변화")

st.plotly_chart(fig, use_container_width=True)
