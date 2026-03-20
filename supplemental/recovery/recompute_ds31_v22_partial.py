#!/usr/bin/env python3
"""Recompute recoverable DeepSeek v2.2 prefill RE from raw router logits.

This recovery is intentionally partial. The raw output tree on ExternalSSD
contains only a subset of the original 32 prompts with complete router capture.

DeepSeek V3.1 is sigmoid-gated. This script reconstructs routed expert weights
 from captured ``ffn_moe_logits`` using the repo's DeepSeek gate approximation:

1. ``sigmoid(logits)``
2. noaux_tc group filtering
3. top-k expert selection
4. renormalization over selected experts

It then computes normalized Shannon entropy over the reconstructed routed
probabilities for:
- all prefill tokens across all valid layers
- the final prefill token for each valid layer
"""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import numpy as np
from scipy import stats


REPO_ROOT = Path(__file__).resolve().parents[4]
ARCHIVE_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = Path("/Volumes/ExternalSSD/llama-eeg-tests/ds31-v22-32q-1/output")
SUMMARY_SOURCE = REPO_ROOT / "experiments/ds31-v22-32q-1/results_ds31_v22_prefill.json"
MANIFEST_SOURCE = REPO_ROOT / "experiments/ds31-v22-32q-1/prompt_manifest_v22.json"
ROUTER_PATH = REPO_ROOT / "experiments/deepseek/ds31-5cond-1/deepseek_router.py"

OUT_JSON = ARCHIVE_ROOT / "supplemental/recovery/ds31_v22_partial_raw_recovery.json"
OUT_MD = ARCHIVE_ROOT / "supplemental/recovery/ds31_v22_partial_raw_recovery.md"


