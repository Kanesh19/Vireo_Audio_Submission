# 3-minute screen recording

**0:00–0:25 — Problem**
"Vireo wants a weekly complaint digest and a closure leaderboard. I cleaned the
migration duplicates first and made the reporting definitions explicit."

**0:25–0:55 — Prompts**
Show `prompts.md`. Explain why version 1 was discarded and why version 2
separates KPI calculation from narrative generation.

**0:55–1:35 — Digest**
Show a full week in the Streamlit app. Point out volume, complaint mix,
repeat-contact rate, SLA breach rate and CSAT. Generate the AI narrative if
a key is configured.

**1:35–2:10 — Leaderboard**
Show the Tier 1 leaderboard and point out that Tier 2 warranty is excluded
because the policy says those cases are measured in days, not weekly volume.

**2:10–2:40 — Validation**
Show the validation tab: duplicate cleanup, zero broken joins, and the fact
that Python owns KPI calculations.

**2:40–3:00 — Scope**
"I deliberately left out RAG, vector databases, agentic workflows and
LLM-based KPI calculation. They would add complexity without being necessary
for this client's stated need."
