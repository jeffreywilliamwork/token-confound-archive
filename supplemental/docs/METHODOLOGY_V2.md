# Methodology V2 (Token-Confound Safe)

## Status and Scope
This protocol supersedes prior methods for primary claims.

- **Cutoff date:** March 5, 2026.
- Runs before this date are archived under `legacy/pre-2026-03-05/` and treated as exploratory.
- Confirmatory claims must come from runs executed under this V2 protocol.

## Research Design
V2 is split into two studies to separate clean inference from dynamic exploration.

### Study A (Primary, Confirmatory)
- **Mode:** prefill only (`n_predict=0`).
- **Prompt set:** `experiments/selfref-paired-1/prompt_suite.json`.
- **Design:** token-matched minimal-substitution pairs (`A` = self-referential, `B` = matched third-person control).
- **Goal:** isolate routing changes caused by minimal self-reference under paired lexical control.
- **Unit of analysis:** paired prompt summaries at the last prefill token, aggregated across shared MoE layers.

### Study B (Secondary, Exploratory)
- **Mode:** generation enabled.
- **Prompt set:** `experiments/6block-prompts-qwen397b/`.
- **Goal:** characterize hysteresis, relaxation, and regime transitions over decoding steps and block boundaries.
- **Constraint:** all comparisons use fixed matched windows or block-aligned segments, never full generated length as a primary claim source.

## Prompt and Control Design
- Primary confirmatory claims must come from token-matched A/B pairs with minimal substitutions only.
- Pair members should differ only in indexical/self-referential wording (for example `this system` vs `a system`) while preserving syntax and token count.
- Use exact tokenizer verification before capture; any pair mismatch fails the run.
- Use fixed chat templates per model and record exact template string hash.
- Keep the Cal-Manip-Cal sandwich structure for the paired experiment.
- `prompt-suite-v2.2.json` is the active auxiliary prompt-development asset for the next prefill-only run, not the default source of primary confirmatory claims.

## Locked Inference Configuration
For each model family, lock the following across runs:

- model file hash and quantization
- binary hash (`capture_activations`)
- `-ngl`, `-c`, `-t`, cache flags, flash-attention flags
- routing capture filter (`ffn_moe_logits` only)

Any change creates a new protocol version (`V2.x`) and cannot be pooled silently.

## Metric Definitions
- **Primary endpoints (Study A):**
  - mean last-token KL divergence between paired A/B routing distributions across shared layers
  - mean expert-set overlap at the last token (top-`k` Jaccard across shared layers)
  - mean last-token cross-layer disagreement within each prompt, analyzed as paired `A - B` difference
- **Descriptive statistics (Study A):**
  - last-token entropy
  - mean prefill entropy
- **Exploratory dynamic endpoints (Study B):**
  - fixed-window KL-to-baseline
  - token-to-token JSD
  - cross-layer disagreement
  - entropy
- Report exact formulas and normalization constants in run outputs.

## Quality Gates
Reject or flag runs when any condition fails:

- missing layer files
- token split mismatch (`n_tokens_prompt` parse failure)
- paired token mismatch after exact tokenizer audit
- no shared valid MoE layers across a paired comparison
- known partial-layer bug (for example layer 57 row loss) not masked
- unexpected template drift

## Reproducibility Artifacts
Every run must emit:

- `run_metadata.json` (model hash, binary hash, flags, template, prompt-suite hash, date/time, host)
- `results_*.json` (metrics and per-prompt outputs)
- `experiment.log` (ground truth execution trace)

## Reporting Rules
- Primary section includes only Study A paired minimal-substitution outcomes.
- Entropy is reported as descriptive context, not as the sole confirmatory endpoint.
- Study B is reported as secondary/exploratory with explicit hysteresis and relaxation framing.
- Legacy pre-March 5, 2026 findings can be cited for context, not confirmation.
