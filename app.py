import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="2026 국가 방역 전략 대시보드", layout="wide")

# 2. 데이터 로드 (보고서 제 10장 부록 데이터셋 기반) 
@st.cache_data
def load_data():
    # 실제 구현 시에는 CSV 파일로 관리하는 것이 좋습니다.
    data = [
        [1, 2024, "서울", "인플루엔자", 18.5, 42.0, 92.4, "백신 부족 및 밀집 유행"],
        [2, 2025, "서울", "인플루엔자", 12.2, 68.5, 96.8, "스마트 공조 및 순회 접종"],
        [3, 2024, "서울", "COVID-19", 25.6, 35.0, 94.2, "환기 미비로 인한 확산"],
        [4, 2025, "서울", "COVID-19", 18.4, 72.4, 97.5, "AI 공조 시스템 전면 교체"],
        [5, 2024, "경기", "RSV", 34.2, 22.5, 91.2, "보육시설 내 집단 감염"],
        [6, 2025, "경기", "RSV", 22.8, 45.0, 95.6, "클린 에듀케이션 의무화"],
        [13, 2024, "전라", "노로바이러스", 14.5, 13.2, 96.5, "수산물 유통 위생 취약"],
        [14, 2025, "전라", "노로바이러스", 8.8, 32.4, 98.7, "미생물 이력제 전면 시행"],
        [25, 2024, "강원", "COVID-19", 24.2, 50.4, 89.5, "산간 지역 접종률 저조"],
        [26, 2025, "강원", "COVID-19", 15.1, 82.5, 95.2, "모빌리티 보건소 상시 운영"]
        # ... (보고서 부록 50행 데이터를 모두 추가 가능)
    ]
    df = pd.DataFrame(data, columns=['순번', '연도', '지역', '바이러스', '발병률', '면역율', '완치율', '주요대책_성과'])
    return df

df = load_data()

# 3. 사이드바 - 분석 조건 필터
st.sidebar.header("🔍 분석 필터")
selected_region = st.sidebar.multiselect("지역 선택", options=df["지역"].unique(), default=df["지역"].unique())
selected_virus = st.sidebar.multiselect("바이러스 선택", options=df["바이러스"].unique(), default=df["바이러스"].unique())

filtered_df = df[(df["지역"].isin(selected_region)) & (df["바이러스"].isin(selected_virus))]

# 4. 상단 헤더 및 핵심 지표 (KPI) [cite: 22, 23, 25]
st.title("🛡️ 2024-2025 국가 감염병 통합 관리 실효성 평가")
st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("평균 발병률 감소", "12.82%", "-34.1%", help="2024년 대비 2025년 평균 발병률 변화")
with col2:
    st.metric("평균 면역율 상승", "62.40%", "+74.3%", help="전국 평균 면역율 상승 수치")
with col3:
    st.metric("상관관계 (r)", "-0.85", "강한 음의 상관관계", help="면역율 상승 시 중증 환자 발생률 감소")

st.markdown("---")

# 5. 시각화 섹션
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 지역별/연도별 발병률 추이")
    fig1 = px.bar(filtered_df, x="지역", y="발병률", color="연도", barmode="group", 
                  title="정책 시행 전후 발병률 변화")
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.subheader("📈 면역율과 발병률의 상관관계")
    fig2 = px.scatter(filtered_df, x="면역율", y="발병률", color="바이러스", size="완치율",
                     hover_data=['지역', '주요대책_성과'], title="데이터 기반 상관관계 분석")
    st.plotly_chart(fig2, use_container_width=True)

# 6. 하단 데이터 그리드
st.subheader("📋 상세 성과 데이터 분석")
st.dataframe(filtered_df.sort_values(by=["지역", "연도"]), use_container_width=True)

# 7. 향후 정책 로드맵 (K-방역 3.0) [cite: 123, 126, 129]
with st.expander("🚀 2026-2030 향후 전략 로드맵 확인"):
    st.write("""
    * **디지털 트윈 방역망**: 도시 단위 가상 시뮬레이션을 통한 확산 예측 [cite: 126]
    * **유니버설 백신**: 주요 호흡기 바이러스 통합 '멀티-콤보 백신' 개발 [cite: 129]
    * **글로벌 조기 경보**: 국제 하수 역학 감시망(GWSN) 주도 [cite: 132]
    """)
