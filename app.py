import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="한강 수질 분석 대시보드",
    page_icon="💧",
    layout="wide"
)

st.markdown("""
<style>
    .main { background-color: #f0f4f8; }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0; }
</style>
""", unsafe_allow_html=True)

# ── 측정소 위치 정보 ─────────────────────────────────────────
STATIONS = {
    "노량진": {"lat": 37.5110, "lon": 126.9333, "color": "#1F77B4"},
    "선유":   {"lat": 37.5330, "lon": 126.8780, "color": "#FF7F0E"},
}

# ── 기초 통계 데이터 (기획안 기반) ──────────────────────────
BASE_STATS = {
    "노량진": {"pH_mean": 7.29, "pH_min": 6.80, "pH_max": 8.30, "pH_std": 0.21,
               "DO_mean": 8.46, "DO_min": 2.1,  "DO_max": 12.3, "DO_std": 1.89},
    "선유":   {"pH_mean": 7.32, "pH_min": 6.60, "pH_max": 8.40, "pH_std": 0.29,
               "DO_mean": 8.26, "DO_min": 2.0,  "DO_max": 12.5, "DO_std": 1.93},
}

# ── 월별 패턴 데이터 (계절 특성 반영) ───────────────────────
MONTHLY = {
    "month": list(range(1, 13)),
    "label": ["1월","2월","3월","4월","5월","6월","7월","8월","9월","10월","11월","12월"],
    "노량진_pH": [7.4, 7.4, 7.7, 8.1, 7.8, 7.3, 7.2, 7.2, 7.3, 7.5, 7.4, 7.4],
    "선유_pH":  [7.4, 7.4, 7.8, 8.2, 7.9, 7.3, 7.2, 7.1, 7.3, 7.5, 7.4, 7.4],
    "노량진_DO": [11.17, 10.8, 9.5, 8.8, 7.5, 5.95, 5.3, 5.5, 7.2, 9.1, 10.5, 11.17],
    "선유_DO":  [10.91, 10.5, 9.2, 8.5, 7.2, 5.51, 4.9, 5.2, 6.9, 8.8, 10.2, 10.91],
}

# ── 미래 예측 데이터 ─────────────────────────────────────────
FUTURE = {
    "year": [2026, 2030, 2040, 2050],
    "SSP245_노량진_DO": [8.26, 7.93, 7.43, 6.96],
    "SSP245_선유_DO":   [8.04, 7.73, 7.24, 6.77],
    "SSP245_노량진_pH": [7.275, 7.267, 7.247, 7.227],
    "SSP245_선유_pH":   [7.305, 7.297, 7.277, 7.257],
    "SSP585_노량진_DO": [8.11, 7.51, 6.51, 5.54],
    "SSP585_선유_DO":   [7.90, 7.31, 6.34, 5.37],
    "SSP585_노량진_pH": [7.275, 7.257, 7.207, 7.137],
    "SSP585_선유_pH":   [7.305, 7.287, 7.237, 7.167],
}

df_future = pd.DataFrame(FUTURE)
df_monthly = pd.DataFrame(MONTHLY)

# ── 헬퍼: DO 등급 색상 ───────────────────────────────────────
def do_grade(val):
    if val >= 7.5:  return "🟢 1등급", "#2ECC71"
    elif val >= 5.0: return "🟡 2~3등급", "#F39C12"
    elif val >= 2.0: return "🟠 4등급", "#E67E22"
    else:            return "🔴 5등급↓", "#E74C3C"

def do_color_hex(val):
    if val >= 7.5:   return "#2ECC71"
    elif val >= 5.0: return "#F39C12"
    elif val >= 2.0: return "#E67E22"
    else:            return "#E74C3C"

# ════════════════════════════════════════════════════════════
# 헤더
# ════════════════════════════════════════════════════════════
st.title("💧 한강 수질 분석 대시보드")
st.caption("노량진·선유 측정소 | 2020년 실측 데이터 + IPCC 기후변화 시나리오 예측")
st.divider()

