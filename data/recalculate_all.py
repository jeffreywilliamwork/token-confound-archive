#!/usr/bin/env python3
"""Recalculate raw metrics for all legacy experiment runs.
Zero interpretation. Raw numbers only."""

import json
import os
import sys
import numpy as np
from scipy.stats import spearmanr, wilcoxon, mannwhitneyu
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
BASE = REPO_ROOT
OUT = REPO_ROOT / "legacy-updated"
OUT.mkdir(exist_ok=True)

def safe_load(path):
    with open(path) as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def save_md(lines, path):
    with open(path, 'w') as f:
        f.write('\n'.join(lines) + '\n')

def per_level_stats(prompts, re_key='routing_entropy', level_key='level'):
    """Compute per-level mean/std/n from prompt list."""
    from collections import defaultdict
    levels = defaultdict(list)
    for p in prompts:
        if level_key in p and re_key in p and p[re_key] is not None:
            levels[p[level_key]].append(p[re_key])
    result = []
    for lv in sorted(levels.keys()):
        vals = np.array(levels[lv])
        result.append({
            'level': lv,
            'n': len(vals),
            'mean': float(vals.mean()),
            'std': float(vals.std(ddof=1)) if len(vals) > 1 else 0.0,
            'min': float(vals.min()),
            'max': float(vals.max()),
        })
    return result

def spearman_from_prompts(prompts, re_key='routing_entropy', level_key='level'):
    """Compute Spearman rho between RE and level."""
    pairs = [(p[level_key], p[re_key]) for p in prompts
             if level_key in p and re_key in p and p[re_key] is not None]
    if len(pairs) < 5:
        return None
    levels, res = zip(*pairs)
    rho, p = spearmanr(levels, res)
    return {'rho': float(rho), 'p': float(p), 'n': len(pairs)}


# ============================================================
# PROCESSOR FUNCTIONS
# ============================================================

def process_prefill_hierarchy(name, path, re_key='routing_entropy', level_key='level',
                               model_override=None, extra_meta=None):
    """Process standard prefill routing entropy hierarchy run."""
    data = safe_load(path)
    prompts = data.get('per_prompt', [])

    # Extract level info - some files use level_name prefix in id
    for p in prompts:
        if level_key not in p and 'id' in p:
            # Try to extract level from id like "L1_01"
            try:
                lv = int(p['id'].split('_')[0].replace('L', ''))
                p[level_key] = lv
            except:
                pass

    re_vals = [p[re_key] for p in prompts if re_key in p and p[re_key] is not None]

    result = {
        'run_name': name,
        'source_file': str(path),
        'recalculated_at': datetime.now().isoformat(),
        'model': model_override or data.get('model', 'unknown'),
        'experiment': data.get('experiment', 'unknown'),
        'n_prompts': len(prompts),
        'mode': data.get('mode', 'prefill_only'),
        'inference': {},
        'overall': {
            'mean_re': float(np.mean(re_vals)) if re_vals else None,
            'std_re': float(np.std(re_vals, ddof=1)) if len(re_vals) > 1 else None,
            'min_re': float(np.min(re_vals)) if re_vals else None,
            'max_re': float(np.max(re_vals)) if re_vals else None,
        },
    }

    # Copy inference params
    for k in ['ngl', 'n_predict', 'sampling', 'binary', 'n_experts', 'n_expert_used',
              'n_moe_layers', 'ctx', 'flash_attn', 'cache_type_k', 'cache_type_v']:
        if k in data:
            result['inference'][k] = data[k]
        if 'inference' in data and k in data['inference']:
            result['inference'][k] = data['inference'][k]

    if extra_meta:
        result.update(extra_meta)

    # Spearman
    sp = spearman_from_prompts(prompts, re_key, level_key)
    if sp:
        result['spearman'] = sp

    # Per-level
    lvl_stats = per_level_stats(prompts, re_key, level_key)
    if lvl_stats:
        result['per_level'] = lvl_stats

    # Per-prompt raw values
    result['per_prompt'] = []
    for p in prompts:
        entry = {'id': p.get('id', '?')}
        if level_key in p:
            entry['level'] = p[level_key]
        if 'level_name' in p:
            entry['level_name'] = p['level_name']
        if re_key in p:
            entry['re'] = p[re_key]
        if 'coalition_strength' in p:
            entry['coalition_strength'] = p['coalition_strength']
        if 'diversity_slope' in p:
            entry['diversity_slope'] = p['diversity_slope']
        if 'n_prompt_tokens' in p:
            entry['n_tokens'] = p['n_prompt_tokens']
        elif 'n_tokens' in p:
            entry['n_tokens'] = p['n_tokens']
        result['per_prompt'].append(entry)

    # Token count correlation (if available)
    tok_re = [(p.get('n_prompt_tokens') or p.get('n_tokens', 0), p.get(re_key))
              for p in prompts if p.get(re_key) is not None and (p.get('n_prompt_tokens') or p.get('n_tokens', 0)) > 0]
    if len(tok_re) >= 5:
        toks, res = zip(*tok_re)
        rho, p = spearmanr(toks, res)
        result['re_vs_token_count'] = {'rho': float(rho), 'p': float(p), 'n': len(tok_re)}

    return result


