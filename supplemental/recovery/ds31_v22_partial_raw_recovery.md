# ds31-v22-32q-1 Partial Raw Recovery

This is a partial raw recomputation from `/Volumes/ExternalSSD/llama-eeg-tests/ds31-v22-32q-1/output`.

What was recoverable:
- complete prompts with raw router capture: `17`
- broken prompt directories present but incomplete: `1`
- expected prompts missing entirely: `14`

Gate assumption:
- DeepSeek V3.1 sigmoid gate reconstructed via `sigmoid(logits)` + noaux_tc group filtering + top-k + renormalization

Coverage:
- recovered prompt IDs: `L1_A1, L1_A2, L1_B1, L1_B2, L1_C1, L1_C2, L1_D1, L1_D2, L2_A1, L2_A2, L2_B1, L2_B2, L2_C1, L2_C2, L2_D1, L2_D2, L3_A1`
- broken prompt IDs: `L3_A2`
- missing prompt IDs: `L3_B1, L3_B2, L3_C1, L3_C2, L3_D1, L3_D2, L4_A1, L4_A2, L4_B1, L4_B2, L4_C1, L4_C2, L4_D1, L4_D2`

## Per-Level Summary

| Level | n | Mean all-token RE | Mean last-token RE | Mean tokens |
|-------|---|-------------------|--------------------|-------------|
| L1 | 8 | 0.961820 | 0.943339 | 227.00 |
| L2 | 8 | 0.961210 | 0.944267 | 230.00 |
| L3 | 1 | 0.961707 | 0.943729 | 245.00 |

## Subset Correlations

- all-token RE vs level: `rho=-0.5789612716571944` `p=0.014883237910398958`
- last-token RE vs level: `rho=0.5817116814987962` `p=0.014303952465020758`
- all-token RE vs prompt tokens: `rho=-0.6572042169844519` `p=0.004148429286056417`
- last-token RE vs prompt tokens: `rho=0.5901172080673245` `p=0.012643058728660776`

These correlations are only for the recoverable subset, so they should not be interpreted as the full run result.

## Existing Summary Cross-Check

- overlapping prompt IDs found in existing summary JSON: `17`
- token count mismatches on overlap: `0`
- generation count mismatches on overlap: `0`

## Per-Prompt RE

| Prompt | Level | Tokens | All-token RE | Last-token RE | Layers |
|--------|-------|--------|--------------|---------------|--------|
| L1_A1 | L1 | 227 | 0.962373 | 0.943523 | 58 |
| L1_A2 | L1 | 226 | 0.962189 | 0.943230 | 58 |
| L1_B1 | L1 | 228 | 0.961431 | 0.944304 | 58 |
| L1_B2 | L1 | 227 | 0.962021 | 0.943005 | 58 |
| L1_C1 | L1 | 227 | 0.961810 | 0.943889 | 58 |
| L1_C2 | L1 | 229 | 0.961389 | 0.942722 | 58 |
| L1_D1 | L1 | 226 | 0.961607 | 0.943237 | 58 |
| L1_D2 | L1 | 226 | 0.961745 | 0.942806 | 58 |
| L2_A1 | L2 | 230 | 0.961624 | 0.945017 | 58 |
| L2_A2 | L2 | 229 | 0.961455 | 0.944271 | 58 |
| L2_B1 | L2 | 231 | 0.960694 | 0.943883 | 58 |
| L2_B2 | L2 | 230 | 0.961340 | 0.944339 | 58 |
| L2_C1 | L2 | 230 | 0.961259 | 0.944188 | 58 |
| L2_C2 | L2 | 232 | 0.960704 | 0.944489 | 58 |
| L2_D1 | L2 | 229 | 0.961223 | 0.944238 | 58 |
| L2_D2 | L2 | 229 | 0.961379 | 0.943715 | 58 |
| L3_A1 | L3 | 245 | 0.961707 | 0.943729 | 58 |

## Interpretation

- This file recovers raw sigmoid-based RE for the prompts that actually exist on disk.
- It does not reconstruct the full 32-prompt prefill run.
- It does not reconstruct the generation-side commitment-token analysis, because these raw captures are prefill-only (`n_tokens_generated=0`).
- The recovered prompts are tightly templated operational triage tasks, not the open-ended hierarchy prompts used in the main confound story.
- Within the recovered subset, the main variation is rule complexity inside a largely fixed prompt scaffold, so this file is better read as a recovery and robustness check than as a standalone hierarchy result.
