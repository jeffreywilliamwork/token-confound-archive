#!/usr/bin/env python3
"""Generate TSV from prompt suite with R1 chat template wrapping.

R1 requires: <｜User｜>{text}<｜Assistant｜><think>\n
Without this, the model treats input as raw text completion and produces garbage.
"""
import json

CHAT_PREFIX = '<｜User｜>'
CHAT_SUFFIX = '<｜Assistant｜><think>\n'

with open('/workspace/experiment-r1-28q-1/prompt-suite.json') as f:
    data = json.load(f)

lines = []
for cond in data['conditions']:
    for prompt in cond['prompts']:
        text = prompt['text'].replace('\n', ' ').replace('\t', ' ')
        wrapped = f"{CHAT_PREFIX}{text}{CHAT_SUFFIX}"
        lines.append(f"{prompt['id']}\t{wrapped}")

with open('/workspace/experiment-r1-28q-1/prompts_28.tsv', 'w') as f:
    f.write('\n'.join(lines) + '\n')

print(f'{len(lines)} prompts written to prompts_28.tsv (R1 chat template wrapped)')
