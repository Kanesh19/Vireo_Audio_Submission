# Prompt log

## Version 1 — discarded
> Read these support tickets and summarize what customers are complaining about.
> Identify the biggest themes and suggest actions.

**Discarded because:** it allowed unsupported counts/causes and did not separate
calculation from interpretation.

## Version 2 — used
The final prompt instructs the model to:
- use only supplied evidence,
- treat Python-calculated metrics as authoritative,
- avoid customer/order identifiers and verbatim quotes,
- produce a short executive summary, three grounded themes, two actions, and
  one caveat.

The application sends a small sample of tickets plus deterministic metrics.
The model does not calculate KPIs.

## Thrown away
- LLM-based weekly counts
- LLM agent ranking
- Feeding all 18 months of tickets into one prompt
- RAG/vector database
- Comparing Tier 2 warranty agents with Tier 1

## Cost decision
No API calls were required for the deterministic analysis. The LLM is opt-in
through `OPENAI_API_KEY`, avoiding surprise per-ticket spend.
