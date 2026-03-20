#!/usr/bin/env python3
"""
r1-28q-1: Generation-phase routing entropy trajectories on DeepSeek R1.

Changes from gen-r1:
  - R1 chat template wrapping in TSV (generate_tsv.py)
  - Flash attention + q8 KV cache: -fa on --cache-type-k q8_0 --cache-type-v q8_0
  - Context 16384 (was 4096), n_predict 2000 (was 256) to let R1 finish naturally
  - --no-stream flag (suppresses stdout text streaming)
  - Binary saves generated_text.txt per prompt automatically
  - Surfaces saved BEFORE cleanup (no data loss)
"""
import subprocess, json, numpy as np, os, glob, sys, shutil
from scipy import stats
from scipy.special import softmax

MODEL = '/workspace/models/DeepSeek-R1-UD-Q2_K_XL/DeepSeek-R1-UD-Q2_K_XL-00001-of-00005.gguf'
BINARY = '/workspace/consciousness-experiment/capture_activations'
TSV = '/workspace/experiment-r1-28q-1/prompts_28.tsv'
OUTPUT_DIR = '/workspace/experiment-r1-28q-1/output'
SURFACES_DIR = '/workspace/experiment-r1-28q-1/surfaces'
RESULTS_JSON = '/workspace/experiment-r1-28q-1/results_gen_trajectories.json'
NGL = 30
CTX = 16384
N_PREDICT = 2000
THREADS = 16

def run_capture():
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = '/workspace/llama.cpp.new/build/bin:' + env.get('LD_LIBRARY_PATH', '')
    cmd = [BINARY, '-m', MODEL, '--prompt-file', TSV,
           '-o', OUTPUT_DIR,
           '-n', str(N_PREDICT), '-ngl', str(NGL),
           '-c', str(CTX), '-t', str(THREADS),
           '-fa', 'on',
           '--cache-type-k', 'q8_0',
           '--cache-type-v', 'q8_0',
           '--routing-only',
           '--no-stream']
    print('Running:', ' '.join(cmd))
    sys.stdout.flush()
    subprocess.run(cmd, env=env)

def get_metadata(output_dir):
    meta = os.path.join(output_dir, 'metadata.txt')
    info = {}
    if os.path.exists(meta):
        with open(meta) as f:
            for line in f:
                line = line.strip()
                if '=' in line:
                    key, val = line.split('=', 1)
                    info[key] = val
    n_prompt = int(info.get('n_tokens_prompt', 0))
    n_gen = int(info.get('n_tokens_generated', 0))
    return n_prompt, n_gen

def compute_entropy_surface(output_dir, n_prompt, n_gen):
    """Compute per-step entropy surface [n_gen_steps, 58 layers]."""
    router_dir = os.path.join(output_dir, 'router')
    if not os.path.exists(router_dir):
        return None, None, None, None, None, None

    gate_files = sorted(glob.glob(os.path.join(router_dir, 'ffn_moe_logits-*.npy')))
    if not gate_files:
        return None, None, None, None, None, None

    n_layers = len(gate_files)
    if n_gen == 0:
        return None, None, None, None, None, None

    # Build entropy surface [gen_steps, layers]
    surface = np.zeros((n_gen, n_layers))
    prefill_ents = []
    layer_ids = []

    for i, f in enumerate(gate_files):
        logits = np.load(f)
        if logits.ndim != 2:
            continue

        fname = os.path.basename(f)
        layer_num = int(fname.replace('ffn_moe_logits-', '').replace('.npy', ''))
        layer_ids.append(layer_num)

        n_total = logits.shape[0]
        max_ent = np.log2(logits.shape[1])

        # Full entropy
        probs = softmax(logits, axis=-1)
        ent = -np.sum(probs * np.log2(probs + 1e-10), axis=-1) / max_ent

        # Prefill slice
        if n_prompt > 0 and n_prompt <= n_total:
            prefill_ents.extend(ent[:n_prompt].tolist())

        # Generation slice — one row per step
        gen_start = min(n_prompt, n_total)
        gen_end = min(gen_start + n_gen, n_total)
        gen_ent = ent[gen_start:gen_end]

        # Zero-mask layer 57 bug: may have fewer rows
        surface[:len(gen_ent), i] = gen_ent

    # Per-layer detail
    per_layer = []
    for li in range(n_layers):
        col = surface[:, li]
        valid = col > 0  # Mask zero-padded rows (layer 57 bug)
        if valid.sum() >= 10:
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                np.where(valid)[0], col[valid])
            layer_detail = {
                'layer': layer_ids[li] if li < len(layer_ids) else li,
                'mean': float(np.mean(col[valid])),
                'std': float(np.std(col[valid])),
                'min': float(np.min(col[valid])),
                'max': float(np.max(col[valid])),
                'slope': float(slope),
                'r_squared': float(r_value**2),
                'n_valid': int(valid.sum()),
            }
        elif valid.sum() > 0:
            layer_detail = {
                'layer': layer_ids[li] if li < len(layer_ids) else li,
                'mean': float(np.mean(col[valid])),
                'std': float(np.std(col[valid])),
                'min': float(np.min(col[valid])),
                'max': float(np.max(col[valid])),
                'slope': float('nan'),
                'r_squared': float('nan'),
                'n_valid': int(valid.sum()),
            }
        else:
            layer_detail = {
                'layer': layer_ids[li] if li < len(layer_ids) else li,
                'mean': 0.0, 'std': 0.0, 'min': 0.0, 'max': 0.0,
                'slope': float('nan'), 'r_squared': float('nan'),
                'n_valid': 0,
            }
        per_layer.append(layer_detail)

    # Slopes vector (for backward compat)
    slopes = np.array([d['slope'] for d in per_layer])

    prefill_re = float(np.mean(prefill_ents)) if prefill_ents else None
    gen_re = float(np.mean(surface[surface > 0])) if np.any(surface > 0) else 0.0

    return surface, slopes, prefill_re, gen_re, layer_ids, per_layer

