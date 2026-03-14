import math

import streamlit as st
import pandas as pd
import altair as alt


def calculate_prize_distribution(
    total_participants: int,
    total_prize: float,
    p: float = 1.2,
) -> dict[int, float]:
    """
    Calculate prize amounts for each rank using Power Law distribution.

    Only the top 50% of participants receive a cash prize.
    Prize for rank k is proportional to 1 / k^p, normalized to sum to
    total_prize.

    Args:
        total_participants: Total number of participants in the competition.
        total_prize: Total prize pool to distribute.
        p: Power Law exponent controlling prize concentration.
           Lower p = flatter distribution; higher p = more top-heavy.
           Recommended value: 1.2.

    Returns:
        A dictionary mapping rank (int) to prize amount (float),
        covering ranks 1 through total_participants // 2.
    """
    n_winners = total_participants // 2

    scores = [1.0 / (k ** p) for k in range(1, n_winners + 1)]
    total_score = math.fsum(scores)
    prizes = [total_prize * s / total_score for s in scores]

    return {k: round(v, 2) for k, v in enumerate(prizes, start=1)}


# ── UI ────────────────────────────────────────────────────────────────────────

st.title("競賽獎金模擬器")
st.caption("Power Law Distribution — 前50%獲獎者")

# Sidebar controls
with st.sidebar:
    st.header("參數設定")
    total_participants = st.slider(
        "總參賽人數", min_value=10, max_value=428, value=214, step=1
    )
    total_prize = st.number_input(
        "總獎金（元）", min_value=100, max_value=1_000_000, value=10_000, step=100
    )
    p = st.slider(
        "p 值（坡度）", min_value=0.5, max_value=2.5, value=1.2, step=0.1,
        help="越大越集中頂端；推薦 1.2"
    )

# Compute
result = calculate_prize_distribution(total_participants, total_prize, p)
df = pd.DataFrame(
    {"rank": list(result.keys()), "prize": list(result.values())}
)

# ── Metrics ───────────────────────────────────────────────────────────────────
n_winners = total_participants // 2
top1_prize = df["prize"].iloc[0]
top1_pct = top1_prize / total_prize * 100
top10_pct = df["prize"].iloc[:10].sum() / total_prize * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("獲獎人數", f"{n_winners} 人")
col2.metric("第1名獎金", f"{top1_prize:,.0f}")
col3.metric("第1名佔比", f"{top1_pct:.1f}%")
col4.metric("前10名合計佔比", f"{top10_pct:.1f}%")

# ── Chart ─────────────────────────────────────────────────────────────────────
st.subheader("獎金分配曲線")
chart = (
    alt.Chart(df)
    .mark_bar(color="#378ADD", cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
    .encode(
        x=alt.X("rank:Q", title="名次", scale=alt.Scale(domainMin=1)),
        y=alt.Y("prize:Q", title="獎金（元）"),
        tooltip=[
            alt.Tooltip("rank:Q", title="名次"),
            alt.Tooltip("prize:Q", title="獎金", format=",.2f"),
        ],
    )
    .properties(height=300)
)
st.altair_chart(chart, use_container_width=True)

# ── Table ─────────────────────────────────────────────────────────────────────
st.subheader("名次明細")
st.dataframe(
    df.rename(columns={"rank": "名次", "prize": "獎金（元）"}),
    use_container_width=True,
    hide_index=True,
)
