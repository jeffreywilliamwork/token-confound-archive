

# Token-Position Confound in MoE Routing Entropy (Archive)

This archive documents a specific, easy-to-miss failure mode when analyzing MoE routing:

> **If routing entropy increases with token position, then any “mean entropy over all tokens” metric will be confounded by prompt length.**

This matters directly to mechanistic interpretability work that uses router-entropy summaries to compare prompts, tasks, or “cognitive” categories.

## What This Archive Establishes

- **An early “complexity hierarchy” experiment was invalid.** It was driven by token position / prompt length.
- **The confound is real and cross-model.** It appears in DeepSeek V3.1 and Qwen 397B, and it explains why DeepSeek R1 “replicated” the same hierarchy.
- **A simple control breaks the hierarchy:** compute routing entropy at a fixed position (e.g., last prompt token) instead of averaging over all prefill tokens.

At-a-glance (Spearman, n=168 prompts per model):

| Model | rho(all-token RE, level) | rho(last-token RE, level) | rho(all-token RE, token_count) |
|---|---:|---:|---:|
| DeepSeek V3.1 | +0.8019 | +0.0177 | +0.8797 |
| Qwen 397B | +0.6166 | -0.0622 | +0.7813 |

## Historical Warning

Some files in `raw/` are preserved exactly because they show what was believed at the time.

- They are part of the evidence trail.
- They are not the archive's final interpretation.
- If a raw writeup conflicts with `NARRATIVE.md` or `CROSS_MODEL_POSITION_CONFOUND.md`, treat the archive-level documents as the corrected interpretation.

## Start Here

1. `CROSS_MODEL_POSITION_CONFOUND.md` (evidence and tables)
2. `NARRATIVE.md` (chronology: what was claimed, what broke, what survived)
3. `raw/168q-r1-deepseek-r1/168q-r1_RESULTS.md` (the original R1 headline writeup as written)
4. `raw/r1-28q-1/r1-28q-1_RESULTS.md` (generation follow-up where the confound first became hard to ignore)
5. `PARTIAL-RESULTS.md` (what can and cannot be recomputed from recovered raw captures)
6. `MANIFEST.md` (inventory)

## Definitions (Minimal)

- **Prefill**: processing the prompt tokens only (no generation).
- **All-token mean RE**: mean routing-entropy computed across all prompt tokens.
- **Last-token RE**: routing-entropy at a single fixed position (the final prompt token).
- **Confound mechanism**: if later positions systematically have higher RE, longer prompts will have higher mean RE even if content is unrelated.

Operationally: the confound is detected when `rho(all-token RE, level)` is large but `rho(last-token RE, level)` collapses to ~0, while `rho(all-token RE, token_count)` stays large.

## Practical Guidance (For Mech Interp Use)

If you want to use router entropy as a summary statistic:
- Do not compare prompts of different lengths using all-token means without a position control.
- Prefer fixed-position metrics (last token, matched boundary tokens) or explicitly stratify by position.
- Always report `rho(RE, token_count)` alongside any `rho(RE, label)` and treat it as a rival explanation.

## Raw vs Recalculated (In This Folder)

- `raw/` contains original copied experiment artifacts and result writeups.
- `data/` contains standardized summaries derived from those sources (useful for quick comparison).

Example:

- `raw/168q-r1-deepseek-r1/results_168_r1_prefill.json` is an original per-prompt R1 results file.
- `data/168q-r1_R1_prefill.json` is a standardized recalculation derived from it.

The recalculated files are easier to scan. The raw files are the source of record.

## Naming Decoder (Legacy Labels)

Some legacy files use historical branch labels like `14q-r1`, `14q-r3`, etc. These labels are not level numbers and not chronological order.

| Branch | Added level(s) | Content theme |
|--------|----------------|---------------|
| `14q-r3` | L8 | Strange loops |
| `14q-r1` | L9 | Deep self-reference |
| `14q-r2` | L10 | Nexus-7 third-person |
| `14q-r4` | L11 | Architectural introspection |
| `14q-r5` | L12 | Echo persona |
| `14q-r6` | L10 control | Bob name control |
| `14q-r7` | L10 control | Aether name control |

## Scope

Core archive:
- DeepSeek V3.1 hierarchy buildup
- DeepSeek R1 hierarchy replication
- R1 generation follow-up
- Qwen position-control comparison

Supplemental archive:
- DeepSeek forced-choice and multiseed runs
- post-confound methodology notes

Those supplemental files are preserved because they were adjacent in time, but they are not load-bearing for the token-confound claim.
