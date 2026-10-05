import os
from pathlib import Path
import pandas as pd
import streamlit as st

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
SLA_TARGETS = {"chat": 15, "voice": 120, "social": 240, "email": 480}
CHANNEL_COSTS = {"chat": 210, "email": 260, "voice": 520, "social": 240}

@st.cache_data
def load_data():
    tickets = pd.read_csv(DATA / "tickets.csv")
    agents = pd.read_csv(DATA / "agents.csv")
    customers = pd.read_csv(DATA / "customers.csv")
    orders = pd.read_csv(DATA / "orders.csv")
    products = pd.read_csv(DATA / "products.csv")

    for c in ["created_at", "first_response_at", "resolved_at"]:
        tickets[c+"_dt"] = pd.to_datetime(tickets[c], dayfirst=True, errors="coerce")

    tickets["_source_rank"] = tickets["source_system"].map(
        {"helpdesk": 0, "legacy_fd": 1}
    ).fillna(9)
    tickets = tickets.sort_values(["ticket_id", "_source_rank"]).drop_duplicates(
        "ticket_id", keep="first"
    ).copy()

    legacy = (tickets.source_system == "legacy_fd") & tickets.resolved_at_dt.notna()
    tickets.loc[legacy, "resolved_at_dt"] += pd.Timedelta(hours=5, minutes=30)

    tickets["attendance"] = tickets.status.isin(["resolved", "closed"])
    tickets["sla_target_mins"] = tickets.channel.map(SLA_TARGETS)
    tickets["first_response_mins"] = (
        tickets.first_response_at_dt-tickets.created_at_dt
    ).dt.total_seconds()/60
    tickets["breach"] = tickets.first_response_mins > tickets.sla_target_mins

    rpt = tickets[tickets.attendance & tickets.resolved_at_dt.notna()].sort_values(
        ["customer_id", "created_at_dt"]
    ).copy()
    rpt["prev_resolved"] = rpt.groupby("customer_id").resolved_at_dt.shift(1)
    rpt["prev_category"] = rpt.groupby("customer_id").category.shift(1)
    rpt["prev_product"] = rpt.groupby("customer_id").product_sku.shift(1)
    rpt["repeat_contact"] = (
        rpt.prev_resolved.notna()
        & (rpt.created_at_dt >= rpt.prev_resolved)
        & (rpt.created_at_dt-rpt.prev_resolved <= pd.Timedelta(days=30))
        & (rpt.category == rpt.prev_category)
        & ((rpt.product_sku == rpt.prev_product) |
           (rpt.product_sku.isna() & rpt.prev_product.isna()))
    )
    rpt["contact_cost"] = rpt.channel.map(CHANNEL_COSTS)
    tickets = tickets.merge(
        rpt[["ticket_id","repeat_contact"]], on="ticket_id", how="left"
    )
    tickets["repeat_contact"] = tickets.repeat_contact.fillna(False)

    agents["from_date_dt"] = pd.to_datetime(agents.from_date, dayfirst=True, errors="coerce")
    agents["to_date_dt"] = pd.to_datetime(agents.to_date, dayfirst=True, errors="coerce")
    return tickets, agents, customers, orders, products

def week_start(series):
    s = pd.to_datetime(series)
    return s.dt.normalize()-pd.to_timedelta(s.dt.weekday, unit="D")

def deterministic_digest(df):
    if len(df) == 0:
        return "No tickets were created in this period."
    cat = df.category.value_counts().rename_axis("category").reset_index(name="tickets")
    lines = [
        f"- {x.category}: {x.tickets} tickets ({x.tickets/len(df):.1%})."
        for x in cat.head(5).itertuples()
    ]
    resolved = df[df.attendance]
    repeat = resolved.repeat_contact.mean() if len(resolved) else float("nan")
    breach = df.breach.mean()
    csat = df.csat_score.dropna()
    out = "Deterministic weekly digest\n\n" + "\n".join(lines)
    out += f"\n\n- Repeat-contact signal: {repeat:.1%} among resolved/closed tickets." if len(resolved) else ""
    out += f"\n- First-response SLA breach rate: {breach:.1%}."
    out += f"\n- Mean CSAT: {csat.mean():.2f}/5 among respondents." if len(csat) else "\n- Mean CSAT: no responses."
    return out

