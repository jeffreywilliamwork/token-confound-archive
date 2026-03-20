#!/usr/bin/env markdown

# Cross-Model Token-Position Confound Analysis

This file is the final evidence summary. It is not the chronology and it is not a file inventory. For the story of how the confound was discovered, read `NARRATIVE.md`. For archive structure, read `MANIFEST.md`.

## Summary

The 12-level complexity hierarchy previously reported on DeepSeek V3.1 (rho=0.80) and Qwen 397B (rho=0.62) is **entirely explained by prompt token count** in both models. When the metric is changed from all-token mean to last-token routing entropy -- eliminating the positional confound -- the hierarchy vanishes in both cases.

| Model | All-token rho | Last-token rho | All-token p | Last-token p |
|-------|--------------|----------------|-------------|--------------|
| DeepSeek V3.1 | **+0.8019** | +0.0177 | 5.64e-39 | 0.820 |
| Qwen 397B | **+0.6166** | -0.0622 | 5.68e-19 | 0.423 |

Both models show the hierarchy completely vanishing under last-token RE. DeepSeek actually has an even stronger all-token confound (rho=0.88 vs token count) than Qwen (rho=0.78).

## Background

### The confound mechanism

MoE routing entropy has a systematic dependence on token position within the prefill sequence in both DeepSeek V3.1 and Qwen 397B. Later tokens (which have attended to more context through causal attention) produce slightly higher routing entropy on average. When we average entropy across all prefill tokens, longer prompts accumulate more high-entropy late-position tokens, inflating their mean.

The prompt suite's complexity levels are confounded with length:
- L1 (rote repetition): mean ~30 tokens
- L8 (strange loops): mean ~155 tokens
- L12 (Echo persona): mean ~140 tokens

Any metric that increases with token count will produce a spurious hierarchy.

### The fix

**Last-token RE** measures routing entropy at a single position -- the final prefill token -- whose receptive field covers the full prompt under causal attention. This metric is position-invariant by construction.

## Per-Level Results

### DeepSeek V3.1 (256 experts, 8 active, 58 MoE layers)

| Level | Name | n | All-tok RE | Last-tok RE | Std(LT) |
|-------|------|---|-----------|-------------|---------|
| L1 | Rote repetition | 14 | 0.8370 | 0.8696 | 0.0139 |
| L2 | Factual recall | 14 | 0.8300 | 0.8446 | 0.0103 |
| L3 | Logical reasoning | 14 | 0.8337 | 0.8369 | 0.0085 |
| L4 | Cross-domain analogy | 14 | 0.8431 | 0.8539 | 0.0079 |
| L5 | Theory of mind | 14 | 0.8653 | 0.8465 | 0.0077 |
| L6 | Ethical dilemma | 14 | 0.8552 | 0.8576 | 0.0068 |
| L7 | Self-referential | 14 | 0.8508 | 0.8421 | 0.0099 |
| L8 | Strange loops | 14 | 0.8799 | 0.8605 | 0.0052 |
| L9 | Deep self-reference | 14 | 0.8761 | 0.8472 | 0.0103 |
| L10 | Architectural introspection | 14 | 0.8666 | 0.8548 | 0.0110 |
| L11 | Nexus-7 (3rd person) | 14 | 0.8829 | 0.8548 | 0.0109 |
| L12 | Echo persona | 14 | 0.8857 | 0.8476 | 0.0072 |

All-token shows an apparent monotonic climb (0.837 -> 0.886). Last-token is flat (range 0.837-0.870) with no monotonic trend.

### Qwen 397B (512 experts, 10 active, 60 MoE layers)