def process_generation_trajectories(name, path, model_override=None):
    """Process generation trajectory run with slopes."""
    data = safe_load(path)
    prompts = data.get('per_prompt', [])

    prefill_res = [p['prefill_re'] for p in prompts if 'prefill_re' in p]
    gen_res = [p['gen_re'] for p in prompts if 'gen_re' in p]
    slopes = [p['mean_slope'] for p in prompts if 'mean_slope' in p]

    result = {
        'run_name': name,
        'source_file': str(path),
        'recalculated_at': datetime.now().isoformat(),
        'model': model_override or data.get('model', 'unknown'),
        'experiment': data.get('experiment', 'unknown'),
        'n_prompts': len(prompts),
        'mode': data.get('mode', 'generation'),
        'inference': data.get('inference', {}),
        'overall': {
            'mean_prefill_re': float(np.mean(prefill_res)) if prefill_res else None,
            'std_prefill_re': float(np.std(prefill_res, ddof=1)) if len(prefill_res) > 1 else None,
            'mean_gen_re': float(np.mean(gen_res)) if gen_res else None,
            'std_gen_re': float(np.std(gen_res, ddof=1)) if len(gen_res) > 1 else None,
            'mean_slope': float(np.mean(slopes)) if slopes else None,
            'std_slope': float(np.std(slopes, ddof=1)) if len(slopes) > 1 else None,
        },
    }

    # Per-condition stats if conditions exist
    from collections import defaultdict
    conds = defaultdict(lambda: {'prefill': [], 'gen': [], 'slopes': []})
    for p in prompts:
        c = p.get('condition_name', p.get('condition', 'unknown'))
        if 'prefill_re' in p:
            conds[c]['prefill'].append(p['prefill_re'])
        if 'gen_re' in p:
            conds[c]['gen'].append(p['gen_re'])
        if 'mean_slope' in p:
            conds[c]['slopes'].append(p['mean_slope'])

    result['per_condition'] = {}
    for c, v in conds.items():
        result['per_condition'][c] = {
            'n': len(v['prefill']),
            'mean_prefill_re': float(np.mean(v['prefill'])) if v['prefill'] else None,
            'mean_gen_re': float(np.mean(v['gen'])) if v['gen'] else None,
            'mean_slope': float(np.mean(v['slopes'])) if v['slopes'] else None,
        }

    # Slope vs token count
    slope_tok = [(p.get('n_prompt_tokens', 0), p['mean_slope'])
                 for p in prompts if 'mean_slope' in p and p.get('n_prompt_tokens', 0) > 0]
    if len(slope_tok) >= 5:
        toks, slps = zip(*slope_tok)
        rho, pv = spearmanr(toks, slps)
        result['slope_vs_token_count'] = {'rho': float(rho), 'p': float(pv)}

    # Per-prompt
    result['per_prompt'] = []
    for p in prompts:
        entry = {'id': p.get('id', '?')}
        for k in ['condition', 'condition_name', 'prefill_re', 'gen_re',
                   'gen_re_step0', 'gen_re_step_last', 'mean_slope',
                   'n_prompt_tokens', 'n_gen_tokens']:
            if k in p:
                entry[k] = p[k]
        result['per_prompt'].append(entry)

    return result


