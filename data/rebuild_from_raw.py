#!/usr/bin/env python3
"""
Rebuild a small set of self-contained `data/*.json` + `data/*.md` summaries from `raw/`.

This is intentionally narrow-scope:
- DeepSeek V3.1 ds31-168q-1 (all-token vs last-token RE)
- Qwen 397B qwen-168q-1 run1 + run2 (all-token vs last-token RE)
- position-diagnostic (copy-through JSON)

Goal: make this archive portable (no absolute paths) and keep the evidence tables reproducible.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr


ARCHIVE = Path(__file__).resolve().parents[1]
RAW = ARCHIVE / "raw"
DATA = ARCHIVE / "data"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(obj: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=False)
        f.write("\n")


def _save_md(lines: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")


def _parse_level(level) -> int:
    s = str(level)
    if s.startswith("L"):
        s = s[1:]
    return int(s)


@dataclass(frozen=True)
class PrefillSchema:
    all_token_key: str
    last_token_key: str
    token_count_key: str


SCHEMA_PREFILL_RE = PrefillSchema(
    all_token_key="prefill_re",
    last_token_key="last_token_re",
    token_count_key="n_prompt_tokens",
)


def _spearman(x: np.ndarray, y: np.ndarray) -> dict:
    rho, p = spearmanr(x, y)
    return {"rho": float(rho), "p": float(p), "n": int(len(x))}


def _level_stats(levels: np.ndarray, vals: np.ndarray, name: str) -> list[dict]:
    out: list[dict] = []
    for lv in sorted(set(levels.tolist())):
        v = vals[levels == lv]
        out.append(
            {
                "level": int(lv),
                "n": int(len(v)),
                f"mean_{name}": float(v.mean()),
                f"min_{name}": float(v.min()),
                f"max_{name}": float(v.max()),
            }
        )
    return out


def rebuild_prefill_run(
    *,
    run_name: str,
    source_rel: str,
    out_stem: str,
    schema: PrefillSchema,
) -> None:
    src = RAW / source_rel
    d = _load_json(src)
    prompts = d.get("per_prompt", [])
    if not prompts:
        raise RuntimeError(f"no per_prompt in {src}")

    levels = np.array([_parse_level(p["level"]) for p in prompts], dtype=int)
    toks = np.array([int(p[schema.token_count_key]) for p in prompts], dtype=int)
    all_re = np.array([float(p[schema.all_token_key]) for p in prompts], dtype=float)
    has_last = schema.last_token_key in prompts[0]
    lt_re = None
    if has_last:
        lt_re = np.array([float(p[schema.last_token_key]) for p in prompts], dtype=float)

    out_json = {
        "run_name": run_name,
        "source_file": source_rel,
        "rebuilt_at": _now_iso(),
        "model": d.get("model", "unknown"),
        "experiment": d.get("experiment", "unknown"),
        "mode": d.get("inference", {}).get("mode") or d.get("mode") or "prefill_only",
        "n_prompts": int(len(prompts)),
        "inference": {
            "architecture": d.get("architecture"),
            "n_experts": d.get("n_experts"),
            "n_expert_used": d.get("n_expert_used"),
            "n_moe_layers": d.get("n_moe_layers"),
            "chat_template": d.get("chat_template") or d.get("chat_template_name") or d.get("chat_template"),
        },
        "spearman": {
            "all_token_re_vs_level": _spearman(levels, all_re),
            "all_token_re_vs_tokens": _spearman(toks, all_re),
            "last_token_available": bool(has_last),
        },
        "overall": {
            "all_token_re": {
                "mean": float(all_re.mean()),
                "min": float(all_re.min()),
                "max": float(all_re.max()),
                "std_pop": float(all_re.std(ddof=0)),
            },
        },
        "per_level": {
            "all_token_re": _level_stats(levels, all_re, "all_token_re"),
        },
        "per_prompt": [
            {
                "id": p.get("id"),
                "level": int(_parse_level(p.get("level"))),
                "level_name": p.get("level_name"),
                "n_prompt_tokens": int(p.get(schema.token_count_key)),
                "prefill_re": float(p.get(schema.all_token_key)),
                "last_token_re": float(p.get(schema.last_token_key)) if has_last else None,
            }
            for p in prompts
        ],
    }

    if has_last and lt_re is not None:
        out_json["spearman"]["last_token_re_vs_level"] = _spearman(levels, lt_re)
        out_json["spearman"]["last_token_re_vs_tokens"] = _spearman(toks, lt_re)
        out_json["overall"]["last_token_re"] = {
            "mean": float(lt_re.mean()),
            "min": float(lt_re.min()),
            "max": float(lt_re.max()),
            "std_pop": float(lt_re.std(ddof=0)),
        }
        out_json["per_level"]["last_token_re"] = _level_stats(levels, lt_re, "last_token_re")

    out_json_path = DATA / f"{out_stem}.json"
    _save_json(out_json, out_json_path)

    lines: list[str] = []
    lines.append(f"# {out_stem}")
    lines.append("")
    lines.append("## Run Info")
    lines.append("")
    lines.append(f"- **Source**: `{source_rel}`")
    lines.append(f"- **Rebuilt**: `{out_json['rebuilt_at']}`")
    lines.append(f"- **Model**: {out_json['model']}")
    lines.append(f"- **Mode**: {out_json['mode']}")
    lines.append(f"- **N prompts**: {out_json['n_prompts']}")
    lines.append("")
    lines.append("## Spearman (Prompt-Level)")
    lines.append("")
    sp = out_json["spearman"]
    lines.append("| Comparison | rho | p | n |")
    lines.append("|---|---:|---:|---:|")
    rows = [
        ("all_token_re_vs_level", "all-token RE vs level"),
        ("all_token_re_vs_tokens", "all-token RE vs token_count"),
    ]
    if sp.get("last_token_available"):
        rows.insert(1, ("last_token_re_vs_level", "last-token RE vs level"))
        rows.append(("last_token_re_vs_tokens", "last-token RE vs token_count"))

    for k, label in rows:
        v = sp[k]
        lines.append(f"| {label} | {v['rho']:+.4f} | {v['p']:.3g} | {v['n']} |")
    lines.append("")
    lines.append("## Overall Means")
    lines.append("")
    lines.append(f"- all-token mean RE: `{out_json['overall']['all_token_re']['mean']:.6f}`")
    if sp.get("last_token_available") and "last_token_re" in out_json["overall"]:
        lines.append(f"- last-token mean RE: `{out_json['overall']['last_token_re']['mean']:.6f}`")
    else:
        lines.append("- last-token mean RE: unavailable in this source JSON")

    _save_md(lines, DATA / f"{out_stem}.md")


def rebuild_position_diagnostic() -> None:
    src = RAW / "position-diagnostic/diagnostic_results.json"
    d = _load_json(src)
    out = {
        "run_name": "position-diagnostic",
        "source_file": "raw/position-diagnostic/diagnostic_results.json",
        "rebuilt_at": _now_iso(),
        "data": d,
    }
    _save_json(out, DATA / "position-diagnostic.json")

def rewrite_data_source_paths() -> None:
    """
    Rewrite `data/*.json` + `data/*.md` so they don't embed machine-specific absolute paths.
    This doesn't change any metrics; it only updates provenance pointers.
    """
    mapping = {
        # Pre-confound hierarchy build-up (JSON sources copied into raw/preconfound/)
        "results_98_routing_prefill.json": "raw/preconfound/98q-r1/results_98_routing_prefill.json",
        "results_98_routing.json": "raw/preconfound/98q-r1/results_98_routing.json",
        "results_14_routing_prefill.json": "raw/preconfound/14q-r1/results_14_routing_prefill.json",
        "results_14_nexus7_prefill.json": "raw/preconfound/14q-r2/results_14_nexus7_prefill.json",
        "results_14_strange_loops_prefill.json": "raw/preconfound/14q-r3/results_14_strange_loops_prefill.json",
        "results_14_architectural_prefill.json": "raw/preconfound/14q-r4/results_14_architectural_prefill.json",
        "results_14_echo_prefill.json": "raw/preconfound/14q-r5/results_14_echo_prefill.json",
        "results_14_bob_prefill.json": "raw/preconfound/14q-r6/results_14_bob_prefill.json",
        "results_14_aether_prefill.json": "raw/preconfound/14q-r7/results_14_aether_prefill.json",
        # R1 prefill (source already inside raw/)
        "results_168_r1_prefill.json": "raw/168q-r1-deepseek-r1/results_168_r1_prefill.json",
        # Generation trajectories
        "results_gen_trajectories.json": None,  # handled by run-specific heuristics below
    }

    # JSON: rewrite source_file
    for p in sorted(DATA.glob("*.json")):
        try:
            d = _load_json(p)
        except Exception:
            continue

        src = d.get("source_file")
        if not isinstance(src, str) or not src.startswith("/"):
            continue

        basename = Path(src).name
        repl = mapping.get(basename)
        if repl:
            d["source_file"] = repl
        elif basename == "results_gen_trajectories.json":
            # Two known cases in this archive.
            if "14q-ds31-run1" in src:
                d["source_file"] = "raw/preconfound/14q-ds31-run1/results_gen_trajectories.json"
            elif "r1-28q-1" in src:
                d["source_file"] = "raw/r1-28q-1/results_gen_trajectories.json"
        _save_json(d, p)

    # MD: rewrite "- **Source**: `...`" to match the JSON source_file when possible.
    for p in sorted(DATA.glob("*.md")):
        txt = p.read_text(encoding="utf-8", errors="replace").splitlines()
        out: list[str] = []
        replaced = False
        for line in txt:
            if (not replaced) and line.strip().startswith("- **Source**:"):
                m = line.split("`")
                if len(m) >= 3:
                    old = m[1]
                    if old.startswith("/"):
                        base = Path(old).name
                        repl = mapping.get(base)
                        if repl is None and base == "results_gen_trajectories.json":
                            if "14q-ds31-run1" in old:
                                repl = "raw/preconfound/14q-ds31-run1/results_gen_trajectories.json"
                            elif "r1-28q-1" in old:
                                repl = "raw/r1-28q-1/results_gen_trajectories.json"
                        if repl:
                            line = f"- **Source**: `{repl}`"
                            replaced = True
            out.append(line)
        if replaced:
            p.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    rebuild_prefill_run(
        run_name="ds31-168q-1",
        source_rel="ds31-168q-1/results_168q_ds31_prefill.json",
        out_stem="ds31-168q-1_prefill",
        schema=SCHEMA_PREFILL_RE,
    )
    rebuild_prefill_run(
        run_name="qwen-168q-1 (run1)",
        source_rel="qwen-168q-1/results_168q_qwen_prefill.json",
        out_stem="qwen-168q-1_run1",
        schema=SCHEMA_PREFILL_RE,
    )
    rebuild_prefill_run(
        run_name="qwen-168q-1 (run2)",
        source_rel="qwen-168q-1/results_168q_qwen_prefill_run2.json",
        out_stem="qwen-168q-1_run2",
        schema=SCHEMA_PREFILL_RE,
    )
    rebuild_position_diagnostic()
    rewrite_data_source_paths()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
