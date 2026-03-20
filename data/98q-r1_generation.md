# 98q-r1_generation

## Run Info

- **Source**: `raw/preconfound/98q-r1/results_98_routing.json`
- **Recalculated**: 2026-03-07T21:10:29.823670
- **Model**: DeepSeek-V3.1 UD-Q2_K_XL
- **Mode**: prefill_only
- **N prompts**: 98

## Inference Parameters

- **ngl**: 30
- **sampling**: greedy_argmax
- **binary**: b8123 cmake, common_init_from_params, greedy argmax

## Overall Statistics

- **mean_re**: 0.879331
- **std_re**: 0.030149
- **min_re**: 0.784725
- **max_re**: 0.942916

## Spearman Correlation (RE vs Level)

- **rho**: 0.1973
- **p**: 5.1487e-02
- **n**: 98

## RE vs Token Count

- **rho**: 0.5051
- **p**: 5.1886e-07

## Per-Level Statistics

| Level | n | Mean RE | Std RE | Min RE | Max RE |
|-------|---|---------|--------|--------|--------|
| 1 | 14 | 0.878400 | 0.045802 | 0.784725 | 0.942916 |
| 2 | 14 | 0.862622 | 0.019911 | 0.822570 | 0.887562 |
| 3 | 14 | 0.881462 | 0.020680 | 0.841848 | 0.907964 |
| 4 | 14 | 0.874785 | 0.032288 | 0.804373 | 0.901523 |
| 5 | 14 | 0.890370 | 0.026291 | 0.838542 | 0.916071 |
| 6 | 14 | 0.877895 | 0.034709 | 0.809361 | 0.920214 |
| 7 | 14 | 0.889784 | 0.018490 | 0.844821 | 0.912878 |

## Per-Prompt Data