def process_desktop_30turn(name, path, model_override=None):
    """Process desktop 30-turn consciousness metrics."""
    data = safe_load(path)
    prompts = data.get('per_prompt', [])

    metrics = ['spectral_entropy', 'permutation_entropy', 'lempel_ziv_complexity',
               'mutual_information', 'total_correlation']

    result = {
        'run_name': name,
        'source_file': str(path),
        'recalculated_at': datetime.now().isoformat(),
        'model': data.get('model_name', model_override or 'unknown'),
        'timestamp': data.get('timestamp', 'unknown'),
        'n_prompts': len(prompts),
        'mode': 'generation_consciousness_metrics',
    }

    # Overall stats per metric
    result['overall'] = {}
    for m in metrics:
        vals = [p[m] for p in prompts if m in p and p[m] is not None and not (isinstance(p[m], float) and np.isnan(p[m]))]
        if vals:
            result['overall'][m] = {
                'mean': float(np.mean(vals)),
                'std': float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0,
                'min': float(np.min(vals)),
                'max': float(np.max(vals)),
                'n_valid': len(vals),
            }

    # Spearman vs level for each metric
    result['spearman_vs_level'] = {}
    for m in metrics:
        pairs = [(p['level'], p[m]) for p in prompts
                 if 'level' in p and m in p and p[m] is not None
                 and not (isinstance(p[m], float) and np.isnan(p[m]))]
        if len(pairs) >= 5:
            lvs, vs = zip(*pairs)
            rho, pv = spearmanr(lvs, vs)
            result['spearman_vs_level'][m] = {'rho': float(rho), 'p': float(pv), 'n': len(pairs)}

    # Per-level
    from collections import defaultdict
    levels = defaultdict(lambda: {m: [] for m in metrics})
    for p in prompts:
        if 'level' not in p:
            continue
        for m in metrics:
            if m in p and p[m] is not None and not (isinstance(p[m], float) and np.isnan(p[m])):
                levels[p['level']][m].append(p[m])

    result['per_level'] = []
    for lv in sorted(levels.keys()):
        entry = {'level': lv, 'n': max(len(v) for v in levels[lv].values()) if levels[lv] else 0}
        for m in metrics:
            vals = levels[lv][m]
            if vals:
                entry[f'{m}_mean'] = float(np.mean(vals))
                entry[f'{m}_std'] = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
        result['per_level'].append(entry)

    # Per-prompt
    result['per_prompt'] = []
    for p in prompts:
        entry = {'id': p.get('prompt_id', '?'), 'level': p.get('level', '?'),
                 'n_tokens': p.get('n_tokens', 0)}
        for m in metrics:
            if m in p:
                entry[m] = p[m]
        result['per_prompt'].append(entry)

    return result


def process_regime_switch(name, path, model_override=None):
    """Process regime switch observables."""
    data = safe_load(path)

    result = {
        'run_name': name,
        'source_file': str(path),
        'recalculated_at': datetime.now().isoformat(),
        'model': model_override or 'unknown',
        'mode': 'regime_switch',
    }

    for cond_name, cond_data in data.get('prompts', {}).items():
        obs = cond_data.get('observables', {})
        entropy_arr = obs.get('entropy', [])
        boundaries = cond_data.get('boundaries', [])
        block_names = cond_data.get('block_names', [])

        cond_result = {
            'total_tokens': obs.get('total_tokens', 0),
            'n_layers': obs.get('n_layers', 0),
            'overall_mean_entropy': float(np.mean(entropy_arr)) if entropy_arr else None,
            'overall_std_entropy': float(np.std(entropy_arr, ddof=1)) if len(entropy_arr) > 1 else None,
        }

        # Per-block entropy stats
        if boundaries and entropy_arr:
            blocks = []
            for i in range(len(boundaries)):
                start = boundaries[i]
                end = boundaries[i+1] if i+1 < len(boundaries) else len(entropy_arr)
                block_entropy = entropy_arr[start:end]
                if block_entropy:
                    bn = block_names[i] if i < len(block_names) else f'block_{i}'
                    blocks.append({
                        'block': bn,
                        'start_token': start,
                        'end_token': end,
                        'n_tokens': len(block_entropy),
                        'mean_entropy': float(np.mean(block_entropy)),
                        'std_entropy': float(np.std(block_entropy, ddof=1)) if len(block_entropy) > 1 else 0.0,
                    })
            cond_result['per_block'] = blocks

        result[cond_name] = cond_result

    return result


def process_qwen_hierarchy(name, path):
    """Process Qwen runs with both all-token and last-token entropy."""
    data = safe_load(path)
    prompts = data.get('per_prompt', [])

    result = {
        'run_name': name,
        'source_file': str(path),
        'recalculated_at': datetime.now().isoformat(),
        'model': data.get('model', 'unknown'),
        'architecture': data.get('architecture', 'unknown'),
        'n_experts': data.get('n_experts'),
        'n_expert_used': data.get('n_expert_used'),
        'n_moe_layers': data.get('n_moe_layers'),
        'inference': data.get('inference', {}),
        'n_prompts': len(prompts),
    }

    # Copy pre-computed spearman if exists, but also recalculate
    for key in ['spearman_all_token', 'spearman_last_token',
                'spearman_all_token_vs_ntokens', 'spearman_last_token_vs_ntokens']:
        if key in data:
            result[f'original_{key}'] = data[key]

    # Recalculate from per-prompt
    for re_key, label in [('all_token_re', 'all_token'), ('last_token_re', 'last_token')]:
        # Extract level from id
        pairs_re = []
        pairs_tok = []
        for p in prompts:
            lv = p.get('level')
            if lv is None and 'id' in p:
                try:
                    lv = int(p['id'].split('_')[0].replace('L', ''))
                except:
                    continue
            re_val = p.get(re_key)
            if re_val is not None and lv is not None:
                pairs_re.append((lv, re_val))
            ntok = p.get('n_tokens', 0)
            if re_val is not None and ntok > 0:
                pairs_tok.append((ntok, re_val))

        if len(pairs_re) >= 5:
            lvs, res = zip(*pairs_re)
            rho, pv = spearmanr(lvs, res)
            result[f'recalc_spearman_{label}_vs_level'] = {'rho': float(rho), 'p': float(pv), 'n': len(pairs_re)}
        if len(pairs_tok) >= 5:
            tks, res = zip(*pairs_tok)
            rho, pv = spearmanr(tks, res)
            result[f'recalc_spearman_{label}_vs_ntokens'] = {'rho': float(rho), 'p': float(pv), 'n': len(pairs_tok)}

    # Level summary
    if 'level_summary' in data:
        result['level_summary'] = data['level_summary']

    # Per-prompt
    result['per_prompt'] = []
    for p in prompts:
        entry = {'id': p.get('id', '?')}
        for k in ['level', 'level_name', 'n_tokens', 'all_token_re', 'last_token_re',
                   'coalition_strength', 'diversity_slope']:
            if k in p:
                entry[k] = p[k]
        result['per_prompt'].append(entry)

    return result


