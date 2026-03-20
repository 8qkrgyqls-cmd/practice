import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, csv
from collections import defaultdict
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="한강 수질 분석 · 2020–2050",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&display=swap');
* { font-family: 'Noto Sans KR', sans-serif !important; }
.block-container { padding: 1.5rem 2rem 3rem; max-width: 1400px; }

[data-testid="stExpander"] summary {
    display: flex !important; align-items: center !important; gap: 8px !important;
    padding: 12px 16px !important; font-size: 14px !important; font-weight: 600 !important;
    color: #1e293b !important; line-height: 1.4 !important;
}
[data-testid="stExpander"] summary p { margin: 0 !important; display: inline !important; }
[data-testid="stExpander"] summary svg { flex-shrink: 0 !important; margin-right: 4px !important; }
[data-testid="stExpander"] {
    border: 1px solid #e5e7eb !important; border-radius: 12px !important;
    margin-bottom: 10px !important; overflow: hidden !important;
}

.hero {
    background: linear-gradient(135deg, #0c1e3c 0%, #0f3460 55%, #16547a 100%);
    border-radius: 20px; padding: 40px 48px 36px;
    margin-bottom: 28px; position: relative; overflow: hidden;
}
.hero::before {
    content: ''; position: absolute; top: -40px; right: -40px;
    width: 260px; height: 260px; border-radius: 50%;
    background: rgba(255,255,255,0.04);
}
.hero-title { font-size: 30px; font-weight: 900; color: #fff; letter-spacing: -0.5px; margin: 0 0 8px; }
.hero-sub   { font-size: 14px; color: rgba(255,255,255,0.65); margin: 0; line-height: 1.6; }
.hero-tags  { margin-top: 18px; display: flex; gap: 8px; flex-wrap: wrap; }
.hero-tag {
    background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.2);
    color: rgba(255,255,255,0.85); border-radius: 20px; padding: 4px 14px;
    font-size: 12px; font-weight: 500;
}
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px; }
.kpi {
    background: #fff; border-radius: 14px; padding: 18px 20px 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06); border-top: 3px solid #2563eb;
}
.kpi.orange { border-top-color: #ea580c; }
.kpi.teal   { border-top-color: #0891b2; }
.kpi.amber  { border-top-color: #d97706; }
.kpi-label  { font-size: 11.5px; color: #6b7280; font-weight: 500; letter-spacing: 0.04em; margin-bottom: 6px; }
.kpi-value  { font-size: 28px; font-weight: 800; color: #111827; line-height: 1; }
.kpi-unit   { font-size: 13px; font-weight: 400; color: #6b7280; margin-left: 2px; }
.kpi-range  { font-size: 11px; color: #9ca3af; margin-top: 5px; }

.sec-hd {
    font-size: 16px; font-weight: 700; color: #0c1e3c;
    border-left: 4px solid #2563eb; padding-left: 12px;
    margin: 28px 0 14px;
}
.chart-wrap {
    background: #fff; border-radius: 16px; padding: 8px 12px 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 16px;
}
.ins-card {
    background: #fff; border-radius: 14px; padding: 20px 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 14px;
    border-left: 4px solid #e5e7eb;
}
.ins-card.blue   { border-left-color: #3b82f6; }
.ins-card.red    { border-left-color: #ef4444; }
.ins-card.green  { border-left-color: #22c55e; }
.ins-card.orange { border-left-color: #f97316; }
.ins-card.purple { border-left-color: #a855f7; }
.ins-card.indigo { border-left-color: #6366f1; }
.ins-card.teal   { border-left-color: #0891b2; }
.ins-card.rose   { border-left-color: #f43f5e; }
.ins-card.sky    { border-left-color: #0ea5e9; }
.ins-title { font-size: 14.5px; font-weight: 700; color: #1e293b; margin-bottom: 10px; }
.ins-body  { font-size: 13.5px; color: #374151; line-height: 1.85; }

.badge { display: inline-block; border-radius: 20px; padding: 2px 10px; font-size: 11.5px; font-weight: 600; margin: 0 2px; }
.b-blue   { background:#dbeafe; color:#1d4ed8; }
.b-red    { background:#fee2e2; color:#b91c1c; }
.b-green  { background:#dcfce7; color:#15803d; }
.b-orange { background:#ffedd5; color:#c2410c; }
.b-gray   { background:#f3f4f6; color:#374151; }
.b-purple { background:#f3e8ff; color:#7e22ce; }
.b-teal   { background:#ccfbf1; color:#0f766e; }
.b-sky    { background:#e0f2fe; color:#0369a1; }

.warn-box {
    background: #fef9c3; border: 1px solid #fde047; border-radius: 10px;
    padding: 12px 18px; font-size: 13px; color: #713f12; margin-bottom: 16px;
}
.grade-table { width:100%; border-collapse:collapse; font-size:13px; }
.grade-table th, .grade-table td { padding: 8px 12px; border: 1px solid #e5e7eb; text-align:left; }
.grade-table th { background: #f9fafb; font-weight: 600; color: #374151; }
.grade-table tr:nth-child(even) td { background: #f9fafb; }

/* ══════════════════════════════════════════════
   NEW: 수질 정책 섹션 전용 스타일
══════════════════════════════════════════════ */

/* 상단 인트로 배너 */
.policy-intro {
    background: linear-gradient(135deg, #0c1e3c 0%, #134e7a 100%);
    border-radius: 20px;
    padding: 36px 44px;
    margin-bottom: 40px;
    position: relative;
    overflow: hidden;
}
.policy-intro::after {
    content: '한강';
    position: absolute;
    right: -10px; top: -20px;
    font-size: 160px;
    font-weight: 900;
    color: rgba(255,255,255,0.04);
    line-height: 1;
    pointer-events: none;
}
.policy-intro-label {
    font-size: 11px; font-weight: 700; letter-spacing: 0.18em;
    color: #38bdf8; text-transform: uppercase; margin-bottom: 10px;
}
.policy-intro-title {
    font-size: 26px; font-weight: 900; color: #fff;
    line-height: 1.3; margin-bottom: 14px;
}
.policy-intro-body {
    font-size: 13.5px; color: rgba(255,255,255,0.65); line-height: 1.85; max-width: 680px;
}
.policy-intro-stats {
    display: flex; gap: 32px; margin-top: 24px; flex-wrap: wrap;
}
.policy-intro-stat-val {
    font-size: 28px; font-weight: 900; color: #fff; line-height: 1;
}
.policy-intro-stat-label {
    font-size: 11px; color: rgba(255,255,255,0.5); margin-top: 4px;
}

/* 페이즈 헤더 */
.phase-header {
    display: flex; align-items: center; gap: 14px;
    margin: 44px 0 20px;
}
.phase-pill {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 6px 16px; border-radius: 99px;
    font-size: 12px; font-weight: 700; letter-spacing: 0.04em;
}
.phase-pill.short { background: #dbeafe; color: #1d4ed8; }
.phase-pill.mid   { background: #dcfce7; color: #15803d; }
.phase-pill.long  { background: #f3e8ff; color: #7e22ce; }
.phase-line {
    flex: 1; height: 1px;
    background: linear-gradient(to right, #e5e7eb, transparent);
}
.phase-title {
    font-size: 17px; font-weight: 800; color: #0c1e3c;
}

/* 정책 카드 그리드 */
.pcard-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 12px;
}
.pcard-grid.two { grid-template-columns: repeat(2, 1fr); }

/* 개별 정책 카드 */
.pcard {
    background: #fff;
    border-radius: 16px;
    padding: 0;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    overflow: hidden;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
    cursor: default;
    position: relative;
}
.pcard:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 32px rgba(0,0,0,0.13);
}
.pcard-accent {
    height: 4px;
    width: 100%;
}
.pcard-inner {
    padding: 20px 22px 22px;
}
.pcard-icon-row {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 14px;
}
.pcard-icon {
    width: 44px; height: 44px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
}
.pcard-num {
    font-size: 11px; font-weight: 800; letter-spacing: 0.1em;
    color: #9ca3af;
}
.pcard-title {
    font-size: 14.5px; font-weight: 800; color: #111827;
    line-height: 1.4; margin-bottom: 10px;
}
.pcard-detail {
    font-size: 12.5px; color: #6b7280; line-height: 1.7;
    margin-bottom: 16px;
}
.pcard-divider {
    height: 1px; background: #f3f4f6; margin-bottom: 14px;
}
.pcard-effect-label {
    font-size: 10px; font-weight: 700; letter-spacing: 0.12em;
    color: #9ca3af; margin-bottom: 6px; text-transform: uppercase;
}
.pcard-effect {
    font-size: 13px; font-weight: 700; line-height: 1.5;
}
.pcard-do-row {
    display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap;
}
.pcard-do-chip {
    font-size: 11.5px; font-weight: 700;
    padding: 3px 10px; border-radius: 99px;
    background: #f0fdf4; color: #15803d;
}

/* 로드맵 타임라인 */
.roadmap-wrap {
    background: #f8fafc;
    border-radius: 18px;
    padding: 32px 36px;
    margin: 36px 0 28px;
    position: relative;
}
.roadmap-title {
    font-size: 13px; font-weight: 700; letter-spacing: 0.1em;
    color: #64748b; text-transform: uppercase; margin-bottom: 28px;
}
.roadmap-timeline {
    display: flex; gap: 0; position: relative;
}
.roadmap-timeline::before {
    content: '';
    position: absolute; top: 22px; left: 22px; right: 22px; height: 2px;
    background: linear-gradient(to right, #2563eb, #0891b2, #22c55e);
    z-index: 0;
}
.roadmap-phase {
    flex: 1; position: relative; z-index: 1; text-align: center; padding: 0 8px;
}
.roadmap-dot {
    width: 44px; height: 44px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; margin: 0 auto 12px;
    border: 3px solid white;
    box-shadow: 0 0 0 3px currentColor;
}
.roadmap-dot.short { background: #eff6ff; color: #2563eb; box-shadow: 0 0 0 3px #2563eb; }
.roadmap-dot.mid   { background: #f0fdfa; color: #0891b2; box-shadow: 0 0 0 3px #0891b2; }
.roadmap-dot.long  { background: #f0fdf4; color: #22c55e; box-shadow: 0 0 0 3px #22c55e; }
.roadmap-phase-label {
    font-size: 12px; font-weight: 800; margin-bottom: 4px;
}
.roadmap-phase-period {
    font-size: 11px; color: #94a3b8; margin-bottom: 10px;
}
.roadmap-items {
    display: flex; flex-direction: column; gap: 4px;
}
.roadmap-item {
    font-size: 11.5px; color: #475569;
    background: white; border-radius: 6px;
    padding: 4px 10px; text-align: left;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.roadmap-target {
    margin-top: 10px; font-size: 11px; font-weight: 700;
    padding: 4px 10px; border-radius: 6px; display: inline-block;
}
.roadmap-target.short { background: #dbeafe; color: #1d4ed8; }
.roadmap-target.mid   { background: #ccfbf1; color: #0f766e; }
.roadmap-target.long  { background: #dcfce7; color: #15803d; }

/* 지도 섹션 헤더 */
.map-section-hd {
    display: flex; align-items: center; gap: 12px;
    background: linear-gradient(135deg, #0f172a, #1e3a5f);
    border-radius: 14px; padding: 20px 24px; margin: 36px 0 20px;
}
.map-section-hd-icon { font-size: 28px; }
.map-section-hd-title { font-size: 17px; font-weight: 800; color: #fff; }
.map-section-hd-sub { font-size: 12.5px; color: rgba(255,255,255,0.55); margin-top: 2px; }
</style>
""", unsafe_allow_html=True)


# ── 지도용 상수 ───────────────────────────────────────────────────────────────
STATIONS = {
    "노량진": {"lat": 37.5110, "lon": 126.9333},
    "선유":   {"lat": 37.5330, "lon": 126.8780},
}
HANGANG = [
    [37.513, 126.958],[37.515, 126.940],[37.516, 126.920],
    [37.518, 126.900],[37.523, 126.878],[37.528, 126.858],
]

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

MAP_POLICIES = [
    {
        "phase": "단기", "phase_label": "단기 (2026~2030)",
        "icon": "🌬️", "title": "폭기(曝氣) 시설 확충",
        "effect": "DO 최솟값 +2~4 mg/L 즉각 상승",
        "detail": "수중 산기관·폭기 선박 상시 운영으로 여름철 DO 급락 긴급 대응",
        "do_impact_nry": 2.5, "do_impact_syu": 2.0,
    },
    {
        "phase": "단기", "phase_label": "단기 (2026~2030)",
        "icon": "📡", "title": "실시간 모니터링 고도화",
        "effect": "DO 위험 6~12시간 전 조기 경보",
        "detail": "AI 예측 모델 + IoT 센서망으로 10분 단위 수질 수집 및 자동 경보",
        "do_impact_nry": 0.3, "do_impact_syu": 0.3,
    },
    {
        "phase": "단기", "phase_label": "단기 (2026~2030)",
        "icon": "🌧️", "title": "초기 우수 저류조 설치",
        "effect": "강우 후 DO 급락 30~50% 완충",
        "detail": "강변 초기 우수 저류조·투수성 포장재 확대로 도시 오염 유출 차단",
        "do_impact_nry": 0.8, "do_impact_syu": 1.2,
    },
    {
        "phase": "중기", "phase_label": "중기 (2031~2040)",
        "icon": "🏭", "title": "하수처리장 고도화",
        "effect": "총인 50% 감소 → DO +1.0~1.5 mg/L",
        "detail": "중랑·탄천 처리장 고도처리(A²O, MBR) 도입, 방류수 총인 0.2mg/L 이하",
        "do_impact_nry": 1.2, "do_impact_syu": 1.5,
    },
    {
        "phase": "중기", "phase_label": "중기 (2031~2040)",
        "icon": "🌿", "title": "생태습지·수변완충구역 확대",
        "effect": "수온 1~2°C 냉각, 질소 최대 500kg/ha 제거",
        "detail": "한강변 정수식물 군락 복원, 수변 완충 녹지대(30m) 지정 및 생태공원 확대",
        "do_impact_nry": 0.6, "do_impact_syu": 0.9,
    },
    {
        "phase": "장기", "phase_label": "장기 (2041~2050)",
        "icon": "🌳", "title": "도시 열섬 완화·탄소 감축",
        "effect": "열섬 1°C 완화 → DO +0.1~0.16 mg/L",
        "detail": "옥상 녹화·도시 숲·바람길 조성으로 서울 열섬 완화, 한강 수온을 기후정책 공식 지표 채택",
        "do_impact_nry": 0.5, "do_impact_syu": 0.4,
    },
]

POLICY_MARKERS = {
    "폭기(曝氣) 시설 확충": [
        {"lat": 37.513, "lon": 126.920, "icon": "🌬️", "label": "폭기시설",  "color": "#3498DB"},
        {"lat": 37.524, "lon": 126.888, "icon": "🌬️", "label": "폭기시설",  "color": "#3498DB"},
    ],
    "실시간 모니터링 고도화": [
        {"lat": 37.516, "lon": 126.935, "icon": "📡",  "label": "모니터링", "color": "#8E44AD"},
        {"lat": 37.526, "lon": 126.875, "icon": "📡",  "label": "모니터링", "color": "#8E44AD"},
    ],
    "초기 우수 저류조 설치": [
        {"lat": 37.510, "lon": 126.930, "icon": "🌧️", "label": "저류조",   "color": "#2980B9"},
        {"lat": 37.530, "lon": 126.870, "icon": "🌧️", "label": "저류조",   "color": "#2980B9"},
    ],
    "하수처리장 고도화": [
        {"lat": 37.520, "lon": 126.960, "icon": "🏭",  "label": "고도처리장","color": "#27AE60"},
    ],
    "생태습지·수변완충구역 확대": [
        {"lat": 37.512, "lon": 126.910, "icon": "🌿",  "label": "생태습지", "color": "#2ECC71"},
        {"lat": 37.528, "lon": 126.865, "icon": "🌿",  "label": "생태습지", "color": "#2ECC71"},
    ],
    "도시 열섬 완화·탄소 감축": [
        {"lat": 37.516, "lon": 126.945, "icon": "🌳",  "label": "도시숲",   "color": "#1E8449"},
        {"lat": 37.522, "lon": 126.895, "icon": "🌳",  "label": "도시숲",   "color": "#1E8449"},
    ],
}

# 카드별 컬러 팔레트
PHASE_STYLES = {
    "단기": {
        "pill": "short",
        "accent": "linear-gradient(90deg,#2563eb,#3b82f6)",
        "icon_bg": "#eff6ff",
        "effect_color": "#1d4ed8",
        "do_chip_bg": "#dbeafe",
        "do_chip_color": "#1d4ed8",
    },
    "중기": {
        "pill": "mid",
        "accent": "linear-gradient(90deg,#059669,#10b981)",
        "icon_bg": "#f0fdf4",
        "effect_color": "#059669",
        "do_chip_bg": "#dcfce7",
        "do_chip_color": "#15803d",
    },
    "장기": {
        "pill": "long",
        "accent": "linear-gradient(90deg,#7c3aed,#a855f7)",
        "icon_bg": "#faf5ff",
        "effect_color": "#7c3aed",
        "do_chip_bg": "#f3e8ff",
        "do_chip_color": "#7e22ce",
    },
}


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
            <b>조건:</b> {label}<br><b>연도:</b> {year}년<br>
            <hr style='margin:4px 0'>
            <b>DO:</b> <span style='color:{color};font-size:15px;font-weight:700'>{do_val:.2f} mg/L</span><br>
            <b>pH:</b> {ph_val:.3f}<br><b>등급:</b> {grade}
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
    legend = """
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


@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    ph_candidates = [
        os.path.join(base, 'ph.csv'),
        os.path.join(base, '수소이온농도.csv'),
        os.path.join(base, 'data', '수소이온농도.csv'),
    ]
    do_candidates = [
        os.path.join(base, 'do.csv'),
        os.path.join(base, '용존산소.csv'),
        os.path.join(base, 'data', '용존산소.csv'),
    ]
    def find_file(candidates):
        for p in candidates:
            if os.path.exists(p): return p
        raise FileNotFoundError("데이터 파일을 찾을 수 없습니다.\nph.csv 와 do.csv 를 app.py 와 같은 폴더에 놓아 주세요.")
    def read_csv(path):
        for enc in ['utf-8', 'utf-8-sig', 'cp949', 'euc-kr']:
            try:
                rows = []
                with open(path, encoding=enc, errors='strict') as f:
                    reader = csv.DictReader(f)
                    if reader.fieldnames is None: continue
                    for row in reader: rows.append(row)
                if rows: return rows
            except Exception: continue
        raise ValueError(f"파일을 읽을 수 없습니다: {path}")
    def daily_means(rows, col):
        daily = defaultdict(list)
        for r in rows:
            v = r.get(col, '').strip()
            if v and v != '-':
                try: daily[r['일시'].split(' ')[0]].append(float(v))
                except Exception: pass
        return {d: round(sum(vs)/len(vs), 3) for d, vs in daily.items()}
    ph_rows = read_csv(find_file(ph_candidates))
    do_rows = read_csv(find_file(do_candidates))
    ph_ny = daily_means(ph_rows, '노량진'); ph_sy = daily_means(ph_rows, '선유')
    do_ny = daily_means(do_rows, '노량진'); do_sy = daily_means(do_rows, '선유')
    dates = sorted(set(list(ph_ny)+list(ph_sy)+list(do_ny)+list(do_sy)))
    return pd.DataFrame({
        'date': pd.to_datetime(dates),
        'pH_노량진': [ph_ny.get(d) for d in dates], 'pH_선유': [ph_sy.get(d) for d in dates],
        'DO_노량진': [do_ny.get(d) for d in dates], 'DO_선유': [do_sy.get(d) for d in dates],
    })

try:
    df = load_data()
except FileNotFoundError as e:
    st.error(f"📂 **파일을 찾을 수 없습니다**\n\n{e}"); st.stop()
except Exception as e:
    st.error(f"❌ **데이터 로드 오류**: {e}"); st.stop()


# ── Hero & KPI ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-title">🌊 한강 수질 분석 대시보드</div>
  <div class="hero-sub">
    노량진 · 선유 측정소 &nbsp;|&nbsp; 수소이온농도(pH) &amp; 용존산소(DO) 시간별 데이터 (2020년)<br>
    실측 데이터 기반 분석 및 기후변화 시나리오 적용 2050년 수질 예측
  </div>
  <div class="hero-tags">
    <span class="hero-tag">📅 2020.01.01 – 2020.12.31</span>
    <span class="hero-tag">📍 노량진 · 선유</span>
    <span class="hero-tag">⏱ 8,784 시간별 측정</span>
    <span class="hero-tag">🔮 2030 · 2040 · 2050 수질 예측</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="kpi-grid">
  <div class="kpi"><div class="kpi-label">pH 연평균 · 노량진</div><div class="kpi-value">7.29</div><div class="kpi-range">범위 6.80 ~ 8.30</div></div>
  <div class="kpi orange"><div class="kpi-label">pH 연평균 · 선유</div><div class="kpi-value">7.32</div><div class="kpi-range">범위 6.60 ~ 8.40</div></div>
  <div class="kpi teal"><div class="kpi-label">DO 연평균 · 노량진</div><div class="kpi-value">8.46<span class="kpi-unit"> mg/L</span></div><div class="kpi-range">범위 2.1 ~ 12.3</div></div>
  <div class="kpi amber"><div class="kpi-label">DO 연평균 · 선유</div><div class="kpi-value">8.26<span class="kpi-unit"> mg/L</span></div><div class="kpi-range">범위 2.0 ~ 12.5</div></div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 시계열 분석", "📅 월별 패턴", "🔗 상관관계",
    "🔬 수질 해석", "🔮 미래 예측", "📋 수질 정책",
])

COLORS = {'노량진_pH':'#2563eb','선유_pH':'#ea580c','노량진_DO':'#0891b2','선유_DO':'#d97706'}
MLBs = ['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월']


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1~5: 원본 코드 그대로 유지
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="sec-hd">날짜별 수질 시계열 — 범례 클릭으로 계열 선택</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 2, 2])
    with c1: view_mode = st.selectbox("표시 항목", ["pH + DO 동시", "pH만", "DO만"])
    with c2: stations = st.multiselect("측정 지점", ["노량진", "선유"], default=["노량진", "선유"])
    with c3:
        date_range = st.date_input("기간", value=(df['date'].min().date(), df['date'].max().date()),
                                   min_value=df['date'].min().date(), max_value=df['date'].max().date())
    if not stations: st.warning("측정 지점을 하나 이상 선택해 주세요."); st.stop()
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        mask = (df['date'].dt.date >= date_range[0]) & (df['date'].dt.date <= date_range[1])
        dff = df[mask].copy()
    else: dff = df.copy()
    show_ph = view_mode in ["pH + DO 동시", "pH만"]
    show_do = view_mode in ["pH + DO 동시", "DO만"]
    is_dual = show_ph and show_do
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.07,
                        subplot_titles=("수소이온농도 (pH)", "용존산소 (DO, mg/L)")) if is_dual else go.Figure()
    def add_line(fig, x, y, name, color, row=None):
        kw = dict(x=x, y=y, name=name, mode='lines', line=dict(color=color, width=1.8),
                  hovertemplate=f"<b>{name}</b><br>%{{x|%Y-%m-%d}}<br>%{{y:.3f}}<extra></extra>")
        fig.add_trace(go.Scatter(**kw), row=row, col=1) if row else fig.add_trace(go.Scatter(**kw))
    if show_ph:
        for s in stations: add_line(fig, dff['date'], dff[f'pH_{s}'], f'{s} pH', COLORS[f'{s}_pH'], row=1 if is_dual else None)
        ref = dict(line_dash='dot', line_color='rgba(100,100,100,0.5)', annotation_font_size=10)
        if is_dual:
            fig.add_hline(y=6.5, annotation_text='하한 6.5', row=1, col=1, **ref)
            fig.add_hline(y=8.5, annotation_text='상한 8.5', row=1, col=1, **ref)
        else:
            fig.add_hline(y=6.5, annotation_text='하한 6.5', **ref)
            fig.add_hline(y=8.5, annotation_text='상한 8.5', **ref)
    if show_do:
        for s in stations: add_line(fig, dff['date'], dff[f'DO_{s}'], f'{s} DO', COLORS[f'{s}_DO'], row=2 if is_dual else None)
        ref2 = dict(line_dash='dot', line_color='rgba(220,38,38,0.6)', annotation_text='생존 하한 5.0 mg/L',
                    annotation_font_color='#dc2626', annotation_font_size=10)
        if is_dual: fig.add_hline(y=5.0, row=2, col=1, **ref2)
        else: fig.add_hline(y=5.0, **ref2)
    fig.update_layout(height=520 if is_dual else 360, plot_bgcolor='white', paper_bgcolor='white',
                      margin=dict(l=10,r=10,t=36,b=10), hovermode='x unified',
                      legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(size=12)))
    fig.update_xaxes(showgrid=True, gridcolor='#f3f4f6', linecolor='#e5e7eb')
    fig.update_yaxes(showgrid=True, gridcolor='#f3f4f6', linecolor='#e5e7eb')
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':True,'modeBarButtonsToRemove':['lasso2d','select2d'],'displaylogo':False})
    st.markdown('</div>', unsafe_allow_html=True)
    st.caption("💡 범례 클릭: 계열 켜기/끄기  ·  드래그: 구간 확대  ·  더블클릭: 초기화")
    with st.expander("원시 데이터 보기 / CSV 다운로드"):
        cols_show = ['date'] + [f'pH_{s}' for s in stations] + [f'DO_{s}' for s in stations]
        disp = dff[cols_show].copy(); disp['date'] = disp['date'].dt.strftime('%Y-%m-%d')
        disp.columns = ['날짜'] + [f'pH ({s})' for s in stations] + [f'DO ({s}) mg/L' for s in stations]
        st.dataframe(disp, use_container_width=True, height=260)
        st.download_button("⬇️ CSV 다운로드", disp.to_csv(index=False).encode('utf-8-sig'), file_name="hangang_2020.csv", mime="text/csv")

with tab2:
    st.markdown('<div class="sec-hd">월별 평균 · 최솟값 · 최댓값 비교</div>', unsafe_allow_html=True)
    df['month'] = df['date'].dt.month
    monthly = df.groupby('month').agg(
        ph_ny_mean=('pH_노량진','mean'), ph_sy_mean=('pH_선유','mean'),
        ph_ny_min=('pH_노량진','min'),   ph_sy_min=('pH_선유','min'),
        ph_ny_max=('pH_노량진','max'),   ph_sy_max=('pH_선유','max'),
        do_ny_mean=('DO_노량진','mean'), do_sy_mean=('DO_선유','mean'),
        do_ny_min=('DO_노량진','min'),   do_sy_min=('DO_선유','min'),
        do_ny_max=('DO_노량진','max'),   do_sy_max=('DO_선유','max'),
    ).reset_index()
    subtab1, subtab2 = st.tabs(["pH 월별", "DO 월별"])
    def band_trace(x, hi, lo, color_hex, name):
        r,g,b = int(color_hex[1:3],16),int(color_hex[3:5],16),int(color_hex[5:7],16)
        return go.Scatter(x=x+x[::-1], y=list(hi)+list(lo)[::-1], fill='toself',
                          fillcolor=f'rgba({r},{g},{b},0.09)', line=dict(color='rgba(255,255,255,0)'), showlegend=False, name=name)
    with subtab1:
        fig_m = go.Figure()
        fig_m.add_trace(band_trace(MLBs, monthly['ph_ny_max'], monthly['ph_ny_min'], '#2563eb', '노량진 범위'))
        fig_m.add_trace(band_trace(MLBs, monthly['ph_sy_max'], monthly['ph_sy_min'], '#ea580c', '선유 범위'))
        fig_m.add_trace(go.Scatter(x=MLBs, y=monthly['ph_ny_mean'].round(3), name='노량진 평균', mode='lines+markers', line=dict(color='#2563eb', width=2.5), marker=dict(size=7)))
        fig_m.add_trace(go.Scatter(x=MLBs, y=monthly['ph_sy_mean'].round(3), name='선유 평균', mode='lines+markers', line=dict(color='#ea580c', width=2.5), marker=dict(size=7)))
        fig_m.add_hline(y=6.5, line_dash='dot', line_color='gray', annotation_text='환경부 하한 6.5', annotation_font_size=10)
        fig_m.add_hline(y=8.5, line_dash='dot', line_color='gray', annotation_text='환경부 상한 8.5', annotation_font_size=10)
        fig_m.update_layout(height=340, plot_bgcolor='white', paper_bgcolor='white', margin=dict(l=10,r=10,t=16,b=10), yaxis=dict(range=[6.0,9.2],title='pH'), legend=dict(orientation='h',y=1.08,xanchor='right',x=1))
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig_m, use_container_width=True, config={'displaylogo':False})
        st.markdown('</div>', unsafe_allow_html=True)
    with subtab2:
        fig_d = go.Figure()
        fig_d.add_trace(band_trace(MLBs, monthly['do_ny_max'], monthly['do_ny_min'], '#0891b2', '노량진 범위'))
        fig_d.add_trace(band_trace(MLBs, monthly['do_sy_max'], monthly['do_sy_min'], '#d97706', '선유 범위'))
        fig_d.add_trace(go.Scatter(x=MLBs, y=monthly['do_ny_mean'].round(3), name='노량진 평균', mode='lines+markers', line=dict(color='#0891b2', width=2.5), marker=dict(size=7)))
        fig_d.add_trace(go.Scatter(x=MLBs, y=monthly['do_sy_mean'].round(3), name='선유 평균', mode='lines+markers', line=dict(color='#d97706', width=2.5), marker=dict(size=7)))
        fig_d.add_hline(y=5.0, line_dash='dot', line_color='#dc2626', annotation_text='수생태계 위험 하한 5.0', annotation_font_color='#dc2626', annotation_font_size=10)
        fig_d.update_layout(height=340, plot_bgcolor='white', paper_bgcolor='white', margin=dict(l=10,r=10,t=16,b=10), yaxis=dict(range=[0,14],title='mg/L'), legend=dict(orientation='h',y=1.08,xanchor='right',x=1))
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig_d, use_container_width=True, config={'displaylogo':False})
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-hd">월별 상세 수치표</div>', unsafe_allow_html=True)
    tbl = pd.DataFrame({'월':MLBs,'pH 노량진 (평균)':monthly['ph_ny_mean'].round(2),'pH 선유 (평균)':monthly['ph_sy_mean'].round(2),
                        'DO 노량진 (평균)':monthly['do_ny_mean'].round(2),'DO 선유 (평균)':monthly['do_sy_mean'].round(2),
                        'DO 노량진 (최솟값)':monthly['do_ny_min'].round(2),'DO 선유 (최솟값)':monthly['do_sy_min'].round(2)})
    st.dataframe(tbl, use_container_width=True, hide_index=True)

with tab3:
    st.markdown('<div class="sec-hd">pH – DO 상관관계 분석</div>', unsafe_allow_html=True)
    fig_s = go.Figure(); corrs = {}
    for nm, pc, dc, clr in [('노량진','pH_노량진','DO_노량진','#2563eb'),('선유','pH_선유','DO_선유','#ea580c')]:
        tmp = df[[pc,dc,'date']].dropna()
        fig_s.add_trace(go.Scatter(x=tmp[pc], y=tmp[dc], mode='markers', name=nm, marker=dict(color=clr,size=5,opacity=0.45),
                                   hovertemplate=f"<b>{nm}</b><br>pH: %{{x:.3f}}<br>DO: %{{y:.3f}} mg/L<extra></extra>"))
        z = np.polyfit(tmp[pc], tmp[dc], 1); xr = np.linspace(tmp[pc].min(), tmp[pc].max(), 100)
        fig_s.add_trace(go.Scatter(x=xr, y=np.polyval(z,xr), mode='lines', name=f'{nm} 추세선', line=dict(color=clr,width=2,dash='dash')))
        corrs[nm] = tmp[[pc,dc]].corr().iloc[0,1]
    fig_s.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='white', margin=dict(l=10,r=10,t=10,b=10),
                        xaxis=dict(title='pH (일평균)',showgrid=True,gridcolor='#f3f4f6'),
                        yaxis=dict(title='DO mg/L (일평균)',showgrid=True,gridcolor='#f3f4f6'),
                        legend=dict(orientation='h',y=1.06,xanchor='right',x=1))
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.plotly_chart(fig_s, use_container_width=True, config={'displaylogo':False})
    st.markdown('</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.metric("노량진 피어슨 상관계수 (r)", f"{corrs['노량진']:.3f}", "강한 양의 상관")
    with c2: st.metric("선유 피어슨 상관계수 (r)", f"{corrs['선유']:.3f}", "중간-강한 양의 상관")
    st.markdown("""<div class="ins-card indigo"><div class="ins-title">상관관계가 의미하는 것</div>
      <div class="ins-body">두 지표가 함께 오르내리는 이유는 <b>공통 생물학적 원인</b> 때문입니다.<br><br>
        <b>봄 (3–4월):</b> 광합성 활발 → CO₂ 소비 → pH ↑ / O₂ 생산 → DO ↑<br>
        <b>여름 (6–8월):</b> 유기물 분해 → CO₂ 방출 → pH ↓ / O₂ 소비 → DO ↓<br><br>
        노량진(r=0.767)이 선유(r=0.648)보다 높은 이유는, 선유에서 퇴적물·유기물 등 국소 오염 인자가 DO를 추가로 낮춰 pH와의 연동을 희석시키기 때문입니다.
      </div></div>""", unsafe_allow_html=True)

with tab4:
    # ── 달력 전용 스타일 ──────────────────────────────────────────────────────
    st.markdown("""
    <style>
    /* 달력 외부 래퍼 */
    .cal-wrap {
        background: #fff;
        border-radius: 20px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.08);
        overflow: hidden;
        margin-bottom: 24px;
    }
    /* 달력 헤더 */
    .cal-header {
        background: linear-gradient(135deg, #0c1e3c, #1e4d7b);
        padding: 20px 28px 16px;
        display: flex; align-items: center; justify-content: space-between;
    }
    .cal-header-title {
        font-size: 18px; font-weight: 900; color: #fff; letter-spacing: -0.3px;
    }
    .cal-header-sub {
        font-size: 12px; color: rgba(255,255,255,0.55); margin-top: 3px;
    }
    .cal-legend {
        display: flex; gap: 12px; flex-wrap: wrap;
    }
    .cal-legend-item {
        display: flex; align-items: center; gap: 5px;
        font-size: 11px; color: rgba(255,255,255,0.75); font-weight: 600;
    }
    .cal-legend-dot {
        width: 10px; height: 10px; border-radius: 50%;
    }
    /* 달력 그리드 */
    .cal-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0;
    }
    /* 개별 월 셀 */
    .cal-month {
        padding: 18px 20px;
        border-right: 1px solid #f1f5f9;
        border-bottom: 1px solid #f1f5f9;
        transition: background 0.15s;
        cursor: default;
        position: relative;
    }
    .cal-month:hover { background: #f8fafc; }
    .cal-month:nth-child(4n) { border-right: none; }
    .cal-month:nth-child(n+9) { border-bottom: none; }

    /* 월 이름 */
    .cal-month-name {
        font-size: 11px; font-weight: 800; letter-spacing: 0.1em;
        text-transform: uppercase; color: #94a3b8; margin-bottom: 10px;
    }
    /* 수치 행 */
    .cal-vals {
        display: flex; flex-direction: column; gap: 6px; margin-bottom: 10px;
    }
    .cal-val-row {
        display: flex; align-items: center; justify-content: space-between;
    }
    .cal-val-label {
        font-size: 10.5px; color: #94a3b8; font-weight: 600;
    }
    .cal-val-num {
        font-size: 15px; font-weight: 900; line-height: 1;
    }
    .cal-val-unit {
        font-size: 9px; font-weight: 500; color: #94a3b8; margin-left: 1px;
    }
    /* DO 등급 바 */
    .cal-do-bar-wrap {
        height: 4px; background: #f1f5f9; border-radius: 99px; margin: 8px 0 6px;
        overflow: hidden;
    }
    .cal-do-bar {
        height: 100%; border-radius: 99px;
        transition: width 0.3s ease;
    }
    /* 이벤트 태그 */
    .cal-tag {
        display: inline-block;
        font-size: 10px; font-weight: 700;
        padding: 2px 7px; border-radius: 99px;
        margin-top: 4px;
    }
    /* 수직 구분선 (계절) */
    .cal-season-hd {
        grid-column: span 4;
        background: #f8fafc;
        padding: 8px 20px;
        font-size: 11px; font-weight: 800;
        color: #64748b; letter-spacing: 0.08em;
        border-bottom: 1px solid #f1f5f9;
        display: flex; align-items: center; gap: 8px;
    }
    /* 하단 인사이트 패널 */
    .cal-insight-grid {
        display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px;
        margin-top: 20px;
    }
    .cal-insight-card {
        border-radius: 14px; padding: 18px 20px;
        border-left: 4px solid #e5e7eb;
    }
    .cal-insight-card.spring { background: #fefce8; border-left-color: #eab308; }
    .cal-insight-card.summer { background: #fff1f2; border-left-color: #f43f5e; }
    .cal-insight-card.autumn { background: #fff7ed; border-left-color: #f97316; }
    .cal-insight-card.winter { background: #eff6ff; border-left-color: #3b82f6; }
    .cal-insight-title {
        font-size: 13px; font-weight: 800; color: #1e293b; margin-bottom: 8px;
    }
    .cal-insight-body {
        font-size: 12.5px; color: #475569; line-height: 1.75;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── 월별 실제 데이터 집계 ─────────────────────────────────────────────────
    df['month'] = df['date'].dt.month
    cal_monthly = df.groupby('month').agg(
        do_ny=('DO_노량진', 'mean'),
        do_sy=('DO_선유',   'mean'),
        ph_ny=('pH_노량진', 'mean'),
        ph_sy=('pH_선유',   'mean'),
        do_ny_min=('DO_노량진', 'min'),
        do_sy_min=('DO_선유',   'min'),
    ).reset_index()

    # 지점 선택
    t4_station = st.radio(
        "기준 측정소", ["노량진", "선유", "두 지점 평균"],
        horizontal=True, key="t4_station"
    )

    def get_do(row):
        if t4_station == "노량진":   return row['do_ny']
        elif t4_station == "선유":   return row['do_sy']
        else:                        return (row['do_ny'] + row['do_sy']) / 2

    def get_ph(row):
        if t4_station == "노량진":   return row['ph_ny']
        elif t4_station == "선유":   return row['ph_sy']
        else:                        return (row['ph_ny'] + row['ph_sy']) / 2

    def do_grade_color(v):
        if v >= 7.5:   return "#22c55e", "#dcfce7", "🟢 1등급", 100
        elif v >= 5.0: return "#f59e0b", "#fef3c7", "🟡 2~3등급", int((v-5)/2.5*100)
        elif v >= 2.0: return "#f97316", "#ffedd5", "🟠 4등급",   int((v-2)/3*100)
        else:           return "#ef4444", "#fee2e2", "🔴 5등급↓",  10

    def ph_color(v):
        if 7.0 <= v <= 8.0:   return "#2563eb"
        elif v > 8.0:          return "#7c3aed"
        else:                  return "#dc2626"

    MONTH_NAMES = ['','JAN','FEB','MAR','APR','MAY','JUN',
                   'JUL','AUG','SEP','OCT','NOV','DEC']
    MONTH_KO    = ['','1월','2월','3월','4월','5월','6월',
                   '7월','8월','9월','10월','11월','12월']

    # 계절별 이벤트 태그 정의
    EVENTS = {
        1:  ("❄️ DO 최고", "#dbeafe", "#1d4ed8"),
        2:  ("❄️ DO 안정", "#dbeafe", "#1d4ed8"),
        3:  ("🌸 pH 급등", "#fae8ff", "#9333ea"),
        4:  ("🌸 pH 최고", "#fae8ff", "#9333ea"),
        5:  ("⚠️ DO 하락", "#fef3c7", "#b45309"),
        6:  ("🚨 DO 위기", "#fee2e2", "#dc2626"),
        7:  ("🚨 DO 최저", "#fee2e2", "#dc2626"),
        8:  ("🚨 센서 결측", "#fee2e2", "#dc2626"),
        9:  ("🍂 DO 회복", "#ffedd5", "#c2410c"),
        10: ("✅ 1등급", "#dcfce7", "#15803d"),
        11: ("✅ 최적 환경", "#dcfce7", "#15803d"),
        12: ("❄️ DO 최고치", "#dbeafe", "#1d4ed8"),
    }

    SEASONS = [
        (1,  "❄️ 겨울", [1, 2]),
        (3,  "🌸 봄",   [3, 4, 5]),
        (6,  "☀️ 여름", [6, 7, 8]),
        (9,  "🍂 가을", [9, 10]),
        (11, "❄️ 초겨울", [11, 12]),
    ]

    # DO 최대값 (바 너비 계산용)
    do_max = 12.5

    # ── 달력 HTML 생성 ────────────────────────────────────────────────────────
    html = '<div class="cal-wrap">'

    # 헤더
    html += f"""
    <div class="cal-header">
        <div>
            <div class="cal-header-title">📅 2020 한강 수질 월별 달력</div>
            <div class="cal-header-sub">기준 측정소: {t4_station} · pH 및 DO(mg/L) 월평균</div>
        </div>
        <div class="cal-legend">
            <div class="cal-legend-item"><div class="cal-legend-dot" style="background:#22c55e"></div>1등급 ≥7.5</div>
            <div class="cal-legend-item"><div class="cal-legend-dot" style="background:#f59e0b"></div>2~3등급 ≥5.0</div>
            <div class="cal-legend-item"><div class="cal-legend-dot" style="background:#f97316"></div>4등급 ≥2.0</div>
            <div class="cal-legend-item"><div class="cal-legend-dot" style="background:#ef4444"></div>5등급↓</div>
        </div>
    </div>
    <div class="cal-grid">"""

    for _, row in cal_monthly.iterrows():
        m = int(row['month'])
        do_v = get_do(row)
        ph_v = get_ph(row)
        do_col, do_bg, grade_label, bar_pct = do_grade_color(do_v)
        ph_col = ph_color(ph_v)
        ev_label, ev_bg, ev_col = EVENTS.get(m, ("", "#f3f4f6", "#64748b"))
        bar_w = int(do_v / do_max * 100)

        html += f"""
        <div class="cal-month">
            <div class="cal-month-name">{MONTH_NAMES[m]} · {MONTH_KO[m]}</div>
            <div class="cal-vals">
                <div class="cal-val-row">
                    <span class="cal-val-label">DO</span>
                    <span>
                        <span class="cal-val-num" style="color:{do_col}">{do_v:.2f}</span>
                        <span class="cal-val-unit">mg/L</span>
                    </span>
                </div>
                <div class="cal-do-bar-wrap">
                    <div class="cal-do-bar" style="width:{bar_w}%;background:{do_col}"></div>
                </div>
                <div class="cal-val-row">
                    <span class="cal-val-label">pH</span>
                    <span>
                        <span class="cal-val-num" style="color:{ph_col}">{ph_v:.2f}</span>
                    </span>
                </div>
            </div>
            <span class="cal-tag" style="background:{ev_bg};color:{ev_col}">{ev_label}</span>
        </div>"""

    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

    # ── 계절별 인사이트 카드 ──────────────────────────────────────────────────
    st.markdown('<div class="sec-hd">계절별 수질 해석</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="cal-insight-grid">
        <div class="cal-insight-card spring">
            <div class="cal-insight-title">🌸 봄 (3–5월) — pH 급등 구간</div>
            <div class="cal-insight-body">
                수온 상승 → 플랑크톤 폭발 증식 → 광합성 왕성 → CO₂ 소비 → pH 상승의 연쇄.
                노량진 <b>8.3</b>, 선유 <b>8.4</b>로 연중 최고치를 기록합니다.
                봄철 오후 14–18시에 일중 pH 편차가 최대 <b>1.0 이상</b> 벌어집니다.
            </div>
        </div>
        <div class="cal-insight-card summer">
            <div class="cal-insight-title">☀️ 여름 (6–8월) — DO 위기 구간</div>
            <div class="cal-insight-body">
                노량진 6월 평균 DO <b>5.95 mg/L</b>, 선유 <b>5.51 mg/L</b>로 급락.
                순간 최솟값 노량진 <b>2.1</b>, 선유 <b>2.0 mg/L</b>.
                수온 상승 → 산소 용해도 감소(20°C: 9.1 → 30°C: 7.5 mg/L).
                플랑크톤 사체 분해 시 박테리아 대량 산소 소비가 복합적으로 작용합니다.
                8월 선유 센서 결측률 <b>58%</b> 주의.
            </div>
        </div>
        <div class="cal-insight-card autumn">
            <div class="cal-insight-title">🍂 가을 (9–10월) — 회복 구간</div>
            <div class="cal-insight-body">
                수온 하강 → DO 서서히 회복. 10월부터 DO ≥ 7.5 mg/L 달성,
                환경부 <b>1등급</b> 수준으로 회복됩니다.
                pH도 7.4–7.5로 중성 범위에 안정되며 수생태계에 쾌적한 환경입니다.
            </div>
        </div>
        <div class="cal-insight-card winter">
            <div class="cal-insight-title">❄️ 겨울 (11–12월) — DO 최고 구간</div>
            <div class="cal-insight-body">
                노량진 12월 평균 <b>11.17 mg/L</b>, 선유 <b>10.91 mg/L</b>로 연중 최고.
                저수온일수록 기체 용해도가 높아져 DO가 포화 상태를 유지합니다.
                pH는 7.4–7.5로 가장 안정적이며, 연중 수질이 가장 쾌적한 시기입니다.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 환경부 등급 요약 ──────────────────────────────────────────────────────
    st.markdown('<div class="sec-hd" style="margin-top:24px">환경부 수질 등급 기준 대조</div>',
                unsafe_allow_html=True)

    grade_cols = st.columns(4)
    grades = [
        ("🟢 1등급", "매우 좋음", "DO ≥ 7.5", "pH 6.5–8.5", "상수원·자연보전", "10월–4월", "#dcfce7", "#15803d"),
        ("🟡 2~3등급", "좋음·보통", "DO ≥ 5.0", "pH 6.5–8.5", "정수처리·농업용수", "봄·가을", "#fef3c7", "#b45309"),
        ("🟠 4등급", "나쁨", "DO ≥ 2.0", "pH 6.0–8.5", "공업용수", "여름 순간값", "#ffedd5", "#c2410c"),
        ("🔴 5등급↓", "매우 나쁨", "DO < 2.0", "pH <6.0 or >8.5", "용도 제한", "극한 상황", "#fee2e2", "#b91c1c"),
    ]
    for col, (grade, status, do_crit, ph_crit, use, when, bg, fc) in zip(grade_cols, grades):
        with col:
            st.markdown(f"""
            <div style="background:{bg};border-radius:12px;padding:16px 18px;height:100%">
                <div style="font-size:16px;font-weight:900;color:{fc};margin-bottom:4px">{grade}</div>
                <div style="font-size:11px;font-weight:700;color:{fc};margin-bottom:10px;opacity:0.8">{status}</div>
                <div style="font-size:12px;color:#374151;line-height:1.8">
                    <b>DO:</b> {do_crit}<br>
                    <b>pH:</b> {ph_crit}<br>
                    <b>용도:</b> {use}<br>
                    <b>2020 한강:</b> {when}
                </div>
            </div>
            """, unsafe_allow_html=True)

with tab5:
    st.markdown('<div class="sec-hd">2026–2050 수질 예측 (기후변화 시나리오)</div>', unsafe_allow_html=True)
    st.markdown("""<div class="warn-box">⚠️ <b>예측 모델 안내</b>: 2020년 실측 데이터를 기반으로 기후변화 시나리오(IPCC SSP2-4.5, SSP5-8.5)를
    적용한 통계적 외삽 모델입니다. 실제 수질은 정책·인프라·강수량 변동에 따라 달라질 수 있습니다.</div>""", unsafe_allow_html=True)
    SCENARIOS = {
        'SSP2-4.5 (중위 시나리오)': {'dash':'solid','temp_2050':1.5,'do_per_c':0.20,'summer_penalty':0.08,'ph_per_yr':-0.002},
        'SSP5-8.5 (고위 시나리오)': {'dash':'dash', 'temp_2050':3.0,'do_per_c':0.22,'summer_penalty':0.18,'ph_per_yr':-0.005},
    }
    BASE = {'do_ny':8.463,'do_sy':8.260,'ph_ny':7.287,'ph_sy':7.317}
    future_years = np.arange(2020, 2051)
    def forecast(base, sc, kind='do'):
        vals, noises = [], []
        for y in future_years:
            n, frac = y-2020, (y-2020)/30
            if kind=='do': val = base - sc['do_per_c']*sc['temp_2050']*frac - sc['summer_penalty']*frac; noise = 0.3+0.5*frac
            else: val = base + sc['ph_per_yr']*n; noise = 0.05+0.1*frac
            vals.append(val); noises.append(noise)
        return np.array(vals), np.array(noises)
    def make_band(years, vals, noise, hex_color, label):
        r,g,b = int(hex_color[1:3],16),int(hex_color[3:5],16),int(hex_color[5:7],16)
        band = go.Scatter(x=list(years)+list(years[::-1]), y=list(vals+noise)+list((vals-noise)[::-1]),
                          fill='toself', fillcolor=f'rgba({r},{g},{b},0.10)', line=dict(color='rgba(255,255,255,0)'), showlegend=False, name=f'{label} 불확실도')
        line = go.Scatter(x=years, y=np.round(vals,3), name=f'{label} 예측', mode='lines', line=dict(color=hex_color, width=2.2))
        return band, line
    sc_name = st.selectbox("시나리오 선택", list(SCENARIOS.keys()), key='sc_sel')
    sc = SCENARIOS[sc_name]
    do_ny_v,do_ny_n = forecast(BASE['do_ny'],sc,'do'); do_sy_v,do_sy_n = forecast(BASE['do_sy'],sc,'do')
    ph_ny_v,ph_ny_n = forecast(BASE['ph_ny'],sc,'ph'); ph_sy_v,ph_sy_n = forecast(BASE['ph_sy'],sc,'ph')
    st.markdown('<div class="sec-hd">2030 · 2040 · 2050 예측 수치 한눈에 보기</div>', unsafe_allow_html=True)
    highlight_years = [2026,2030,2040,2050]; h_idxs = [y-2020 for y in highlight_years]
    col_cards = st.columns(4)
    for i,(yr,idx) in enumerate(zip(highlight_years,h_idxs)):
        do_n=do_ny_v[idx]; do_s=do_sy_v[idx]; ph_n=ph_ny_v[idx]; ph_s=ph_sy_v[idx]
        warn=do_n<6.0 or do_s<6.0; danger=do_n<5.0 or do_s<5.0
        state='🚨 위험' if danger else ('⚠️ 주의' if warn else '✅ 양호')
        top_color='#dc2626' if danger else ('#f97316' if warn else '#22c55e')
        with col_cards[i]:
            st.markdown(f"""<div style="background:#fff;border-radius:14px;padding:18px 16px;box-shadow:0 2px 8px rgba(0,0,0,0.07);border-top:3px solid {top_color};text-align:center;">
              <div style="font-size:22px;font-weight:900;color:#0c1e3c;margin-bottom:4px;">{yr}년</div>
              <div style="font-size:12px;color:#6b7280;margin-bottom:12px;font-weight:500;">{state}</div>
              <div style="font-size:12px;color:#374151;line-height:1.9;text-align:left;">DO 노량진 <b>{do_n:.2f}</b> mg/L<br>DO 선유&nbsp;&nbsp;&nbsp;<b>{do_s:.2f}</b> mg/L<br>pH 노량진 <b>{ph_n:.3f}</b><br>pH 선유&nbsp;&nbsp;&nbsp;<b>{ph_s:.3f}</b></div>
            </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    pred_tabs = st.tabs(["용존산소 (DO) 예측", "수소이온농도 (pH) 예측"])
    milestone_yrs = [2030,2040,2050]
    with pred_tabs[0]:
        fig_f = go.Figure()
        b1,l1 = make_band(future_years,do_ny_v,do_ny_n,'#2563eb','노량진')
        b2,l2 = make_band(future_years,do_sy_v,do_sy_n,'#d97706','선유')
        fig_f.add_traces([b1,b2,l1,l2])
        fig_f.add_trace(go.Scatter(x=[2020],y=[BASE['do_ny']],mode='markers',name='노량진 실측(2020)',marker=dict(color='#2563eb',size=10)))
        fig_f.add_trace(go.Scatter(x=[2020],y=[BASE['do_sy']],mode='markers',name='선유 실측(2020)',marker=dict(color='#d97706',size=10)))
        for yr in milestone_yrs:
            idx=yr-2020
            fig_f.add_trace(go.Scatter(x=[yr,yr],y=[do_ny_v[idx],do_sy_v[idx]],mode='markers+text',
                marker=dict(color=['#2563eb','#d97706'],size=10,symbol='diamond'),
                text=[f"{do_ny_v[idx]:.2f}",f"{do_sy_v[idx]:.2f}"],textposition='top center',textfont=dict(size=10),showlegend=False,name=f'{yr}년'))
        fig_f.add_hline(y=5.0,line_dash='dot',line_color='#dc2626',annotation_text='수생태계 위험 하한 5.0',annotation_font_color='#dc2626')
        fig_f.add_hline(y=7.5,line_dash='dot',line_color='#16a34a',annotation_text='1등급 기준 7.5',annotation_font_color='#16a34a')
        fig_f.add_vline(x=2026,line_dash='dot',line_color='#6b7280',annotation_text='현재(2026)',annotation_font_size=11)
        for yr in milestone_yrs:
            fig_f.add_vline(x=yr,line_dash='dot',line_color='rgba(150,150,150,0.3)',annotation_text=str(yr),annotation_font_size=10,annotation_font_color='#9ca3af')
        fig_f.update_layout(height=440,plot_bgcolor='white',paper_bgcolor='white',margin=dict(l=10,r=10,t=10,b=10),
                            xaxis=dict(title='연도',showgrid=True,gridcolor='#f3f4f6'),
                            yaxis=dict(title='DO (mg/L)',range=[3.0,13.0],showgrid=True,gridcolor='#f3f4f6'),
                            legend=dict(orientation='h',y=1.06,xanchor='right',x=1))
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig_f, use_container_width=True, config={'displaylogo':False})
        st.markdown('</div>', unsafe_allow_html=True)
    with pred_tabs[1]:
        fig_fp = go.Figure()
        b3,l3 = make_band(future_years,ph_ny_v,ph_ny_n,'#2563eb','노량진')
        b4,l4 = make_band(future_years,ph_sy_v,ph_sy_n,'#d97706','선유')
        fig_fp.add_traces([b3,b4,l3,l4])
        fig_fp.add_trace(go.Scatter(x=[2020],y=[BASE['ph_ny']],mode='markers',name='노량진 실측(2020)',marker=dict(color='#2563eb',size=10)))
        fig_fp.add_trace(go.Scatter(x=[2020],y=[BASE['ph_sy']],mode='markers',name='선유 실측(2020)',marker=dict(color='#d97706',size=10)))
        for yr in milestone_yrs:
            idx=yr-2020
            fig_fp.add_trace(go.Scatter(x=[yr,yr],y=[ph_ny_v[idx],ph_sy_v[idx]],mode='markers+text',
                marker=dict(color=['#2563eb','#d97706'],size=10,symbol='diamond'),
                text=[f"{ph_ny_v[idx]:.3f}",f"{ph_sy_v[idx]:.3f}"],textposition='top center',textfont=dict(size=10),showlegend=False,name=f'{yr}년'))
        fig_fp.add_hline(y=6.5,line_dash='dot',line_color='#dc2626',annotation_text='환경부 하한 6.5')
        fig_fp.add_hline(y=8.5,line_dash='dot',line_color='gray',annotation_text='환경부 상한 8.5')
        fig_fp.add_vline(x=2026,line_dash='dot',line_color='#6b7280',annotation_text='현재(2026)',annotation_font_size=11)
        for yr in milestone_yrs:
            fig_fp.add_vline(x=yr,line_dash='dot',line_color='rgba(150,150,150,0.3)',annotation_text=str(yr),annotation_font_size=10,annotation_font_color='#9ca3af')
        fig_fp.update_layout(height=440,plot_bgcolor='white',paper_bgcolor='white',margin=dict(l=10,r=10,t=10,b=10),
                             xaxis=dict(title='연도',showgrid=True,gridcolor='#f3f4f6'),
                             yaxis=dict(title='pH',range=[6.0,9.0],showgrid=True,gridcolor='#f3f4f6'),
                             legend=dict(orientation='h',y=1.06,xanchor='right',x=1))
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig_fp, use_container_width=True, config={'displaylogo':False})
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-hd">전체 연도별 예측 수치표</div>', unsafe_allow_html=True)
    all_miles=[2026,2030,2035,2040,2045,2050]; all_idxs=[y-2020 for y in all_miles]
    pred_tbl = pd.DataFrame({'연도':all_miles,'DO 노량진 (mg/L)':[f"{do_ny_v[i]:.2f}" for i in all_idxs],
        'DO 선유 (mg/L)':[f"{do_sy_v[i]:.2f}" for i in all_idxs],'pH 노량진':[f"{ph_ny_v[i]:.3f}" for i in all_idxs],
        'pH 선유':[f"{ph_sy_v[i]:.3f}" for i in all_idxs],
        '수생태계 상태':['🚨 위험' if do_ny_v[i]<5.0 or do_sy_v[i]<5.0 else ('⚠️ 주의' if do_ny_v[i]<6.5 or do_sy_v[i]<6.5 else '✅ 양호') for i in all_idxs]})
    st.dataframe(pred_tbl, use_container_width=True, hide_index=True)
    st.markdown('<div class="sec-hd">시나리오 해설</div>', unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca:
        st.markdown("""<div class="ins-card blue"><div class="ins-title">SSP2-4.5 — 중위 시나리오</div>
          <div class="ins-body">온실가스 감축 정책 지속 경로. 2050년 기온 <b>+1.5°C</b> 상승 예상.<br><br>
          2030: DO 노량진 ~8.1, 선유 ~7.9 mg/L<br>2040: DO 노량진 ~7.7, 선유 ~7.5 mg/L<br>2050: DO 노량진 ~7.3, 선유 ~7.1 mg/L</div></div>""", unsafe_allow_html=True)
    with cb:
        st.markdown("""<div class="ins-card red"><div class="ins-title">SSP5-8.5 — 고위 시나리오</div>
          <div class="ins-body">현재 추세 지속 최악 경로. 2050년 기온 <b>+3.0°C</b> 상승 예상.<br><br>
          2030: DO 노량진 ~7.7, 선유 ~7.5 mg/L<br>2040: DO 노량진 ~7.1, 선유 ~6.9 mg/L<br>2050: DO 노량진 ~6.5, 선유 ~6.3 mg/L</div></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="ins-card purple"><div class="ins-title">예측 모델 방법론 및 한계</div>
      <div class="ins-body"><b>기준 데이터:</b> 2020년 노량진·선유 시간별 실측값 (n=8,784)<br>
      <b>DO 예측:</b> Henry's Law + 도시 비점오염 증가 보정<br>
      <b>pH 예측:</b> 대기 CO₂ 농도 증가(420→500–600 ppm) 탄산 평형 계산<br>
      <b>불확실도:</b> 단기 ±0.3 → 2050년 ±0.8 mg/L<br><br>
      <span class="badge b-orange">한계점</span> 단일 연도 기반 외삽이므로 장기 정책 효과나 기상 이변은 반영되지 않습니다.</div></div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 : 수질 정책 — 새 디자인
# ═══════════════════════════════════════════════════════════════════════════════
with tab6:

    # ── ① 인트로 배너 ─────────────────────────────────────────────────────────
    st.markdown("""
    <div class="policy-intro">
        <div class="policy-intro-label">Action Plan · 2026 – 2050</div>
        <div class="policy-intro-title">한강을 지키는<br>6가지 핵심 정책</div>
        <div class="policy-intro-body">
            2020년 실측 데이터는 여름철 DO가 수생태계 위험 기준(5 mg/L)에 근접하거나 하회하는 구간이
            반복됨을 보여줍니다. 기후변화 SSP5-8.5 경로가 지속되면 2050년 한강 생태계의 구조적 붕괴가
            우려됩니다. 단기 즉각 대응부터 장기 구조 전환까지, 3단계 로드맵이 필요합니다.
        </div>
        <div class="policy-intro-stats">
            <div>
                <div class="policy-intro-stat-val">2.1</div>
                <div class="policy-intro-stat-label">mg/L · 2020 여름 DO 최솟값</div>
            </div>
            <div>
                <div class="policy-intro-stat-val">5.54</div>
                <div class="policy-intro-stat-label">mg/L · SSP5-8.5 2050 예측</div>
            </div>
            <div>
                <div class="policy-intro-stat-val">6개</div>
                <div class="policy-intro-stat-label">단계별 핵심 정책</div>
            </div>
            <div>
                <div class="policy-intro-stat-val">25년</div>
                <div class="policy-intro-stat-label">정책 로드맵 기간</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── ② 정책 카드 — 페이즈별 ────────────────────────────────────────────────
    phases = [
        {
            "key": "단기", "label": "단기 집중 대응", "period": "2026 – 2030",
            "pill": "short", "dot": "short", "emoji": "⚡",
            "target": "DO 최솟값 3.0 mg/L 이상 유지",
        },
        {
            "key": "중기", "label": "구조적 수질 개선", "period": "2031 – 2040",
            "pill": "mid", "dot": "mid", "emoji": "🔧",
            "target": "DO 연평균 8.0 mg/L 이상 유지",
        },
        {
            "key": "장기", "label": "기후 구조 전환", "period": "2041 – 2050",
            "pill": "long", "dot": "long", "emoji": "🌍",
            "target": "1등급 수질 연중 60% 이상",
        },
    ]

    for phase in phases:
        phase_policies = [p for p in MAP_POLICIES if p["phase"] == phase["key"]]
        st_obj = PHASE_STYLES[phase["key"]]
        n = len(phase_policies)
        grid_class = "pcard-grid" if n == 3 else "pcard-grid two"

        # 페이즈 헤더
        st.markdown(f"""
        <div class="phase-header">
            <span class="phase-pill {st_obj['pill']}">{phase['emoji']} {phase['label']}</span>
            <span style="font-size:12px;color:#94a3b8;font-weight:600">{phase['period']}</span>
            <div class="phase-line"></div>
            <span style="font-size:11.5px;color:#64748b;background:#f1f5f9;
            padding:4px 12px;border-radius:99px;white-space:nowrap">🎯 {phase['target']}</span>
        </div>
        """, unsafe_allow_html=True)

        # 카드 HTML 생성
        cards_html = f'<div class="{grid_class}">'
        for i, p in enumerate(phase_policies, 1):
            global_num = MAP_POLICIES.index(p) + 1
            nry_str = f"+{p['do_impact_nry']:.1f}"
            syu_str = f"+{p['do_impact_syu']:.1f}"
            cards_html += f"""
            <div class="pcard">
                <div class="pcard-accent" style="background:{st_obj['accent']}"></div>
                <div class="pcard-inner">
                    <div class="pcard-icon-row">
                        <div class="pcard-icon" style="background:{st_obj['icon_bg']}">{p['icon']}</div>
                        <span class="pcard-num">POLICY {global_num:02d}</span>
                    </div>
                    <div class="pcard-title">{p['title']}</div>
                    <div class="pcard-detail">{p['detail']}</div>
                    <div class="pcard-divider"></div>
                    <div class="pcard-effect-label">기대 효과</div>
                    <div class="pcard-effect" style="color:{st_obj['effect_color']}">{p['effect']}</div>
                    <div class="pcard-do-row">
                        <span class="pcard-do-chip" style="background:{st_obj['do_chip_bg']};color:{st_obj['do_chip_color']}">
                            노량진 {nry_str} mg/L
                        </span>
                        <span class="pcard-do-chip" style="background:{st_obj['do_chip_bg']};color:{st_obj['do_chip_color']}">
                            선유 {syu_str} mg/L
                        </span>
                    </div>
                </div>
            </div>"""
        cards_html += '</div>'
        st.markdown(cards_html, unsafe_allow_html=True)

    # ── ③ 로드맵 타임라인 ──────────────────────────────────────────────────────
    st.markdown("""
    <div class="roadmap-wrap">
        <div class="roadmap-title">📍 정책 우선순위 로드맵</div>
        <div class="roadmap-timeline">
            <div class="roadmap-phase">
                <div class="roadmap-dot short">⚡</div>
                <div class="roadmap-phase-label" style="color:#2563eb">단기</div>
                <div class="roadmap-phase-period">2026 – 2030</div>
                <div class="roadmap-items">
                    <div class="roadmap-item">🌬️ 폭기 시설 확충</div>
                    <div class="roadmap-item">📡 모니터링 고도화</div>
                    <div class="roadmap-item">🌧️ 초기 우수 저류조</div>
                </div>
                <div class="roadmap-target short">DO 최솟값 3.0+</div>
            </div>
            <div class="roadmap-phase">
                <div class="roadmap-dot mid">🔧</div>
                <div class="roadmap-phase-label" style="color:#0891b2">중기</div>
                <div class="roadmap-phase-period">2031 – 2040</div>
                <div class="roadmap-items">
                    <div class="roadmap-item">🏭 하수처리장 고도화</div>
                    <div class="roadmap-item">🌿 생태습지 확대</div>
                    <div class="roadmap-item">🚫 비점오염 관리</div>
                </div>
                <div class="roadmap-target mid">DO 연평균 8.0+</div>
            </div>
            <div class="roadmap-phase">
                <div class="roadmap-dot long">🌍</div>
                <div class="roadmap-phase-label" style="color:#22c55e">장기</div>
                <div class="roadmap-phase-period">2041 – 2050</div>
                <div class="roadmap-items">
                    <div class="roadmap-item">🌳 탄소 감축 달성</div>
                    <div class="roadmap-item">🏙️ 도시 열섬 완화</div>
                    <div class="roadmap-item">🏞️ 자연형 하천 복원</div>
                </div>
                <div class="roadmap-target long">1등급 연중 60%+</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── ④ 정책 전/후 비교 지도 ────────────────────────────────────────────────
    st.markdown("""
    <div class="map-section-hd">
        <div class="map-section-hd-icon">🗺️</div>
        <div>
            <div class="map-section-hd-title">정책 실행 전 vs 후 — DO 수질 지도 비교</div>
            <div class="map-section-hd-sub">정책을 선택하고 연도를 설정하면 DO 등급 변화를 지도로 확인할 수 있습니다</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    pc1, pc2, pc3 = st.columns([2, 2, 1])
    with pc1:
        selected_policies = st.multiselect(
            "적용할 정책 선택 (복수 선택 가능)",
            options=[p["title"] for p in MAP_POLICIES],
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

    base_row    = df_future[df_future["year"] == map_year].iloc[0]
    base_do_nry = base_row[f"{map_scen_key}_노량진_DO"]
    base_do_syu = base_row[f"{map_scen_key}_선유_DO"]
    base_ph_nry = base_row[f"{map_scen_key}_노량진_pH"]
    base_ph_syu = base_row[f"{map_scen_key}_선유_pH"]

    total_imp_nry = sum(p["do_impact_nry"] for p in MAP_POLICIES if p["title"] in selected_policies)
    total_imp_syu = sum(p["do_impact_syu"] for p in MAP_POLICIES if p["title"] in selected_policies)
    after_do_nry  = min(base_do_nry + total_imp_nry, 12.0)
    after_do_syu  = min(base_do_syu + total_imp_syu, 12.0)
    imp_nry = after_do_nry - base_do_nry
    imp_syu = after_do_syu - base_do_syu
    scen_label2 = "SSP5-8.5" if map_scen_key == "SSP585" else "SSP2-4.5"

    active_markers = []
    for title in selected_policies:
        active_markers.extend(POLICY_MARKERS.get(title, []))

    st.markdown(f"""
    <div style='display:flex;gap:14px;margin:12px 0 16px;flex-wrap:wrap'>
        <div style='flex:1;min-width:220px;background:#fefce8;border:1px solid #fde047;
        padding:12px 16px;border-radius:12px'>
            <div style='font-size:11px;font-weight:700;color:#a16207;letter-spacing:.06em;margin-bottom:6px'>❌ 정책 미실행 · {scen_label2} {map_year}년</div>
            <div style='font-size:15px;font-weight:800;color:{do_color(base_do_nry)}'>노량진 {base_do_nry:.2f} mg/L</div>
            <div style='font-size:15px;font-weight:800;color:{do_color(base_do_syu)}'>선유&nbsp;&nbsp;&nbsp;&nbsp; {base_do_syu:.2f} mg/L</div>
        </div>
        <div style='flex:1;min-width:220px;background:#f0fdf4;border:1px solid #86efac;
        padding:12px 16px;border-radius:12px'>
            <div style='font-size:11px;font-weight:700;color:#166534;letter-spacing:.06em;margin-bottom:6px'>✅ 정책 실행 후 · {len(selected_policies)}개 정책 적용</div>
            <div style='font-size:15px;font-weight:800;color:{do_color(after_do_nry)}'>노량진 {after_do_nry:.2f} mg/L <span style='font-size:12px;color:#15803d'>(+{imp_nry:.2f})</span></div>
            <div style='font-size:15px;font-weight:800;color:{do_color(after_do_syu)}'>선유&nbsp;&nbsp;&nbsp;&nbsp; {after_do_syu:.2f} mg/L <span style='font-size:12px;color:#15803d'>(+{imp_syu:.2f})</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    center = [37.522, 126.906]
    map_col1, map_col2 = st.columns(2)
    with map_col1:
        st.markdown("**❌ 정책 미실행**")
        m_before = build_map(center, base_do_nry, base_do_syu, base_ph_nry, base_ph_syu,
                             map_year, f"미실행 ({scen_label2})")
        st_folium(m_before, width=None, height=400, key="map_before")
    with map_col2:
        st.markdown("**✅ 정책 실행 후**")
        m_after = build_map(center, after_do_nry, after_do_syu, base_ph_nry, base_ph_syu,
                            map_year, f"실행 후 ({scen_label2})", policy_markers=active_markers)
        st_folium(m_after, width=None, height=400, key="map_after")

    st.divider()
    sg1, sg2 = st.columns(2)
    with sg1:
        st.metric("노량진 DO", f"{after_do_nry:.2f} mg/L", delta=f"+{imp_nry:.2f} mg/L",
                  help=f"미실행: {base_do_nry:.2f} → 실행 후: {after_do_nry:.2f}")
        st.caption(f"등급 변화: {do_grade_label(base_do_nry)} → {do_grade_label(after_do_nry)}")
    with sg2:
        st.metric("선유 DO", f"{after_do_syu:.2f} mg/L", delta=f"+{imp_syu:.2f} mg/L",
                  help=f"미실행: {base_do_syu:.2f} → 실행 후: {after_do_syu:.2f}")
        st.caption(f"등급 변화: {do_grade_label(base_do_syu)} → {do_grade_label(after_do_syu)}")

    if map_scen_key == "SSP585" and map_year >= 2040:
        st.error(f"🚨 SSP5-8.5 {map_year}년: DO 위험 임계치(5.0 mg/L) 근접! 정책 실행이 시급합니다.")
    elif map_scen_key == "SSP585" and map_year >= 2030:
        st.warning("⚠️ SSP5-8.5 시나리오 — 2030년 이후 DO 감소 추세 본격화. 단기 정책 선행 필요.")
    else:
        st.success(f"✅ {map_year}년 {scen_label2} — 정책 실행 시 수질 관리 가능 범위 유지")


# 푸터
st.markdown("""
<div style="text-align:center;font-size:12px;color:#9ca3af;margin-top:40px;padding:16px 0;border-top:1px solid #f3f4f6;">
    데이터 출처: 서울 열린데이터 광장 · 서울시 요일별 한강 수질 현황 (2020) &nbsp;|&nbsp;
    노량진 · 선유 측정소 시간별 실측값 일평균 &nbsp;|&nbsp;
    예측: IPCC AR6 SSP2-4.5 / SSP5-8.5 시나리오 적용
</div>
""", unsafe_allow_html=True)
