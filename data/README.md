# Data Guide

`data/` contains recalculated summaries, not raw captures.

Use `data/` when you want:
- a normalized summary format across runs
- per-run Spearman tables and level means
- quick comparison across DeepSeek, R1, and Qwen

Use `raw/` when you want:
- the original result files as written at the time
- original per-prompt JSON outputs
- rerunnable generation surfaces and reanalysis artifacts

The most important raw/recalculated pair in this archive is:

- `raw/168q-r1-deepseek-r1/results_168_r1_prefill.json`
- `data/168q-r1_R1_prefill.json`

They refer to the same R1 prefill run. The `data/` version is a standardized recalculation for comparison. The `raw/` version is the historical source file.

Rebuild note:
- `rebuild_from_raw.py` regenerates a few key `data/*.json` summaries from `raw/` so the archive stays portable.