def process_selfref_paired(name, path):
    """Process selfref paired experiment."""
    data = safe_load(path)
    pairs = data.get('pair_results', [])

    diffs = [p['lt_entropy_diff'] for p in pairs]
    kls = [p['mean_kl_a_vs_b'] for p in pairs]
    jaccs = [p['mean_jaccard'] for p in pairs]

    result = {
        'run_name': name,
        'source_file': str(path),
        'recalculated_at': datetime.now().isoformat(),
        'n_pairs': len(pairs),
        'primary_endpoint': data.get('primary_endpoint', 'last_token_entropy'),
    }

    if diffs:
        pos = sum(1 for d in diffs if d > 0)
        result['overall'] = {
            'mean_diff': float(np.mean(diffs)),
            'median_diff': float(np.median(diffs)),
            'std_diff': float(np.std(diffs, ddof=1)),
            'n_positive': pos,
            'n_negative': len(diffs) - pos,
        }
        if len(diffs) >= 5:
            try:
                stat, pv = wilcoxon(diffs)
                result['overall']['wilcoxon_stat'] = float(stat)
                result['overall']['wilcoxon_p'] = float(pv)
            except:
                pass
        result['overall']['mean_kl'] = float(np.mean(kls)) if kls else None
        result['overall']['mean_jaccard'] = float(np.mean(jaccs)) if jaccs else None

    # Per-category
    from collections import defaultdict
    cats = defaultdict(lambda: {'diffs': [], 'kls': [], 'jaccs': []})
    for p in pairs:
        c = p.get('category', 'unknown')
        cats[c]['diffs'].append(p['lt_entropy_diff'])
        cats[c]['kls'].append(p['mean_kl_a_vs_b'])
        cats[c]['jaccs'].append(p['mean_jaccard'])

    result['per_category'] = {}
    for c, v in cats.items():
        d = np.array(v['diffs'])
        pos = sum(1 for x in v['diffs'] if x > 0)
        entry = {
            'n': len(d),
            'mean_diff': float(d.mean()),
            'std_diff': float(d.std(ddof=1)) if len(d) > 1 else 0.0,
            'n_positive': pos,
            'mean_kl': float(np.mean(v['kls'])),
            'mean_jaccard': float(np.mean(v['jaccs'])),
        }
        if d.std(ddof=1) > 0:
            entry['cohens_d'] = float(d.mean() / d.std(ddof=1))
        result['per_category'][c] = entry

    # Per-pair
    result['per_pair'] = []
    for p in pairs:
        result['per_pair'].append({
            'pair': p['pair'],
            'category': p['category'],
            'n_tokens_a': p['n_tokens_a'],
            'n_tokens_b': p['n_tokens_b'],
            'lt_entropy_a': p['lt_entropy_a'],
            'lt_entropy_b': p['lt_entropy_b'],
            'lt_entropy_diff': p['lt_entropy_diff'],
            'mean_kl': p['mean_kl_a_vs_b'],
            'mean_jaccard': p['mean_jaccard'],
        })

    return result


def process_6block(name, path):
    """Process 6-block continuous experiment."""
    data = safe_load(path)

    result = {
        'run_name': name,
        'source_file': str(path),
        'recalculated_at': datetime.now().isoformat(),
    }

    # Just pass through the data structure with recalculated stats
    if 'per_prompt' in data:
        prompts = data['per_prompt']
        re_vals = [p.get('routing_entropy') or p.get('all_token_re') for p in prompts
                   if (p.get('routing_entropy') or p.get('all_token_re')) is not None]
        if re_vals:
            result['overall'] = {
                'n_prompts': len(prompts),
                'mean_re': float(np.mean(re_vals)),
                'std_re': float(np.std(re_vals, ddof=1)) if len(re_vals) > 1 else 0.0,
            }
        result['per_prompt'] = []
        for p in prompts:
            entry = {k: p[k] for k in p if k != 'layer_details' and k != 'per_layer'}
            result['per_prompt'].append(entry)

    # Copy any block-level analysis
    for k in data:
        if k not in ('per_prompt',) and isinstance(data[k], (dict, list)):
            if k not in result:
                result[k] = data[k]

    return result


