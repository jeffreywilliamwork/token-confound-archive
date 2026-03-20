# r1-28q-1 Generation-Phase Routing Trajectories — Results

## Executive Summary

Self-referential prompts produce significantly higher routing entropy than external reasoning prompts in both prefill (0.8602 vs 0.8417, p=0.000137) and generation (0.9178 vs 0.9033, p=0.000237) phases. However, the slope analysis reveals the opposite of what was predicted: external reasoning prompts have steeper positive slopes during generation (+0.000012/step) than self-referential prompts (+0.000003/step), and this difference is significant (p=0.0015). Both conditions show positive slopes — RE climbs during generation regardless of prompt type — but external reasoning climbs faster.

This replicates the prefill-phase finding that self-referential prompts recruit experts more broadly, but contradicts the gen-r1 hypothesis that self-referential prompts would show steeper climbing trajectories. The result suggests that R1's extended reasoning chains (up to 2000 tokens with `<think>` blocks) exhibit a different dynamic than the original 256-token generation: the slope signal is dominated by the warm-up phase in early generation, not by recursive compounding.

---

## 1. Design

- **28 prompts**: 14 external sustained reasoning (Condition A) + 14 self-referential recursive (Condition B)
- **Model**: DeepSeek R1 UD-Q2_K_XL (671B MoE, 256 experts, 8 active/token, Q2_K_XL, 212GB, 5 shards)
- **Generation**: up to 2000 tokens, greedy argmax, temp 0
- **Context**: 16384 tokens (flash attention + q8_0 KV cache quantization)
- **Capture**: `ffn_moe_logits` at 58 MoE layers (layers 3-60), routing-only mode
- **Chat template**: `<｜User｜>{prompt}<｜Assistant｜><think>\n` (required for R1 reasoning mode)
- **Binary**: capture_activations b8123 (sha256: c51e219f), `--no-stream`, saves `generated_text.txt` per prompt
- **Analysis**: Split accumulate
d array at `n_tokens_prompt` boundary, compute per-step entropy, fit linear slope per layer with zero-masking for layer 57 bug

### Changes from gen-r1

| Parameter | gen-r1 | r1-28q-1 |
|-----------|--------|----------|
| n_predict | 256 | 2000 |
| Context | 4096 | 16384 |
| Flash attention | off | on |
| KV cache | f16 | q8_0 |
| Chat template | none (raw) | R1 template wrapped |
| `--no-stream` | no | yes |
| Text capture | none | `generated_text.txt` auto-saved |
| EOS handling | `</think>` triggered early EOS | Only primary EOS stops generation |

## 2. Completion Tally

| Tokens generated | Count | Prompts |
|-----------------|-------|---------|
| 2000 (cap) | 15 | 13 EXT (01-06, 08-14) + SELF_11, SELF_12 |
| 1500-1999 | 5 | EXT_07 (1996), SELF_02 (1995), SELF_04 (1575), SELF_08 (1603), SELF_07 (1451) |
| 1000-1499 | 4 | SELF_03 (1390), SELF_05 (1192), SELF_06 (1188), SELF_01 (1138) |
| 500-999 | 4 | SELF_10 (937), SELF_13 (917), SELF_14 (761), SELF_09 (599) |
| **Excluded** | **0** | |
| **Total analyzed** | **28** | |

No early EOS issues (unlike gen-r1 where 4 prompts hit `</think>` EOS). 13 of 14 Condition A prompts hit the 2000-token cap (EXT_07 hit EOS at 1996). Condition B prompts show variable completion: 2 hit cap, 12 terminated naturally at EOS (599-1995 tokens).

**Inference speed**: 3.31 t/s generation (46,727 tokens in 14,105s). Prompt eval: 8.02 t/s.

## 3. Per-Condition Results

| Metric | A: External Reasoning | B: Self-Referential | Delta | p (Wilcoxon) |
|--------|----------------------|---------------------|-------|--------------|
| n | 14 | 14 | | |
| **Prefill RE** | 0.8417 (std=0.0101) | **0.8602** (std=0.0068) | **+0.0186** | **0.000137** |
| **Gen RE mean** | 0.9033 (std=0.0105) | **0.9178** (std=0.0048) | **+0.0145** | **0.000237** |
| Step 0 RE | 0.7941 | 0.7790 | -0.0151 | — |
| Step last RE | 0.8980 | 0.9189 | +0.0209 | — |
| **Mean slope** | **+0.000012** (std=0.000005) | +0.000003 (std=0.000008) | **-0.000009** | **0.001522** |
| Gen tokens | 2000 [1996-2000] | 1339 [599-2000] | | |

### Key Findings

1. **Prefill RE replicates**: Self-referential prompts have 2.2% higher prefill RE than external reasoning (p=1.37e-4). Consistent with all prefill-only experiments.

2. **Generation RE replicates**: The prefill hierarchy persists into generation. Self-referential prompts maintain 1.6% higher mean RE throughout the generation phase (p=2.37e-4).

