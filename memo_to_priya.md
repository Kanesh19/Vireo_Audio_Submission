# Memo to Priya Raman — Vireo Audio

**Subject: Weekly support intelligence — recommended first target**

## Bottom line

The export has **12,528 rows but 11,875 unique ticket IDs**.
After migration cleanup, repeat contact is the clearest queue-cost signal.
In **Q2 2026, 246 of 2,343 resolved/closed tickets (10.5%)**
were followed by another contact from the same customer about the same
category/product within 30 days.

## Business goal

**Reduce repeat contacts from 10.5% to 8.0%.**

At the Q2 run-rate, that is about **59 fewer repeat contacts per quarter** and
approximately **₹15,321 of contact cost avoided per quarter**
using the policy's channel costs. This is a planning estimate, not a guarantee.

## What to watch

Delivery & Shipping is the largest complaint category overall, followed by
Billing & Payments, Connectivity, Returns & Refunds, and Charging & Battery.
The weekly tool makes those trends visible without requiring anyone to read the
full export.

Q2 also had **221 first-response SLA breaches**, implying
**₹77,350 in automatic ₹350 breach credits**. I keep this
separate from the repeat-contact business case to avoid double counting.

## Actions

1. Use the weekly digest to identify the biggest repeat-contact categories and
   turn them into frontline coaching / knowledge-base fixes.
2. Track repeat-contact rate and SLA breach rate weekly alongside volume.
3. Keep Tier 2 warranty out of the volume leaderboard; its cases are explicitly
   measured differently by policy.

## Caveats

The pack contains migration duplicates and an empty README. The tool documents
its decisions rather than silently assuming clean data. "Same issue" is
approximated by customer/category/product plus a 30-day window; it is not a
semantic judgement. The LLM is only used for narrative generation.

**Build cost:** no API spend was required for the deterministic analysis.
