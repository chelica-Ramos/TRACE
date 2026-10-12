"""Offline tests for unavailable Ollama and interrupted chat streams."""
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import httpx
import streamlit as st
from streamlit.testing.v1 import AppTest
from i18n import CATALOGS


class TraceyFallbackTests(unittest.TestCase):
    def setUp(self):
        st.cache_resource.clear()

    def assert_usable(self, app, lang):
        self.assertFalse(app.exception, [item.message for item in app.exception])
        self.assertFalse(app.error)
        self.assertEqual(len(app.tabs), 4)
        self.assertEqual(len(app.chat_input), 1)
        self.assertEqual(app.session_state['messages'][-2]['content'], 'Test question')
        self.assertIn(CATALOGS[lang]['tracey_fallback_notice'], app.session_state['messages'][-1]['content'])
        self.assertTrue(any(item.value == CATALOGS[lang]['tracey_fallback_notice'] for item in app.info))
        self.assertTrue(any('tracey-response-idle' in item.value for item in app.markdown))

    def test_connection_and_timeout_failures_in_both_languages(self):
        for lang, error in [('en', ConnectionError('refused')),
                            ('tl', httpx.ConnectError('refused')),
                            ('en', httpx.ConnectTimeout('timeout'))]:
            with self.subTest(lang=lang, error=type(error).__name__):
                st.cache_resource.clear()
                client = MagicMock()
                client.show.side_effect = error
                with patch('i18n._switcher', return_value=SimpleNamespace(language=lang)), patch('ollama.Client', return_value=client):
                    app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=60)
                    app.chat_input[0].set_value('Test question').run(timeout=60)
                self.assert_usable(app, lang)
                client.chat.assert_not_called()

    def test_partial_stream_is_preserved_and_next_request_recovers(self):
        def interrupted():
            yield {'message': {'content': 'Partial answer.'}}
            raise httpx.ReadError('connection lost')
        client = MagicMock()
        client.chat.return_value = interrupted()
        with patch('i18n._switcher', return_value=SimpleNamespace(language='en')), patch('ollama.Client', return_value=client):
            app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=60)
            app.chat_input[0].set_value('Test question').run(timeout=60)
            self.assert_usable(app, 'en')
            self.assertTrue(app.session_state['messages'][-1]['content'].startswith('Partial answer.'))
            count = len(app.session_state['messages'])
            client.chat.return_value = iter([{'message': {'content': 'Recovered reply.'}}])
            app.chat_input[0].set_value('Try again').run(timeout=60)
            self.assertFalse(app.exception)
            self.assertFalse(app.error)
            self.assertEqual(len(app.session_state['messages']), count + 2)
            self.assertEqual(app.session_state['messages'][-1]['content'], 'Recovered reply.')

    def test_missing_python_package_keeps_chat_available(self):
        with patch('i18n._switcher', return_value=SimpleNamespace(language='en')), patch.dict(sys.modules, {'ollama': None}):
            app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=60)
            self.assertEqual(len(app.chat_input), 1)
            app.chat_input[0].set_value('Test question').run(timeout=60)
            self.assert_usable(app, 'en')


if __name__ == '__main__':
    unittest.main()