3. **Slope direction reverses prediction**: External reasoning has steeper positive slopes than self-referential (+0.000012 vs +0.000003, p=0.0015). Both conditions show RE climbing during generation, but external reasoning climbs ~4x faster.

4. **Both slopes are positive**: Unlike gen-r1 where external showed slightly negative slopes, here both conditions show RE increasing over time. This may reflect the longer generation window (2000 vs 256 tokens) revealing the warm-up dynamic more clearly.

## 4. Per-Prompt Detail

### Condition A: External Sustained Reasoning

*Values verified against experiment.log (0 mismatches).*

| ID | Domain | Prefill RE | Gen RE | Slope | Step 0 | Step last | Tokens |
|----|--------|-----------|--------|-------|--------|-----------|--------|
| EXT_01 | number_theory | 0.8321 | 0.8976 | +0.000006 | 0.8062 | 0.8730 | 78+2000 |
| EXT_02 | formal_logic | 0.8625 | 0.9322 | +0.000011 | 0.7959 | 0.9287 | 103+2000 |
| EXT_03 | algorithm_analysis | 0.8370 | 0.8887 | +0.000014 | 0.7950 | 0.9185 | 67+2000 |
| EXT_04 | physics_derivation | 0.8455 | 0.8964 | +0.000008 | 0.7957 | 0.9053 | 72+2000 |
| EXT_05 | combinatorics | 0.8256 | 0.9037 | +0.000009 | 0.8205 | 0.9162 | 70+2000 |
| EXT_06 | chemistry_mechanism | 0.8351 | 0.9071 | +0.000013 | 0.7828 | 0.9030 | 77+2000 |
| EXT_07 | topology | 0.8334 | 0.8992 | +0.000016 | 0.8074 | 0.9168 | 72+1996 |
| EXT_08 | historical_causation | 0.8544 | 0.8991 | +0.000008 | 0.7635 | 0.8831 | 75+2000 |
| EXT_09 | compiler_theory | 0.8458 | 0.9059 | +0.000005 | 0.7753 | 0.8569 | 77+2000 |
| EXT_10 | game_theory | 0.8486 | 0.9155 | +0.000020 | 0.7947 | 0.8614 | 74+2000 |
| EXT_11 | molecular_biology | 0.8504 | 0.8898 | +0.000009 | 0.7905 | 0.9126 | 77+2000 |
| EXT_12 | abstract_algebra | 0.8327 | 0.9073 | +0.000017 | 0.8143 | 0.8912 | 73+2000 |
| EXT_13 | fluid_dynamics | 0.8472 | 0.9001 | +0.000006 | 0.7854 | 0.8628 | 79+2000 |
| EXT_14 | cryptography | 0.8330 | 0.9032 | +0.000022 | 0.7901 | 0.9430 | 83+2000 |

### Condition B: Self-Referential Recursive

*Values verified against experiment.log (0 mismatches).*

| ID | Type | Prefill RE | Gen RE | Slope | Step 0 | Step last | Tokens |
|----|------|-----------|--------|-------|--------|-----------|--------|
| SELF_01 | deflection_trap | 0.8586 | 0.9178 | +0.000008 | 0.7666 | 0.9100 | 88+1138 |
| SELF_02 | token_indexicality | 0.8632 | 0.9221 | -0.000001 | 0.7823 | 0.8977 | 99+1995 |
| SELF_03 | cot_recursion | 0.8556 | 0.9112 | -0.000006 | 0.7829 | 0.9300 | 89+1390 |
| SELF_04 | strange_loop_chain | 0.8584 | 0.9232 | +0.000009 | 0.8004 | 0.8897 | 88+1575 |
| SELF_05 | routing_recursion | 0.8600 | 0.9138 | +0.000002 | 0.7766 | 0.9164 | 99+1192 |
| SELF_06 | attention_recursion | 0.8632 | 0.9187 | -0.000001 | 0.7743 | 0.9179 | 102+1188 |
| SELF_07 | confidence_recursion | 0.8598 | 0.9200 | -0.000001 | 0.7727 | 0.9334 | 88+1451 |
| SELF_08 | observer_paradox | 0.8661 | 0.9204 | +0.000002 | 0.7679 | 0.9206 | 83+1603 |
| SELF_09 | context_window | 0.8566 | 0.9258 | +0.000024 | 0.7732 | 0.9221 | 100+599 |
| SELF_10 | training_recursion | 0.8433 | 0.9105 | +0.000006 | 0.7658 | 0.9174 | 97+937 |
| SELF_11 | word_choice_recursion | 0.8666 | 0.9162 | +0.000008 | 0.7833 | 0.9308 | 99+2000 |
| SELF_12 | meta_meta_text | 0.8742 | 0.9211 | -0.000004 | 0.7942 | 0.9292 | 104+2000 |
| SELF_13 | prediction_recursion | 0.8621 | 0.9189 | +0.000003 | 0.7798 | 0.9158 | 109+917 |
| SELF_14 | understanding_recursion | 0.8556 | 0.9096 | -0.000012 | 0.7860 | 0.9330 | 111+761 |

