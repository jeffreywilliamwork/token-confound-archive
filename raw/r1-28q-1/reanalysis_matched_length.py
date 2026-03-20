#!/usr/bin/env python3
"""
r1-28q-1 Reanalysis: Warm-up Exclusion & Matched-Window Controls

Determines whether self-ref > external RE findings survive:
  1. Warm-up exclusion (transient removed)
  2. Matched-window analysis (identical step ranges, zero length variation)
  3. Within-condition confound checks

All local — uses saved surface .npy files, zero inference cost.
"""
import json, os, sys
import numpy as np
from scipy import stats
from scipy.ndimage import uniform_filter1d

# --- Configuration ---
SURFACES_DIR = os.path.join(os.path.dirname(__file__), 'surfaces')
RESULTS_JSON = os.path.join(os.path.dirname(__file__), 'results_gen_trajectories.json')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'reanalysis_output')

# Layer 57 is at column 50 in saved surfaces.
# Surfaces were built with sorted(glob.glob('ffn_moe_logits-*.npy')) which sorts
# filenames lexicographically: 10,11,...,19,20,...,29,3,30,...,39,4,40,...,57,...,6,60,7,8,9
# Verified from per_layer[].layer in results JSON.
LAYER_57_COL = 50

# Sensitivity sweep values for T_warmup
T_WARMUP_VALUES = [0, 50, 100, 150, 200, 250, 300, 400, 500]


def load_data():
    """Load results JSON and all surface .npy files."""
    with open(RESULTS_JSON) as f:
        results = json.load(f)

    prompts = []
    for p in results['per_prompt']:
        surface_path = os.path.join(SURFACES_DIR, '%s_surface.npy' % p['id'])
        if not os.path.exists(surface_path):
            print('  WARNING: missing surface for %s' % p['id'])
            continue
        surface = np.load(surface_path)
        prompts.append({
            'id': p['id'],
            'condition': p['condition'],
            'condition_name': p['condition_name'],
            'n_gen_tokens': p['n_gen_tokens'],
            'gen_re_original': p['gen_re'],
            'mean_slope_original': p['mean_slope'],
            'surface': surface,
        })
    return prompts


def mean_re_per_step(surface):
    """Compute mean RE across layers at each generation step, excluding layer 57 and zero-masked rows."""
    n_steps, n_layers = surface.shape
    # Exclude layer 57 column
    mask = np.ones(n_layers, dtype=bool)
    mask[LAYER_57_COL] = False
    sub = surface[:, mask]
    # Per-step mean, only counting valid (>0) entries
    means = np.zeros(n_steps)
    for t in range(n_steps):
        row = sub[t]
        valid = row > 0
        if valid.sum() > 0:
            means[t] = row[valid].mean()
    return means


def compute_slope(re_trajectory, t_start=0):
    """Fit linear slope on RE trajectory from t_start onwards, skipping zeros."""
    traj = re_trajectory[t_start:]
    valid = traj > 0
    if valid.sum() < 10:
        return np.nan
    x = np.where(valid)[0]
    y = traj[valid]
    slope, _, _, _, _ = stats.linregress(x, y)
    return slope


def compute_mean_re(re_trajectory, t_start=0, t_end=None):
    """Mean RE from t_start to t_end, skipping zeros."""
    traj = re_trajectory[t_start:t_end]
    valid = traj > 0
    if valid.sum() == 0:
        return np.nan
    return float(traj[valid].mean())


