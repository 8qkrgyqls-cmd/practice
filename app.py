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

# 1. 페이지 설정
st.set_page_config(
    page_title="한강 수질 분석 · 2020–2050",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. CSS 스타일 적용
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
* { font-family: 'Noto Sans KR', sans-serif !important; }
.block-container { padding: 1.5rem 2rem 3rem; max-width: 1400px; }
.hero {
    background: linear-gradient(135deg, #0c1e3c 0%, #0f3460 55%, #16547a 100%);
    border-radius: 20px; padding: 40px 48px 36px;
    margin-bottom: 28px; position: relative; overflow: hidden;
}
.hero-title { font-size: 30px; font-weight: 900; color: #fff; margin: 0 0 8px; }
.hero-sub { font-size: 14px; color: rgba(255,255,255,0.65); line-height: 1.6; }
.hero-tag {
    background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.2);
    color: rgba(255,255,255,0.85); border-radius: 20px; padding: 4px 14px;
    font-size: 12px; margin-top: 10px; display: inline-block;
}
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px; }
.kpi {
    background: #fff; border-radius: 14px; padding: 18px 20px 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06); border-top: 3px solid #2563eb;
}
.kpi.orange { border-top-color: #ea580c; }
.kpi.teal { border-top-color: #0891b2; }
.kpi.amber { border-top-color: #d97706; }
.kpi-label { font-size: 11.5px; color: #6b7280; font-weight: 500; }
.kpi-value { font-size: 28px; font-weight: 800; color: #111827; }
.sec-hd {
    font-size: 16px; font-weight: 700; color: #0c1e3c;
    border-left: 4px solid #2563eb; padding-left: 12px; margin: 28px 0 14px;
}
.ins-card {
    background: #fff; border-radius: 14px; padding: 20px 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 14px; border-left: 4px solid #e5e7eb;
}
.ins-card.blue { border-left-color: #3b82f6; }
.ins-card.red { border-left-color: #ef4444; }
.ins-card.green { border-left-color: #22c55e; }
.ins-card.orange { border-left-color: #f97316; }
.ins-card.purple { border-left-color: #a855f7; }
.badge { display: inline-block; border-radius: 20px; padding: 2px 10px; font-size: 11.5px; font-weight: 600; }
.b-blue { background:#dbeafe; color:#1d4ed8; }
.grade-table { width:100%; border-collapse:collapse; font-size:13px; margin-top:10px;}
.grade-table th, .grade-table td { padding: 8px; border: 1px solid #e5e7eb; text-align:left; }
.policy-card { background: #fff; border-radius: 14px; padding: 22px; box-shadow: 0 2px 8px rgba(0,0,0,0.07); border-top: 3px solid #2563eb; }
</style>
""", unsafe_allow_html=True)

# 3. 상수 데이터 정의
STATIONS = {"노량진": {"lat": 37.5110, "lon": 126.9333}, "선유": {"lat": 37.5330, "lon": 126.8780}}
HANGANG = [[37.513, 126.958], [37.515, 126.940], [37.516, 126.920], [37.518, 126.900], [37.523, 126.878], [37.528, 126.858]]
FUTURE = {
    "year": [2026, 2030, 2040, 2050],
    "SSP245_노량진_DO": [8.26, 7.93, 7.43, 6.96], "SSP245_선유_DO": [8.04, 7.73, 7.24, 6.77],
    "SSP585_노량진_DO": [8.11, 7.51, 6.51, 5.54], "SSP585_선유_DO": [7.90, 7.31, 6.34, 5.37],
}
df_future = pd.DataFrame(FUTURE)

POLICIES = [
    {"title": "폭기(曝氣) 시설 확충", "icon": "🌬️", "phase_label": "단기 (2026~2030)", "effect": "DO 최솟값 +2~4 mg/L 상승", "detail": "수중 산기관 운영으로 여름철 DO 급락 긴급 대응", "do_impact_nry": 2.5, "do_impact_syu": 2.0},
    {"title": "하수처리장 고도화", "icon": "🏭", "phase_label": "중기 (2031~2040)", "effect": "DO +1.0~1.5 mg/L 상승", "detail": "방류수 총인 농도 저감을 통한 유기물 분해 산소 소비 억제", "do_impact_nry": 1.2, "do_impact_syu": 1.5},
]

# 4. 데이터 로드 함수
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    ph_path = os.path.join(base, 'ph.csv')
    do_path = os.path.join(base, 'do.csv')

    if not (os.path.exists(ph_path) and os.path.exists(do_path)):
        raise FileNotFoundError("ph.csv와 do.csv 파일이 app.py와 같은 폴더에 있는지 확인해주세요.")

    def read_csv_dynamic(path):
        for enc in ['utf-8-sig', 'cp949']:
            try: return pd.read_csv(path, encoding=enc)
            except: continue
        return pd.read_csv(path)

    ph_df = read_csv_dynamic(ph_path)
    do_df = read_csv_dynamic(do_path)
    
    # 간단한 전처리 (일시 기준 병합)
    ph_df['date'] = pd.to_datetime(ph_df['일시']).dt.date
    do_df['date'] = pd.to_datetime(do_df['일시']).dt.date
    
    ph_m = ph_df.groupby('date')[['노량진', '선유']].mean().reset_index()
    do_m = do_df.groupby('date')[['노량진', '선유']].mean().reset_index()
    
    merged = pd.merge(ph_m, do_m, on='date', suffixes=('_pH', '_DO'))
    merged['date'] = pd.to_datetime(merged['date'])
    return merged

try:
    df = load_data()
except Exception as e:
    st.error(f"📂 **파일 에러**: {e}")
    st.stop()

# 5. 메인 레이아웃 (Hero & KPI)
st.markdown(f"""
<div class="hero">
  <div class="hero-title">🌊 한강 수질 분석 대시보드</div>
  <div class="hero-sub">노량진 · 선유 측정소 실측 데이터 기반 분석 및 2050년 수질 예측</div>
  <div class="hero-tag">📅 데이터 기간: {df['date'].min().date()} ~ {df['date'].max().date()}</div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.markdown('<div class="kpi"><div class="kpi-label">pH 연평균 (노량진)</div><div class="kpi-value">7.29</div></div>', unsafe_allow_html=True)
c2.markdown('<div class="kpi orange"><div class="kpi-label">pH 연평균 (선유)</div><div class="kpi-value">7.32</div></div>', unsafe_allow_html=True)
c3.markdown('<div class="kpi teal"><div class="kpi-label">DO 연평균 (노량진)</div><div class="kpi-value">8.46</div></div>', unsafe_allow_html=True)
c4.markdown('<div class="kpi amber"><div class="kpi-label">DO 연평균 (선유)</div><div class="kpi-value">8.26</div></div>', unsafe_allow_html=True)

# 6. 탭 구성
tabs = st.tabs(["📈 시계열", "📅 월별", "🔗 상관관계", "🔬 해석", "🔮 예측", "📋 정책"])

# --- Tab 1: 시계열 ---
with tabs[0]:
    st.markdown('<div class="sec-hd">일자별 수질 변화</div>', unsafe_allow_html=True)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1)
    fig.add_trace(go.Scatter(x=df['date'], y=df['노량진_pH'], name="노량진 pH", line=dict(color='#2563eb')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['date'], y=df['선유_pH'], name="선유 pH", line=dict(color='#ea580c')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['date'], y=df['노량진_DO'], name="노량진 DO", line=dict(color='#0891b2')), row=2, col=1)
    fig.add_trace(go.Scatter(x=df['date'], y=df['선유_DO'], name="선유 DO", line=dict(color='#d97706')), row=2, col=1)
    fig.update_layout(height=500, template="plotly_white", margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 2: 월별 ---
with tabs[1]:
    df['month'] = df['date'].dt.month
    m_avg = df.groupby('month').mean()
    fig_m = go.Figure()
    fig_m.add_trace(go.Bar(x=m_avg.index, y=m_avg['노량진_DO'], name="노량진 DO", marker_color='#0891b2'))
    fig_m.add_trace(go.Bar(x=m_avg.index, y=m_avg['선유_DO'], name="선유 DO", marker_color='#d97706'))
    fig_m.update_layout(title="월별 평균 용존산소(DO) 비교", template="plotly_white")
    st.plotly_chart(fig_m, use_container_width=True)

# --- Tab 3: 상관관계 ---
with tabs[2]:
    st.markdown('<div class="sec-hd">pH와 DO의 관계</div>', unsafe_allow_html=True)
    fig_s = go.Figure()
    fig_s.add_trace(go.Scatter(x=df['노량진_pH'], y=df['노량진_DO'], mode='markers', name="노량진", marker=dict(opacity=0.5)))
    fig_s.add_trace(go.Scatter(x=df['선유_pH'], y=df['선유_DO'], mode='markers', name="선유", marker=dict(opacity=0.5)))
    fig_s.update_layout(xaxis_title="pH", yaxis_title="DO (mg/L)", template="plotly_white")
    st.plotly_chart(fig_s, use_container_width=True)

# --- Tab 4: 해석 ---
with tabs[3]:
    insights = [
        ("blue", "봄철 pH 급등", "3~4월 광합성 활발로 인해 pH가 연중 최고치를 기록합니다."),
        ("red", "여름철 DO 위기", "수온 상승 및 유기물 분해로 DO가 5mg/L 이하로 떨어지는 구간이 발생합니다."),
        ("purple", "환경부 수질 등급", "평균적으로 2~3등급이나 여름철 순간 수질은 4등급까지 악화될 수 있습니다.")
    ]
    for color, title, body in insights:
        st.markdown(f'<div class="ins-card {color}"><div class="ins-title">{title}</div><div>{body}</div></div>', unsafe_allow_html=True)

# --- Tab 5: 예측 ---
with tabs[4]:
    st.markdown('<div class="sec-hd">2050 기후변화 시나리오 예측</div>', unsafe_allow_html=True)
    ssp = st.radio("시나리오 선택", ["SSP2-4.5 (온건)", "SSP5-8.5 (심각)"])
    prefix = "SSP245" if "2-4.5" in ssp else "SSP585"
    
    fig_f = go.Figure()
    fig_f.add_trace(go.Scatter(x=FUTURE['year'], y=FUTURE[f'{prefix}_노량진_DO'], name="노량진 예측", mode='lines+markers'))
    fig_f.add_trace(go.Scatter(x=FUTURE['year'], y=FUTURE[f'{prefix}_선유_DO'], name="선유 예측", mode='lines+markers'))
    fig_f.add_hline(y=5.0, line_dash="dash", line_color="red", annotation_text="생존 한계선")
    fig_f.update_layout(template="plotly_white", yaxis_range=[4, 10])
    st.plotly_chart(fig_f, use_container_width=True)

# --- Tab 6: 정책 ---
with tabs[5]:
    st.markdown('<div class="sec-hd">수질 개선 정책 시뮬레이션</div>', unsafe_allow_html=True)
    p_name = st.selectbox("정책 선택", [p['title'] for p in POLICIES])
    p_data = next(p for p in POLICIES if p['title'] == p_name)
    
    c1, c2 = st.columns([2, 1])
    with c1:
        # 간단한 지도 구현
        m = folium.Map(location=[37.52, 126.91], zoom_start=12)
        folium.Marker([37.511, 126.933], popup="노량진").add_to(m)
        folium.Marker([37.533, 126.878], popup="선유").add_to(m)
        st_folium(m, width="100%", height=400)
    with c2:
        st.markdown(f"""
        <div class="policy-card">
            <h3>{p_data['icon']} {p_name}</h3>
            <p><b>단계:</b> {p_data['phase_label']}</p>
            <p>{p_data['detail']}</p>
            <hr>
            <p><b>예상 DO 개선:</b> +{p_data['do_impact_nry']} mg/L</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.caption("본 대시보드는 교육용 시뮬레이션이며 실측치와 모델링 데이터가 혼합되어 있습니다.")
