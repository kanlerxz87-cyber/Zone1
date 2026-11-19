#!/usr/bin/env python3
"""Run a check, preserve its exit code and expose a bounded failure tail in Actions.

Some environments cannot fetch Actions' signed external log archive. An annotation
keeps the useful diagnostic available through GitHub's ordinary check-runs API.
No environment dump, credential output or raw report data is added by this wrapper.
"""
from collections import deque
import os
import subprocess
import sys


def run(command):
    tail = deque(maxlen=90)
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, encoding='utf-8', errors='replace', bufsize=1) as child:
        for line in child.stdout:
            print(line, end='', flush=True)
            tail.append(line)
        code = child.wait()
    if code and os.environ.get('GITHUB_ACTIONS') == 'true':
        detail = ''.join(tail)
        if len(detail) > 16000:
            detail = detail[:3000] + '\n[diagnostic middle omitted]\n' + detail[-12000:]
        detail = detail.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')
        print('::error title=Verification command failed::' + detail, flush=True)
    return code if code >= 0 else 128 - code


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise SystemExit('usage: annotated_check.py COMMAND [ARG ...]')
    raise SystemExit(run(sys.argv[1:]))
