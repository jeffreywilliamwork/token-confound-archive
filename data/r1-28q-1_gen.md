# r1-28q-1_gen

## Run Info

- **Source**: `raw/r1-28q-1/results_gen_trajectories.json`
- **Recalculated**: 2026-03-07T21:10:29.973427
- **Model**: DeepSeek-R1 UD-Q2_K_XL
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

- **mean_prefill_re**: 0.850949
- **std_prefill_re**: 0.012881
- **mean_gen_re**: 0.910540
- **std_gen_re**: 0.011123
- **mean_slope**: 0.000007
- **std_slope**: 0.000008

## Per-Condition Statistics

| Condition | n | Mean Prefill RE | Mean Gen RE | Mean Slope |
|-----------|---|-----------------|-------------|------------|
| external_sustained_reasoning | 14 | 0.841658 | 0.903272 | 1.175336e-05 |
| self_referential_recursive | 14 | 0.860240 | 0.917807 | 2.608875e-06 |

## Per-Prompt Data

| id | condition | condition_name | prefill_re | gen_re | gen_re_step0 | gen_re_step_last | mean_slope | n_prompt_tokens | n_gen_tokens |
|---|---|---|---|---|---|---|---|---|---|
| EXT_01 | A | external_sustained_reasoning | 0.832124 | 0.897558 | 0.806182 | 0.872988 | 6.437507e-06 | 78 | 2000 |
| EXT_02 | A | external_sustained_reasoning | 0.862498 | 0.932189 | 0.795904 | 0.928702 | 1.068409e-05 | 103 | 2000 |
| EXT_03 | A | external_sustained_reasoning | 0.836987 | 0.888745 | 0.795041 | 0.918516 | 1.439220e-05 | 67 | 2000 |
| EXT_04 | A | external_sustained_reasoning | 0.845486 | 0.896366 | 0.795680 | 0.905337 | 7.799110e-06 | 72 | 2000 |
| EXT_05 | A | external_sustained_reasoning | 0.825573 | 0.903667 | 0.820458 | 0.916246 | 8.566840e-06 | 70 | 2000 |
| EXT_06 | A | external_sustained_reasoning | 0.835103 | 0.907110 | 0.782839 | 0.903022 | 1.314293e-05 | 77 | 2000 |
| EXT_07 | A | external_sustained_reasoning | 0.833358 | 0.899164 | 0.807401 | 0.916810 | 1.631647e-05 | 72 | 1996 |
| EXT_08 | A | external_sustained_reasoning | 0.854421 | 0.899059 | 0.763547 | 0.883126 | 7.900463e-06 | 75 | 2000 |
| EXT_09 | A | external_sustained_reasoning | 0.845812 | 0.905933 | 0.775326 | 0.856878 | 5.458657e-06 | 77 | 2000 |
| EXT_10 | A | external_sustained_reasoning | 0.848628 | 0.915543 | 0.794662 | 0.861354 | 2.004070e-05 | 74 | 2000 |
| EXT_11 | A | external_sustained_reasoning | 0.850386 | 0.889825 | 0.790459 | 0.912605 | 9.002339e-06 | 77 | 2000 |
| EXT_12 | A | external_sustained_reasoning | 0.832686 | 0.907323 | 0.814281 | 0.891212 | 1.653873e-05 | 73 | 2000 |
| EXT_13 | A | external_sustained_reasoning | 0.847159 | 0.900096 | 0.785362 | 0.862830 | 6.223690e-06 | 79 | 2000 |
| EXT_14 | A | external_sustained_reasoning | 0.832992 | 0.903235 | 0.790116 | 0.943043 | 2.204334e-05 | 83 | 2000 |
| SELF_01 | B | self_referential_recursive | 0.858579 | 0.917829 | 0.766593 | 0.909973 | 7.629492e-06 | 88 | 1138 |
| SELF_02 | B | self_referential_recursive | 0.863231 | 0.922075 | 0.782276 | 0.897691 | -1.159762e-06 | 99 | 1995 |
| SELF_03 | B | self_referential_recursive | 0.855646 | 0.911213 | 0.782873 | 0.930036 | -6.365462e-06 | 89 | 1390 |
| SELF_04 | B | self_referential_recursive | 0.858426 | 0.923203 | 0.800380 | 0.889750 | 8.899272e-06 | 88 | 1575 |
| SELF_05 | B | self_referential_recursive | 0.860037 | 0.913814 | 0.776617 | 0.916428 | 1.656214e-06 | 99 | 1192 |
| SELF_06 | B | self_referential_recursive | 0.863172 | 0.918681 | 0.774299 | 0.917887 | -1.155754e-06 | 102 | 1188 |
| SELF_07 | B | self_referential_recursive | 0.859786 | 0.920012 | 0.772743 | 0.933393 | -6.911894e-07 | 88 | 1451 |
| SELF_08 | B | self_referential_recursive | 0.866082 | 0.920417 | 0.767879 | 0.920582 | 2.198996e-06 | 83 | 1603 |
| SELF_09 | B | self_referential_recursive | 0.856623 | 0.925843 | 0.773198 | 0.922124 | 2.412962e-05 | 100 | 599 |
| SELF_10 | B | self_referential_recursive | 0.843297 | 0.910463 | 0.765836 | 0.917381 | 5.675049e-06 | 97 | 937 |
| SELF_11 | B | self_referential_recursive | 0.866601 | 0.916239 | 0.783270 | 0.930756 | 8.467363e-06 | 99 | 2000 |
| SELF_12 | B | self_referential_recursive | 0.874189 | 0.921073 | 0.794235 | 0.929208 | -3.671111e-06 | 104 | 2000 |
| SELF_13 | B | self_referential_recursive | 0.862137 | 0.918854 | 0.779820 | 0.915793 | 2.551117e-06 | 109 | 917 |
| SELF_14 | B | self_referential_recursive | 0.855551 | 0.909585 | 0.786038 | 0.933044 | -1.163959e-05 | 111 | 761 |
