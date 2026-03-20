
#!/usr/bin/env markdown

# Token-Position Confound in MoE Routing Entropy (Archive)

This repo is a self-contained archive documenting a specific, easy-to-miss failure mode when analyzing MoE routing:

> **If routing entropy increases with token position, then any “mean entropy over all tokens” metric will be confounded by prompt length.**

This matters directly to mechanistic interpretability work that uses router-entropy summaries to compare prompts, tasks, or dataset categories.

## TL;DR (What This Repo Establishes)
- **Within-prefill routing entropy is token-position-sensitive.** Later prompt tokens have systematically higher routing entropy than earlier prompt tokens.
- **Therefore, all-token means are prompt-length-confounded.** If you average RE over all prompt tokens, longer prompts will look “higher RE” even when content is irrelevant.
- **This effect is cross-model.** It appears in DeepSeek V3.1 and Qwen 397B, and it also explains an apparent DeepSeek R1 “replication” that was actually length-driven.
- **A simple position control removes the artifact:** evaluate RE at a fixed position (for example, the last prompt token) rather than averaging over all prompt tokens.

At-a-glance (Spearman, n=168 prompts per model):

| Model | rho(all-token RE, level) | rho(last-token RE, level) | rho(all-token RE, token_count) |
|---|---:|---:|---:|
| DeepSeek V3.1 | +0.8019 | +0.0177 | +0.8797 |
| Qwen 397B | +0.6166 | -0.0622 | +0.7813 |

The interpretation is: the “level” label looked predictive only because it co-varied with prompt length.

## Start Here (Reading Order)

1. `CROSS_MODEL_POSITION_CONFOUND.md` (the evidence tables: all-token vs last-token)
2. `NARRATIVE.md` (how the mistake happened, how it was detected)
3. `MANIFEST.md` (inventory and what each folder is for)
4. `PARTIAL-RESULTS.md` (a recovered subset that can only be recomputed partially)

## Quick Diagnostic (What To Report In Your Own Work)

If you want to use router entropy as a summary statistic:

- Always report `rho(RE, token_count)` alongside `rho(RE, label)` (or any across-prompt comparison).
- Prefer fixed-position metrics (last token, matched region boundaries) or explicitly stratify by token position.
- If you must use all-token means, length-match prompts (or match positions) and say exactly how.

Operationally, the confound is present when:

- `rho(all-token RE, label)` is large
- `rho(all-token RE, token_count)` is also large
- `rho(last-token RE, label)` collapses to near 0

## What’s In This Repo

- `raw/`: copied source artifacts (original JSON outputs, logs, and “as-written” historical writeups)
- `data/`: standardized summaries derived from `raw/` for easy cross-run comparison
- `figures/`: plots used in the cross-model comparison
- `supplemental/`: adjacent-but-nonloadbearing artifacts (including a partial raw recovery from an external SSD)

Some files in `raw/` preserve conclusions that were later invalidated. They are kept because they are part of the evidence trail. If a raw writeup conflicts with `NARRATIVE.md` or `CROSS_MODEL_POSITION_CONFOUND.md`, treat the archive-level docs as the corrected interpretation.

## Reproducing The Summary Tables

The key standardized summaries in `data/` can be rebuilt from the checked-in `raw/` sources:

```bash
python3 -m pip install numpy scipy
python3 data/rebuild_from_raw.py
```

This regenerates the small set of `data/*.json` and `data/*.md` files used by the archive’s tables (and rewrites any machine-specific provenance paths to portable repo-relative paths).

## Definitions (Minimal)

- **Prefill**: processing the prompt tokens only (no generation).
- **All-token mean RE**: mean routing-entropy computed across all prompt tokens.
- **Last-token RE**: routing-entropy at a single fixed position (the final prompt token).
- **Confound mechanism**: if later positions systematically have higher RE, longer prompts will have higher mean RE even if content is unrelated.

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
- cross-model position confound tables (DeepSeek V3.1 vs Qwen 397B)
- DeepSeek R1 run artifacts used as an additional cross-check
- a small per-token position diagnostic suite

Supplemental archive:
- an external-SSD partial raw recovery (documented in `PARTIAL-RESULTS.md`)
- adjacent multiseed / v2.2 artifacts kept for forensic completeness

Those supplemental files are preserved because they were adjacent in time, but they are not load-bearing for the token-confound claim.
