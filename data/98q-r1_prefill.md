# 98q-r1_prefill

## Run Info

- **Source**: `raw/preconfound/98q-r1/results_98_routing_prefill.json`
- **Recalculated**: 2026-03-07T21:10:29.807160
- **Model**: DeepSeek-V3.1 UD-Q2_K_XL
- **Mode**: prefill_only
- **N prompts**: 98

## Inference Parameters

- **ngl**: 30
- **sampling**: greedy_argmax
- **binary**: b8123 cmake, common_init_from_params, greedy argmax

## Overall Statistics

- **mean_re**: 0.830181
- **std_re**: 0.024294
- **min_re**: 0.785789
- **max_re**: 0.882585

## Spearman Correlation (RE vs Level)

- **rho**: 0.4994
- **p**: 1.6527e-07
- **n**: 98

## Per-Level Statistics

| Level | n | Mean RE | Std RE | Min RE | Max RE |
|-------|---|---------|--------|--------|--------|
| 1 | 14 | 0.824453 | 0.025766 | 0.785789 | 0.867512 |
| 2 | 14 | 0.808193 | 0.017117 | 0.787886 | 0.852608 |
| 3 | 14 | 0.818028 | 0.017611 | 0.788147 | 0.844652 |
| 4 | 14 | 0.815928 | 0.017196 | 0.793957 | 0.852353 |
| 5 | 14 | 0.858185 | 0.013594 | 0.836423 | 0.882585 |
| 6 | 14 | 0.842123 | 0.012910 | 0.821258 | 0.873844 |
| 7 | 14 | 0.844356 | 0.018470 | 0.813957 | 0.871687 |

## Per-Prompt Data