# ════════════════════════════════════════════════════════════
# 탭 구성
# ════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["📊 현황 분석", "🗺️ 미래 예측 지도", "📈 예측 트렌드"])

# ────────────────────────────────────────────────────────────
# TAB 1: 현황 분석
# ────────────────────────────────────────────────────────────
with tab1:
    st.subheader("2020년 연간 기초 통계")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("노량진 pH 연평균", "7.29", delta="범위 6.80~8.30")
    col2.metric("선유 pH 연평균",   "7.32", delta="범위 6.60~8.40")
    col3.metric("노량진 DO 연평균", "8.46 mg/L", delta="최솟값 2.1 mg/L", delta_color="inverse")
    col4.metric("선유 DO 연평균",   "8.26 mg/L", delta="최솟값 2.0 mg/L", delta_color="inverse")

    st.divider()
    st.subheader("월별 수질 변화 패턴")

    indicator = st.radio("지표 선택", ["DO (용존산소, mg/L)", "pH"], horizontal=True)
    key = "DO" if "DO" in indicator else "pH"
    y_label = "DO (mg/L)" if key == "DO" else "pH"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_monthly["label"], y=df_monthly[f"노량진_{key}"],
        name="노량진", mode="lines+markers",
        line=dict(color="#1F77B4", width=3),
        marker=dict(size=8)
    ))
    fig.add_trace(go.Scatter(
        x=df_monthly["label"], y=df_monthly[f"선유_{key}"],
        name="선유", mode="lines+markers",
        line=dict(color="#FF7F0E", width=3, dash="dot"),
        marker=dict(size=8)
    ))
    if key == "DO":
        fig.add_hline(y=7.5, line_dash="dash", line_color="#2ECC71",
                      annotation_text="1등급 기준 (7.5)", annotation_position="top left")
        fig.add_hline(y=5.0, line_dash="dash", line_color="#E67E22",
                      annotation_text="생존 위험 기준 (5.0)", annotation_position="bottom left")
    fig.update_layout(
        xaxis_title="월", yaxis_title=y_label,
        height=380, plot_bgcolor="white",
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.info("🌸 **봄철(3~4월)**: pH 최고치 — 플랑크톤 광합성으로 CO₂ 소비 → pH 급등")
        st.warning("☀️ **여름철(6~8월)**: DO 위기 — 수온 상승·유기물 분해로 산소 급감")
    with col_b:
        st.success("❄️ **겨울철(11~12월)**: DO 최고치 — 저수온에서 산소 용해도 최대")
        st.info("🔗 **pH·DO 상관계수**: 노량진 r=0.767 / 선유 r=0.648")

# ────────────────────────────────────────────────────────────
# TAB 2: 미래 예측 지도
# ────────────────────────────────────────────────────────────
with tab2:
    st.subheader("🗺️ 미래 수질 예측 — 측정소 위치 및 DO 등급")

    col_ctrl1, col_ctrl2 = st.columns(2)
    with col_ctrl1:
        scenario = st.selectbox(
            "기후 시나리오",
            ["SSP2-4.5 (중위 — 감축 지속)", "SSP5-8.5 (고위 — 현재 추세)"],
        )
        scen_key = "SSP245" if "SSP245" in scenario or "2-4.5" in scenario else "SSP585"
    with col_ctrl2:
        year = st.select_slider("예측 연도", options=[2026, 2030, 2040, 2050], value=2030)

    row = df_future[df_future["year"] == year].iloc[0]
    do_nry = row[f"{scen_key}_노량진_DO"]
    do_syu = row[f"{scen_key}_선유_DO"]
    ph_nry = row[f"{scen_key}_노량진_pH"]
    ph_syu = row[f"{scen_key}_선유_pH"]

    grade_nry, _ = do_grade(do_nry)
    grade_syu, _ = do_grade(do_syu)

    # 지도 생성
    m = folium.Map(location=[37.522, 126.906], zoom_start=13,
                   tiles="CartoDB positron")

    for name, info, do_val, ph_val, grade in [
        ("노량진", STATIONS["노량진"], do_nry, ph_nry, grade_nry),
        ("선유",   STATIONS["선유"],   do_syu, ph_syu, grade_syu),
    ]:
        color = do_color_hex(do_val)
        popup_html = f"""
        <div style='font-family:Arial; min-width:200px'>
            <h4 style='color:{color}; margin:0'>📍 {name} 측정소</h4>
            <hr style='margin:6px 0'>
            <b>예측 연도:</b> {year}년<br>
            <b>시나리오:</b> {"SSP2-4.5" if scen_key=="SSP245" else "SSP5-8.5"}<br>
            <hr style='margin:6px 0'>
            <b>DO:</b> <span style='color:{color}; font-size:16px'><b>{do_val:.2f} mg/L</b></span><br>
            <b>pH:</b> {ph_val:.3f}<br>
            <b>수질 등급:</b> {grade}
        </div>
        """
        radius = 18 + (do_val - 5) * 3  # DO 높을수록 크게
        folium.CircleMarker(
            location=[info["lat"], info["lon"]],
            radius=max(radius, 12),
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=f"{name}: DO {do_val:.2f} mg/L  |  {grade}"
        ).add_to(m)

        folium.Marker(
            location=[info["lat"] + 0.003, info["lon"]],
            icon=folium.DivIcon(html=f"""
                <div style='background:{color};color:white;padding:4px 8px;
                border-radius:6px;font-size:12px;font-weight:bold;
                box-shadow:0 2px 4px rgba(0,0,0,0.3);white-space:nowrap'>
                {name} {do_val:.1f}mg/L
                </div>""")
        ).add_to(m)

    # 한강 라인 추가
    hangang_line = [
        [37.513, 126.958], [37.515, 126.940], [37.516, 126.920],
        [37.518, 126.900], [37.523, 126.878], [37.528, 126.858]
    ]
    folium.PolyLine(hangang_line, color="#4A90D9", weight=8, opacity=0.4,
                    tooltip="한강").add_to(m)

    # 범례
    legend_html = """
    <div style='position:fixed; bottom:30px; left:30px; z-index:1000;
    background:white; padding:12px 16px; border-radius:10px;
    box-shadow:0 2px 8px rgba(0,0,0,0.2); font-family:Arial; font-size:13px'>
    <b>🎨 DO 등급 범례</b><br>
    <span style='color:#2ECC71'>●</span> 1등급 (≥7.5 mg/L)<br>
    <span style='color:#F39C12'>●</span> 2~3등급 (5.0~7.5)<br>
    <span style='color:#E67E22'>●</span> 4등급 (2.0~5.0)<br>
    <span style='color:#E74C3C'>●</span> 5등급 (&lt;2.0)
    </div>"""
    m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, width=None, height=500)

    # 수치 카드
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("노량진 DO", f"{do_nry:.2f} mg/L", delta=f"{do_nry-8.46:.2f} vs 2020")
    c2.metric("선유 DO",   f"{do_syu:.2f} mg/L", delta=f"{do_syu-8.26:.2f} vs 2020")
    c3.metric("노량진 pH", f"{ph_nry:.3f}", delta=f"{ph_nry-7.29:.3f} vs 2020")
    c4.metric("선유 pH",   f"{ph_syu:.3f}", delta=f"{ph_syu-7.32:.3f} vs 2020")

    if scen_key == "SSP585" and year >= 2040:
        st.error(f"🚨 **경고**: SSP5-8.5 {year}년 예측 DO가 생태계 위험 임계치(5.0 mg/L)에 근접! 민감 어종 서식 위협 가능")
    elif scen_key == "SSP585" and year == 2030:
        st.warning("⚠️ SSP5-8.5 시나리오에서 2030년 이후 DO 감소 추세 본격화 예상")
    else:
        st.success(f"✅ {year}년 {('SSP2-4.5' if scen_key=='SSP245' else 'SSP5-8.5')} 시나리오 — 현재까지 수질 관리 가능 범위")