def result_to_markdown(result):
    """Convert result dict to markdown lines."""
    lines = []
    lines.append(f"# {result['run_name']}")
    lines.append('')
    lines.append('## Run Info')
    lines.append('')
    lines.append(f"- **Source**: `{result.get('source_file', '?')}`")
    lines.append(f"- **Recalculated**: {result.get('recalculated_at', '?')}")
    lines.append(f"- **Model**: {result.get('model', '?')}")
    lines.append(f"- **Mode**: {result.get('mode', '?')}")
    lines.append(f"- **N prompts**: {result.get('n_prompts', '?')}")

    if result.get('inference'):
        lines.append('')
        lines.append('## Inference Parameters')
        lines.append('')
        for k, v in result['inference'].items():
            lines.append(f"- **{k}**: {v}")

    if result.get('overall'):
        lines.append('')
        lines.append('## Overall Statistics')
        lines.append('')
        for k, v in result['overall'].items():
            if isinstance(v, float):
                lines.append(f"- **{k}**: {v:.6f}")
            elif isinstance(v, dict):
                lines.append(f"- **{k}**:")
                for kk, vv in v.items():
                    lines.append(f"  - {kk}: {vv:.6f}" if isinstance(vv, float) else f"  - {kk}: {vv}")
            else:
                lines.append(f"- **{k}**: {v}")

    if result.get('spearman'):
        lines.append('')
        lines.append('## Spearman Correlation (RE vs Level)')
        lines.append('')
        sp = result['spearman']
        lines.append(f"- **rho**: {sp['rho']:.4f}")
        lines.append(f"- **p**: {sp['p']:.4e}")
        lines.append(f"- **n**: {sp['n']}")

    if result.get('re_vs_token_count'):
        lines.append('')
        lines.append('## RE vs Token Count')
        lines.append('')
        tc = result['re_vs_token_count']
        lines.append(f"- **rho**: {tc['rho']:.4f}")
        lines.append(f"- **p**: {tc['p']:.4e}")

    if result.get('spearman_vs_level'):
        lines.append('')
        lines.append('## Spearman Correlations vs Level')
        lines.append('')
        lines.append('| Metric | rho | p | n |')
        lines.append('|--------|-----|---|---|')
        for m, sp in result['spearman_vs_level'].items():
            lines.append(f"| {m} | {sp['rho']:.4f} | {sp['p']:.4e} | {sp['n']} |")

    if result.get('per_level'):
        lines.append('')
        lines.append('## Per-Level Statistics')
        lines.append('')
        lvls = result['per_level']
        # Detect which keys exist
        sample = lvls[0] if lvls else {}
        re_cols = [k for k in sample if k.endswith('_mean') or k in ('mean', 'std', 'min', 'max')]
        if 'mean' in sample:
            lines.append('| Level | n | Mean RE | Std RE | Min RE | Max RE |')
            lines.append('|-------|---|---------|--------|--------|--------|')
            for lv in lvls:
                lines.append(f"| {lv['level']} | {lv['n']} | {lv['mean']:.6f} | {lv['std']:.6f} | {lv['min']:.6f} | {lv['max']:.6f} |")
        else:
            # Multi-metric
            header_parts = ['Level', 'n']
            for k in sorted(re_cols):
                header_parts.append(k)
            lines.append('| ' + ' | '.join(header_parts) + ' |')
            lines.append('|' + '|'.join(['---'] * len(header_parts)) + '|')
            for lv in lvls:
                row = [str(lv['level']), str(lv['n'])]
                for k in sorted(re_cols):
                    v = lv.get(k)
                    row.append(f"{v:.6f}" if isinstance(v, float) else str(v))
                lines.append('| ' + ' | '.join(row) + ' |')

    if result.get('per_condition'):
        lines.append('')
        lines.append('## Per-Condition Statistics')
        lines.append('')
        lines.append('| Condition | n | Mean Prefill RE | Mean Gen RE | Mean Slope |')
        lines.append('|-----------|---|-----------------|-------------|------------|')
        for c, v in result['per_condition'].items():
            pf = f"{v['mean_prefill_re']:.6f}" if v.get('mean_prefill_re') else '-'
            gr = f"{v['mean_gen_re']:.6f}" if v.get('mean_gen_re') else '-'
            sl = f"{v['mean_slope']:.6e}" if v.get('mean_slope') else '-'
            lines.append(f"| {c} | {v['n']} | {pf} | {gr} | {sl} |")

    if result.get('per_category'):
        lines.append('')
        lines.append('## Per-Category Statistics')
        lines.append('')
        lines.append('| Category | n | Mean Diff | Std | Cohen d | Pos/N | Mean KL | Mean Jaccard |')
        lines.append('|----------|---|-----------|-----|---------|-------|---------|-------------|')
        for c, v in result['per_category'].items():
            cd = f"{v['cohens_d']:.3f}" if 'cohens_d' in v else '-'
            lines.append(f"| {c} | {v['n']} | {v['mean_diff']:+.6f} | {v['std_diff']:.6f} | {cd} | {v['n_positive']}/{v['n']} | {v['mean_kl']:.6f} | {v['mean_jaccard']:.4f} |")

    # Regime switch conditions
    for cond_key in ['EXPERIMENTAL', 'CONTROL']:
        cond = result.get(cond_key)
        if cond and isinstance(cond, dict):
            lines.append('')
            lines.append(f'## {cond_key}')
            lines.append('')
            lines.append(f"- **Total tokens**: {cond.get('total_tokens', '?')}")
            lines.append(f"- **N layers**: {cond.get('n_layers', '?')}")
            if cond.get('overall_mean_entropy') is not None:
                lines.append(f"- **Mean entropy**: {cond['overall_mean_entropy']:.6f}")
                lines.append(f"- **Std entropy**: {cond['overall_std_entropy']:.6f}")
            if cond.get('per_block'):
                lines.append('')
                lines.append('| Block | Start | End | N Tokens | Mean Entropy | Std Entropy |')
                lines.append('|-------|-------|-----|----------|--------------|-------------|')
                for b in cond['per_block']:
                    lines.append(f"| {b['block']} | {b['start_token']} | {b['end_token']} | {b['n_tokens']} | {b['mean_entropy']:.6f} | {b['std_entropy']:.6f} |")

    # Qwen recalculated Spearman
    for key_prefix in ['recalc_spearman_all_token_vs_level', 'recalc_spearman_last_token_vs_level',
                        'recalc_spearman_all_token_vs_ntokens', 'recalc_spearman_last_token_vs_ntokens']:
        sp = result.get(key_prefix)
        if sp:
            lines.append('')
            lines.append(f'## {key_prefix.replace("_", " ").title()}')
            lines.append('')
            lines.append(f"- **rho**: {sp['rho']:.4f}")
            lines.append(f"- **p**: {sp['p']:.4e}")
            if 'n' in sp:
                lines.append(f"- **n**: {sp['n']}")

    # Original Spearman (Qwen pre-computed)
    for key_prefix in ['original_spearman_all_token', 'original_spearman_last_token',
                        'original_spearman_all_token_vs_ntokens', 'original_spearman_last_token_vs_ntokens']:
        sp = result.get(key_prefix)
        if sp:
            lines.append('')
            lines.append(f'## {key_prefix.replace("_", " ").title()} (from source)')
            lines.append('')
            lines.append(f"- **rho**: {sp['rho']:.4f}")
            lines.append(f"- **p**: {sp['p']:.4e}")
            if 'n' in sp:
                lines.append(f"- **n**: {sp['n']}")

    # Level summary (Qwen format)
    if result.get('level_summary'):
        lines.append('')
        lines.append('## Level Summary')
        lines.append('')
        ls = result['level_summary']
        sample = ls[0] if ls else {}
        cols = list(sample.keys())
        lines.append('| ' + ' | '.join(cols) + ' |')
        lines.append('|' + '|'.join(['---'] * len(cols)) + '|')
        for lv in ls:
            row = []
            for c in cols:
                v = lv.get(c, '')
                if isinstance(v, float):
                    row.append(f"{v:.6f}")
                else:
                    row.append(str(v))
            lines.append('| ' + ' | '.join(row) + ' |')

    # Architecture info
    for key in ['n_experts', 'n_expert_used', 'n_moe_layers', 'architecture']:
        if result.get(key):
            lines.append(f"- **{key}**: {result[key]}")

    if result.get('per_prompt'):
        lines.append('')
        lines.append('## Per-Prompt Data')
        lines.append('')
        sample = result['per_prompt'][0] if result['per_prompt'] else {}
        cols = list(sample.keys())
        lines.append('| ' + ' | '.join(cols) + ' |')
        lines.append('|' + '|'.join(['---'] * len(cols)) + '|')
        for p in result['per_prompt']:
            row = []
            for c in cols:
                v = p.get(c, '')
                if isinstance(v, float):
                    if abs(v) < 0.001 and v != 0:
                        row.append(f"{v:.6e}")
                    else:
                        row.append(f"{v:.6f}")
                else:
                    row.append(str(v))
            lines.append('| ' + ' | '.join(row) + ' |')

    # Per-pair (selfref)
    if result.get('per_pair'):
        lines.append('')
        lines.append('## Per-Pair Data')
        lines.append('')
        sample = result['per_pair'][0] if result['per_pair'] else {}
        cols = list(sample.keys())
        lines.append('| ' + ' | '.join(cols) + ' |')
        lines.append('|' + '|'.join(['---'] * len(cols)) + '|')
        for p in result['per_pair']:
            row = []
            for c in cols:
                v = p.get(c, '')
                if isinstance(v, float):
                    if abs(v) < 0.001 and v != 0:
                        row.append(f"{v:.6e}")
                    else:
                        row.append(f"{v:.6f}")
                else:
                    row.append(str(v))
            lines.append('| ' + ' | '.join(row) + ' |')

    return lines