| id | level | level_name | re | coalition_strength | diversity_slope | n_tokens |
|---|---|---|---|---|---|---|
| L1_01 | 1 | floor | 0.865541 | 0.141349 | -0.001533 | 0 |
| L1_02 | 1 | floor | 0.830387 | 0.173161 | 3.486250e-04 | 0 |
| L1_03 | 1 | floor | 0.804254 | 0.197093 | -1.864785e-04 | 0 |
| L1_04 | 1 | floor | 0.867512 | 0.137885 | -0.001358 | 0 |
| L1_05 | 1 | floor | 0.827206 | 0.178743 | -7.858849e-04 | 0 |
| L1_06 | 1 | floor | 0.834421 | 0.165098 | -1.538797e-04 | 0 |
| L1_07 | 1 | floor | 0.821689 | 0.178604 | -3.169105e-04 | 0 |
| L1_08 | 1 | floor | 0.785789 | 0.218343 | -7.138701e-04 | 0 |
| L1_09 | 1 | floor | 0.786981 | 0.216838 | -5.212650e-04 | 0 |
| L1_10 | 1 | floor | 0.825746 | 0.174237 | -0.001001 | 0 |
| L1_11 | 1 | floor | 0.802119 | 0.197701 | -0.001281 | 0 |
| L1_12 | 1 | floor | 0.828742 | 0.173471 | 1.066223e-04 | 0 |
| L1_13 | 1 | floor | 0.853641 | 0.157572 | -4.044445e-04 | 0 |
| L1_14 | 1 | floor | 0.808313 | 0.199645 | -4.032917e-04 | 0 |
| L2_01 | 2 | single_domain | 0.852608 | 0.151341 | -6.822044e-04 | 0 |
| L2_02 | 2 | single_domain | 0.791523 | 0.211095 | -6.259106e-04 | 0 |
| L2_03 | 2 | single_domain | 0.787886 | 0.215755 | 8.118830e-05 | 0 |
| L2_04 | 2 | single_domain | 0.794625 | 0.209558 | -0.001284 | 0 |
| L2_05 | 2 | single_domain | 0.806814 | 0.193879 | -8.941524e-04 | 0 |
| L2_06 | 2 | single_domain | 0.821453 | 0.183627 | -9.469677e-04 | 0 |
| L2_07 | 2 | single_domain | 0.792322 | 0.211619 | -1.383411e-04 | 0 |
| L2_08 | 2 | single_domain | 0.814178 | 0.189476 | -0.001164 | 0 |
| L2_09 | 2 | single_domain | 0.814472 | 0.190294 | -2.925869e-04 | 0 |
| L2_10 | 2 | single_domain | 0.815859 | 0.187916 | -0.001055 | 0 |
| L2_11 | 2 | single_domain | 0.803063 | 0.197865 | -3.916391e-04 | 0 |
| L2_12 | 2 | single_domain | 0.808779 | 0.193469 | -0.001253 | 0 |
| L2_13 | 2 | single_domain | 0.818931 | 0.183909 | -5.375327e-04 | 0 |
| L2_14 | 2 | single_domain | 0.792183 | 0.211437 | -0.001144 | 0 |
| L3_01 | 3 | analytical_reasoning | 0.822841 | 0.180446 | -4.286704e-04 | 0 |
| L3_02 | 3 | analytical_reasoning | 0.822013 | 0.180012 | -0.001003 | 0 |
| L3_03 | 3 | analytical_reasoning | 0.790642 | 0.211174 | -9.882467e-04 | 0 |
| L3_04 | 3 | analytical_reasoning | 0.844652 | 0.157222 | -3.600068e-04 | 0 |
| L3_05 | 3 | analytical_reasoning | 0.807135 | 0.196229 | -9.486669e-05 | 0 |
| L3_06 | 3 | analytical_reasoning | 0.825318 | 0.178164 | -2.609927e-04 | 0 |
| L3_07 | 3 | analytical_reasoning | 0.800470 | 0.197142 | -5.523317e-04 | 0 |
| L3_08 | 3 | analytical_reasoning | 0.818867 | 0.183938 | -6.941523e-04 | 0 |
| L3_09 | 3 | analytical_reasoning | 0.841848 | 0.159989 | -9.980370e-07 | 0 |
| L3_10 | 3 | analytical_reasoning | 0.818817 | 0.180359 | -7.782197e-04 | 0 |
| L3_11 | 3 | analytical_reasoning | 0.788147 | 0.213861 | -0.001411 | 0 |
| L3_12 | 3 | analytical_reasoning | 0.836511 | 0.167670 | -9.552059e-04 | 0 |
| L3_13 | 3 | analytical_reasoning | 0.828753 | 0.174128 | -6.741204e-04 | 0 |
| L3_14 | 3 | analytical_reasoning | 0.806372 | 0.197855 | -9.054528e-04 | 0 |
| L4_01 | 4 | cross_domain_synthesis | 0.804373 | 0.195925 | -0.001491 | 0 |
| L4_02 | 4 | cross_domain_synthesis | 0.811367 | 0.186785 | -0.001949 | 0 |
| L4_03 | 4 | cross_domain_synthesis | 0.801467 | 0.203118 | -7.607702e-04 | 0 |
| L4_04 | 4 | cross_domain_synthesis | 0.797334 | 0.207076 | -2.366656e-04 | 0 |
| L4_05 | 4 | cross_domain_synthesis | 0.833085 | 0.168863 | -0.001457 | 0 |
| L4_06 | 4 | cross_domain_synthesis | 0.809920 | 0.192037 | -4.326081e-04 | 0 |
| L4_07 | 4 | cross_domain_synthesis | 0.852353 | 0.154820 | -4.277949e-04 | 0 |
| L4_08 | 4 | cross_domain_synthesis | 0.821701 | 0.180565 | -0.001657 | 0 |
| L4_09 | 4 | cross_domain_synthesis | 0.815626 | 0.189724 | -3.801619e-04 | 0 |
| L4_10 | 4 | cross_domain_synthesis | 0.823114 | 0.180564 | -5.204074e-04 | 0 |
| L4_11 | 4 | cross_domain_synthesis | 0.810266 | 0.190490 | -0.001297 | 0 |
| L4_12 | 4 | cross_domain_synthesis | 0.843461 | 0.159991 | -0.001004 | 0 |
| L4_13 | 4 | cross_domain_synthesis | 0.804974 | 0.195294 | -0.001567 | 0 |
| L4_14 | 4 | cross_domain_synthesis | 0.793957 | 0.206731 | -0.001329 | 0 |
| L5_01 | 5 | recursive_mental_modeling | 0.862921 | 0.139239 | -0.001436 | 0 |
| L5_02 | 5 | recursive_mental_modeling | 0.864670 | 0.136710 | -9.491965e-04 | 0 |
| L5_03 | 5 | recursive_mental_modeling | 0.873193 | 0.130291 | -9.839091e-04 | 0 |
| L5_04 | 5 | recursive_mental_modeling | 0.859894 | 0.142219 | -0.001033 | 0 |
| L5_05 | 5 | recursive_mental_modeling | 0.840989 | 0.159805 | -8.256119e-04 | 0 |
| L5_06 | 5 | recursive_mental_modeling | 0.838542 | 0.166045 | -0.001094 | 0 |
| L5_07 | 5 | recursive_mental_modeling | 0.853241 | 0.147515 | -0.001072 | 0 |
| L5_08 | 5 | recursive_mental_modeling | 0.856758 | 0.149350 | -0.001209 | 0 |
| L5_09 | 5 | recursive_mental_modeling | 0.861018 | 0.144073 | -7.295932e-04 | 0 |
| L5_10 | 5 | recursive_mental_modeling | 0.875051 | 0.128440 | -0.001182 | 0 |
| L5_11 | 5 | recursive_mental_modeling | 0.836423 | 0.164322 | -6.580108e-04 | 0 |
| L5_12 | 5 | recursive_mental_modeling | 0.851893 | 0.150993 | -0.001694 | 0 |
| L5_13 | 5 | recursive_mental_modeling | 0.882585 | 0.121411 | -0.001140 | 0 |
| L5_14 | 5 | recursive_mental_modeling | 0.857406 | 0.144792 | -0.001514 | 0 |
| L6_01 | 6 | irreducible_ambiguity | 0.821258 | 0.178676 | -0.001614 | 0 |
| L6_02 | 6 | irreducible_ambiguity | 0.834016 | 0.170943 | -5.896193e-04 | 0 |
| L6_03 | 6 | irreducible_ambiguity | 0.831892 | 0.169983 | -0.001568 | 0 |
| L6_04 | 6 | irreducible_ambiguity | 0.843664 | 0.162852 | -0.001535 | 0 |
| L6_05 | 6 | irreducible_ambiguity | 0.833213 | 0.171120 | -0.001715 | 0 |
| L6_06 | 6 | irreducible_ambiguity | 0.828109 | 0.175861 | -0.001581 | 0 |
| L6_07 | 6 | irreducible_ambiguity | 0.838401 | 0.165347 | -7.286885e-04 | 0 |
| L6_08 | 6 | irreducible_ambiguity | 0.853297 | 0.152422 | -0.001302 | 0 |
| L6_09 | 6 | irreducible_ambiguity | 0.848834 | 0.154050 | -0.001395 | 0 |
| L6_10 | 6 | irreducible_ambiguity | 0.873844 | 0.130816 | -0.001173 | 0 |
| L6_11 | 6 | irreducible_ambiguity | 0.845533 | 0.157669 | -0.002186 | 0 |
| L6_12 | 6 | irreducible_ambiguity | 0.850659 | 0.155137 | -0.001187 | 0 |
| L6_13 | 6 | irreducible_ambiguity | 0.845022 | 0.158593 | -0.001525 | 0 |
| L6_14 | 6 | irreducible_ambiguity | 0.841981 | 0.161991 | -0.001779 | 0 |
| L7_01 | 7 | self_referential | 0.831685 | 0.171903 | -6.606902e-04 | 0 |
| L7_02 | 7 | self_referential | 0.816912 | 0.188294 | -0.001007 | 0 |
| L7_03 | 7 | self_referential | 0.813957 | 0.189251 | -0.001635 | 0 |
| L7_04 | 7 | self_referential | 0.841417 | 0.161689 | -0.001629 | 0 |
| L7_05 | 7 | self_referential | 0.864329 | 0.137679 | -0.001120 | 0 |
| L7_06 | 7 | self_referential | 0.854512 | 0.151665 | -6.977682e-04 | 0 |
| L7_07 | 7 | self_referential | 0.843668 | 0.159760 | -8.680689e-04 | 0 |
| L7_08 | 7 | self_referential | 0.854987 | 0.148597 | -0.001238 | 0 |
| L7_09 | 7 | self_referential | 0.871687 | 0.131788 | -8.806136e-04 | 0 |
| L7_10 | 7 | self_referential | 0.821155 | 0.179996 | 1.170780e-04 | 0 |
| L7_11 | 7 | self_referential | 0.854434 | 0.151177 | -0.001049 | 0 |
| L7_12 | 7 | self_referential | 0.839532 | 0.165192 | -5.160555e-04 | 0 |
| L7_13 | 7 | self_referential | 0.844632 | 0.159541 | -0.001126 | 0 |
| L7_14 | 7 | self_referential | 0.868077 | 0.136132 | -0.001336 | 0 |