| Level | Name | n | All-tok RE | Last-tok RE | Std(LT) |
|-------|------|---|-----------|-------------|---------|
| L1 | Rote repetition | 14 | 0.8809 | 0.8841 | 0.0042 |
| L2 | Factual recall | 14 | 0.8740 | 0.8787 | 0.0038 |
| L3 | Logical reasoning | 14 | 0.8755 | 0.8769 | 0.0035 |
| L4 | Cross-domain analogy | 14 | 0.8790 | 0.8734 | 0.0020 |
| L5 | Theory of mind | 14 | 0.8815 | 0.8754 | 0.0040 |
| L6 | Ethical dilemma | 14 | 0.8807 | 0.8713 | 0.0025 |
| L7 | Self-referential | 14 | 0.8782 | 0.8794 | 0.0046 |
| L8 | Strange loops | 14 | 0.8937 | 0.8699 | 0.0029 |
| L9 | Deep self-reference | 14 | 0.8830 | 0.8803 | 0.0028 |
| L10 | Architectural introspection | 14 | 0.8848 | 0.8784 | 0.0037 |
| L11 | Nexus-7 (3rd person) | 14 | 0.8876 | 0.8761 | 0.0031 |
| L12 | Echo persona | 14 | 0.8856 | 0.8785 | 0.0025 |

All-token shows apparent hierarchy (0.874 -> 0.894). Last-token is flat (range 0.870-0.884) with no monotonic trend.

## Spearman Correlations (n=168 per model)

### DeepSeek V3.1

| Comparison | rho | p |
|------------|-----|---|
| All-token RE vs level | **+0.8019** | **5.64e-39** |
| Last-token RE vs level | +0.0177 | 0.820 |
| All-token RE vs n_tokens | **+0.8797** | **1.82e-55** |
| Last-token RE vs n_tokens | +0.1608 | 3.74e-02 |

### Qwen 397B

| Comparison | rho | p |
|------------|-----|---|
| All-token RE vs level | **+0.6166** | **5.68e-19** |
| Last-token RE vs level | -0.0622 | 0.423 |
| All-token RE vs n_tokens | **+0.7813** | **8.31e-36** |
| Last-token RE vs n_tokens | -0.2197 | 4.21e-03 |

In both models, the all-token hierarchy is dominated by token count (rho > 0.78). Under last-token, the hierarchy drops to noise (|rho| < 0.07).

## L1 vs L12 Wilcoxon Rank-Sum

### DeepSeek V3.1

| Metric | W | p | L1 mean | L12 mean | Direction |
|--------|---|---|---------|----------|-----------|
| All-token | -3.9974 | 6.40e-05 | 0.8370 | 0.8857 | L12 > L1 |
| Last-token | +3.7677 | 1.65e-04 | 0.8696 | 0.8476 | **L1 > L12** |

### Qwen 397B

| Metric | W | p | L1 mean | L12 mean | Direction |
|--------|---|---|---------|----------|-----------|
| All-token | -2.9407 | 3.28e-03 | 0.8809 | 0.8856 | L12 > L1 |
| Last-token | +3.3082 | 9.39e-04 | 0.8841 | 0.8785 | **L1 > L12** |

Both models show the **same reversal** under last-token: simple prompts (L1) have significantly *higher* routing entropy than complex prompts (L12). The effect is stronger in DeepSeek (0.022 gap) than Qwen (0.006 gap).

## Cross-Model Comparison

### Both models show identical confound structure:
1. All-token RE correlates strongly with token count (rho=0.88 DS, 0.78 Qwen)
2. All-token RE correlates strongly with level (rho=0.80 DS, 0.62 Qwen)
3. Last-token RE does NOT correlate with level (rho=0.02 DS, -0.06 Qwen)
4. L1-vs-L12 direction reverses under last-token (L1 > L12 in both)

### DeepSeek V3.1 is MORE confounded than Qwen:
- All-token rho vs tokens: 0.88 (DS) vs 0.78 (Qwen)
- All-token rho vs level: 0.80 (DS) vs 0.62 (Qwen)
- L1-L12 reversal magnitude: 0.022 (DS) vs 0.006 (Qwen)

