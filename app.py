import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="River Pulse Pro", layout="wide")

# --- 2. 인코딩 대응 데이터 로드 함수 ---
def load_data(file):
    if file is None: return None
    for enc in ['utf-8', 'cp949', 'euc-kr']:
        try:
            file.seek(0)
            return pd.read_csv(file, encoding=enc)
        except:
            continue
    return None

# --- 3. 사이드바 구성 ---
st.sidebar.title("🌊 River Pulse")
st.sidebar.info("한강 수질 데이터를 분석합니다.")

up_do = st.sidebar.file_uploader("용존산소(DO) 파일 업로드", type=['csv'])
up_ph = st.sidebar.file_uploader("수소이온농도(pH) 파일 업로드", type=['csv'])

# --- 4. 메인 로직 ---
if up_do and up_ph:
    df_do = load_data(up_do)
    df_ph = load_data(up_ph)
    
    # 전처리: '일시' 컬럼 처리
    for df in [df_do, df_ph]:
        df['일시'] = pd.to_datetime(df['일시'])
    
    # 지점 선택
    location = st.sidebar.selectbox("📍 분석 지점 선택", ["노량진", "선유"])
    
    st.title(f"📊 {location} 지점 수질 분석 보고서")
    
    # --- 상단 지표 (Metrics) ---
    m1, m2, m3 = st.columns(3)
    latest_do = df_do[location].iloc[-1]
    latest_ph = df_ph[location].iloc[-1]
    
    with m1:
        st.metric("최근 용존산소(DO)", f"{latest_do} mg/L")
    with m2:
        st.metric("최근 pH 농도", f"{latest_ph}")
    with m3:
        # 간단한 판정 로직
        status = "✅ 우수" if latest_do >= 7.0 else "⚠️ 점검 필요"
        st.metric("현재 수질 상태", status)

    st.divider()

    # --- 시각화 (여기가 에러 났던 구간입니다) ---
    st.subheader("💡 시계열 데이터 추이")
    
    c1, c2 = st.columns(2)
    
    with c1:
        # 이 블록 안이 비어있으면 에러가 납니다. 반드시 한 줄 이상의 코드가 있어야 합니다.
        fig_do = px.line(df_do, x='일시', y=location, 
                         title=f"{location} 용존산소 추이",
                         line_shape='spline', color_discrete_sequence=['#3498db'])
        st.plotly_chart(fig_do, use_container_width=True)
        
    with c2:
        fig_ph = px.area(df_ph, x='일시', y=location, 
                         title=f"{location} pH 변화량",
                         color_discrete_sequence=['#2ecc71'])
        st.plotly_chart(fig_ph, use_container_width=True)

    # --- 고급 분석 (Box Plot) ---
    st.subheader("🔍 통계적 분포 비교")
    # 두 지점 데이터를 합쳐서 비교 시각화
    compare_do = df_do.melt(id_vars='일시', var_name='지점', value_name='DO')
    fig_box = px.box(compare_do, x='지점', y='DO', color='지점', notched=True)
    st.plotly_chart(fig_box, use_container_width=True)

else:
    # 데이터가 없을 때의 초기 화면 (포트폴리오용 신박한 디자인)
    st.warning("👈 사이드바에서 데이터를 먼저 업로드해주세요.")
    st.image("https://images.unsplash.com/photo-1437622368342-7a3d73a34c8f?auto=format&fit=crop&w=1200&q=80", 
             caption="데이터 분석을 대기 중입니다.")
