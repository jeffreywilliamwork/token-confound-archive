# Manifest

Archive: `experiments/token-confound-archive-mechinterp/`
Created: 2026-03-20
Approx. size: `~33MB`

## How To Read This Archive

Core path:
- `README.md`
- `NARRATIVE.md`
- `CROSS_MODEL_POSITION_CONFOUND.md`
- `PARTIAL-RESULTS.md`
- `raw/168q-r1-deepseek-r1/`
- `raw/r1-28q-1/`
 - `raw/ds31-168q-1/`
 - `raw/qwen-168q-1/`
 - `raw/position-diagnostic/`

Supporting but still relevant:
- `data/`
- `figures/`

Tangential or post-confound material:
- `supplemental/`

## Top-Level Structure

```
token-confound-archive-mechinterp/
  README.md
  NARRATIVE.md
  CROSS_MODEL_POSITION_CONFOUND.md
  PARTIAL-RESULTS.md
  MANIFEST.md

  data/            recalculated summaries used for cross-run comparison
  figures/         final plots used in the cross-model confound analysis
  raw/             copied source artifacts and historical writeups
  supplemental/    related but non-load-bearing material
```

## `data/` Contents

These are recalculated summaries, not original captures.

- `98q-r1_prefill.*`
  DeepSeek V3.1 98-prompt prefill baseline.
- `98q-r1_generation.*`
  DeepSeek V3.1 generation baseline where generation length first looked confounded.
- `14q-r1_prefill.*` through `14q-r7_prefill.*`
  Incremental 14-prompt batches that extended the hierarchy from L8 to L12 plus controls.
- `168q-r1_R1_prefill.*`
  Recalculated summary of the original DeepSeek R1 168-prompt hierarchy run.
- `14q-ds31-run1_gen.*`
  DeepSeek V3.1 generation trajectories.
- `r1-28q-1_gen.*`
  DeepSeek R1 generation trajectories.
- `ds31-168q-1_prefill.*`
  Recalculated DeepSeek V3.1 168-prompt comparison file.
- `qwen-168q-1_run1.*`, `qwen-168q-1_run2.*`
  Qwen comparison runs used in the final cross-model control.
- `diagnostic_results.json`
  Per-token position diagnostic data.
- `position-diagnostic.json`
  Companion recalculated diagnostic summary.
- `rebuild_from_raw.py`
  Rebuilds key `data/*.json` summaries from the `raw/` sources in this archive (portable).
- `recalculate_all.py`
  Legacy internal script retained for provenance; not required for the core confound story.

## `raw/` Contents

These are copied source artifacts. They are the historical record.

Important:
- some raw writeups contain conclusions that were later invalidated
- they are kept because they document the mistake, not because the archive still endorses those claims
- use `NARRATIVE.md` and `CROSS_MODEL_POSITION_CONFOUND.md` for the corrected interpretation

- `raw/168q-r1-deepseek-r1/`
  - `168q-r1_RESULTS.md`: original R1 headline result writeup
  - `results_168_r1_prefill.json`: original per-prompt R1 results
- `raw/r1-28q-1/`
  - `surfaces/*.npy`: saved metric surfaces for recomputation
  - `reanalysis_output/*.csv`: matched-length control attempt
  - `results_gen_trajectories.json`: per-prompt generation trajectory data
  - `experiment.log`, `reanalysis.log`: run logs
  - `prompt-suite.json`, `generate_tsv.py`, `run_experiment.py`: run bundle
  - `output/*/metadata.txt`, `generated_text.txt`: generation outputs
  - `r1-28q-1_RESULTS.md`: original generation writeup

- `raw/ds31-168q-1/`
  - `results_168q_ds31_prefill.json`: DeepSeek V3.1 168-prompt run (all-token + last-token RE per prompt)
  - `experiment.log`: run log

- `raw/qwen-168q-1/`
  - `results_168q_qwen_prefill.json`: Qwen 397B run1
  - `results_168q_qwen_prefill_run2.json`: Qwen 397B run2
  - `experiment.log`: run log

- `raw/position-diagnostic/`
  - `diagnostic_results.json`: per-token entropy curves (small diagnostic suite)

- `raw/preconfound/`
  Copied JSON sources for the earlier “hierarchy build-up” era, kept so `data/*.json` is reproducible without the parent repo.

## `supplemental/` Contents

This material is preserved but not required for the token-confound story.

- `supplemental/data/ds31-v22-32q-1_prefill.*`
- `supplemental/data/ds31-v22-32q-1_multiseed_seed_*.json`
- `supplemental/docs/METHODOLOGY_V2.md`
- `supplemental/recovery/ds31_v22_partial_raw_recovery.*`
  Partial raw sigmoid-gated RE recomputation from the recoverable ExternalSSD subset.

## Provenance

Nothing was modified in the original source locations:
- `legacy/`
- `legacy-updated/`
- pre-existing experiment folders outside this archive
