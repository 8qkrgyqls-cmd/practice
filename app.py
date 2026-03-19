import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
 
# ── 페이지 설정 ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="2026 방역 전략 대시보드",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)
 
# ── 글로벌 스타일 ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600&display=swap');
 
html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}
.block-container {
    padding: 2rem 3rem;
    max-width: 1400px;
}
 
/* 메트릭 카드 */
[data-testid="stMetric"] {
    background: #f8f9fb;
    border: 1px solid #e8eaed;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
}
[data-testid="stMetricLabel"] { font-size: 0.75rem; color: #6b7280; letter-spacing: 0.03em; }
[data-testid="stMetricValue"] { font-size: 1.6rem; font-weight: 600; color: #111827; }
[data-testid="stMetricDelta"] { font-size: 0.78rem; }
 
/* 섹션 구분선 */
hr { border: none; border-top: 1px solid #e8eaed; margin: 1.8rem 0; }
 
/* 지역 카드 */
.region-card {
    background: #fff;
    border: 1px solid #e8eaed;
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.75rem;
}
.region-card h4 { margin: 0 0 4px; font-size: 0.9rem; font-weight: 600; color: #111827; }
.region-card p  { margin: 0; font-size: 0.78rem; color: #6b7280; }
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 99px;
    font-size: 0.7rem;
    font-weight: 500;
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
    margin-top: 6px;
}
 
/* 사이드바 숨기기 */
[data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)
 
 
# ── 데이터 ────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    rows = [
        ["서울", "인플루엔자", 18.5, 12.2, 42.0, 68.5, "스마트 공조"],
        ["경기", "RSV",        34.2, 22.8, 22.5, 45.0, "클린 에듀케이션"],
        ["인천", "노로바이러스", 15.8,  9.5, 12.0, 35.5, "워터-세이프"],
        ["강원", "COVID-19",   24.2, 15.1, 50.4, 82.5, "모빌리티 보건소"],
        ["전라", "노로바이러스", 14.5,  8.8, 13.2, 32.4, "미생물 이력제"],
    ]
    return pd.DataFrame(
        rows,
        columns=["지역", "바이러스", "발병률_24", "발병률_25",
                 "면역율_24", "면역율_25", "핵심정책"]
    )
 
df = load_data()
 
ACCENT_COLORS = ["#185FA5", "#0F6E56", "#993C1D", "#533AB7", "#854F0B"]
 
 
# ── 헤더 ──────────────────────────────────────────────────────────────────────
st.markdown("### 2024–2025 국가 방역 성과 분석")
st.caption("데이터 기반 능동형 방역 시스템의 실효성을 정량적으로 평가한 결과입니다.")
st.markdown("---")
 
 
# ── 지표 카드 ─────────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
m1.metric("발병률 감소 (전국)",    "12.82%", "−34.1% 개선")
m2.metric("면역율 상승 (전국)",    "62.40%", "+74.3% 증가")
m3.metric("중증 감소 상관관계",   "r = −0.85", "매우 강한 음의 상관")
m4.metric("경제적 편익",          "4,700억", "자본 투자 효과")
st.markdown("---")
 
 
# ── 본문 레이아웃: 좌(차트) / 우(지역 카드) ───────────────────────────────────
col_chart, col_region = st.columns([1.6, 1], gap="large")
 
with col_chart:
    st.markdown("**정책 시행 전후 데이터 비교**")
    metric_opt = st.radio(
        "지표 선택",
        ["발병률 추이", "면역율 추이"],
        horizontal=True,
        label_visibility="collapsed",
    )
 
    y_cols = (["발병률_24", "발병률_25"]
              if metric_opt == "발병률 추이"
              else ["면역율_24", "면역율_25"])
    y_label = "발병률 (%)" if metric_opt == "발병률 추이" else "면역율 (%)"
 
    fig = go.Figure()
    colors_24 = "#B5D4F4"
    colors_25 = "#185FA5"
 
    fig.add_trace(go.Bar(
        name="2024", x=df["지역"], y=df[y_cols[0]],
        marker_color=colors_24, marker_line_width=0,
    ))
    fig.add_trace(go.Bar(
        name="2025", x=df["지역"], y=df[y_cols[1]],
        marker_color=colors_25, marker_line_width=0,
    ))
 
    fig.update_layout(
        barmode="group",
        yaxis_title=y_label,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Noto Sans KR", size=12, color="#374151"),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1,
        ),
        margin=dict(t=40, b=20, l=20, r=20),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="#f3f4f6", zeroline=False),
    )
 
    st.plotly_chart(fig, use_container_width=True)
 
    # 지역별 꺾은선 비교
    st.markdown("**지역별 발병률 vs 면역율 분포 (2025)**")
    fig2 = px.scatter(
        df, x="발병률_25", y="면역율_25",
        text="지역", size_max=18,
        color="지역", color_discrete_sequence=ACCENT_COLORS,
        labels={"발병률_25": "발병률 2025 (%)", "면역율_25": "면역율 2025 (%)"},
    )
    fig2.update_traces(textposition="top center", marker=dict(size=14))
    fig2.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Noto Sans KR", size=12, color="#374151"),
        legend_title_text="지역",
        margin=dict(t=20, b=20, l=20, r=20),
        xaxis=dict(showgrid=True, gridcolor="#f3f4f6", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#f3f4f6", zeroline=False),
    )
    st.plotly_chart(fig2, use_container_width=True)
 
 
with col_region:
    st.markdown("**권역별 심층 성과**")
    for _, row in df.iterrows():
        reduction = (row["발병률_24"] - row["발병률_25"]) / row["발병률_24"] * 100
        immunity_gain = row["면역율_25"] - row["면역율_24"]
        st.markdown(f"""
<div class="region-card">
  <h4>📍 {row['지역']} 권역</h4>
  <p>핵심 정책: <strong>{row['핵심정책']}</strong></p>
  <p>발병률: {row['발병률_24']}% → {row['발병률_25']}%
     &nbsp;<span style="color:#993C1D;">▼ {reduction:.1f}%</span></p>
  <p>면역율: {row['면역율_24']}% → {row['면역율_25']}%
     &nbsp;<span style="color:#0F6E56;">▲ +{immunity_gain:.1f}%p</span></p>
  <span class="badge">{row['바이러스']}</span>
</div>
""", unsafe_allow_html=True)
 
st.markdown("---")
 
# ── 하단: 상세 데이터 테이블 ──────────────────────────────────────────────────
with st.expander("📋 원본 데이터 테이블 보기"):
    display_df = df.copy()
    display_df["발병률 감소율"] = (
        (display_df["발병률_24"] - display_df["발병률_25"])
        / display_df["발병률_24"] * 100
    ).round(1).astype(str) + "%"
    display_df["면역율 증가량"] = (
        display_df["면역율_25"] - display_df["면역율_24"]
    ).round(1).astype(str) + "%p"
    st.dataframe(
        display_df[["지역", "바이러스", "발병률_24", "발병률_25",
                    "발병률 감소율", "면역율_24", "면역율_25",
                    "면역율 증가량", "핵심정책"]],
        use_container_width=True,
        hide_index=True,
    )
 
