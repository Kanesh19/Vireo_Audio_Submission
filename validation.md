# Validation and correctness

| Check | Result |
|---|---:|
| Raw ticket rows | 12,528 |
| Unique ticket IDs after dedupe | 11,875 |
| Duplicate rows removed | 653 |
| Unknown agent IDs | 0 |
| Unknown customer IDs | 0 |
| Unknown order IDs | 0 |
| Unknown product SKUs | 0 |
| Refund + replacement conflicts | 4 |

## KPI definitions

- **SLA breach:** first response later than the channel target in the supplied policy.
- **Attendance:** `resolved` or `closed`.
- **Leaderboard:** tickets resolved/closed in the selected week, Tier 1 only.
- **Repeat contact:** same customer + category + product (or both missing), with
  the new ticket created within 30 days after prior resolution.

## AI validation

The model never calculates the numeric KPIs. Python supplies authoritative
metrics and a small evidence sample. For manual acceptance, sample 20 AI
digests and verify:
1. every number matches the displayed metric,
2. every named theme is present in supplied evidence,
3. no identifiers are exposed,
4. no unsupported financial claim appears,
5. recommendations are clearly framed as recommendations.

The deterministic fallback remains available with no API key.

## Limitations

- `README.txt` in the supplied ZIP is empty.
- `submission-form.md` is absent from the supplied ZIP.
- The repeat-contact definition is an operational proxy rather than semantic
  issue matching.