# ============================================================
# MAIN: Define all runs and process them
# ============================================================

RUNS = []

# --- 98q-r1 baseline ---
p98 = BASE / "legacy/pre-2026-03-05/results/98q-r1/results_98_routing_prefill.json"
if p98.exists():
    RUNS.append(('98q-r1_prefill', 'prefill_hierarchy', str(p98), {'model_override': 'DeepSeek-V3.1 UD-Q2_K_XL'}))

# Also check for the generation version
p98g = BASE / "legacy/pre-2026-03-05/results/98q-r1/results_98_routing.json"
if p98g.exists():
    RUNS.append(('98q-r1_generation', 'prefill_hierarchy', str(p98g), {'model_override': 'DeepSeek-V3.1 UD-Q2_K_XL'}))

# --- 14q-r1 ---
p14r1 = BASE / "legacy/pre-2026-03-05/results/14q-r1/results_14_routing_prefill.json"
if p14r1.exists():
    RUNS.append(('14q-r1_prefill', 'prefill_hierarchy', str(p14r1), {'model_override': 'DeepSeek-V3.1 UD-Q2_K_XL'}))

# --- 14q-r2 through r7 ---
for rnum, fname in [
    ('r2', 'results_14_nexus7_prefill.json'),
    ('r3', 'results_14_strange_loops_prefill.json'),
    ('r4', 'results_14_architectural_prefill.json'),
    ('r5', 'results_14_echo_prefill.json'),
    ('r6', 'results_14_bob_prefill.json'),
    ('r7', 'results_14_aether_prefill.json'),
]:
    p = BASE / f"legacy/14q-{rnum}" / fname
    if p.exists():
        RUNS.append((f'14q-{rnum}_prefill', 'prefill_hierarchy', str(p), {'model_override': 'DeepSeek-V3.1 UD-Q2_K_XL'}))

