import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import DualMap
from streamlit_folium import st_folium
import plotly.graph_objects as go
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
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0; }

    /* 정책 카드 */
    .policy-card {
        background: white;
        border-radius: 14px;
        padding: 20px 18px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.10);
        height: 100%;
        border-top: 5px solid #ccc;
        transition: box-shadow 0.2s;
    }
    .policy-card.short  { border-top-color: #3498DB; }
    .policy-card.mid    { border-top-color: #2ECC71; }
    .policy-card.long   { border-top-color: #9B59B6; }

    .policy-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .badge-short { background:#EBF5FB; color:#3498DB; }
    .badge-mid   { background:#EAFAF1; color:#27AE60; }
    .badge-long  { background:#F5EEF8; color:#8E44AD; }

    .policy-title {
        font-size: 15px;
        font-weight: 700;
        color: #2C3E50;
        margin: 6px 0 4px 0;
    }
    .policy-effect {
        font-size: 13px;
        color: #555;
        margin-top: 8px;
        padding: 8px 10px;
        background: #F8F9FA;
        border-radius: 8px;
    }
    .policy-icon {
        font-size: 28px;
        margin-bottom: 4px;
    }
    .do-delta-pos { color: #27AE60; font-weight: 700; }
    .do-delta-neg { color: #E74C3C; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ── 측정소 위치 ───────────────────────────────────────────────
STATIONS = {
    "노량진": {"lat": 37.5110, "lon": 126.9333},
    "선유":   {"lat": 37.5330, "lon": 126.8780},
}

# ── 한강 라인 ────────────────────────────────────────────────
HANGANG = [
    [37.513, 126.958],[37.515, 126.940],[37.516, 126.920],
    [37.518, 126.900],[37.523, 126.878],[37.528, 126.858],
]

# ── 월별 데이터 ───────────────────────────────────────────────
MONTHLY = {
    "label": ["1월","2월","3월","4월","5월","6월","7월","8월","9월","10월","11월","12월"],
    "노량진_pH": [7.4,7.4,7.7,8.1,7.8,7.3,7.2,7.2,7.3,7.5,7.4,7.4],
    "선유_pH":   [7.4,7.4,7.8,8.2,7.9,7.3,7.2,7.1,7.3,7.5,7.4,7.4],
    "노량진_DO": [11.17,10.8,9.5,8.8,7.5,5.95,5.3,5.5,7.2,9.1,10.5,11.17],
    "선유_DO":   [10.91,10.5,9.2,8.5,7.2,5.51,4.9,5.2,6.9,8.8,10.2,10.91],
}

# ── 미래 예측 데이터 ──────────────────────────────────────────
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

# ── 정책 데이터 ───────────────────────────────────────────────
POLICIES = [
    {
        "phase": "단기",  "phase_label": "단기 (2026~2030)",
        "badge": "badge-short", "card": "short",
        "icon": "🌬️",
        "title": "폭기(曝氣) 시설 확충",
        "effect": "DO 최솟값 +2~4 mg/L 즉각 상승",
        "detail": "수중 산기관·폭기 선박 상시 운영으로 여름철 DO 급락 긴급 대응",
        "do_impact_nry": +2.5, "do_impact_syu": +2.0,
    },
    {
        "phase": "단기",  "phase_label": "단기 (2026~2030)",
        "badge": "badge-short", "card": "short",
        "icon": "📡",
        "title": "실시간 모니터링 고도화",
        "effect": "DO 위험 6~12시간 전 조기 경보",
        "detail": "AI 예측 모델 + IoT 센서망으로 10분 단위 수질 수집 및 자동 경보",
        "do_impact_nry": +0.3, "do_impact_syu": +0.3,
    },
    {
        "phase": "단기",  "phase_label": "단기 (2026~2030)",
        "badge": "badge-short", "card": "short",
        "icon": "🌧️",
        "title": "초기 우수 저류조 설치",
        "effect": "강우 후 DO 급락 30~50% 완충",
        "detail": "강변 초기 우수 저류조·투수성 포장재 확대로 도시 오염 유출 차단",
        "do_impact_nry": +0.8, "do_impact_syu": +1.2,
    },
    {
        "phase": "중기",  "phase_label": "중기 (2031~2040)",
        "badge": "badge-mid", "card": "mid",
        "icon": "🏭",
        "title": "하수처리장 고도화",
        "effect": "총인 50% 감소 → DO +1.0~1.5 mg/L",
        "detail": "중랑·탄천 처리장 고도처리(A²O, MBR) 도입, 방류수 총인 0.2mg/L 이하",
        "do_impact_nry": +1.2, "do_impact_syu": +1.5,
    },
    {
        "phase": "중기",  "phase_label": "중기 (2031~2040)",
        "badge": "badge-mid", "card": "mid",
        "icon": "🌿",
        "title": "생태습지·수변완충구역 확대",
        "effect": "수온 1~2°C 냉각, 질소 연간 최대 500kg/ha 제거",
        "detail": "한강변 정수식물 군락 복원, 수변 완충 녹지대(30m) 지정 및 생태공원 확대",
        "do_impact_nry": +0.6, "do_impact_syu": +0.9,
    },
    {
        "phase": "장기",  "phase_label": "장기 (2041~2050)",
        "badge": "badge-long", "card": "long",
        "icon": "🌳",
        "title": "도시 열섬 완화·탄소 감축",
        "effect": "열섬 1°C 완화 → DO +0.1~0.16 mg/L",
        "detail": "옥상 녹화·도시 숲·바람길 조성으로 서울 열섬 완화, 한강 수온을 기후정책 공식 지표 채택",
        "do_impact_nry": +0.5, "do_impact_syu": +0.4,
    },
]

# ── 헬퍼 ─────────────────────────────────────────────────────
def do_color(val):
    if val >= 7.5:   return "#2ECC71"
    elif val >= 5.0: return "#F39C12"
    elif val >= 2.0: return "#E67E22"
    else:            return "#E74C3C"

def do_grade_label(val):
    if val >= 7.5:   return "🟢 1등급"
    elif val >= 5.0: return "🟡 2~3등급"
    elif val >= 2.0: return "🟠 4등급"
    else:            return "🔴 5등급↓"

def build_map(center, do_nry, do_syu, ph_nry, ph_syu, year, label, policy_markers=None):
    """단일 Folium 지도 생성"""
    m = folium.Map(location=center, zoom_start=13, tiles="CartoDB positron")
    folium.PolyLine(HANGANG, color="#4A90D9", weight=8, opacity=0.35, tooltip="한강").add_to(m)

    for name, lat, lon, do_val, ph_val in [
        ("노량진", STATIONS["노량진"]["lat"], STATIONS["노량진"]["lon"], do_nry, ph_nry),
        ("선유",   STATIONS["선유"]["lat"],   STATIONS["선유"]["lon"],   do_syu, ph_syu),
    ]:
        color = do_color(do_val)
        grade = do_grade_label(do_val)
        popup_html = f"""
        <div style='font-family:Arial;min-width:190px'>
            <h4 style='color:{color};margin:0 0 6px 0'>📍 {name} 측정소</h4>
            <hr style='margin:4px 0'>
            <b>조건:</b> {label}<br>
            <b>연도:</b> {year}년<br>
            <hr style='margin:4px 0'>
            <b>DO:</b> <span style='color:{color};font-size:15px;font-weight:700'>{do_val:.2f} mg/L</span><br>
            <b>pH:</b> {ph_val:.3f}<br>
            <b>등급:</b> {grade}
        </div>"""
        folium.CircleMarker(
            location=[lat, lon],
            radius=max(14 + (do_val - 5) * 2.5, 10),
            color=color, fill=True, fill_color=color, fill_opacity=0.75,
            popup=folium.Popup(popup_html, max_width=240),
            tooltip=f"{name} | DO {do_val:.2f} mg/L | {grade}"
        ).add_to(m)
        folium.Marker(
            location=[lat + 0.0028, lon],
            icon=folium.DivIcon(html=f"""
                <div style='background:{color};color:white;padding:3px 8px;
                border-radius:6px;font-size:12px;font-weight:700;
                box-shadow:0 2px 5px rgba(0,0,0,0.25);white-space:nowrap'>
                {name} {do_val:.1f} mg/L</div>""")
        ).add_to(m)

    # 정책 시설 마커 (정책 실행 시)
    if policy_markers:
        for pm in policy_markers:
            folium.Marker(
                location=[pm["lat"], pm["lon"]],
                icon=folium.DivIcon(html=f"""
                    <div style='background:white;border:2px solid {pm["color"]};
                    color:{pm["color"]};padding:3px 7px;border-radius:8px;
                    font-size:11px;font-weight:700;
                    box-shadow:0 2px 5px rgba(0,0,0,0.2);white-space:nowrap'>
                    {pm["icon"]} {pm["label"]}</div>"""),
                tooltip=pm["label"]
            ).add_to(m)

    # 범례
    legend = f"""
    <div style='position:fixed;bottom:20px;left:20px;z-index:1000;
    background:white;padding:10px 14px;border-radius:10px;
    box-shadow:0 2px 8px rgba(0,0,0,0.18);font-family:Arial;font-size:12px'>
    <b>DO 등급</b><br>
    <span style='color:#2ECC71'>●</span> 1등급 ≥7.5<br>
    <span style='color:#F39C12'>●</span> 2~3등급 ≥5.0<br>
    <span style='color:#E67E22'>●</span> 4등급 ≥2.0<br>
    <span style='color:#E74C3C'>●</span> 5등급 &lt;2.0
    </div>"""
    m.get_root().html.add_child(folium.Element(legend))
    return m

# ════════════════════════════════════════════════════════════
# 헤더
# ════════════════════════════════════════════════════════════
st.title("💧 한강 수질 분석 대시보드")
st.caption("노량진·선유 측정소 | 2020년 실측 데이터 + IPCC 기후변화 시나리오 예측")
st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 현황 분석",
    "🗺️ 미래 예측 지도",
    "📈 예측 트렌드",
    "🏛️ 정책 효과 비교"
])

# ────────────────────────────────────────────────────────────
# TAB 1: 현황 분석
# ────────────────────────────────────────────────────────────
with tab1:
    st.subheader("2020년 연간 기초 통계")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("노량진 pH 연평균", "7.29", delta="범위 6.80~8.30")
    c2.metric("선유 pH 연평균",   "7.32", delta="범위 6.60~8.40")
    c3.metric("노량진 DO 연평균", "8.46 mg/L", delta="최솟값 2.1 mg/L", delta_color="inverse")
    c4.metric("선유 DO 연평균",   "8.26 mg/L", delta="최솟값 2.0 mg/L", delta_color="inverse")

    st.divider()
    st.subheader("월별 수질 변화 패턴")
    indicator = st.radio("지표 선택", ["DO (용존산소, mg/L)", "pH"], horizontal=True)
    key = "DO" if "DO" in indicator else "pH"

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_monthly["label"], y=df_monthly[f"노량진_{key}"],
        name="노량진", mode="lines+markers",
        line=dict(color="#1F77B4", width=3), marker=dict(size=8)))
    fig.add_trace(go.Scatter(x=df_monthly["label"], y=df_monthly[f"선유_{key}"],
        name="선유", mode="lines+markers",
        line=dict(color="#FF7F0E", width=3, dash="dot"), marker=dict(size=8)))
    if key == "DO":
        fig.add_hline(y=7.5, line_dash="dash", line_color="#2ECC71",
                      annotation_text="1등급 기준 (7.5)", annotation_position="top left")
        fig.add_hline(y=5.0, line_dash="dash", line_color="#E67E22",
                      annotation_text="생존 위험 기준 (5.0)", annotation_position="bottom left")
    fig.update_layout(xaxis_title="월", yaxis_title=key,
                      height=380, plot_bgcolor="white",
                      legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, use_container_width=True)

    ca, cb = st.columns(2)
    with ca:
        st.info("🌸 **봄철(3~4월)**: pH 최고치 — 플랑크톤 광합성으로 CO₂ 소비 → pH 급등")
        st.warning("☀️ **여름철(6~8월)**: DO 위기 — 수온 상승·유기물 분해로 산소 급감")
    with cb:
        st.success("❄️ **겨울철(11~12월)**: DO 최고치 — 저수온에서 산소 용해도 최대")
        st.info("🔗 **pH·DO 상관계수**: 노량진 r=0.767 / 선유 r=0.648")

# ────────────────────────────────────────────────────────────
# TAB 2: 미래 예측 지도
# ────────────────────────────────────────────────────────────
with tab2:
    st.subheader("🗺️ 미래 수질 예측 — 측정소 위치 및 DO 등급")
    cc1, cc2 = st.columns(2)
    with cc1:
        scenario = st.selectbox("기후 시나리오",
            ["SSP2-4.5 (중위 — 감축 지속)", "SSP5-8.5 (고위 — 현재 추세)"])
        scen_key = "SSP245" if "2-4.5" in scenario else "SSP585"
    with cc2:
        year = st.select_slider("예측 연도", options=[2026,2030,2040,2050], value=2030)

    row = df_future[df_future["year"] == year].iloc[0]
    do_nry = row[f"{scen_key}_노량진_DO"]
    do_syu = row[f"{scen_key}_선유_DO"]
    ph_nry = row[f"{scen_key}_노량진_pH"]
    ph_syu = row[f"{scen_key}_선유_pH"]

    scen_label = "SSP2-4.5" if scen_key == "SSP245" else "SSP5-8.5"
    m2 = build_map([37.522, 126.906], do_nry, do_syu, ph_nry, ph_syu, year, scen_label)
    st_folium(m2, width=None, height=480)

    st.divider()
    m1, m2_, m3_, m4_ = st.columns(4)
    m1.metric("노량진 DO", f"{do_nry:.2f} mg/L", delta=f"{do_nry-8.46:+.2f} vs 2020", delta_color="normal")
    m2_.metric("선유 DO",  f"{do_syu:.2f} mg/L", delta=f"{do_syu-8.26:+.2f} vs 2020", delta_color="normal")
    m3_.metric("노량진 pH", f"{ph_nry:.3f}", delta=f"{ph_nry-7.29:+.3f} vs 2020")
    m4_.metric("선유 pH",   f"{ph_syu:.3f}", delta=f"{ph_syu-7.32:+.3f} vs 2020")

    if scen_key == "SSP585" and year >= 2040:
        st.error(f"🚨 SSP5-8.5 {year}년: DO 위험 임계치(5.0 mg/L) 근접! 민감 어종 서식 위협")
    elif scen_key == "SSP585" and year >= 2030:
        st.warning("⚠️ SSP5-8.5 시나리오 — 2030년 이후 DO 감소 추세 본격화 예상")
    else:
        st.success(f"✅ {year}년 {scen_label} — 수질 관리 가능 범위")

# ────────────────────────────────────────────────────────────
# TAB 3: 예측 트렌드
# ────────────────────────────────────────────────────────────
with tab3:
    st.subheader("📈 시나리오별 DO 예측 트렌드 (2026~2050)")
    fig2 = make_subplots(rows=1, cols=2,
                         subplot_titles=["노량진 측정소", "선유 측정소"],
                         shared_yaxes=True)
    colors = {"SSP245": ("#1F77B4","#AEC6E8"), "SSP585": ("#D62728","#F5A0A0")}
    for ci, station in enumerate(["노량진","선유"], 1):
        for scen, (c1c, c2c) in colors.items():
            col_c = c1c if station=="노량진" else c2c
            fig2.add_trace(go.Scatter(
                x=df_future["year"], y=df_future[f"{scen}_{station}_DO"],
                name=f"{'SSP2-4.5' if scen=='SSP245' else 'SSP5-8.5'} {station}",
                mode="lines+markers",
                line=dict(color=col_c, width=3, dash="dot" if scen=="SSP585" else "solid"),
                marker=dict(size=9, symbol="diamond" if scen=="SSP585" else "circle"),
                legendgroup=scen
            ), row=1, col=ci)
    for ci in [1,2]:
        fig2.add_hline(y=7.5, line_dash="dash", line_color="#2ECC71",
                       annotation_text="1등급", row=1, col=ci)
        fig2.add_hline(y=5.0, line_dash="dash", line_color="#E74C3C",
                       annotation_text="위험", row=1, col=ci)
    fig2.update_layout(height=420, plot_bgcolor="white",
                       yaxis_title="DO (mg/L)", legend=dict(orientation="h", y=-0.2))
    fig2.update_xaxes(tickvals=[2026,2030,2040,2050])
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("시나리오별 2050년 예측 요약")
    st.dataframe(pd.DataFrame({
        "구분": ["SSP2-4.5 노량진","SSP2-4.5 선유","SSP5-8.5 노량진","SSP5-8.5 선유"],
        "2026": [8.26,8.04,8.11,7.90],
        "2030": [7.93,7.73,7.51,7.31],
        "2040": [7.43,7.24,6.51,6.34],
        "2050": [6.96,6.77,5.54,5.37],
        "2050 상태": ["⚠️ 주의","⚠️ 주의","🚨 위험","🚨 위험"],
    }), use_container_width=True, hide_index=True)

# ────────────────────────────────────────────────────────────
# TAB 4: 정책 효과 비교 (카드 + 비교 지도)
# ────────────────────────────────────────────────────────────
with tab4:

    # ── ① 6대 정책 카드 ────────────────────────────────────
    st.subheader("📋 6대 정책 제안")
    st.caption("각 카드를 확인하여 정책 상세 내용 및 DO 개선 효과를 확인하세요.")

    # 2행 3열 카드 레이아웃
    for row_idx in range(2):
        cols = st.columns(3, gap="medium")
        for col_idx in range(3):
            p = POLICIES[row_idx * 3 + col_idx]
            with cols[col_idx]:
                nry_str = f"+{p['do_impact_nry']:.1f}" if p['do_impact_nry'] >= 0 else f"{p['do_impact_nry']:.1f}"
                syu_str = f"+{p['do_impact_syu']:.1f}" if p['do_impact_syu'] >= 0 else f"{p['do_impact_syu']:.1f}"
                delta_class = "do-delta-pos"
                st.markdown(f"""
                <div class="policy-card {p['card']}">
                    <div class="policy-icon">{p['icon']}</div>
                    <span class="policy-badge {p['badge']}">{p['phase_label']}</span>
                    <div class="policy-title">{p['title']}</div>
                    <div style='font-size:12px;color:#777;margin-top:4px'>{p['detail']}</div>
                    <div class="policy-effect">
                        💡 {p['effect']}
                    </div>
                    <div style='margin-top:10px;font-size:12px;color:#555'>
                        DO 개선 효과<br>
                        <span class='{delta_class}'>노량진 {nry_str} mg/L</span> &nbsp;|&nbsp;
                        <span class='{delta_class}'>선유 {syu_str} mg/L</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    st.divider()

    # ── ② 정책 실행 전/후 비교 지도 ────────────────────────
    st.subheader("🗺️ 정책 실행 전 vs 후 — DO 수질 지도 비교")
    st.caption("정책을 선택하고 연도를 설정하면, 실행하지 않았을 때와 실행했을 때의 DO 변화를 지도로 비교합니다.")

    pc1, pc2, pc3 = st.columns([2, 2, 1])
    with pc1:
        selected_policies = st.multiselect(
            "적용할 정책 선택 (복수 선택 가능)",
            options=[p["title"] for p in POLICIES],
            default=["폭기(曝氣) 시설 확충", "하수처리장 고도화"],
        )
    with pc2:
        map_scenario = st.selectbox(
            "기후 시나리오",
            ["SSP5-8.5 (고위 — 현재 추세)", "SSP2-4.5 (중위 — 감축 지속)"],
            key="map_scen"
        )
        map_scen_key = "SSP585" if "SSP5-8.5" in map_scenario else "SSP245"
    with pc3:
        map_year = st.select_slider("예측 연도", options=[2026,2030,2040,2050], value=2040, key="map_year")

    # 기준 DO (정책 미실행)
    base_row = df_future[df_future["year"] == map_year].iloc[0]
    base_do_nry = base_row[f"{map_scen_key}_노량진_DO"]
    base_do_syu = base_row[f"{map_scen_key}_선유_DO"]
    base_ph_nry = base_row[f"{map_scen_key}_노량진_pH"]
    base_ph_syu = base_row[f"{map_scen_key}_선유_pH"]

    # 정책 적용 DO
    total_imp_nry = sum(p["do_impact_nry"] for p in POLICIES if p["title"] in selected_policies)
    total_imp_syu = sum(p["do_impact_syu"] for p in POLICIES if p["title"] in selected_policies)
    after_do_nry = min(base_do_nry + total_imp_nry, 12.0)
    after_do_syu = min(base_do_syu + total_imp_syu, 12.0)

    # 정책 시설 마커 정의
    policy_markers_map = {
        "폭기(曝氣) 시설 확충": [
            {"lat": 37.513, "lon": 126.920, "icon": "🌬️", "label": "폭기시설", "color": "#3498DB"},
            {"lat": 37.524, "lon": 126.888, "icon": "🌬️", "label": "폭기시설", "color": "#3498DB"},
        ],
        "실시간 모니터링 고도화": [
            {"lat": 37.516, "lon": 126.935, "icon": "📡", "label": "모니터링", "color": "#8E44AD"},
            {"lat": 37.526, "lon": 126.875, "icon": "📡", "label": "모니터링", "color": "#8E44AD"},
        ],
        "초기 우수 저류조 설치": [
            {"lat": 37.510, "lon": 126.930, "icon": "🌧️", "label": "저류조", "color": "#2980B9"},
            {"lat": 37.530, "lon": 126.870, "icon": "🌧️", "label": "저류조", "color": "#2980B9"},
        ],
        "하수처리장 고도화": [
            {"lat": 37.520, "lon": 126.960, "icon": "🏭", "label": "고도처리장", "color": "#27AE60"},
        ],
        "생태습지·수변완충구역 확대": [
            {"lat": 37.512, "lon": 126.910, "icon": "🌿", "label": "생태습지", "color": "#2ECC71"},
            {"lat": 37.528, "lon": 126.865, "icon": "🌿", "label": "생태습지", "color": "#2ECC71"},
        ],
        "도시 열섬 완화·탄소 감축": [
            {"lat": 37.516, "lon": 126.945, "icon": "🌳", "label": "도시숲", "color": "#1E8449"},
            {"lat": 37.522, "lon": 126.895, "icon": "🌳", "label": "도시숲", "color": "#1E8449"},
        ],
    }
    active_markers = []
    for title in selected_policies:
        active_markers.extend(policy_markers_map.get(title, []))

    # 개선량 표시
    imp_nry = after_do_nry - base_do_nry
    imp_syu = after_do_syu - base_do_syu
    scen_label2 = "SSP5-8.5" if map_scen_key=="SSP585" else "SSP2-4.5"

    st.markdown(f"""
    <div style='display:flex;gap:16px;margin:8px 0 12px 0'>
        <div style='flex:1;background:#FEF9E7;border-left:4px solid #F39C12;
        padding:10px 14px;border-radius:8px'>
            <b>📍 정책 미실행</b> | {scen_label2} {map_year}년<br>
            노량진 DO: <b style='color:{do_color(base_do_nry)}'>{base_do_nry:.2f} mg/L</b> &nbsp;
            선유 DO: <b style='color:{do_color(base_do_syu)}'>{base_do_syu:.2f} mg/L</b>
        </div>
        <div style='flex:1;background:#EAFAF1;border-left:4px solid #27AE60;
        padding:10px 14px;border-radius:8px'>
            <b>✅ 정책 실행 후</b> | 선택 정책 {len(selected_policies)}개 적용<br>
            노량진 DO: <b style='color:{do_color(after_do_nry)}'>{after_do_nry:.2f} mg/L</b>
            <span style='color:#27AE60;font-size:12px'>(+{imp_nry:.2f})</span> &nbsp;
            선유 DO: <b style='color:{do_color(after_do_syu)}'>{after_do_syu:.2f} mg/L</b>
            <span style='color:#27AE60;font-size:12px'>(+{imp_syu:.2f})</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    center = [37.522, 126.906]
    map_col1, map_col2 = st.columns(2)

    with map_col1:
        st.markdown("#### ❌ 정책 미실행")
        m_before = build_map(center, base_do_nry, base_do_syu,
                             base_ph_nry, base_ph_syu,
                             map_year, f"미실행 ({scen_label2})")
        st_folium(m_before, width=None, height=400, key="map_before")

    with map_col2:
        st.markdown("#### ✅ 정책 실행 후")
        m_after = build_map(center, after_do_nry, after_do_syu,
                            base_ph_nry, base_ph_syu,
                            map_year, f"실행 후 ({scen_label2})",
                            policy_markers=active_markers)
        st_folium(m_after, width=None, height=400, key="map_after")

    # 등급 변화 요약
    before_grade_nry = do_grade_label(base_do_nry)
    after_grade_nry  = do_grade_label(after_do_nry)
    before_grade_syu = do_grade_label(base_do_syu)
    after_grade_syu  = do_grade_label(after_do_syu)

    st.divider()
    st.markdown("#### 📊 수질 등급 변화 요약")
    sg1, sg2 = st.columns(2)
    with sg1:
        st.metric("노량진 DO", f"{after_do_nry:.2f} mg/L",
                  delta=f"+{imp_nry:.2f} mg/L",
                  help=f"미실행: {base_do_nry:.2f} → 실행 후: {after_do_nry:.2f}")
        st.caption(f"등급 변화: {before_grade_nry} → {after_grade_nry}")
    with sg2:
        st.metric("선유 DO", f"{after_do_syu:.2f} mg/L",
                  delta=f"+{imp_syu:.2f} mg/L",
                  help=f"미실행: {base_do_syu:.2f} → 실행 후: {after_do_syu:.2f}")
        st.caption(f"등급 변화: {before_grade_syu} → {after_grade_syu}")

    st.info("💡 **핵심 메시지**: 기후변화 속 여름철 DO 취약성이 심화되고 있습니다. "
            "단기 폭기시설·모니터링부터 장기 탄소감축까지 3단계 정책이 한강의 미래를 결정합니다.")