# ────────────────────────────────────────────────────────────
# TAB 3: 예측 트렌드
# ────────────────────────────────────────────────────────────
with tab3:
    st.subheader("📈 시나리오별 DO 예측 트렌드 (2026~2050)")

    fig2 = make_subplots(rows=1, cols=2,
                         subplot_titles=["노량진 측정소", "선유 측정소"],
                         shared_yaxes=True)

    for col_idx, station in enumerate(["노량진", "선유"], start=1):
        fig2.add_trace(go.Scatter(
            x=df_future["year"],
            y=df_future[f"SSP245_{station}_DO"],
            name=f"SSP2-4.5 {station}",
            mode="lines+markers",
            line=dict(color="#1F77B4" if station=="노량진" else "#AEC6E8", width=3),
            marker=dict(size=9, symbol="circle"),
            legendgroup="SSP245"
        ), row=1, col=col_idx)

        fig2.add_trace(go.Scatter(
            x=df_future["year"],
            y=df_future[f"SSP585_{station}_DO"],
            name=f"SSP5-8.5 {station}",
            mode="lines+markers",
            line=dict(color="#D62728" if station=="노량진" else "#F5A0A0", width=3, dash="dot"),
            marker=dict(size=9, symbol="diamond"),
            legendgroup="SSP585"
        ), row=1, col=col_idx)

    # 기준선
    for col_idx in [1, 2]:
        fig2.add_hline(y=7.5, line_dash="dash", line_color="#2ECC71",
                       annotation_text="1등급 기준", row=1, col=col_idx)
        fig2.add_hline(y=5.0, line_dash="dash", line_color="#E74C3C",
                       annotation_text="위험 기준", row=1, col=col_idx)

    fig2.update_layout(height=420, plot_bgcolor="white",
                       yaxis_title="DO (mg/L)", legend=dict(orientation="h", y=-0.2))
    fig2.update_xaxes(tickvals=[2026, 2030, 2040, 2050])
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("시나리오별 2050년 예측 요약")
    summary_data = {
        "구분": ["SSP2-4.5 노량진", "SSP2-4.5 선유", "SSP5-8.5 노량진", "SSP5-8.5 선유"],
        "2026 DO": [8.26, 8.04, 8.11, 7.90],
        "2030 DO": [7.93, 7.73, 7.51, 7.31],
        "2040 DO": [7.43, 7.24, 6.51, 6.34],
        "2050 DO": [6.96, 6.77, 5.54, 5.37],
        "2050 등급": ["⚠️ 주의", "⚠️ 주의", "🚨 위험", "🚨 위험"],
    }
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("📋 6대 정책 제안 요약")
    policies = [
        ("🏭 단기 (2026~2030)", "폭기(曝氣) 시설 확충", "DO 최솟값 3.0 mg/L 이상 유지"),
        ("📡 단기 (2026~2030)", "실시간 모니터링 고도화", "DO 5mg/L 하회 6~12시간 전 예측"),
        ("🌧️ 단기 (2026~2030)", "초기 우수 저류조 설치", "강우 후 DO 급락 30~50% 완충"),
        ("🏗️ 중기 (2031~2040)", "하수처리장 고도화", "총인 50% 감소 → DO +1.0~1.5 mg/L"),
        ("🌿 중기 (2031~2040)", "생태습지·수변완충구역 확대", "수온 1~2°C 냉각, 질소 제거"),
        ("🌳 장기 (2041~2050)", "도시 열섬 완화·탄소 감축", "열섬 1°C 완화 → DO +0.1~0.16 mg/L"),
    ]
    for period, title, effect in policies:
        with st.expander(f"{period} — {title}"):
            st.write(f"**기대 효과:** {effect}")

    st.info("💡 **핵심 메시지**: 한강 수질은 지금 당장 위기는 아니지만, "
            "기후변화 속 여름철 취약성이 심화되고 있습니다. "
            "데이터 기반 예측과 선제적 정책이 한강의 미래를 결정합니다.")