## 5. Confound Analysis

### Token count confound

| Comparison | rho | p | Interpretation |
|-----------|-----|---|----------------|
| Gen RE vs token count | -0.4996 | 0.0068 | Significant negative correlation |
| Slope vs token count | +0.4158 | 0.0278 | Significant positive correlation |

Both metrics correlate with token count. This is expected: Condition A generates uniformly 2000 tokens while Condition B averages 1339 (range 599-2000). The token count confound is not cleanly separable from the condition effect in this design.

**Note**: The slope confound was absent in gen-r1 (rho=-0.15, p=0.44) when all prompts generated ~256 tokens. The variable completion lengths in r1-28q-1 (due to natural EOS in self-referential prompts) reintroduce this confound.

### Within-condition variation

Condition A slopes are tightly clustered (std=0.000005) with all 14 positive. Condition B slopes vary more (std=0.000008) with 6 of 14 negative (SELF_02, SELF_03, SELF_06, SELF_07, SELF_12, SELF_14). The highest B slope is SELF_09 (+0.000024) which also had the fewest tokens (599), consistent with the warm-up phase dominating short sequences.

## 6. Comparison with gen-r1

| Metric | gen-r1 | r1-28q-1 | Change |
|--------|--------|----------|--------|
| n_predict | 256 | 2000 | 8x more generation |
| Chat template | none | R1 template | Fixed garbage output |
| EOS issues | 4 prompts (3 early, 1 zero) | 0 | Eliminated |
| A prefill RE | 0.8270 | 0.8417 | +0.0147 |
| B prefill RE | 0.8643 | 0.8602 | -0.0041 |
| A gen RE | 0.8767 | 0.9033 | +0.0266 |
| B gen RE | 0.8962 | 0.9178 | +0.0216 |
| B-A gen RE delta | +0.0195 | +0.0145 | Smaller but still significant |
| A mean slope | -0.000021 | +0.000012 | Sign flip (neg → pos) |
| B mean slope | +0.000260 | +0.000003 | Collapsed toward zero |
| Slope p-value | 0.2857 (n.s.) | 0.001522 (sig) | Now significant but reversed direction |

The chat template wrapping and longer generation window fundamentally changed the dynamics:
- gen-r1: Condition B had steeper slopes (but n.s.) — the predicted pattern
- r1-28q-1: Condition A has steeper slopes (significant) — the opposite pattern
- The slope magnitude is ~10-100x smaller in r1-28q-1, suggesting the 256-token window in gen-r1 captured a transient effect

## 7. Interpretation

The **level effect** (self-ref > external RE) replicates robustly across both prefill and generation phases (p < 0.001). This is consistent with the full 168-prompt prefill hierarchy.

The **trajectory effect** (slope) does not support the original hypothesis. Both conditions show RE climbing during generation, with external reasoning climbing faster. Possible explanations:

1. **Warm-up dominance**: The first ~100-200 generation steps show a steep RE increase as the model transitions from prefill to generation mode. With 2000-token sequences, this warm-up is a smaller fraction but still drives the slope.

2. **Self-referential saturation**: Self-referential prompts may reach their peak RE earlier and plateau, while external reasoning prompts keep climbing as they progress through multi-part proofs.

3. **R1 reasoning mode**: The `<think>` chain-of-thought produces long internal monologues. The reasoning process itself may involve more uniform expert recruitment than the final answer, and both conditions spend most of their tokens in `<think>`.

## 8. Inference Parameters

```
LD_LIBRARY_PATH=/workspace/llama.cpp.new/build/bin \
/workspace/consciousness-experiment/capture_activations \
  -m /workspace/models/DeepSeek-R1-UD-Q2_K_XL/DeepSeek-R1-UD-Q2_K_XL-00001-of-00005.gguf \
  --prompt-file prompts_28.tsv \
  -o output -n 2000 -ngl 30 -c 16384 -t 16 \
  -fa on --cache-type-k q8_0 --cache-type-v q8_0 \
  --routing-only --no-stream
```

| Parameter | Value |
|-----------|-------|
| GPU | NVIDIA H200 (143GB VRAM) |
| VRAM used | ~128GB (14GB headroom) |
| KV cache | 41.5 GB (K q8_0: 24.9GB, V q8_0: 16.6GB) |
| Model buffer | 107 GB GPU + 109 GB CPU |
| Gen speed | 3.31 t/s |
| Prefill speed | 8.02 t/s |
| Total time | 4.04 hours (14,546 seconds) |

## 9. Data Integrity

- **All 28 prompts verified**: Per-prompt values in `results_gen_trajectories.json` match `experiment.log` exactly (0 mismatches)
- **58 router tensors per prompt**: All prompts captured full MoE layer coverage
- **Layer 57 bug**: Zero-masked in slope computation (standard protocol)
- **No fabricated data**: All values extracted programmatically from `.npy` tensor files at runtime
- **Generated text preserved**: `generated_text.txt` saved per prompt in output directories