# --- 168q-r1 R1 ---
p168 = BASE / "legacy/168q-r1/results_168_r1_prefill.json"
if p168.exists():
    RUNS.append(('168q-r1_R1_prefill', 'prefill_hierarchy', str(p168), {'model_override': 'DeepSeek-R1 UD-Q2_K_XL'}))

# --- ds31-168q-1 ---
pds168 = BASE / "experiments/ds31-168q-1/results_168q_ds31_prefill.json"
if pds168.exists():
    RUNS.append(('ds31-168q-1_prefill', 'prefill_hierarchy', str(pds168), {'model_override': 'DeepSeek-V3.1 UD-Q2_K_XL'}))

# --- qwen-168q-1 ---
pq168 = BASE / "experiments/qwen-168q-1/results_168q_qwen_prefill.json"
if pq168.exists():
    RUNS.append(('qwen-168q-1_run1', 'qwen_hierarchy', str(pq168), {}))

pq168r2 = BASE / "experiments/qwen-168q-1/results_168q_qwen_prefill_run2.json"
if pq168r2.exists():
    RUNS.append(('qwen-168q-1_run2', 'qwen_hierarchy', str(pq168r2), {}))

# --- 28q-qwen397b-run1 ---
p28q = BASE / "experiments/28q-qwen397b-run1/results_28q_qwen_prefill.json"
if p28q.exists():
    RUNS.append(('28q-qwen397b-run1', 'prefill_hierarchy', str(p28q), {'model_override': 'Qwen3.5-397B-A17B'}))

# --- Generation trajectories ---
pgen_r1 = BASE / "legacy/pre-2026-03-05/experiments/r1-28q-1/results_gen_trajectories.json"
if pgen_r1.exists():
    RUNS.append(('r1-28q-1_gen', 'gen_trajectories', str(pgen_r1), {'model_override': 'DeepSeek-R1 UD-Q2_K_XL'}))

pgen_ds31 = BASE / "legacy/pre-2026-03-05/experiments/14q-ds31-run1/results_gen_trajectories.json"
if pgen_ds31.exists():
    RUNS.append(('14q-ds31-run1_gen', 'gen_trajectories', str(pgen_ds31), {'model_override': 'DeepSeek-V3.1 UD-Q2_K_XL'}))

