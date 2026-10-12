"""Offline startup and no-download safeguards: python scripts/test_offline.py."""
import ast
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import ollama
import run_offline


def model_check():
    # Load only the model guard, without executing the Streamlit dashboard.
    node = next(node for node in ast.parse((ROOT / 'app.py').read_text(encoding='utf-8')).body
                if isinstance(node, ast.FunctionDef) and node.name == 'ensure_tracey_model')
    namespace = {'os': os, 'ollama': ollama, 't': lambda key: key}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 '<offline-model-check>', 'exec'), namespace)
    return namespace['ensure_tracey_model']


class OfflineTests(unittest.TestCase):
    def test_missing_model_never_downloads(self):
        client = MagicMock()
        client.show.side_effect = ollama.ResponseError('missing', status_code=404)
        with patch.dict(os.environ, {'TRACE_OFFLINE': '1'}), patch('subprocess.run') as process:
            with self.assertRaisesRegex(RuntimeError, 'tracey_offline_missing_model'):
                model_check()(client)
            process.assert_not_called()

    def test_installed_model_needs_no_process(self):
        with patch.dict(os.environ, {'TRACE_OFFLINE': '1'}), patch('subprocess.run') as process:
            model_check()(MagicMock())
            process.assert_not_called()

    def test_launcher_starts_only_local_ollama(self):
        client = MagicMock()
        client.list.side_effect = [ConnectionError('not running'), {}]
        with patch('ollama.Client', return_value=client), patch('run_offline.shutil.which', return_value='ollama'), patch('run_offline.subprocess.Popen') as process, patch('run_offline.time.sleep'):
            run_offline.check_ollama(start=True)
            self.assertEqual(process.call_args.args[0], ['ollama', 'serve'])
            self.assertEqual(process.call_args.kwargs['env']['OLLAMA_HOST'], 'http://127.0.0.1:11434')
            client.show.assert_called_once_with('llama3')


if __name__ == '__main__':
    unittest.main()
