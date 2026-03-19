import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="River Pulse Pro", layout="wide")

# --- 2. 데이터 로드 함수 (인코딩 & 데이터 타입 클리닝) ---
def load_data(file):
    if file is None: return None
    for enc in ['utf-8', 'cp949', 'euc-kr']:
        try:
            file.seek(0)
            df = pd.read_csv(file, encoding=enc)
            # 숫자가 아닌 값이 섞여있을 경우를 대비해 처리 (노량진, 선유 컬럼)
            for col in ["노량진", "선유"]:
                if col in df.columns:
                    # 숫자로 변환, 변환 안되는 문자열은 NaN(빈값) 처리
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            return df
        except:
            continue
    return None

# --- 3. 사이드바 ---
st.sidebar.title("🌊 River Pulse")
up_do = st.sidebar.file_uploader("용존산소(DO) 파일", type=['csv'])
up_ph = st.sidebar.file_uploader("수소이온농도(pH) 파일", type=['csv'])

if up_do and up_ph:
    df_do = load_data(up_do)
    df_ph = load_data(up_ph)
    
    # '일시' 컬럼 처리 및 빈 값 제거
    df_do['일시'] = pd.to_datetime(df_do['일시'])
    df_ph['일시'] = pd.to_datetime(df_ph['일시'])
    
    location = st.sidebar.selectbox("📍 분석 지점 선택", ["노량진", "선유"])
    
    # --- 핵심 에러 방지 구간 ---
    # 마지막 값이 NaN(빈값)일 수 있으므로 마지막 유효한 숫자를 가져옵니다.
    valid_do = df_do[location].dropna()
    valid_ph = df_ph[location].dropna()

    if not valid_do.empty and not valid_ph.empty:
        latest_do = valid_do.iloc[-1]
        latest_ph = valid_ph.iloc[-1]

        st.title(f"📊 {location} 지점 실시간 보고서")
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("최근 용존산소(DO)", f"{latest_do:.2f} mg/L")
        with m2:
            st.metric("최근 pH 농도", f"{latest_ph:.2f}")
        with m3:
            # 안전하게 비교 연산 수행
            status = "✅ 우수" if latest_do >= 7.0 else "⚠️ 점검 필요"
            st.metric("수질 등급", status)

        st.divider()

        # 차트 시각화
        c1, c2 = st.columns(2)
        with c1:
            fig1 = px.line(df_do, x='일시', y=location, title="용존산소 추이", template="plotly_white")
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            fig2 = px.area(df_ph, x='일시', y=location, title="pH 농도 추이", color_discrete_sequence=['green'])
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.error("선택한 지점에 유효한 수치 데이터가 없습니다.")

else:
    st.info("👈 사이드바에 데이터를 업로드하면 분석이 시작됩니다.")