def cleanup_npy(output_dir):
    """Remove .npy files but keep metadata.txt and generated_text.txt."""
    router_dir = os.path.join(output_dir, 'router')
    if os.path.exists(router_dir):
        shutil.rmtree(router_dir)
    layers_dir = os.path.join(output_dir, 'layers')
    if os.path.exists(layers_dir):
        shutil.rmtree(layers_dir)

def main():
    os.makedirs(SURFACES_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print('=== r1-28q-1: Generation-Phase Routing Trajectories ===')
    print('Model: DeepSeek R1 UD-Q2_K_XL')
    print('Params: n_predict=%d ctx=%d ngl=%d flash_attn=on kv_cache=q8_0' % (N_PREDICT, CTX, NGL))
    print()

    # Phase 1: Capture
    print('=== PHASE 1: Capture (n_predict=%d, routing-only, --no-stream) ===' % N_PREDICT)
    sys.stdout.flush()
    run_capture()

    # Load prompt suite for condition mapping
    with open('/workspace/experiment-r1-28q-1/prompt-suite.json') as f:
        data = json.load(f)

    prompts = []
    for cond in data['conditions']:
        for p in cond['prompts']:
            prompts.append({
                'id': p['id'],
                'condition': cond['condition'],
                'condition_name': cond['name'],
                'text': p['text']
            })

    # Phase 2: Compute
    print('\n=== PHASE 2: Compute entropy surfaces ===')
    sys.stdout.flush()
    results = []
    for p in prompts:
        pid = p['id']
        out = os.path.join(OUTPUT_DIR, pid)
        if not os.path.exists(out):
            print('  SKIP %s: no output' % pid)
            continue

        n_prompt, n_gen = get_metadata(out)
        surface, slopes, prefill_re, gen_re, layer_ids, per_layer = compute_entropy_surface(out, n_prompt, n_gen)

        if surface is None:
            print('  SKIP %s: no valid data (n_prompt=%d, n_gen=%d)' % (pid, n_prompt, n_gen))
            continue

        # Save surface and slopes
        np.save(os.path.join(SURFACES_DIR, '%s_surface.npy' % pid), surface)
        np.save(os.path.join(SURFACES_DIR, '%s_slopes.npy' % pid), slopes)

        # Read generated text length
        gen_text_file = os.path.join(out, 'generated_text.txt')
        gen_text_chars = 0
        if os.path.exists(gen_text_file):
            with open(gen_text_file) as f:
                gen_text_chars = len(f.read())

        valid_slopes = [s for s in slopes if not np.isnan(s)]
        mean_slope = float(np.mean(valid_slopes)) if valid_slopes else float('nan')

        r = {
            'id': pid,
            'condition': p['condition'],
            'condition_name': p['condition_name'],
            'prefill_re': prefill_re,
            'gen_re': gen_re,
            'gen_re_step0': float(np.mean(surface[0][surface[0] > 0])) if np.any(surface[0] > 0) else 0.0,
            'gen_re_step_last': float(np.mean(surface[-1][surface[-1] > 0])) if np.any(surface[-1] > 0) else 0.0,
            'mean_slope': mean_slope,
            'n_prompt_tokens': n_prompt,
            'n_gen_tokens': n_gen,
            'gen_text_chars': gen_text_chars,
            'surface_shape': list(surface.shape),
            'per_layer': per_layer,
        }
        results.append(r)

        pre_s = '%.4f' % prefill_re if prefill_re else 'N/A'
        print('  %s [%s]: prefill=%-6s gen=%.4f slope=%+.6f step0=%.4f last=%.4f tokens=%d+%d' % (
            pid, p['condition'], pre_s, gen_re, mean_slope,
            r['gen_re_step0'], r['gen_re_step_last'],
            n_prompt, n_gen))

        # Cleanup .npy after extraction
        cleanup_npy(out)

    print('\n%d prompts processed' % len(results))
    sys.stdout.flush()

    # Phase 3: Per-condition stats
    print('\n=== PHASE 3: Per-condition statistics ===')
    for cond in ['A', 'B']:
        cr = [r for r in results if r['condition'] == cond]
        if not cr:
            continue
        name = cr[0]['condition_name']
        pre = [r['prefill_re'] for r in cr if r['prefill_re'] is not None]
        gen = [r['gen_re'] for r in cr]
        slopes_list = [r['mean_slope'] for r in cr if not np.isnan(r['mean_slope'])]
        s0 = [r['gen_re_step0'] for r in cr]
        sl = [r['gen_re_step_last'] for r in cr]
        toks = [r['n_gen_tokens'] for r in cr]

        print('\n  Condition %s: %s (n=%d)' % (cond, name, len(cr)))
        if pre:
            print('    Prefill RE:   %.4f (std=%.4f)' % (np.mean(pre), np.std(pre)))
        else:
            print('    Prefill RE:   N/A')
        print('    Gen RE:       %.4f (std=%.4f)' % (np.mean(gen), np.std(gen)))
        print('    Step 0 RE:    %.4f' % np.mean(s0))
        print('    Step last RE: %.4f' % np.mean(sl))
        if slopes_list:
            print('    Mean slope:   %+.6f (std=%.6f)' % (np.mean(slopes_list), np.std(slopes_list)))
        print('    Gen tokens:   mean=%.0f range=[%d, %d]' % (np.mean(toks), min(toks), max(toks)))

    # Phase 4: Statistical tests
    print('\n=== PHASE 4: Statistical tests ===')
    a_slopes = [r['mean_slope'] for r in results if r['condition'] == 'A' and not np.isnan(r['mean_slope'])]
    b_slopes = [r['mean_slope'] for r in results if r['condition'] == 'B' and not np.isnan(r['mean_slope'])]
    a_gen = [r['gen_re'] for r in results if r['condition'] == 'A']
    b_gen = [r['gen_re'] for r in results if r['condition'] == 'B']
    a_pre = [r['prefill_re'] for r in results if r['condition'] == 'A' and r['prefill_re'] is not None]
    b_pre = [r['prefill_re'] for r in results if r['condition'] == 'B' and r['prefill_re'] is not None]

    if a_slopes and b_slopes:
        w, p = stats.ranksums(a_slopes, b_slopes)
        print('  Slope A vs B (rank-sum): W=%.4f p=%.6f' % (w, p))
        print('    A mean slope=%+.6f  B mean slope=%+.6f  delta=%+.6f' % (
            np.mean(a_slopes), np.mean(b_slopes), np.mean(b_slopes) - np.mean(a_slopes)))

    if a_gen and b_gen:
        w, p = stats.ranksums(a_gen, b_gen)
        print('  Gen RE A vs B (rank-sum): W=%.4f p=%.6f' % (w, p))
        print('    A mean=%.4f  B mean=%.4f  delta=%+.4f' % (
            np.mean(a_gen), np.mean(b_gen), np.mean(b_gen) - np.mean(a_gen)))

    if a_pre and b_pre:
        w, p = stats.ranksums(a_pre, b_pre)
        print('  Prefill RE A vs B (rank-sum): W=%.4f p=%.6f' % (w, p))
        print('    A mean=%.4f  B mean=%.4f  delta=%+.4f' % (
            np.mean(a_pre), np.mean(b_pre), np.mean(b_pre) - np.mean(a_pre)))

    # Token count confound
    all_toks = [r['n_gen_tokens'] for r in results]
    all_gen = [r['gen_re'] for r in results]
    all_slopes_v = [r['mean_slope'] for r in results if not np.isnan(r['mean_slope'])]
    all_toks_for_slopes = [r['n_gen_tokens'] for r in results if not np.isnan(r['mean_slope'])]

    if len(set(all_toks)) > 1:
        rho_t, p_t = stats.spearmanr(all_toks, all_gen)
        print('  Gen RE vs token count: rho=%.4f p=%.6f' % (rho_t, p_t))
    if len(set(all_toks_for_slopes)) > 1 and all_slopes_v:
        rho_ts, p_ts = stats.spearmanr(all_toks_for_slopes, all_slopes_v)
        print('  Slope vs token count: rho=%.4f p=%.6f' % (rho_ts, p_ts))

    # Save results
    output = {
        'experiment': 'r1-28q-1',
        'description': 'Generation-phase routing entropy trajectories on DeepSeek R1',
        'model': 'DeepSeek-R1 UD-Q2_K_XL',
        'binary': 'capture_activations (b8123 cmake, sha256:c51e219f)',
        'inference': {
            'ngl': NGL,
            'n_predict': N_PREDICT,
            'ctx': CTX,
            'flash_attn': True,
            'cache_type_k': 'q8_0',
            'cache_type_v': 'q8_0',
            'sampling': 'greedy_argmax',
            'routing_only': True,
            'no_stream': True,
        },
        'chat_template': '<｜User｜>{prompt}<｜Assistant｜><think>\\n',
        'mode': 'prefill_plus_generation_per_step',
        'per_prompt': results,
    }
    with open(RESULTS_JSON, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print('\n=== DONE. Results + surfaces saved. ===')
    print('Surfaces: %s/' % SURFACES_DIR)
    print('Results: %s' % RESULTS_JSON)

if __name__ == '__main__':
    main()