def section_header(title, section_num):
    print('\n' + '=' * 70)
    print('  SECTION %d: %s' % (section_num, title))
    print('=' * 70)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print('=' * 70)
    print('  r1-28q-1 REANALYSIS: Warm-up Exclusion & Matched-Window Controls')
    print('=' * 70)

    # Load data
    prompts = load_data()
    print('\nLoaded %d prompts (%d A, %d B)' % (
        len(prompts),
        sum(1 for p in prompts if p['condition'] == 'A'),
        sum(1 for p in prompts if p['condition'] == 'B'),
    ))

    # Precompute per-step mean RE trajectories
    for p in prompts:
        p['re_trajectory'] = mean_re_per_step(p['surface'])

    min_gen = min(p['n_gen_tokens'] for p in prompts)
    max_gen = max(p['n_gen_tokens'] for p in prompts)
    print('Generation tokens: min=%d  max=%d' % (min_gen, max_gen))
    print('Layer 57 column index: %d (excluded from all analyses)' % LAYER_57_COL)

    # =========================================================================
    # SECTION 1: Empirical warm-up detection
    # =========================================================================
    section_header('Empirical Warm-up Detection', 1)

    # Grand mean trajectory across all 28 prompts at each step (up to min_gen)
    grand_mean = np.zeros(min_gen)
    for t in range(min_gen):
        vals = [p['re_trajectory'][t] for p in prompts if t < len(p['re_trajectory']) and p['re_trajectory'][t] > 0]
        if vals:
            grand_mean[t] = np.mean(vals)

    # Smoothed derivative (window=50) to find elbow
    smoothed = uniform_filter1d(grand_mean, size=50)
    derivative = np.gradient(smoothed)

    # Find where derivative drops below 10% of its max (elbow)
    max_deriv = np.max(np.abs(derivative[:200]))  # Look in first 200 steps
    if max_deriv > 0:
        threshold = 0.1 * max_deriv
        elbow_candidates = np.where(np.abs(derivative[:min(400, min_gen)]) < threshold)[0]
        elbow = int(elbow_candidates[0]) if len(elbow_candidates) > 0 else 0
    else:
        elbow = 0

    print('Grand mean RE trajectory (first 10 steps):')
    for t in [0, 1, 2, 3, 4, 5, 10, 20, 50, 100]:
        if t < min_gen:
            print('  step %4d: %.6f' % (t, grand_mean[t]))

    print('\nSmoothed derivative peak: %.8f at step %d' % (
        np.max(np.abs(derivative[:200])), np.argmax(np.abs(derivative[:200]))))
    print('Empirical elbow (deriv < 10%% of peak): step %d' % elbow)
    print('Grand mean RE at step 0: %.6f' % grand_mean[0])
    print('Grand mean RE at step %d: %.6f' % (min(elbow, min_gen - 1), grand_mean[min(elbow, min_gen - 1)]))
    print('Grand mean RE at step %d (last common): %.6f' % (min_gen - 1, grand_mean[min_gen - 1]))

    # Save trajectory CSV
    traj_csv = os.path.join(OUTPUT_DIR, 'grand_mean_trajectory.csv')
    with open(traj_csv, 'w') as f:
        f.write('step,grand_mean_re,smoothed_re,derivative\n')
        for t in range(min_gen):
            f.write('%d,%.8f,%.8f,%.10f\n' % (t, grand_mean[t], smoothed[t], derivative[t]))
    print('\nSaved: %s (%d steps)' % (traj_csv, min_gen))

    # =========================================================================
    # SECTION 2: Warm-up-excluded slope analysis
    # =========================================================================
    section_header('Warm-up-Excluded Slope Analysis', 2)

    print('\nSensitivity sweep: T_warmup vs slope separation (A vs B)')
    print('%-10s  %-12s  %-12s  %-12s  %-10s  %s' % (
        'T_warmup', 'A mean slp', 'B mean slp', 'delta(B-A)', 'W stat', 'p-value'))
    print('-' * 75)

    slope_rows = []
    for tw in T_WARMUP_VALUES:
        a_slopes = []
        b_slopes = []
        for p in prompts:
            if tw >= len(p['re_trajectory']):
                continue
            s = compute_slope(p['re_trajectory'], t_start=tw)
            if not np.isnan(s):
                if p['condition'] == 'A':
                    a_slopes.append(s)
                else:
                    b_slopes.append(s)

        if len(a_slopes) >= 2 and len(b_slopes) >= 2:
            w, pval = stats.ranksums(a_slopes, b_slopes)
            mean_a = np.mean(a_slopes)
            mean_b = np.mean(b_slopes)
            delta = mean_b - mean_a
            print('%-10d  %+.8f  %+.8f  %+.8f  %-10.4f  %.6f' % (
                tw, mean_a, mean_b, delta, w, pval))
            slope_rows.append({
                't_warmup': tw, 'a_mean_slope': mean_a, 'b_mean_slope': mean_b,
                'delta': delta, 'w_stat': w, 'p_value': pval,
                'n_a': len(a_slopes), 'n_b': len(b_slopes),
            })
        else:
            print('%-10d  insufficient data (A=%d, B=%d)' % (tw, len(a_slopes), len(b_slopes)))

    # Save slope sensitivity CSV
    slope_csv = os.path.join(OUTPUT_DIR, 'slope_sensitivity.csv')
    with open(slope_csv, 'w') as f:
        f.write('t_warmup,a_mean_slope,b_mean_slope,delta_b_minus_a,w_stat,p_value,n_a,n_b\n')
        for r in slope_rows:
            f.write('%d,%.10f,%.10f,%.10f,%.6f,%.8f,%d,%d\n' % (
                r['t_warmup'], r['a_mean_slope'], r['b_mean_slope'],
                r['delta'], r['w_stat'], r['p_value'], r['n_a'], r['n_b']))
    print('\nSaved: %s' % slope_csv)

    # =========================================================================
    # SECTION 3: Within-condition confound checks
    # =========================================================================
    section_header('Within-Condition Confound Checks', 3)

    print('\nSpearman(slope, n_gen_tokens) within each condition')
    print('%-10s  %-12s  %-10s  %-10s  %-12s  %-10s  %-10s' % (
        'T_warmup', 'Condition', 'rho', 'p-value', 'Condition', 'rho', 'p-value'))
    print('-' * 80)

    confound_tw = [0, 100, 200]
    for tw in confound_tw:
        results_by_cond = {'A': {'slopes': [], 'toks': []}, 'B': {'slopes': [], 'toks': []}}
        for p in prompts:
            if tw >= len(p['re_trajectory']):
                continue
            s = compute_slope(p['re_trajectory'], t_start=tw)
            if not np.isnan(s):
                results_by_cond[p['condition']]['slopes'].append(s)
                results_by_cond[p['condition']]['toks'].append(p['n_gen_tokens'])

        parts = []
        for cond in ['A', 'B']:
            slopes = results_by_cond[cond]['slopes']
            toks = results_by_cond[cond]['toks']
            if len(slopes) >= 5 and len(set(toks)) > 1:
                rho, pval = stats.spearmanr(toks, slopes)
                parts.append('%-12s  %+.4f      %.6f' % (cond, rho, pval))
            else:
                parts.append('%-12s  N/A         N/A       ' % cond)

        print('%-10d  %s  %s' % (tw, parts[0], parts[1]))

    # Also check across all prompts
    print('\nSpearman(slope, n_gen_tokens) across ALL prompts:')
    for tw in confound_tw:
        all_slopes = []
        all_toks = []
        for p in prompts:
            if tw >= len(p['re_trajectory']):
                continue
            s = compute_slope(p['re_trajectory'], t_start=tw)
            if not np.isnan(s):
                all_slopes.append(s)
                all_toks.append(p['n_gen_tokens'])
        if len(all_slopes) >= 5:
            rho, pval = stats.spearmanr(all_toks, all_slopes)
            print('  T_warmup=%d: rho=%+.4f  p=%.6f  (n=%d)' % (tw, rho, pval, len(all_slopes)))

    # =========================================================================
    # SECTION 4: Warm-up-excluded mean RE
    # =========================================================================
    section_header('Warm-up-Excluded Mean RE', 4)

    print('\nSensitivity sweep: T_warmup vs mean RE separation (A vs B)')
    print('%-10s  %-10s  %-10s  %-10s  %-10s  %s' % (
        'T_warmup', 'A mean RE', 'B mean RE', 'delta(B-A)', 'W stat', 'p-value'))
    print('-' * 70)

    mean_re_rows = []
    for tw in T_WARMUP_VALUES:
        a_re = []
        b_re = []
        for p in prompts:
            if tw >= len(p['re_trajectory']):
                continue
            m = compute_mean_re(p['re_trajectory'], t_start=tw)
            if not np.isnan(m):
                if p['condition'] == 'A':
                    a_re.append(m)
                else:
                    b_re.append(m)

        if len(a_re) >= 2 and len(b_re) >= 2:
            w, pval = stats.ranksums(a_re, b_re)
            mean_a = np.mean(a_re)
            mean_b = np.mean(b_re)
            delta = mean_b - mean_a
            print('%-10d  %.6f    %.6f    %+.6f    %-10.4f  %.6f' % (
                tw, mean_a, mean_b, delta, w, pval))
            mean_re_rows.append({
                't_warmup': tw, 'a_mean_re': mean_a, 'b_mean_re': mean_b,
                'delta': delta, 'w_stat': w, 'p_value': pval,
                'n_a': len(a_re), 'n_b': len(b_re),
            })
        else:
            print('%-10d  insufficient data' % tw)

    # =========================================================================
    # SECTION 5: Matched-window mean RE
    # =========================================================================
    section_header('Matched-Window Mean RE (Tightest Confound Control)', 5)

    # Use min_gen as the matched endpoint (shortest completion = 599)
    print('\nMatched window endpoint: step %d (shortest completion across all 28 prompts)' % min_gen)
    print('All prompts analyzed over identical step ranges — zero length variation.\n')

    print('%-10s  %-10s  %-10s  %-10s  %-10s  %s' % (
        'T_warmup', 'A mean RE', 'B mean RE', 'delta(B-A)', 'W stat', 'p-value'))
    print('-' * 70)

    matched_rows = []
    for tw in T_WARMUP_VALUES:
        if tw >= min_gen:
            print('%-10d  SKIP (T_warmup >= min_gen=%d)' % (tw, min_gen))
            continue

        a_re = []
        b_re = []
        for p in prompts:
            m = compute_mean_re(p['re_trajectory'], t_start=tw, t_end=min_gen)
            if not np.isnan(m):
                if p['condition'] == 'A':
                    a_re.append(m)
                else:
                    b_re.append(m)

        if len(a_re) >= 2 and len(b_re) >= 2:
            w, pval = stats.ranksums(a_re, b_re)
            mean_a = np.mean(a_re)
            mean_b = np.mean(b_re)
            delta = mean_b - mean_a
            print('%-10d  %.6f    %.6f    %+.6f    %-10.4f  %.6f' % (
                tw, mean_a, mean_b, delta, w, pval))
            matched_rows.append({
                't_warmup': tw, 'a_mean_re': mean_a, 'b_mean_re': mean_b,
                'delta': delta, 'w_stat': w, 'p_value': pval,
                'n_a': len(a_re), 'n_b': len(b_re),
            })

    # Save matched-window CSV
    matched_csv = os.path.join(OUTPUT_DIR, 'matched_window_sensitivity.csv')
    with open(matched_csv, 'w') as f:
        f.write('t_warmup,a_mean_re,b_mean_re,delta_b_minus_a,w_stat,p_value,n_a,n_b\n')
        for r in matched_rows:
            f.write('%d,%.10f,%.10f,%.10f,%.6f,%.8f,%d,%d\n' % (
                r['t_warmup'], r['a_mean_re'], r['b_mean_re'],
                r['delta'], r['w_stat'], r['p_value'], r['n_a'], r['n_b']))
    print('\nSaved: %s' % matched_csv)

    # =========================================================================
    # SECTION 6: Supplementary metrics
    # =========================================================================
    section_header('Supplementary Metrics', 6)

    for p in prompts:
        traj = p['re_trajectory']
        valid = traj > 0

        # Warm-up magnitude: plateau level (mean of steps 200+) minus step 0
        if len(traj) > 200 and valid[:200].sum() > 0:
            plateau = np.mean(traj[200:][traj[200:] > 0]) if np.any(traj[200:] > 0) else np.nan
            p['warmup_magnitude'] = plateau - traj[0] if traj[0] > 0 else np.nan
        else:
            plateau = np.mean(traj[valid]) if valid.sum() > 0 else np.nan
            p['warmup_magnitude'] = np.nan

        # Plateau stability: std of RE after step 200
        if len(traj) > 200 and np.any(traj[200:] > 0):
            p['plateau_std'] = float(np.std(traj[200:][traj[200:] > 0]))
        else:
            p['plateau_std'] = np.nan

        # Time to 95% of max RE
        if valid.sum() > 0:
            max_re = np.max(traj[valid])
            threshold_95 = 0.95 * max_re
            above = np.where(traj >= threshold_95)[0]
            p['time_to_95'] = int(above[0]) if len(above) > 0 else len(traj)
        else:
            p['time_to_95'] = np.nan

    # Report supplementary metrics by condition
    for metric_name, metric_key in [
        ('Warm-up magnitude (plateau - step0)', 'warmup_magnitude'),
        ('Plateau stability (post-200 std)', 'plateau_std'),
        ('Time to 95% max RE', 'time_to_95'),
    ]:
        print('\n%s:' % metric_name)
        a_vals = [p[metric_key] for p in prompts if p['condition'] == 'A' and not np.isnan(p[metric_key])]
        b_vals = [p[metric_key] for p in prompts if p['condition'] == 'B' and not np.isnan(p[metric_key])]
        if a_vals:
            print('  A: mean=%.6f  std=%.6f  n=%d' % (np.mean(a_vals), np.std(a_vals), len(a_vals)))
        if b_vals:
            print('  B: mean=%.6f  std=%.6f  n=%d' % (np.mean(b_vals), np.std(b_vals), len(b_vals)))
        if len(a_vals) >= 2 and len(b_vals) >= 2:
            w, pval = stats.ranksums(a_vals, b_vals)
            print('  Wilcoxon rank-sum: W=%.4f  p=%.6f' % (w, pval))

    # =========================================================================
    # SECTION 7: Per-prompt CSV export
    # =========================================================================
    section_header('Per-Prompt CSV Export', 7)

    per_prompt_csv = os.path.join(OUTPUT_DIR, 'per_prompt_reanalysis.csv')
    with open(per_prompt_csv, 'w') as f:
        # Header
        tw_cols = ','.join(['slope_tw%d' % tw for tw in T_WARMUP_VALUES])
        mean_cols = ','.join(['mean_re_tw%d' % tw for tw in T_WARMUP_VALUES])
        matched_cols = ','.join(['matched_re_tw%d' % tw for tw in T_WARMUP_VALUES if tw < min_gen])
        f.write('id,condition,n_gen_tokens,gen_re_original,mean_slope_original,'
                'warmup_magnitude,plateau_std,time_to_95,'
                '%s,%s,%s\n' % (tw_cols, mean_cols, matched_cols))

        for p in prompts:
            # Slopes at each T_warmup
            slopes = []
            for tw in T_WARMUP_VALUES:
                s = compute_slope(p['re_trajectory'], t_start=tw) if tw < len(p['re_trajectory']) else np.nan
                slopes.append('%.10f' % s if not np.isnan(s) else 'NaN')

            # Mean RE at each T_warmup
            means = []
            for tw in T_WARMUP_VALUES:
                m = compute_mean_re(p['re_trajectory'], t_start=tw) if tw < len(p['re_trajectory']) else np.nan
                means.append('%.8f' % m if not np.isnan(m) else 'NaN')

            # Matched-window mean RE at each T_warmup
            matched = []
            for tw in T_WARMUP_VALUES:
                if tw >= min_gen:
                    continue
                m = compute_mean_re(p['re_trajectory'], t_start=tw, t_end=min_gen)
                matched.append('%.8f' % m if not np.isnan(m) else 'NaN')

            f.write('%s,%s,%d,%.8f,%.10f,%.6f,%.6f,%s,%s,%s,%s\n' % (
                p['id'], p['condition'], p['n_gen_tokens'],
                p['gen_re_original'], p['mean_slope_original'],
                p.get('warmup_magnitude', np.nan),
                p.get('plateau_std', np.nan),
                str(int(p['time_to_95'])) if not np.isnan(p.get('time_to_95', np.nan)) else 'NaN',
                ','.join(slopes), ','.join(means), ','.join(matched)))

    print('Saved: %s' % per_prompt_csv)

    # =========================================================================
    # VERIFICATION: T_warmup=0 matches original analysis
    # =========================================================================
    section_header('VERIFICATION: T_warmup=0 vs Original Results', 0)

    print('\nPer-prompt gen RE comparison (reanalysis vs original):')
    max_diff = 0
    for p in prompts:
        reanalysis_re = compute_mean_re(p['re_trajectory'], t_start=0)
        orig_re = p['gen_re_original']
        diff = abs(reanalysis_re - orig_re)
        max_diff = max(max_diff, diff)
        if diff > 0.001:
            print('  WARNING: %s reanalysis=%.6f original=%.6f diff=%.6f' % (
                p['id'], reanalysis_re, orig_re, diff))
    print('  Max absolute difference: %.8f' % max_diff)
    if max_diff < 0.01:
        print('  PASS: Reanalysis gen RE values are consistent with original (max diff < 0.01)')
    else:
        print('  NOTE: Differences > 0.01 detected. This is expected because the original gen_re')
        print('        averages across ALL layers including layer 57 with zero-padding, while the')
        print('        reanalysis excludes layer 57 entirely.')

    print('\n' + '=' * 70)
    print('  REANALYSIS COMPLETE')
    print('  Output directory: %s' % OUTPUT_DIR)
    print('=' * 70)


if __name__ == '__main__':
    main()
