import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as fgo

# --- 페이지 설정 ---
st.set_page_config(page_title="River Pulse | 수질 모니터링", layout="wide")

# --- 데이터 로드 및 전처리 함수 ---
@st.cache_data
def load_data():
    try:
        df_do = pd.read_csv('용존산소.csv')
        df_ph = pd.read_csv('수소이온농도.csv')
        
        # '일시' 컬럼 시계열 변환
        df_do['일시'] = pd.to_datetime(df_do['일시'])
        df_ph['일시'] = pd.to_datetime(df_ph['일시'])
        
        return df_do, df_ph
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return None, None

df_do, df_ph = load_data()

# --- 사이드바 (필터링) ---
st.sidebar.header("📍 분석 설정")
location = st.sidebar.selectbox("지점 선택", ["노량진", "선유"])
date_range = st.sidebar.date_input("조회 기간", 
                                 [df_do['일시'].min(), df_do['일시'].max()])

# --- 메인 대시보드 레이아웃 ---
st.title("🌊 River Pulse: 한강 수질 데이터 분석")
st.markdown(f"**{location}** 지점의 용존산소(DO) 및 pH 농도 추이를 분석합니다.")

if df_do is not None:
    # 데이터 필터링 (기간)
    mask = (df_do['일시'].dt.date >= date_range[0]) & (df_do['일시'].dt.date <= date_range[1])
    filtered_do = df_do.loc[mask]
    filtered_ph = df_ph.loc[mask]

    # --- Metrics (주요 지표) ---
    col1, col2, col3 = st.columns(3)
    avg_do = filtered_do[location].mean()
    avg_ph = filtered_ph[location].mean()
    
    col1.metric("평균 용존산소 (DO)", f"{avg_do:.2f} mg/L", delta_color="normal")
    col2.metric("평균 수소이온농도 (pH)", f"{avg_ph:.2f} pH", delta_color="normal")
    col3.metric("측정 데이터 수", f"{len(filtered_do):,} 건")

    st.divider()

    # --- 시각화 영역 ---
    tab1, tab2 = st.tabs(["📈 시간별 추이", "📊 지점별 비교"])

    with tab1:
        st.subheader(f"{location} 수질 변화 그래프")
        
        # DO 그래프
        fig_do = px.line(filtered_do, x='일시', y=location, 
                         title='용존산소(DO) 변화', line_shape='spline',
                         color_discrete_sequence=['#007BFF'])
        fig_do.update_layout(yaxis_title="DO (mg/L)")
        st.plotly_chart(fig_do, use_container_width=True)

        # pH 그래프
        fig_ph = px.line(filtered_ph, x='일시', y=location, 
                         title='수소이온농도(pH) 변화', line_shape='spline',
                         color_discrete_sequence=['#28A745'])
        fig_ph.update_layout(yaxis_title="pH")
        st.plotly_chart(fig_ph, use_container_width=True)

    with tab2:
        st.subheader("노량진 vs 선유 비교 분석")
        comp_col1, comp_col2 = st.columns(2)

        with comp_col1:
            st.write("📍 **용존산소(DO) 분포**")
            fig_box_do = px.box(filtered_do.melt(id_vars='일시', var_name='지점', value_name='DO'), 
                                x='지점', y='DO', color='지점')
            st.plotly_chart(fig_box_do, use_container_width=True)

        with comp_col2:
            st.write("📍 **수소이온농도(pH) 분포**")
            fig_box_ph = px.box(filtered_ph.melt(id_vars='일시', var_name='지점', value_name='pH'), 
                                x='지점', y='pH', color='지점')
            st.plotly_chart(fig_box_ph, use_container_width=True)

# --- 인사이트 섹션 ---
st.sidebar.markdown("---")
st.sidebar.info(
    """
    **💡 데이터 인사이트**
    - 용존산소는 수온이 낮을수록 높아지는 경향이 있습니다.
    - pH 7.0 내외는 중성을 의미하며, 한강의 일반적인 범위입니다.
    """
)
