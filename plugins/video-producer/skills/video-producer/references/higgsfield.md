# Compare shot budgets

Use the companion [Higgsfield Shots](../../higgsfield-shots/SKILL.md) for shot direction, submission receipts, repairs and creative QA. Use this calculator for what-if planning across multiple shots. It never submits a generation or reserves credits.

Run `python <skill>/credit_plan.py <plan.json>`. Set the whole-credit cap, previous spend and an optional reserve. Give each pending request a distinct ID. A connector estimate for a batch already includes the requested variants. Enter its total once in `quoted_total`. For a known per-variant price use the legacy `quoted_credits` with `count`. Each request or unit is rounded up conservatively. The calculator returns exit code 2 if the plan exceeds the cap.

```json
{"cap":300,"spent":20,"reserve":30,"shots":[{"id":"three-variant-batch","quoted_total":240,"count":3}]}
```

The illustrative batch leaves 10 credits available. Replace all example amounts with current quotes. Include each draft, finalize, edit and retry as its own request. A separate low-resolution render may change performance when regenerated at delivery quality. When a model supports finalizing a draft, check its validity window and the full-duration finalization quote. Use the same surface for pricing and submission. [Credits](https://higgsfield.ai/creator-hub/help-center/credits/how-credits-work) · [Draft and retake guidance](https://higgsfield.ai/blog/why-ai-video-generations-fail) · [Finalize-draft API](https://open.higgsfield.ai/models/bytedance/seedance-2.5/finalize-draft/api-reference).