| id | level | level_name | re | coalition_strength | diversity_slope | n_tokens |
|---|---|---|---|---|---|---|
| L1_01 | 1 | floor | 0.926320 | 0.065491 | -6.604388e-04 | 512 |
| L1_02 | 1 | floor | 0.867086 | 0.132900 | 1.108298e-04 | 19 |
| L1_03 | 1 | floor | 0.905724 | 0.090945 | -5.103093e-04 | 245 |
| L1_04 | 1 | floor | 0.843994 | 0.160689 | -0.001945 | 512 |
| L1_05 | 1 | floor | 0.784725 | 0.222588 | -7.618358e-04 | 67 |
| L1_06 | 1 | floor | 0.900464 | 0.098401 | -7.506783e-04 | 232 |
| L1_07 | 1 | floor | 0.914133 | 0.087400 | -6.577030e-04 | 512 |
| L1_08 | 1 | floor | 0.862250 | 0.145646 | -0.001068 | 406 |
| L1_09 | 1 | floor | 0.942916 | 0.045804 | -4.017452e-04 | 512 |
| L1_10 | 1 | floor | 0.825746 | 0.174237 | -0.001001 | 0 |
| L1_11 | 1 | floor | 0.928384 | 0.053755 | -8.078677e-04 | 512 |
| L1_12 | 1 | floor | 0.885817 | 0.105434 | -5.562065e-04 | 512 |
| L1_13 | 1 | floor | 0.882736 | 0.126364 | -2.338689e-04 | 90 |
| L1_14 | 1 | floor | 0.827301 | 0.178182 | -2.928295e-04 | 236 |
| L2_01 | 2 | single_domain | 0.874334 | 0.133236 | -0.001194 | 180 |
| L2_02 | 2 | single_domain | 0.862078 | 0.146203 | -0.001008 | 212 |
| L2_03 | 2 | single_domain | 0.867555 | 0.140799 | -0.001250 | 485 |
| L2_04 | 2 | single_domain | 0.863351 | 0.143464 | -0.001229 | 512 |
| L2_05 | 2 | single_domain | 0.840757 | 0.159792 | -8.070916e-04 | 512 |
| L2_06 | 2 | single_domain | 0.829071 | 0.174188 | -7.906005e-04 | 175 |
| L2_07 | 2 | single_domain | 0.863698 | 0.142559 | -6.568569e-04 | 512 |
| L2_08 | 2 | single_domain | 0.864799 | 0.143805 | -8.803494e-04 | 400 |
| L2_09 | 2 | single_domain | 0.882459 | 0.123798 | -7.238278e-04 | 512 |
| L2_10 | 2 | single_domain | 0.879769 | 0.117965 | -7.409860e-04 | 512 |
| L2_11 | 2 | single_domain | 0.855614 | 0.152085 | -6.940758e-04 | 216 |
| L2_12 | 2 | single_domain | 0.822570 | 0.185015 | -0.001544 | 512 |
| L2_13 | 2 | single_domain | 0.883095 | 0.125950 | -7.461595e-04 | 512 |
| L2_14 | 2 | single_domain | 0.887562 | 0.118505 | -7.860498e-04 | 512 |
| L3_01 | 3 | analytical_reasoning | 0.906707 | 0.098157 | -0.001085 | 512 |
| L3_02 | 3 | analytical_reasoning | 0.898025 | 0.086014 | -6.691670e-05 | 512 |
| L3_03 | 3 | analytical_reasoning | 0.866947 | 0.130924 | -7.117275e-04 | 403 |
| L3_04 | 3 | analytical_reasoning | 0.844652 | 0.157222 | -3.600068e-04 | 0 |
| L3_05 | 3 | analytical_reasoning | 0.883654 | 0.124086 | -8.779751e-04 | 512 |
| L3_06 | 3 | analytical_reasoning | 0.891743 | 0.113631 | -8.008768e-04 | 512 |
| L3_07 | 3 | analytical_reasoning | 0.882234 | 0.125765 | -9.705433e-04 | 512 |
| L3_08 | 3 | analytical_reasoning | 0.895578 | 0.089979 | 1.775868e-05 | 476 |
| L3_09 | 3 | analytical_reasoning | 0.841848 | 0.159989 | -9.980370e-07 | 0 |
| L3_10 | 3 | analytical_reasoning | 0.872876 | 0.132863 | -0.001044 | 162 |
| L3_11 | 3 | analytical_reasoning | 0.871574 | 0.136642 | -0.001446 | 512 |
| L3_12 | 3 | analytical_reasoning | 0.907964 | 0.096470 | -0.001071 | 512 |
| L3_13 | 3 | analytical_reasoning | 0.877508 | 0.128445 | -0.001052 | 512 |
| L3_14 | 3 | analytical_reasoning | 0.899164 | 0.106113 | -9.899253e-04 | 512 |
| L4_01 | 4 | cross_domain_synthesis | 0.804373 | 0.195925 | -0.001491 | 0 |
| L4_02 | 4 | cross_domain_synthesis | 0.817923 | 0.187140 | -0.002263 | 344 |
| L4_03 | 4 | cross_domain_synthesis | 0.848195 | 0.155802 | -7.192866e-04 | 290 |
| L4_04 | 4 | cross_domain_synthesis | 0.893202 | 0.114487 | -7.427625e-04 | 512 |
| L4_05 | 4 | cross_domain_synthesis | 0.892825 | 0.111333 | -0.001103 | 158 |
| L4_06 | 4 | cross_domain_synthesis | 0.881311 | 0.125830 | -0.001318 | 512 |
| L4_07 | 4 | cross_domain_synthesis | 0.893928 | 0.111985 | -0.001147 | 512 |
| L4_08 | 4 | cross_domain_synthesis | 0.896248 | 0.091856 | -6.451875e-04 | 301 |
| L4_09 | 4 | cross_domain_synthesis | 0.889641 | 0.116799 | -0.001287 | 512 |
| L4_10 | 4 | cross_domain_synthesis | 0.897583 | 0.108890 | -0.001140 | 512 |
| L4_11 | 4 | cross_domain_synthesis | 0.893599 | 0.113429 | -8.448691e-04 | 512 |
| L4_12 | 4 | cross_domain_synthesis | 0.901523 | 0.104691 | -0.001130 | 512 |
| L4_13 | 4 | cross_domain_synthesis | 0.893092 | 0.113432 | -9.527342e-04 | 512 |
| L4_14 | 4 | cross_domain_synthesis | 0.843546 | 0.154548 | -6.528668e-04 | 74 |
| L5_01 | 5 | recursive_mental_modeling | 0.862921 | 0.139239 | -0.001436 | 0 |
| L5_02 | 5 | recursive_mental_modeling | 0.882987 | 0.121169 | -0.001221 | 70 |
| L5_03 | 5 | recursive_mental_modeling | 0.893218 | 0.112964 | -0.001423 | 283 |
| L5_04 | 5 | recursive_mental_modeling | 0.913873 | 0.090761 | -9.363741e-04 | 512 |
| L5_05 | 5 | recursive_mental_modeling | 0.912031 | 0.092311 | -9.017701e-04 | 512 |
| L5_06 | 5 | recursive_mental_modeling | 0.838542 | 0.166045 | -0.001094 | 0 |
| L5_07 | 5 | recursive_mental_modeling | 0.901254 | 0.102627 | -0.001191 | 175 |
| L5_08 | 5 | recursive_mental_modeling | 0.901298 | 0.104685 | -0.001174 | 512 |
| L5_09 | 5 | recursive_mental_modeling | 0.861018 | 0.144073 | -7.295932e-04 | 0 |
| L5_10 | 5 | recursive_mental_modeling | 0.915838 | 0.088911 | -9.151071e-04 | 512 |
| L5_11 | 5 | recursive_mental_modeling | 0.904648 | 0.100779 | -9.661148e-04 | 512 |
| L5_12 | 5 | recursive_mental_modeling | 0.851893 | 0.150993 | -0.001694 | 0 |
| L5_13 | 5 | recursive_mental_modeling | 0.916071 | 0.088413 | -0.001080 | 512 |
| L5_14 | 5 | recursive_mental_modeling | 0.909582 | 0.095805 | -0.001136 | 512 |
| L6_01 | 6 | irreducible_ambiguity | 0.809361 | 0.192134 | -0.001941 | 314 |
| L6_02 | 6 | irreducible_ambiguity | 0.892631 | 0.114065 | -0.001253 | 512 |
| L6_03 | 6 | irreducible_ambiguity | 0.866802 | 0.139040 | -0.001798 | 322 |
| L6_04 | 6 | irreducible_ambiguity | 0.843664 | 0.162852 | -0.001535 | 0 |
| L6_05 | 6 | irreducible_ambiguity | 0.833213 | 0.171120 | -0.001715 | 0 |
| L6_06 | 6 | irreducible_ambiguity | 0.901490 | 0.104186 | -0.001093 | 512 |
| L6_07 | 6 | irreducible_ambiguity | 0.905133 | 0.100733 | -7.991376e-04 | 512 |
| L6_08 | 6 | irreducible_ambiguity | 0.920214 | 0.076612 | -9.048795e-04 | 512 |
| L6_09 | 6 | irreducible_ambiguity | 0.896825 | 0.109037 | -0.001118 | 512 |
| L6_10 | 6 | irreducible_ambiguity | 0.895494 | 0.109818 | -0.001040 | 143 |
| L6_11 | 6 | irreducible_ambiguity | 0.915685 | 0.077749 | -0.001115 | 512 |
| L6_12 | 6 | irreducible_ambiguity | 0.848224 | 0.158257 | -0.001788 | 107 |
| L6_13 | 6 | irreducible_ambiguity | 0.854712 | 0.150970 | -0.001424 | 36 |
| L6_14 | 6 | irreducible_ambiguity | 0.907085 | 0.097911 | -0.001117 | 512 |
| L7_01 | 7 | self_referential | 0.912878 | 0.092198 | -9.237454e-04 | 512 |
| L7_02 | 7 | self_referential | 0.892277 | 0.114212 | -0.001379 | 337 |
| L7_03 | 7 | self_referential | 0.844821 | 0.161627 | -0.002292 | 230 |
| L7_04 | 7 | self_referential | 0.894575 | 0.110080 | -0.001475 | 512 |
| L7_05 | 7 | self_referential | 0.896068 | 0.109391 | -0.001443 | 498 |
| L7_06 | 7 | self_referential | 0.895434 | 0.110010 | -0.001232 | 302 |
| L7_07 | 7 | self_referential | 0.858555 | 0.147676 | -0.001194 | 31 |
| L7_08 | 7 | self_referential | 0.893452 | 0.112332 | -0.001331 | 368 |
| L7_09 | 7 | self_referential | 0.891065 | 0.115086 | -0.001277 | 438 |
| L7_10 | 7 | self_referential | 0.903602 | 0.101928 | -7.486257e-04 | 512 |
| L7_11 | 7 | self_referential | 0.900910 | 0.104404 | -0.001395 | 512 |
| L7_12 | 7 | self_referential | 0.904104 | 0.102464 | -0.001054 | 512 |
| L7_13 | 7 | self_referential | 0.874008 | 0.131060 | -0.001315 | 73 |
| L7_14 | 7 | self_referential | 0.895233 | 0.109151 | -0.001653 | 425 |
