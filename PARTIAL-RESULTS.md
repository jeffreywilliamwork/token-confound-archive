#!/usr/bin/env markdown

# Partial Results (Recovery and Recompute Notes)

This file summarizes results in the archive that are only partially recoverable from the copied or discovered raw artifacts.

## What Is Complete

- `raw/168q-r1-deepseek-r1/`
  - original DeepSeek R1 168-prompt hierarchy result writeup
  - original per-prompt JSON result file
- `raw/r1-28q-1/`
  - saved generation surfaces
  - rerunnable matched-length reanalysis artifacts
  - recomputable RE/slope summaries from saved arrays

## What Is Only Partial

### `ds31-v22-32q-1` raw recovery

Raw router captures were found outside the original archive at:

- an external SSD path (not included in this archive): `/Volumes/ExternalSSD/llama-eeg-tests/ds31-v22-32q-1/output`

These files support a partial recomputation of DeepSeek V3.1 prefill routing entropy using the DeepSeek sigmoid-gated routing reconstruction.

Recovered outputs:

- `supplemental/recovery/ds31_v22_partial_raw_recovery.md`
- `supplemental/recovery/ds31_v22_partial_raw_recovery.json`
- `supplemental/recovery/recompute_ds31_v22_partial.py`

Coverage:

- expected prompts: `32`
- complete raw prompts recovered: `17`
- broken prompt directories: `1` (`L3_A2`)
- missing prompt directories: `14`

Recovered prompt IDs:

- `L1_A1, L1_A2, L1_B1, L1_B2, L1_C1, L1_C2, L1_D1, L1_D2`
- `L2_A1, L2_A2, L2_B1, L2_B2, L2_C1, L2_C2, L2_D1, L2_D2`
- `L3_A1`

Important scope limit:

- this recovery is prefill-only
- these raw captures have `n_tokens_generated=0`
- this does not reconstruct the generation-side commitment-token analysis from the v2.2 forced-choice work

## Best Available RE Numbers for `ds31-v22-32q-1`

From the partial raw recomputation:

| Level | n | Mean all-token RE | Mean last-token RE | Mean tokens |
|-------|---|-------------------|--------------------|-------------|
| L1 | 8 | 0.961820 | 0.943339 | 227.00 |
| L2 | 8 | 0.961210 | 0.944267 | 230.00 |
| L3 | 1 | 0.961707 | 0.943729 | 245.00 |

Subset-only correlations:

- all-token RE vs level: `rho=-0.5790`, `p=0.0149`
- last-token RE vs level: `rho=+0.5817`, `p=0.0143`
- all-token RE vs prompt tokens: `rho=-0.6572`, `p=0.0041`
- last-token RE vs prompt tokens: `rho=+0.5901`, `p=0.0126`

These should not be treated as the full-run `ds31-v22-32q-1` result. They are statistics on the recoverable subset only.

## Interpretation After Reviewing the Recovered Prompts

The recovered `ds31-v22-32q-1` prompts are not open-ended reasoning prompts like the 12-level hierarchy suite. They are tightly templated operational triage prompts that ask for JSON output under explicit rule sets.

What the recovered subset actually contains:

- `L1` is mostly direct mapping: read a case record and apply a simple threshold or branch.
- `L2` adds rule interaction: two-part classification logic with explicit ignore-fields.
- `L3` adds precedence and exception handling: compute a base class, then apply a downgrade or action override.

Why that matters for interpretation:

- The prompt family is intentionally uniform. Most of the token mass is shared scaffold, not freely varying semantics.
- The surviving subset spans only `L1` to `L3`, and almost all prompts sit in a narrow 227-245 token band.
- That makes this recovery useful as a check that raw sigmoid-gated RE can still be reconstructed from surviving tensors, but weak as evidence about any broad "complexity hierarchy."

The cautious reading is:

- this recovery supports the general warning that RE metrics remain sensitive to prompt construction details even in a different suite
- it does not independently establish a new hierarchy claim
- it is best treated as an archival salvage result, not a core finding

## Practical Interpretation

- The archive contains full evidence for the original DeepSeek hierarchy claim, the R1 generation follow-up, and the later cross-model confound analysis.
- The `ds31-v22-32q-1` material is preserved as supplemental because it is adjacent work, not core evidence for the token-confound story.
- Raw RE for `ds31-v22-32q-1` is now recoverable for the subset that actually exists on disk, but not for the full 32-prompt run.