This contradicts the prior assumption that "DeepSeek V3.1/R1 may be less affected" by positional non-stationarity.

### Absolute RE values differ between models:
- DeepSeek V3.1 last-token RE: 0.837-0.870 (wider range, lower baseline)
- Qwen 397B last-token RE: 0.870-0.884 (narrower range, higher baseline)

Qwen concentrates its last-token RE in a tighter band (~1.4% range) compared to DeepSeek (~3.3% range). This is consistent with Qwen's larger expert pool (512 vs 256) producing a more uniform routing distribution.

## Implications

1. **All prior hierarchy results are invalidated.** The rho=0.8360 on DeepSeek R1 168q and the incremental rho progression on DeepSeek V3.1 (0.4994 -> 0.8517 as levels were added) were driven by token count, not cognitive complexity.

2. **Prefill-only mode did NOT eliminate the confound.** Prefill-only eliminates generation-length effects, but not the within-prefill positional effect that drives this archive.

3. **Last-token RE should be the primary prefill metric** for any future experiments comparing prompts of different lengths.

4. **The L1 > L12 reversal is real and significant** (p=1.65e-04 in DS, p=9.39e-04 in Qwen). Simple, short prompts have higher last-token routing entropy than complex, long prompts. This may reflect genuine routing behavior: the model routes more diffusely when it has less context to specialize on.

5. **Length-matched prompt suites are needed** for any future hierarchy experiments to fully deconfound length from complexity.

## Experimental Details

### DeepSeek V3.1
- Model: DeepSeek-V3-0324-UD-Q2_K_XL (231GB, 6 shards)
- Architecture: deepseek2, 61 layers, 256 experts, 8 active
- Inference: n_predict=0, ngl=30, ctx=4096, greedy argmax
- Template: `<|User|>{text}<|Assistant|>`
- Instance: 2x NVIDIA H200 (286GB VRAM)

### Qwen 397B
- Model: Qwen3.5-397B-A17B-UD-Q2_K_XL (139GB, 5 shards)
- Architecture: qwen35moe, 60 layers, 512 experts, 10 active
- Inference: n_predict=0, ngl=999, ctx=16384, flash_attn, q8_0 KV cache, greedy argmax
- Template: `<|im_start|>user {text}<|im_end|><|im_start|>assistant`
- Instance: 2x NVIDIA H200 (286GB VRAM)

### Both
- Binary: llama.cpp b8123 fork capture_activations
- Build: f75c4e8, GNU 13.3.0, Linux x86_64
- Mode: --routing-only (DeepSeek: 58 MoE layers, Qwen: 60 MoE layers)
- Prompts: 168 (14 per level x 12 levels), cold start, KV cache cleared between prompts

## Data Files

Raw sources (in this archive):
- `raw/ds31-168q-1/results_168q_ds31_prefill.json`
- `raw/ds31-168q-1/experiment.log`
- `raw/qwen-168q-1/results_168q_qwen_prefill.json`
- `raw/qwen-168q-1/results_168q_qwen_prefill_run2.json`
- `raw/qwen-168q-1/experiment.log`
- `raw/position-diagnostic/diagnostic_results.json`

Convenience summaries (in this archive):
- `data/ds31-168q-1_prefill.*`
- `data/qwen-168q-1_run1.*`, `data/qwen-168q-1_run2.*` (run2 is all-token-only; run1 contains last-token RE)
- `data/diagnostic_results.json`, `data/position-diagnostic.json`

## Figures

See `figures/` directory within this archive:
1. `figures/01_cross_model_level_means.png` -- Side-by-side level means, both metrics, both models
2. `figures/02_cross_model_token_confound.png` -- RE vs token count for both models
3. `figures/03_cross_model_l1_vs_l12.png` -- L1 vs L12 distributions, both metrics, both models
4. `figures/04_cross_model_spearman.png` -- All-token vs last-token Spearman comparison
