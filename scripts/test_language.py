"""Offline language regression checks. Run with the project's Python environment.

    .runtime/Scripts/python.exe scripts/test_language.py
"""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
from streamlit.testing.v1 import AppTest
import i18n
from check_translations import check


class LanguageTests(unittest.TestCase):
    def test_catalogs_and_fallback(self):
        check()
        with patch('i18n.language', return_value='tl'):
            text = i18n.CATALOGS['tl'].pop('methodology')
            try:
                with self.assertLogs('i18n', level='WARNING'):
                    self.assertEqual(i18n.t('methodology'), i18n.CATALOGS['en']['methodology'])
            finally:
                i18n.CATALOGS['tl']['methodology'] = text
                i18n.MISSING.discard('tl:methodology')

    def test_language_preserves_widgets_data_and_history(self):
        chosen = ['en']
        client = MagicMock()
        with patch('i18n._switcher', side_effect=lambda **kwargs: SimpleNamespace(language=chosen[0])), patch('ollama.Client', return_value=client):
            app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=60)
            self.assertFalse(app.exception)
            region = app.dataframe[1].value['Region'].value_counts().idxmax()
            app.multiselect(key='region_filter').set_value([region]).run(timeout=60)
            # Choose a year that actually exists in the selected region.
            year = int(app.dataframe[1].value['Year'].value_counts().idxmax())
            app.multiselect(key='year_filter').set_value([year]).run(timeout=60)
            app.selectbox(key='project_selection').set_value(0)
            app.number_input(key='hypothetical_budget_input').set_value(7654321.0)
            next(button for button in app.button if button.label == 'Estimate progress').click().run(timeout=60)
            client.chat.return_value = iter([{'message': {'content': 'English reply.'}}])
            app.chat_input[0].set_value('Explain utilization').run(timeout=60)
            self.assertFalse(app.exception)
            app.session_state['trace_tabs'] = 'Project Explorer'
            frames = [frame.value.copy() for frame in app.dataframe]
            metrics = [metric.value for metric in app.metric]
            charts = [json.loads(chart.proto.spec)['data'] for chart in app.get('plotly_chart')]
            history = copy.deepcopy(app.session_state['messages'][2:])
            years = app.multiselect(key='year_filter').value[:]
            chosen[0] = 'tl'
            app.run(timeout=60)
            self.assertFalse(app.exception, [error.message for error in app.exception])
            self.assertEqual(app.session_state['trace_tabs'], 'Hanap ng Project')
            self.assertEqual(app.multiselect(key='region_filter').value, [region])
            self.assertEqual(app.multiselect(key='year_filter').value, years)
            self.assertEqual(app.selectbox(key='project_selection').value, 0)
            self.assertEqual(app.number_input(key='hypothetical_budget_input').value, 7654321.0)
            self.assertEqual(app.session_state['messages'][2:], history)
            self.assertEqual([metric.value for metric in app.metric], metrics)
            for expected, actual in zip(frames, app.dataframe):
                pd.testing.assert_frame_equal(expected, actual.value)
            current_charts = [json.loads(chart.proto.spec)['data'] for chart in app.get('plotly_chart')]
            for before, after in zip(charts, current_charts):
                for old_trace, new_trace in zip(before, after):
                    for field in ('x', 'y', 'values', 'labels', 'marker'):
                        self.assertEqual(old_trace.get(field), new_trace.get(field), field)
            self.assertIn('Current selected language: Tagalog (TL).', app.session_state['messages'][0]['content'])
            self.assertIn(i18n.LANGUAGE_POLICY, app.session_state['messages'][0]['content'])
            client.chat.return_value = iter([{'message': {'content': 'Sagot sa Filipino.'}}])
            app.chat_input[0].set_value('Ipaliwanag ang utilization').run(timeout=60)
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state['messages'][-1]['content'], 'Sagot sa Filipino.')
            self.assertIn('Tagalog (TL)', client.chat.call_args.kwargs['messages'][0]['content'])
            self.assertTrue(any('Walang available na data ng aktuwal na bayad.' in caption.value for caption in app.caption))
            self.assertEqual(len(app.tabs), 4)


if __name__ == '__main__':
    unittest.main()
