import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 설정 ---
st.set_page_config(page_title="River Pulse 2.0", layout="wide")

# --- 인코딩 안전 로드 함수 ---
def load_data_safe(file):
    if file is None: return None
    encodings = ['utf-8', 'cp949', 'euc-kr']
    for enc in encodings:
        try:
            file.seek(0)
            return pd.read_csv(file, encoding=enc)
        except:
            continue
    return None

# --- UI 디자인 ---
st.markdown("""
    <style>
    .main { background-color: #F0F2F6; }
    .stMetric { border: 1px solid #E0E0E0; padding: 10px; border-radius: 10px; background: white; }
    </style>
""", unsafe_allow_html=True)

st.title("🌊 River Pulse : 한강 수질 실시간 모니터링")
st.caption("공공 데이터를 활용한 노량진/선유 지점 수질 분석 포트폴리오")

# 사이드바
st.sidebar.header("📁 데이터 소스")
up_do = st.sidebar.file_uploader("용존산소(DO) CSV", type=['csv'])
up_ph = st.sidebar.file_uploader("수소이온농도(pH) CSV", type=['csv'])

if up_do and up_ph:
    df_do = load_data_safe(up_do)
    df_ph = load_data_safe(up_ph)
    
    # 전처리
    df_do['일시'] = pd.to_datetime(df_do['일시'])
    df_ph['일시'] = pd.to_datetime(df_ph['일시'])
    
    # 필터
    st.sidebar.divider()
    target = st.sidebar.radio("🎯 분석 타겟 지점", ["노량진", "선유"])
    
    # --- 메인 대시보드 ---
    col1, col2, col4 = st.columns([1, 1, 2])
    
    current_do = df_do[target].iloc[-1]
    current_ph = df_ph[target].iloc[-1]
    
    with col1:
        st.metric("최근 용존산소", f"{current_do} mg/L")
    with col2:
        st.metric("최근 pH 농도", f"{current_ph} pH")
    with col4:
        # 간단한 수질 등급 판정 (DO 기준 예시)
        grade = "매우 좋음" if current_do >= 7.5 else "보통"
        st.success(f"현재 {target} 지점의 수질 상태는 **'{grade}'** 단계입니다.")

    st.divider()

    # 시각화 (인터랙티브 차트)
    tab1, tab2 = st.tabs(["📈 시계열 트렌드", "🌗 상관관계 분석"])
    
    with tab1:
        # Plotly를 활용한 이중 축 그래프 (DO & pH를 한 번에)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_do['일시'], y=df_do[target], name="DO (용존산소)", line=dict(color='#00b894')))
        fig.add_trace(go.Scatter(x=df_ph['일시'], y=df_ph[target], name="pH (수소농도)", yaxis="y2", line=dict(color='#0984e3')))
        
        fig.update_layout(
            title=f"{target} 지점 수질 지표 통합 추이",
            yaxis=dict(title="DO (mg/L)"),
            yaxis2=dict(title="pH", overlaying="y", side="right"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
