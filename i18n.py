"""Offline EN/TL translations and a persistent Streamlit header switcher."""
import json
import logging
import os
from pathlib import Path
from string import Formatter

import streamlit as st

ROOT = Path(__file__).resolve().parent
CATALOGS = {
    lang: json.loads((ROOT / 'locales' / f'{lang}.json').read_text(encoding='utf-8'))
    for lang in ('en', 'tl')
}
DEVELOPMENT = os.getenv('TRACE_ENV', 'development') != 'production'
MISSING = set()
TAB_KEYS = ('tab_overview', 'tab_explorer', 'tab_insights', 'tab_tracey')
COLUMN_KEYS = {
    'Contract ID': 'column_contract_id', 'Description': 'column_description',
    'Category': 'column_category', 'Contractor': 'column_contractor',
    'Region': 'region', 'Province': 'column_province', 'Budget': 'column_budget',
    'Year': 'year', 'Progress': 'column_progress', 'Status': 'status',
    'Start Date': 'column_start', 'Completion Date': 'column_completion',
    'Utilized Budget': 'column_utilized', 'Estimated Remaining Budget': 'column_remaining',
    'Projects': 'column_projects', 'Keyword': 'column_keyword',
    'Mean TF-IDF': 'column_tfidf', 'Measure': 'column_measure', 'PHP': 'budget_php',
}


def language():
    return st.session_state.get('language', 'en')


def t(key, **values):
    lang = language()
    catalog = CATALOGS.get(lang, CATALOGS['en'])
    if key not in catalog:
        MISSING.add(f'{lang}:{key}')
        if DEVELOPMENT:
            logging.getLogger(__name__).warning('Missing %s translation: %s; using English', lang, key)
    text = catalog.get(key, CATALOGS['en'][key])
    return text.format(**values) if values else text


def column_config():
    """Only displayed labels change; dataframe column names and values do not."""
    return {column: st.column_config.Column(t(key)) for column, key in COLUMN_KEYS.items()}


def chart_labels():
    return {column: t(key) for column, key in COLUMN_KEYS.items()}


def chart_config():
    """Translate Plotly tooltips while retaining its default number/date formats."""
    modebar = {
        'Download plot as a PNG': 'chart_download', 'Download plot as a png': 'chart_download',
        'Zoom': 'chart_zoom', 'Pan': 'chart_pan', 'Zoom in': 'chart_zoom_in',
        'Zoom out': 'chart_zoom_out', 'Autoscale': 'chart_autoscale', 'Reset axes': 'chart_reset',
        'Toggle spike lines': 'chart_spikes', 'Show closest data on hover': 'chart_closest',
        'Compare data on hover': 'chart_compare', 'Box Select': 'chart_box', 'Lasso Select': 'chart_lasso',
    }
    if language() == 'en':
        return {}
    return {'locale': 'tl', 'locales': {'tl': {'dictionary': {label: t(key) for label, key in modebar.items()}}}}


def check_catalogs():
    assert CATALOGS['en'].keys() == CATALOGS['tl'].keys(), 'EN/TL dictionary keys differ'
    for key in CATALOGS['en']:
        fields = lambda text: {name for _, name, _, _ in Formatter().parse(text) if name is not None}
        # Plotly hover templates use their own syntax and are checked as literals.
        if key != 'pie_hover':
            assert fields(CATALOGS['en'][key]) == fields(CATALOGS['tl'][key]), key


LANGUAGE_POLICY = (
    "Reply in the user's selected language. If it is Tagalog, use natural, "
    "friendly Filipino (light Taglish is fine) and keep technical terms in "
    "English when that is how Filipinos usually say them. If the user writes "
    "in the other language, reply in the language they wrote in."
)


_switcher = st.components.v2.component(
    'trace_language_switch',
    html='<div class="trace-language-switch" role="group"><button type="button" data-language="en">EN</button><span aria-hidden="true"> | </span><button type="button" data-language="tl">TL</button></div>',
    css='''
    .trace-language-switch {display:flex; align-items:center; justify-content:flex-end; gap:4px; font:600 14px system-ui; color:var(--st-text-color)}
    .trace-language-switch button {min-width:44px; min-height:36px; cursor:pointer; background:transparent; color:inherit; border:1px solid transparent; border-radius:8px; font:inherit}
    .trace-language-switch button[aria-pressed="true"] {border-color:#14b8a6; background:rgba(20,184,166,.14)}
    .trace-language-switch button:focus-visible {outline:2px solid #14b8a6; outline-offset:2px}
    ''',
    js=(ROOT / 'assets' / 'language_switcher.js').read_text(encoding='utf-8'),
)


def language_switcher():
    st.session_state.setdefault('language', 'en')
    result = _switcher(
        key='trace_language_control',
        data={'language': language(), 'catalogs': CATALOGS, 'development': DEVELOPMENT,
              'missing': sorted(MISSING)},
        default={'language': language()},
        on_language_change=lambda: None,
    )
    selected = result.language
    if selected in ('en', 'tl') and selected != language():
        # Translate the tracked tab label before creating the tabs again.
        active = st.session_state.get('trace_tabs')
        for key in TAB_KEYS:
            if active in (CATALOGS['en'][key], CATALOGS['tl'][key]):
                st.session_state['trace_tabs'] = CATALOGS[selected].get(key, CATALOGS['en'][key])
                break
        st.session_state.language = selected
        st.rerun()  # Streamlit updates the existing document over its WebSocket.
