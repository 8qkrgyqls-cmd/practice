import streamlit as st
import pandas as pd
import numpy as np

# 1. 페이지 설정
st.set_page_config(page_title="데이터 분석 리포트", layout="wide")

# 2. 데이터 로드 및 전처리 (에러 발생 지점 수정)
@st.cache_data
def load_data():
    # 예시 데이터를 생성하거나 실제 CSV를 불러옵니다.
    data = pd.DataFrame({
        '지점': ['노량진', '노량진', '선유', '선유', '뚝섬', '뚝섬'],
        '구분': ['오전', '오후', '오전', '오후', '오전', '오후'],
        'DO': [8.2, 7.9, 9.1, 8.8, 8.5, 8.2],
        'pH': [7.4, 7.5, 7.8, 7.9, 7.6, 7.7],
        '이용건수': [120, 150, 90, 110, 200, 250]
    })
    
    # [수정 포인트] numeric_only=True를 추가하여 숫자 데이터만 평균을 구하도록 합니다.
    # 에러 로그의 .mean() 연산 부분입니다.
    avg_data = data.groupby('지점').mean(numeric_only=True).reset_index()
    return data, avg_data

try:
    df, avg_df = load_data()

    # 3. 메인 화면 구성
    st.title("📊 데이터 통합 대시보드")
    
    # KPI 지표 (상단 카드)
    col1, col2, col3 = st.columns(3)
    col1.metric("전체 평균 DO", f"{avg_df['DO'].mean():.2f} mg/L")
    col2.metric("전체 평균 pH", f"{avg_df['pH'].mean():.2f}")
    col3.metric("최대 이용 지점", avg_df.loc[avg_df['이용건수'].idxmax(), '지점'])

    st.divider()

    # 데이터 시각화
    tab1, tab2 = st.tabs(["📈 분석 차트", "📄 상세 데이터"])
    
    with tab1:
        st.subheader("지점별 주요 지표 비교")
        st.bar_chart(avg_df.set_index('지점')[['DO', 'pH']])
        
    with tab2:
        st.subheader("Raw Data 확인")
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"데이터를 처리하는 중 오류가 발생했습니다: {e}")
    st.info("데이터 프레임의 숫자형 데이터 타입을 확인해 주세요.")

# 4. 스타일링 (에러 로그에 보였던 CSS 관련 부분)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { border: 1px solid #e0e0e0; padding: 15px; border-radius: 10px; background: white; }
    </style>
    """, unsafe_allow_html=True)