def make_llm_digest(df):
    if OpenAI is None or not os.getenv("OPENAI_API_KEY"):
        return None, "No OPENAI_API_KEY detected; deterministic mode is active."

    client = OpenAI()    # $env:OPENAI_API_KEY="YOUR_API_KEY"
    model = os.getenv("OPENAI_MODEL", "gpt-6-luna")
    top_cats = df.category.value_counts().head(6).index.tolist()
    samples = []
    for cat in top_cats:
        for row in df[df.category == cat].head(4).itertuples():
            samples.append({
                "category": row.category,
                "channel": row.channel,
                "message": str(row.customer_message).replace("\n"," ")[:450]
            })
    metrics = {
        "ticket_count": int(len(df)),
        "top_categories": df.category.value_counts().head(6).to_dict(),
        "sla_breach_rate": round(float(df.breach.mean()), 4),
        "repeat_contact_rate_resolved_closed": (
            round(float(df.loc[df.attendance, "repeat_contact"].mean()), 4)
            if df.attendance.any() else None
        ),
        "mean_csat": (
            round(float(df.csat_score.dropna().mean()), 2)
            if df.csat_score.notna().any() else None
        ),
    }
    prompt = f"""
You are writing a weekly customer-support digest for Vireo Audio's Head of Customer Experience.

Use ONLY the evidence below. Do not invent counts, causes, products, or financial impact.
Python-calculated metrics are authoritative. Do not mention customer names, IDs, order IDs,
or quote customers verbatim.

Return:
1. 4-6 sentence executive summary
2. three complaint themes grounded in examples
3. two concrete actions for next week
4. one caveat/limitation

CALCULATED METRICS:
{metrics}

SAMPLE TICKETS:
{samples}
"""
    try:
        response = client.responses.create(model=model, input=prompt)
        return response.output_text, f"LLM: {model}"
    except Exception as exc:
        return None, f"LLM failed; deterministic fallback used: {exc}"

st.set_page_config(page_title="Vireo Audio Support Intelligence", layout="wide")
st.title("Vireo Audio — Support Intelligence")
st.caption("Set A • deterministic KPIs + optional LLM narrative")

tickets, agents, customers, orders, products = load_data()
tickets["created_week"] = week_start(tickets.created_at_dt)
tickets["resolved_week"] = week_start(tickets.resolved_at_dt)

weeks = sorted(tickets.created_week.dropna().unique().tolist())
default_week = weeks[-2] if len(weeks) > 1 else weeks[-1]

with st.sidebar:
    st.header("Filters")
    week = st.selectbox(
        "Digest week",
        weeks,
        index=weeks.index(default_week),
        format_func=lambda x: pd.Timestamp(x).strftime("%d %b %Y"),
    )
    channels = sorted(tickets.channel.dropna().unique())
    teams = sorted(tickets.assigned_team.dropna().unique())
    channel = st.multiselect("Channel", channels, default=channels)
    team = st.multiselect("Team", teams, default=teams)

week_df = tickets[
    (tickets.created_week == pd.Timestamp(week))
    & tickets.channel.isin(channel)
    & tickets.assigned_team.isin(team)
].copy()

tab1, tab2, tab3, tab4 = st.tabs(
    ["Weekly Digest", "Agent Leaderboard", "Ticket Explorer", "Validation"]
)

with tab1:
    st.subheader(f"Week of {pd.Timestamp(week).strftime('%d %b %Y')}")
    a,b,c,d = st.columns(4)
    a.metric("Tickets created", len(week_df))
    b.metric("SLA breach rate", f"{week_df.breach.mean():.1%}" if len(week_df) else "—")
    resolved = week_df[week_df.attendance]
    c.metric("Repeat-contact rate", f"{resolved.repeat_contact.mean():.1%}" if len(resolved) else "—")
    csat = week_df.csat_score.dropna()
    d.metric("Mean CSAT", f"{csat.mean():.2f}/5" if len(csat) else "—")

    st.markdown("### Complaint mix")
    cat = week_df.category.value_counts().rename_axis("category").reset_index(name="tickets")
    st.bar_chart(cat.set_index("category"))
    st.dataframe(cat, use_container_width=True, hide_index=True)

    st.markdown("### AI-assisted narrative")
    if st.button("Generate / refresh AI digest"):
        digest, status = make_llm_digest(week_df)
        if digest:
            st.success(status)
            st.markdown(digest)
        else:
            st.info(status)
            st.markdown(deterministic_digest(week_df))
    else:
        st.markdown(deterministic_digest(week_df))
        st.caption("All displayed KPIs are calculated in Python; the LLM only writes the narrative.")

