#!/usr/bin/env markdown

# Chronology: How the Token-Position Confound Was Found

This file is the story. For the evidence tables, read `CROSS_MODEL_POSITION_CONFOUND.md`. For the file inventory, read `MANIFEST.md`.

## One-Paragraph Summary

The original claim was that MoE routing entropy rose with prompt “cognitive complexity” across a 12-level hierarchy. That claim did not survive. The hierarchy was driven by **token position within the prompt**: longer prompts contain more late prefill tokens, and late-position tokens have systematically higher routing entropy. What remains valid is the confound itself. It is reproducible across DeepSeek V3.1, DeepSeek R1, and Qwen 397B, and it matters for any study that averages routing entropy across prompts of different lengths.

## Reading Order

1. `CROSS_MODEL_POSITION_CONFOUND.md` (the key tables: all-token vs last-token)
2. This file (why the project believed the hierarchy, and how it broke)
3. `raw/168q-r1-deepseek-r1/168q-r1_RESULTS.md` (the “as-written” R1 hierarchy claim)
4. `raw/r1-28q-1/r1-28q-1_RESULTS.md` (generation follow-up: early warning)
5. `PARTIAL-RESULTS.md` (what can be recomputed from recovered raw tensors)

## Minimal Decoder for Legacy Labels

Some early runs are labeled `14q-r*`. These are historical branch names, not level numbers and not chronological order. The short decoder is in `README.md`.

## Timeline

### 1. Generation looked confounded first (length confound)

The earliest DeepSeek V3.1 generation run already showed a prompt-length / token-count problem.

- `98q-r1` generation:
  - RE vs level: `rho=0.1973`, `p=0.051`
  - RE vs token count: `rho=0.5051`, `p=5.19e-7`

At the time, the interpretation was: generation length contaminates mean entropy, so switch to prefill-only mode (no generated tokens).

### 2. Prefill-only looked like a fix, but still averaged across positions

The suite then grew from 98 prompts to 168 prompts across 12 levels, and the headline hierarchy appeared to strengthen monotonically under an all-token prefill mean:

| Cumulative prompts | Levels | rho (RE vs level) | Added by |
|--------------------|--------|-------------------|----------|
| 98 | L1-L7 | 0.4994 | `98q-r1` |
| 112 | L1-L8 | 0.6400 | `14q-r3` |
| 126 | L1-L9 | 0.7012 | `14q-r1` |
| 140 | L1-L10 | 0.7647 | `14q-r2` |
| 154 | L1-L11 | 0.8165 | `14q-r4` |
| 168 | L1-L12 | 0.8517 | `14q-r5` |

Independent DeepSeek R1 replication seemed to confirm it:

| Run | Levels | rho (RE vs level) |
|-----|--------|-------------------|
| `168q-r1` | L1-L12 | `0.8360` |

This was the point where the hierarchy looked strongest and most convincing.

### 3. The actual failure mode (prefill has a position effect)

The key miss was assuming “prefill-only” implies position invariance. It does not.

In the R1 168q prefill run:
- RE vs level: `rho=0.8360`, `p=3.91e-45`
- RE vs token count: `rho=0.8589`, `p=4.05e-50`

Token count explained the result at least as well as the supposed complexity variable. The prompt suite itself was length-structured, so averaging across all prefill tokens baked in a positional artifact.

### 4. A position control broke the hierarchy (and generalized)

The decisive move was to compare all-token mean RE against **a fixed-position RE** (last prompt token).

| Model | All-token rho vs level | Last-token rho vs level | All-token rho vs tokens |
|-------|------------------------|-------------------------|-------------------------|
| DeepSeek V3.1 | `+0.8019` | `+0.0177` | `+0.8797` |
| Qwen 397B | `+0.6166` | `-0.0622` | `+0.7813` |

Last-token RE removes the positional averaging confound by construction. Under that control, the hierarchy disappears in both models.

### 5. A partial raw recovery shows the same caution on a different suite

Raw router captures from `ds31-v22-32q-1` were recovered from an external SSD (17 of 32 prompts, L1-L3 only, v2.2 choice-format prompts). These are longer, more uniform prompts (227-245 tokens) from a different suite than the 12-level hierarchy: structured operational triage prompts with tightly controlled wording and JSON-output instructions. Recomputed from `.npy` files:

| Metric pair | rho | p |
|-------------|-----|---|
| all-token RE vs token count | **-0.657** | 0.004 |
| all-token RE vs level | -0.579 | 0.015 |
| last-token RE vs level | +0.582 | 0.014 |

Even here, **token count explains more variance than level**. Because this recovery is only 17 prompts from a tightly templated L1-L3 subset, it is supporting evidence rather than a headline result. Full details in `PARTIAL-RESULTS.md`.

### 6. What survived (and what did not)

The hierarchy claim failed. The confound survived.

Validated:
- routing entropy rises with token position during prefill
- this effect appears in DeepSeek V3.1, DeepSeek R1, and Qwen 397B
- last-token RE is much safer than all-token mean RE when prompt lengths differ
- for the R1 generation run, slope is more robust than mean RE against token-count confounding

Invalidated:
- the original "complexity hierarchy" interpretation
- the belief that prefill-only mode had removed the confound
- the use of R1 replication as confirmation of a complexity effect

## Why This Matters

This archive is worth preserving because the mistake is general: if MoE routing entropy is averaged over prompts with different token lengths, prompt length can masquerade as cognition, difficulty, or task structure.

The mechanistic result that remains is narrower but real:
- MoE routing entropy is position-sensitive.
- The size of that effect differs by model.
- Position-controlled metrics are required before claiming between-prompt routing differences.
