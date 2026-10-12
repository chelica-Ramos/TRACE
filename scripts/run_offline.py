"""Start the installed TRACE app entirely on localhost, without downloads.

Run: python scripts/run_offline.py [--check] [--port 8503]
"""
import argparse
import importlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
HOST = 'http://127.0.0.1:11434'


def runtime_check():
    for module in ('streamlit', 'pandas', 'numpy', 'sklearn', 'plotly', 'ollama'):
        try:
            importlib.import_module(module)
        except ImportError as error:
            raise RuntimeError(
                f'Missing Python dependency: {module}. While online, install '
                f'requirements.txt using this Python: {sys.executable}'
            ) from error
    import streamlit
    if not hasattr(streamlit.components, 'v2') or not hasattr(streamlit, 'iframe'):
        raise RuntimeError('This environment needs Streamlit >=1.65. Install requirements.txt while online.')
    for name in ('app.py', 'i18n.py', 'tracey_component.py', 'assets/tracey.svg',
                 'assets/tracey.css', 'assets/language_switcher.js', 'locales/en.json',
                 'locales/tl.json', 'dpwh-projects-2026-10-06.csv'):
        if not (ROOT / name).is_file():
            raise RuntimeError(f'Missing local app file: {name}')


def check_ollama(start=False):
    import ollama
    import httpx
    client = ollama.Client(host=HOST, trust_env=False, timeout=5.0)
    try:
        client.list()
    except (ConnectionError, httpx.ConnectError, httpx.TimeoutException) as error:
        executable = shutil.which('ollama')
        if not start or executable is None:
            raise RuntimeError('Ollama is not running. Open the Ollama app, then try again.') from error
        cache = ROOT / '.cache'
        cache.mkdir(exist_ok=True)
        environment = os.environ.copy()
        environment['OLLAMA_HOST'] = HOST
        with (cache / 'ollama-offline.log').open('ab') as log:
            subprocess.Popen(
                [executable, 'serve'], env=environment, stdin=subprocess.DEVNULL,
                stdout=log, stderr=log,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
            )
        for attempt in range(60):
            time.sleep(.25)
            try:
                client.list()
                break
            except (ConnectionError, httpx.ConnectError, httpx.TimeoutException):
                continue
        else:
            raise RuntimeError('Ollama did not start. See .cache/ollama-offline.log.')
    try:
        client.show('llama3')
    except ollama.ResponseError as error:
        if error.status_code != 404:
            raise
        raise RuntimeError(
            'llama3 is not downloaded. While online, run `ollama pull llama3` '
            'once. The offline launcher never downloads models.'
        ) from error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check local dependencies and model, then exit.')
    parser.add_argument('--port', type=int, default=8503)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('Port must be between 1 and 65535.')
    runtime_check()
    check_ollama(start=not args.check)
    print('Offline ready: local app files, Python packages, Ollama, and llama3.', flush=True)
    if args.check:
        return 0
    environment = os.environ.copy()
    environment['TRACE_OFFLINE'] = '1'
    environment['OLLAMA_HOST'] = HOST
    environment['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    print(f'Open http://localhost:{args.port}. Keep this window open; Ctrl+C stops TRACE.', flush=True)
    try:
        return subprocess.call(
            [sys.executable, '-m', 'streamlit', 'run', str(ROOT / 'app.py'),
             '--server.address', '127.0.0.1', '--server.port', str(args.port),
             '--server.headless', 'true', '--browser.gatherUsageStats', 'false'],
            cwd=ROOT, env=environment,
        )
    except KeyboardInterrupt:
        return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print(f'Offline startup failed: {error}', file=sys.stderr)
        sys.exit(1)