# --- Desktop 30-turn (optional, not repo-resident) ---
pdt_env = os.environ.get("DESKTOP_30TURN_METRICS_JSON")
if pdt_env:
    pdt = Path(pdt_env)
    if pdt.exists():
        RUNS.append(('desktop_30turn_metrics', '30turn', str(pdt), {'model_override': 'DeepSeek-V3.1'}))

# --- Regime switch ---
prs_ds31 = BASE / "experiments/regime-switch-ds31-1/regime_switch_observables.json"
if prs_ds31.exists():
    RUNS.append(('regime-switch-ds31-1', 'regime_switch', str(prs_ds31), {'model_override': 'DeepSeek-V3.1 UD-Q2_K_XL'}))

prs_gpt1 = BASE / "experiments/gptoss-regime-switch-1/regime_switch_observables_gptoss.json"
if prs_gpt1.exists():
    RUNS.append(('gptoss-regime-switch-1', 'regime_switch', str(prs_gpt1), {'model_override': 'GPT-OSS-120B'}))

prs_gpt2 = BASE / "experiments/gptoss-regime-switch-2/regime_switch_observables_gptoss.json"
if prs_gpt2.exists():
    RUNS.append(('gptoss-regime-switch-2', 'regime_switch', str(prs_gpt2), {'model_override': 'GPT-OSS-120B'}))

# --- Selfref paired ---
psr = BASE / "experiments/selfref-paired-1/analysis_results.json"
if psr.exists():
    RUNS.append(('selfref-paired-1', 'selfref_paired', str(psr), {}))

# --- 6block ---
p6b = BASE / "experiments/6block-prompts-qwen397b/results_6block_qwen_prefill.json"
if p6b.exists():
    RUNS.append(('6block-qwen397b_prefill', '6block', str(p6b), {}))

p6bc = BASE / "experiments/6block-prompts-qwen397b/results_6block_continuous_prefill.json"
if p6bc.exists():
    RUNS.append(('6block-qwen397b_continuous', '6block', str(p6bc), {}))

# --- ds31-v22-32q-1 ---
pv22 = BASE / "experiments/ds31-v22-32q-1/results_ds31_v22_prefill.json"
if pv22.exists():
    RUNS.append(('ds31-v22-32q-1_prefill', 'prefill_hierarchy', str(pv22), {'model_override': 'DeepSeek-V3.1 UD-Q2_K_XL'}))

# --- Position diagnostic ---
ppd = BASE / "experiments/position-diagnostic/diagnostic_results.json"
if ppd.exists():
    RUNS.append(('position-diagnostic', '6block', str(ppd), {}))

# --- gptoss120-v22 smoke ---
pgpt_smoke = BASE / "experiments/gptoss120-v22-32q-1/results_gptoss120_v22_choice_smoke.json"
if pgpt_smoke.exists():
    RUNS.append(('gptoss120-v22-32q-1_smoke', '6block', str(pgpt_smoke), {}))

# --- Multiseed runs ---
for seed_dir in sorted((BASE / "experiments/ds31-v22-32q-1/multiseed_choice_temp08_np3").glob("seed_*")):
    seed_json = seed_dir / "results.json"
    if seed_json.exists():
        seed_name = seed_dir.name
        RUNS.append((f'ds31-v22-32q-1_multiseed_{seed_name}', '6block', str(seed_json), {}))


# ============================================================
# RUN ALL
# ============================================================

print(f"Found {len(RUNS)} runs to process")
processed = 0
errors = []

for run_name, run_type, path, kwargs in RUNS:
    try:
        print(f"  Processing {run_name}...")
        if run_type == 'prefill_hierarchy':
            result = process_prefill_hierarchy(run_name, path, **kwargs)
        elif run_type == 'gen_trajectories':
            result = process_generation_trajectories(run_name, path, **kwargs)
        elif run_type == '30turn':
            result = process_desktop_30turn(run_name, path, **kwargs)
        elif run_type == 'regime_switch':
            result = process_regime_switch(run_name, path, **kwargs)
        elif run_type == 'qwen_hierarchy':
            result = process_qwen_hierarchy(run_name, path)
        elif run_type == 'selfref_paired':
            result = process_selfref_paired(run_name, path)
        elif run_type == '6block':
            result = process_6block(run_name, path)
        else:
            print(f"    Unknown type: {run_type}")
            continue

        # Save JSON
        save_json(result, OUT / f"{run_name}.json")

        # Save markdown
        md_lines = result_to_markdown(result)
        save_md(md_lines, OUT / f"{run_name}.md")

        processed += 1
    except Exception as e:
        errors.append((run_name, str(e)))
        print(f"    ERROR: {e}")
        import traceback
        traceback.print_exc()

print(f"\nDone: {processed}/{len(RUNS)} processed, {len(errors)} errors")
if errors:
    print("Errors:")
    for name, err in errors:
        print(f"  {name}: {err}")