def load_deepseek_router():
    spec = importlib.util.spec_from_file_location("deepseek_router", ROUTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load DeepSeek router helper from {ROUTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_metadata(prompt_dir: Path) -> dict[str, object]:
    meta_path = prompt_dir / "metadata.txt"
    values: dict[str, object] = {"prompt_id": prompt_dir.name}
    if not meta_path.exists():
        return values

    for line in meta_path.read_text().splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if value.isdigit():
            values[key] = int(value)
        else:
            values[key] = value
    return values


def sorted_router_files(router_dir: Path) -> list[Path]:
    return sorted(
        router_dir.glob("ffn_moe_logits-*.npy"),
        key=lambda p: int(p.stem.split("-")[1]),
    )


def compute_prompt_metrics(prompt_dir: Path, reconstruct_probs, normalized_entropy) -> dict[str, object] | None:
    meta = parse_metadata(prompt_dir)
    n_prompt = int(meta.get("n_tokens_prompt", 0))
    router_dir = prompt_dir / "router"
    files = sorted_router_files(router_dir)

    if n_prompt <= 0 or not files:
        return None

    all_entropies: list[float] = []
    last_token_entropies: list[float] = []
    per_layer: list[dict[str, object]] = []
    layer_row_counts: list[int] = []

    for file_path in files:
        logits = np.load(file_path)
        layer_idx = int(file_path.stem.split("-")[1])
        n_rows = min(int(logits.shape[0]), n_prompt)
        if n_rows <= 0:
            continue

        probs = reconstruct_probs(logits[:n_rows])
        ent = normalized_entropy(probs)
        ent = np.asarray(ent, dtype=np.float64)
        valid = np.isfinite(ent) & (ent > 0)
        if not np.any(valid):
            continue

        all_entropies.extend(ent[valid].tolist())
        last_token_entropies.append(float(ent[n_rows - 1]))
        layer_row_counts.append(int(logits.shape[0]))
        per_layer.append(
            {
                "layer": layer_idx,
                "n_rows": int(logits.shape[0]),
                "n_used_rows": n_rows,
                "mean": float(np.mean(ent[valid])),
                "std": float(np.std(ent[valid])),
                "last_token": float(ent[n_rows - 1]),
                "n_valid": int(np.sum(valid)),
            }
        )

    if not per_layer:
        return None

    return {
        "id": prompt_dir.name,
        "prompt_id": prompt_dir.name,
        "n_prompt_tokens": n_prompt,
        "n_tokens_generated": int(meta.get("n_tokens_generated", 0)),
        "n_router_tensors": int(meta.get("n_router_tensors", len(files))),
        "prefill_re": float(np.mean(all_entropies)),
        "last_token_re": float(np.mean(last_token_entropies)),
        "n_layers": len(per_layer),
        "min_layer_rows": int(min(layer_row_counts)),
        "max_layer_rows": int(max(layer_row_counts)),
        "per_layer": per_layer,
        "reconstruction": "sigmoid_noaux_tc_group_filtered_topk_normalized",
    }


def safe_float(value):
    if value is None:
        return None
    value = float(value)
    if math.isnan(value) or math.isinf(value):
        return None
    return value


def build_markdown(result: dict[str, object]) -> str:
    summary = result["summary"]
    level_summary = result["level_summary"]
    prompt_rows = result["recovered_prompts"]
    broken = result["broken_prompts"]
    missing = result["missing_prompts"]
    comparisons = result["summary_comparisons"]

    lines: list[str] = []
    lines.append("# ds31-v22-32q-1 Partial Raw Recovery")
    lines.append("")
    lines.append("This is a partial raw recomputation from `/Volumes/ExternalSSD/llama-eeg-tests/ds31-v22-32q-1/output`.")
    lines.append("")
    lines.append("What was recoverable:")
    lines.append(f"- complete prompts with raw router capture: `{summary['n_complete_prompts']}`")
    lines.append(f"- broken prompt directories present but incomplete: `{summary['n_broken_prompts']}`")
    lines.append(f"- expected prompts missing entirely: `{summary['n_missing_prompts']}`")
    lines.append("")
    lines.append("Gate assumption:")
    lines.append("- DeepSeek V3.1 sigmoid gate reconstructed via `sigmoid(logits)` + noaux_tc group filtering + top-k + renormalization")
    lines.append("")
    lines.append("Coverage:")
    lines.append(f"- recovered prompt IDs: `{', '.join(summary['complete_prompt_ids'])}`")
    if broken:
        lines.append(f"- broken prompt IDs: `{', '.join(item['id'] for item in broken)}`")
    if missing:
        lines.append(f"- missing prompt IDs: `{', '.join(missing)}`")
    lines.append("")
    lines.append("## Per-Level Summary")
    lines.append("")
    lines.append("| Level | n | Mean all-token RE | Mean last-token RE | Mean tokens |")
    lines.append("|-------|---|-------------------|--------------------|-------------|")
    for row in level_summary:
        lines.append(
            f"| {row['level']} | {row['n']} | {row['prefill_re_mean']:.6f} | "
            f"{row['last_token_re_mean']:.6f} | {row['mean_tokens']:.2f} |"
        )
    lines.append("")
    lines.append("## Subset Correlations")
    lines.append("")
    lines.append(f"- all-token RE vs level: `rho={summary['spearman_prefill_vs_level']['rho']}` `p={summary['spearman_prefill_vs_level']['p']}`")
    lines.append(f"- last-token RE vs level: `rho={summary['spearman_last_token_vs_level']['rho']}` `p={summary['spearman_last_token_vs_level']['p']}`")
    lines.append(f"- all-token RE vs prompt tokens: `rho={summary['spearman_prefill_vs_tokens']['rho']}` `p={summary['spearman_prefill_vs_tokens']['p']}`")
    lines.append(f"- last-token RE vs prompt tokens: `rho={summary['spearman_last_token_vs_tokens']['rho']}` `p={summary['spearman_last_token_vs_tokens']['p']}`")
    lines.append("")
    lines.append("These correlations are only for the recoverable subset, so they should not be interpreted as the full run result.")
    lines.append("")
    lines.append("## Existing Summary Cross-Check")
    lines.append("")
    lines.append(f"- overlapping prompt IDs found in existing summary JSON: `{comparisons['overlap_prompt_count']}`")
    lines.append(f"- token count mismatches on overlap: `{comparisons['token_count_mismatches']}`")
    lines.append(f"- generation count mismatches on overlap: `{comparisons['generation_count_mismatches']}`")
    lines.append("")
    lines.append("## Per-Prompt RE")
    lines.append("")
    lines.append("| Prompt | Level | Tokens | All-token RE | Last-token RE | Layers |")
    lines.append("|--------|-------|--------|--------------|---------------|--------|")
    for row in prompt_rows:
        lines.append(
            f"| {row['id']} | {row['condition']} | {row['n_prompt_tokens']} | "
            f"{row['prefill_re']:.6f} | {row['last_token_re']:.6f} | {row['n_layers']} |"
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("- This file recovers raw sigmoid-based RE for the prompts that actually exist on disk.")
    lines.append("- It does not reconstruct the full 32-prompt prefill run.")
    lines.append("- It does not reconstruct the generation-side commitment-token analysis, because these raw captures are prefill-only (`n_tokens_generated=0`).")
    return "\n".join(lines) + "\n"


def main() -> None:
    router = load_deepseek_router()
    reconstruct_probs = router.reconstruct_probs
    normalized_entropy = router.normalized_entropy

    manifest = json.loads(MANIFEST_SOURCE.read_text())
    manifest_prompts = {item["id"]: item for item in manifest["prompts"]}
    summary_source = json.loads(SUMMARY_SOURCE.read_text())
    summary_prompts = {item["id"]: item for item in summary_source["per_prompt"]}

    expected_ids = [item["id"] for item in manifest["prompts"]]
    prompt_dirs = {p.name: p for p in OUTPUT_ROOT.iterdir() if p.is_dir()}

    recovered_prompts: list[dict[str, object]] = []
    broken_prompts: list[dict[str, object]] = []
    missing_prompts: list[str] = []

    for prompt_id in expected_ids:
        prompt_dir = prompt_dirs.get(prompt_id)
        if prompt_dir is None:
            missing_prompts.append(prompt_id)
            continue

        meta_exists = (prompt_dir / "metadata.txt").exists()
        router_files = sorted_router_files(prompt_dir / "router")
        if not meta_exists or len(router_files) != 58:
            broken_prompts.append(
                {
                    "id": prompt_id,
                    "metadata_exists": meta_exists,
                    "n_router_files": len(router_files),
                }
            )
            continue

        metrics = compute_prompt_metrics(prompt_dir, reconstruct_probs, normalized_entropy)
        if metrics is None:
            broken_prompts.append(
                {
                    "id": prompt_id,
                    "metadata_exists": meta_exists,
                    "n_router_files": len(router_files),
                    "compute_failed": True,
                }
            )
            continue

        merged = {**manifest_prompts[prompt_id], **metrics}
        recovered_prompts.append(merged)

    recovered_prompts.sort(key=lambda row: row["id"])

    level_map: dict[str, list[dict[str, object]]] = {}
    for row in recovered_prompts:
        level_map.setdefault(row["condition"], []).append(row)

    level_summary = []
    for level in sorted(level_map.keys(), key=lambda x: int(x[1:])):
        rows = level_map[level]
        level_summary.append(
            {
                "level": level,
                "condition_name": rows[0]["condition_name"],
                "complexity_level": rows[0]["complexity_level"],
                "n": len(rows),
                "prefill_re_mean": float(np.mean([r["prefill_re"] for r in rows])),
                "prefill_re_std": float(np.std([r["prefill_re"] for r in rows])),
                "last_token_re_mean": float(np.mean([r["last_token_re"] for r in rows])),
                "last_token_re_std": float(np.std([r["last_token_re"] for r in rows])),
                "mean_tokens": float(np.mean([r["n_prompt_tokens"] for r in rows])),
            }
        )

    level_ranks = [int(row["condition"][1:]) for row in recovered_prompts]
    prefill_vals = [row["prefill_re"] for row in recovered_prompts]
    last_vals = [row["last_token_re"] for row in recovered_prompts]
    token_vals = [row["n_prompt_tokens"] for row in recovered_prompts]

    rho_prefill_level, p_prefill_level = stats.spearmanr(level_ranks, prefill_vals)
    rho_last_level, p_last_level = stats.spearmanr(level_ranks, last_vals)
    rho_prefill_tokens, p_prefill_tokens = stats.spearmanr(token_vals, prefill_vals)
    rho_last_tokens, p_last_tokens = stats.spearmanr(token_vals, last_vals)

    overlap_ids = sorted(set(summary_prompts) & {row["id"] for row in recovered_prompts})
    token_count_mismatches = 0
    generation_count_mismatches = 0
    for prompt_id in overlap_ids:
        src = summary_prompts[prompt_id]
        rec = next(row for row in recovered_prompts if row["id"] == prompt_id)
        if int(src.get("n_tokens_prompt", -1)) != int(rec["n_prompt_tokens"]):
            token_count_mismatches += 1
        if int(src.get("n_tokens_generated", -1)) != int(rec["n_tokens_generated"]):
            generation_count_mismatches += 1

    result = {
        "archive_root": str(ARCHIVE_ROOT),
        "raw_output_root": str(OUTPUT_ROOT),
        "source_summary_file": str(SUMMARY_SOURCE),
        "source_manifest_file": str(MANIFEST_SOURCE),
        "reconstruction": "sigmoid_noaux_tc_group_filtered_topk_normalized",
        "summary": {
            "n_expected_prompts": len(expected_ids),
            "n_complete_prompts": len(recovered_prompts),
            "n_broken_prompts": len(broken_prompts),
            "n_missing_prompts": len(missing_prompts),
            "complete_prompt_ids": [row["id"] for row in recovered_prompts],
            "spearman_prefill_vs_level": {
                "rho": safe_float(rho_prefill_level),
                "p": safe_float(p_prefill_level),
            },
            "spearman_last_token_vs_level": {
                "rho": safe_float(rho_last_level),
                "p": safe_float(p_last_level),
            },
            "spearman_prefill_vs_tokens": {
                "rho": safe_float(rho_prefill_tokens),
                "p": safe_float(p_prefill_tokens),
            },
            "spearman_last_token_vs_tokens": {
                "rho": safe_float(rho_last_tokens),
                "p": safe_float(p_last_tokens),
            },
        },
        "summary_comparisons": {
            "overlap_prompt_count": len(overlap_ids),
            "token_count_mismatches": token_count_mismatches,
            "generation_count_mismatches": generation_count_mismatches,
        },
        "level_summary": level_summary,
        "broken_prompts": broken_prompts,
        "missing_prompts": missing_prompts,
        "recovered_prompts": recovered_prompts,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2))
    OUT_MD.write_text(build_markdown(result))
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