with tab2:
    st.subheader("Weekly tickets closed — Tier 1 only")
    st.caption("Resolved/closed tickets by resolution week. Tier 2 warranty is excluded per policy.")
    lb = tickets[
        tickets.attendance & (tickets.resolved_week == pd.Timestamp(week))
    ].merge(
        agents[["agent_id","name","team","tier","site","shift"]],
        on="agent_id", how="left"
    )
    lb = lb[lb.tier == 1]
    leaderboard = (
        lb.groupby(["agent_id","name","team","site","shift"]).size()
        .reset_index(name="tickets_closed")
        .sort_values(["tickets_closed","name"], ascending=[False,True])
    )
    st.dataframe(leaderboard.reset_index(drop=True), use_container_width=True, hide_index=True)
    st.caption("Volume is workload visibility, not a quality or individual-performance score.")

with tab3:
    st.subheader("Ticket Explorer")
    search = st.text_input("Search message or closing note", placeholder="refund, tracking, battery, already told")
    show = week_df.copy()
    if search.strip():
        q = search.strip()
        mask = (
            show.customer_message.fillna("").str.contains(q, case=False, regex=False)
            | show.agent_notes.fillna("").str.contains(q, case=False, regex=False)
        )
        show = show[mask]
    cols = ["ticket_id","created_at","channel","category","assigned_team","agent_id",
            "transfers","breach","repeat_contact","csat_score"]
    st.dataframe(show[cols].head(250), use_container_width=True, hide_index=True)
    if len(show):
        selected = st.selectbox("Select ticket", show.ticket_id.tolist())
        row = show[show.ticket_id == selected].iloc[0]
        st.markdown("**Customer message**")
        st.write(row.customer_message)
        st.markdown("**Agent closing note**")
        st.write(row.agent_notes)

with tab4:
    st.subheader("Data quality and method checks")
    raw = pd.read_csv(DATA/"tickets.csv")
    checks = [
        ("Raw ticket rows", len(raw), "Informational"),
        ("Unique ticket IDs after dedupe", tickets.ticket_id.nunique(), "Expected"),
        ("Duplicate rows removed", len(raw)-tickets.ticket_id.nunique(), "Migration duplicates"),
        ("Unknown agent IDs", int((~tickets.agent_id.isin(agents.agent_id)).sum()), "Should be 0"),
        ("Unknown customer IDs", int((~tickets.customer_id.isin(customers.customer_id)).sum()), "Should be 0"),
        ("Unknown order IDs", int((tickets.order_id.notna() & ~tickets.order_id.isin(orders.order_id)).sum()), "Should be 0"),
        ("Unknown product SKUs", int((tickets.product_sku.notna() & ~tickets.product_sku.isin(products.sku)).sum()), "Should be 0"),
        ("Refund + replacement conflicts", int((tickets.refund_amount_inr.fillna(0).gt(0) & tickets.replacement_issued.eq("Y")).sum()), "Policy says escalate"),
        ("Open/pending tickets", int((~tickets.attendance).sum()), "Excluded from closed leaderboard"),
    ]
    st.dataframe(pd.DataFrame(checks, columns=["check","value","interpretation"]), use_container_width=True, hide_index=True)
    st.markdown("### Important decisions")
    st.markdown("""
- Duplicate IDs are deduplicated by preferring `helpdesk` over `legacy_fd`.
- Legacy resolution timestamps are shifted +5:30 because the supplied policy says
  legacy event-log resolution timestamps are UTC while reports are IST.
- Repeat contact = same customer + category + product (or both missing) within
  30 days after the prior resolution.
- Tier 2 / Escalations & Warranty is excluded from the volume leaderboard.
- Python calculates all KPIs; the LLM is only a narrative layer.
""")
