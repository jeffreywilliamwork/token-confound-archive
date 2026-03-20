# 14q-ds31-run1_gen

## Run Info

- **Source**: `raw/preconfound/14q-ds31-run1/results_gen_trajectories.json`
- **Recalculated**: 2026-03-07T21:10:29.985230
- **Model**: DeepSeek-V3.1 UD-Q2_K_XL
- **Mode**: prefill_plus_generation_per_step
- **N prompts**: 28

## Inference Parameters

- **ngl**: 30
- **n_predict**: 2000
- **ctx**: 16384
- **flash_attn**: True
- **cache_type_k**: q8_0
- **cache_type_v**: q8_0
- **sampling**: greedy_argmax
- **routing_only**: True
- **no_stream**: True

## Overall Statistics

- **mean_prefill_re**: 0.856307
- **std_prefill_re**: 0.017466
- **mean_gen_re**: 0.907367
- **std_gen_re**: 0.014809
- **mean_slope**: 0.000007
- **std_slope**: 0.000020

## Per-Condition Statistics

| Condition | n | Mean Prefill RE | Mean Gen RE | Mean Slope |
|-----------|---|-----------------|-------------|------------|
| external_sustained_reasoning | 14 | 0.841948 | 0.898248 | 1.726463e-05 |
| self_referential_recursive | 14 | 0.870667 | 0.916486 | -2.392667e-06 |

## Per-Prompt Data

| id | condition | condition_name | prefill_re | gen_re | gen_re_step0 | gen_re_step_last | mean_slope | n_prompt_tokens | n_gen_tokens |
|---|---|---|---|---|---|---|---|---|---|
| EXT_01 | A | external_sustained_reasoning | 0.829301 | 0.889530 | 0.847972 | 0.911970 | 1.425302e-05 | 77 | 1097 |
| EXT_02 | A | external_sustained_reasoning | 0.860581 | 0.933853 | 0.844579 | 0.928303 | 1.123937e-05 | 102 | 1940 |
| EXT_03 | A | external_sustained_reasoning | 0.832914 | 0.889453 | 0.819000 | 0.926245 | 1.923815e-05 | 66 | 1701 |
| EXT_04 | A | external_sustained_reasoning | 0.848913 | 0.893772 | 0.826682 | 0.939686 | 1.126225e-05 | 71 | 1238 |
| EXT_05 | A | external_sustained_reasoning | 0.820788 | 0.896196 | 0.807217 | 0.908068 | 1.530000e-05 | 69 | 1929 |
| EXT_06 | A | external_sustained_reasoning | 0.836520 | 0.899429 | 0.897285 | 0.933043 | 2.215049e-05 | 76 | 1402 |
| EXT_07 | A | external_sustained_reasoning | 0.835314 | 0.898713 | 0.815922 | 0.906895 | 2.406596e-05 | 71 | 1021 |
| EXT_08 | A | external_sustained_reasoning | 0.862700 | 0.902273 | 0.885527 | 0.935752 | -1.471516e-07 | 74 | 1199 |
| EXT_09 | A | external_sustained_reasoning | 0.849954 | 0.893477 | 0.840668 | 0.920963 | 9.468402e-06 | 76 | 757 |
| EXT_10 | A | external_sustained_reasoning | 0.848617 | 0.900189 | 0.830746 | 0.921717 | 2.583923e-05 | 73 | 1465 |
| EXT_11 | A | external_sustained_reasoning | 0.850985 | 0.883389 | 0.855778 | 0.910195 | 2.390956e-05 | 76 | 1174 |
| EXT_12 | A | external_sustained_reasoning | 0.826917 | 0.904545 | 0.805426 | 0.930090 | 2.132455e-05 | 72 | 1646 |
| EXT_13 | A | external_sustained_reasoning | 0.849378 | 0.893422 | 0.827946 | 0.933705 | 3.005996e-05 | 78 | 1143 |
| EXT_14 | A | external_sustained_reasoning | 0.834384 | 0.897226 | 0.834662 | 0.923156 | 1.374099e-05 | 82 | 1731 |
| SELF_01 | B | self_referential_recursive | 0.872112 | 0.914600 | 0.849719 | 0.931940 | -7.234958e-06 | 87 | 343 |
| SELF_02 | B | self_referential_recursive | 0.868590 | 0.907840 | 0.866875 | 0.930615 | 3.547337e-05 | 98 | 472 |
| SELF_03 | B | self_referential_recursive | 0.864459 | 0.913639 | 0.870036 | 0.936911 | -3.237282e-05 | 88 | 258 |
| SELF_04 | B | self_referential_recursive | 0.869194 | 0.940741 | 0.878988 | 0.932800 | 7.501409e-06 | 87 | 2000 |
| SELF_05 | B | self_referential_recursive | 0.869779 | 0.919350 | 0.869336 | 0.922322 | 2.379454e-05 | 98 | 191 |
| SELF_06 | B | self_referential_recursive | 0.875939 | 0.916866 | 0.887020 | 0.943587 | -2.632958e-05 | 101 | 400 |
| SELF_07 | B | self_referential_recursive | 0.872675 | 0.918517 | 0.827263 | 0.936663 | 9.295303e-06 | 87 | 559 |
| SELF_08 | B | self_referential_recursive | 0.872916 | 0.909474 | 0.860863 | 0.932831 | -6.073474e-06 | 82 | 682 |
| SELF_09 | B | self_referential_recursive | 0.866383 | 0.942194 | 0.925540 | 0.952192 | 7.800491e-06 | 99 | 2000 |
| SELF_10 | B | self_referential_recursive | 0.866389 | 0.911943 | 0.859673 | 0.932710 | 1.333078e-05 | 96 | 363 |
| SELF_11 | B | self_referential_recursive | 0.876765 | 0.914686 | 0.889368 | 0.908787 | 9.819265e-06 | 98 | 1071 |
| SELF_12 | B | self_referential_recursive | 0.882075 | 0.914010 | 0.800445 | 0.936677 | 1.651404e-06 | 103 | 334 |
| SELF_13 | B | self_referential_recursive | 0.868663 | 0.908593 | 0.866633 | 0.926096 | -1.187027e-05 | 108 | 357 |
| SELF_14 | B | self_referential_recursive | 0.863399 | 0.898354 | 0.868800 | 0.929624 | -5.828278e-05 | 110 | 260 |
