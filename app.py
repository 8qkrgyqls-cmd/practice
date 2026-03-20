import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, csv
from collections import defaultdict
import folium
from folium.plugins import DualMap
from streamlit_folium import st_folium

# 1. 페이지 설정 및 CSS 스타일 (파일 1 기준)
st.set_page_config(
    page_title="한강 수질 분석 · 2020–2050",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
* { font-family: 'Noto Sans KR', sans-serif !important; }
.hero {
    background: linear-gradient(135deg, #0c1e3c 0%, #0f3460 55%, #16547a 100%);
    border-radius: 20px; padding: 40px 48px; margin-bottom: 28px; color: white;
}
.sec-hd {
    font-size: 16px; font-weight: 700; color: #0c1e3c;
    border-left: 4px solid #2563eb; padding-left: 12px; margin: 28px 0 14px;
}
.policy-card {
    background: #fff; border-radius: 14px; padding: 22px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07); border-top: 4px solid #2563eb;
}
.map-label {
    position: absolute; bottom: 10px; left: 10px; z-index: 1000;
    background: rgba(255,255,255,0.8); padding: 5px 10px; border-radius: 5px; font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# 2. 데이터 로드 로직 (파일 1의 안정적인 로직 사용)
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    ph_path = os.path.join(base, 'ph.csv')
    do_path = os.path.join(base, 'do.csv')

    if not (os.path.exists(ph_path) and os.path.exists(do_path)):
        # 파일이 없을 경우 예시 데이터 생성 (실행 확인용)
        dates = pd.date_range("2020-01-01", "2020-12-31")
        return pd.DataFrame({
            'date': dates, 'pH_노량진': 7.2, 'pH_선유': 7.3, 'DO_노량진': 8.4, 'DO_선유': 8.2
        })

    def read_csv_smart(path):
        for enc in ['utf-8-sig', 'cp949']:
            try: return pd.read_csv(path, encoding=enc)
            except: continue
        return pd.read_csv(path)

    ph_df = read_csv_smart(ph_path)
    do_df = read_csv_smart(do_path)
    ph_df['date'] = pd.to_datetime(ph_df['일시']).dt.date
    do_df['date'] = pd.to_datetime(do_df['일시']).dt.date
    merged = pd.merge(
        ph_df.groupby('date')[['노량진', '선유']].mean().reset_index(),
        do_df.groupby('date')[['노량진', '선유']].mean().reset_index(),
        on='date', suffixes=('_pH', '_DO')
    )
    merged['date'] = pd.to_datetime(merged['date'])
    return merged

df = load_data()

# 3. Hero & KPI 섹션
st.markdown('<div class="hero"><h1>🌊 한강 수질 분석 대시보드</h1><p>데이터 기반 수질 진단 및 정책 시뮬레이션</p></div>', unsafe_allow_html=True)

# 4. 탭 구성
tabs = st.tabs(["📈 시계열", "📅 월별", "🔗 상관관계", "🔬 수질 해석", "🔮 미래 예측", "📋 수질 정책"])

# (Tab 1 ~ Tab 5는 파일 1의 기존 시각화 코드를 넣으시면 됩니다. 여기서는 생략)
with tabs[0]: st.info("일자별 수질 변화 시계열 차트 영역")
with tabs[4]: st.info("2050년 기후변화 시나리오 예측 영역")

# 5. [핵심 통합] Tab 6 : 정책 실행 전 vs 후 수질 지도 비교
with tabs[5]:
    st.markdown('<div class="sec-hd">정책 도입 시뮬레이션: 2050년 DO 수질 개선 효과</div>', unsafe_allow_html=True)
    
    # 정책 데이터베이스
    POLICIES = {
        "선택 안함": {"do_up": 0.0, "color": "red", "desc": "현재 추세 유지 시 수질 악화 고착화"},
        "인공 폭기 시스템": {"do_up": 2.2, "color": "blue", "desc": "수중 산소 직접 공급으로 DO 급락 방지"},
        "수변 녹지 조성": {"do_up": 0.7, "color": "green", "desc": "차광 효과를 통한 수온 상승 억제"},
        "하수처리 고도화": {"do_up": 1.4, "color": "purple", "desc": "유기물 저감으로 미생물 산소 소비 억제"}
    }
    
    col_ui, col_map = st.columns([1, 2])
    
    with col_ui:
        st.write("### 🛠️ 정책 시나리오 설정")
        p_name = st.selectbox("적용할 수질 개선 정책", list(POLICIES.keys()))
        p_info = POLICIES[p_name]
        
        st.markdown(f"""
        <div class="policy-card">
            <h4>{p_name}</h4>
            <p>{p_info['desc']}</p>
            <hr>
            <p><b>기대 개선치:</b> <span style='color:blue; font-weight:bold;'>+{p_info['do_up']} mg/L</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.caption("※ 2050년 SSP5-8.5(고탄소) 시나리오 기준 시뮬레이션입니다.")

    with col_map:
        # 2050년 기본 수치 (정책 전)
        base_nry = 5.54 
        base_syu = 5.37
        
        # 정책 후 수치
        after_nry = base_nry + p_info['do_up']
        after_syu = base_syu + p_info['do_up']

        # DualMap 생성 (왼쪽: 전 / 오른쪽: 후)
        d_map = DualMap(location=[37.52, 126.91], zoom_start=12)

        # 왼쪽 지도 (정책 전 - 현재 예측)
        folium.Marker(
            [37.511, 126.933], popup=f"노량진: {base_nry}mg/L",
            icon=folium.Icon(color='red', icon='warning-sign'), tooltip="정책 전 (노량진)"
        ).add_to(d_map.m1)
        folium.Marker(
            [37.533, 126.878], popup=f"선유: {base_syu}mg/L",
            icon=folium.Icon(color='red', icon='warning-sign'), tooltip="정책 전 (선유)"
        ).add_to(d_map.m1)

        # 오른쪽 지도 (정책 후 - 개선 예측)
        folium.Marker(
            [37.511, 126.933], popup=f"개선 후: {after_nry:.2f}mg/L",
            icon=folium.Icon(color='blue', icon='ok-sign'), tooltip="정책 후 (노량진)"
        ).add_to(d_map.m2)
        folium.Marker(
            [37.533, 126.878], popup=f"개선 후: {after_syu:.2f}mg/L",
            icon=folium.Icon(color='blue', icon='ok-sign'), tooltip="정책 후 (선유)"
        ).add_to(d_map.m2)

        # 지도 출력
        st_folium(d_map, width="100%", height=500)
        st.write("⬅️ **왼쪽: 정책 적용 전** (위험) | **오른쪽: 정책 적용 후** (개선) ➡️")

st.markdown("---")
st.caption("본 대시보드는 실측 데이터와 기후 시나리오를 결합한 가상 시뮬레이션 도구입니다.")
