"""Reusable Streamlit Tracey(size='sm'|'md'|'lg', state=...) component.

The source SVG is shared by interactive mascots, native chat avatars and the tab.
Only CSS moves the original artwork; JavaScript handles click/keyboard happiness.
"""
from base64 import b64encode
from html import escape
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from i18n import t, language

ASSETS = Path(__file__).resolve().parent / 'assets'
SVG = (ASSETS / 'tracey.svg').read_text(encoding='utf-8')
CSS = (ASSETS / 'tracey.css').read_text(encoding='utf-8')
SIZES = {'sm': 32, 'md': 96, 'lg': 200}
STATES = {'idle', 'thinking', 'talking', 'happy'}


def avatar(state='idle'):
    """Self-contained animated SVG URL for Streamlit's native chat avatar."""
    if state not in STATES:
        raise ValueError('Invalid Tracey state')
    svg = SVG.replace('class="tracey"', f'class="tracey tracey-{state}"', 1)
    svg = svg.replace('Tracey the tarsier construction worker', escape(t('tracey_accessible'), quote=True))
    # For an image, the state class lives on the SVG rather than its wrapper.
    style = CSS.replace('.tracey-happy .tracey', '.tracey.tracey-happy')
    svg = svg.replace('>', f'><style>{style}</style>', 1)
    return 'data:image/svg+xml;base64,' + b64encode(svg.encode()).decode()


def install_tab_avatar():
    """Streamlit tab labels accept text; add a decorative icon via scoped CSS."""
    st.markdown(f'''<style>
    .stTabs [role="tab"]:nth-child(4)::before {{
      content:""; flex-shrink:0; width:32px; height:32px;
      background:url("{avatar()}") center/contain no-repeat;
    }}
    @media(max-width:600px) {{.stTabs [data-baseweb="tab-list"] {{gap:12px}}}}
    </style>''', unsafe_allow_html=True)
    for state in ('idle', 'thinking', 'talking'):
        st.markdown(f'''<style>
        [data-testid="stChatMessage"]:has(.tracey-response-{state})
        [data-testid="stChatMessageAvatarCustom"] {{content:url("{avatar(state)}")}}
        </style>''', unsafe_allow_html=True)


def Tracey(size='md', state='idle', *, line='', decorative=False):
    """Render an accessible mascot. Larger copies support hover and click."""
    if size not in SIZES or state not in STATES:
        raise ValueError('Invalid Tracey size or state')
    pixels = SIZES[size]
    svg = SVG
    svg = svg.replace('Tracey the tarsier construction worker', escape(t('tracey_accessible'), quote=True))
    # Group the existing head shapes without changing their geometry or colors.
    svg = svg.replace('<ellipse cx="100" cy="92"', '<g class="tracey-head"><ellipse cx="100" cy="92"', 1)
    svg = svg.replace('<g class="arm">', '</g><g class="arm">', 1)
    if decorative:
        svg = svg.replace('role="img"', 'aria-hidden="true"')
    interactive = size != 'sm' and not decorative
    tag = 'button' if interactive else 'div'
    label = f' aria-label="{escape(t("tracey_happy_label"), quote=True)}" type="button"' if interactive else ''
    control = ' tracey-interactive' if interactive else ''
    document = f'''<!doctype html><html lang="{language()}"><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <style>html,body{{margin:0;background:transparent;color:#12304a}}
    @media(prefers-color-scheme:dark){{body{{color:#e6f3f1}}}}
    {CSS}</style></head><body>
    <{tag} class="tracey-stage tracey-{state}{control}"{label} style="width:{pixels}px">
    {svg}<span class="tracey-bubble" aria-hidden="true">...</span></{tag}>
    <p class="tracey-line">{escape(line)}</p>
    <script>
    // Match the actual Streamlit theme, including a user-selected dark theme.
    try {{document.body.style.color = getComputedStyle(window.parent.document.querySelector('.stApp')).color;}} catch (e) {{}}
    const stage = document.querySelector('.tracey-stage');
    let timer;
    function happy() {{
      clearTimeout(timer);
      stage.classList.remove('tracey-idle','tracey-thinking','tracey-talking','tracey-happy');
      void stage.offsetWidth;
      stage.classList.add('tracey-happy');
      timer = setTimeout(() => {{stage.classList.remove('tracey-happy');
        stage.classList.add('tracey-idle');}}, 700);
    }}
    if (stage.tagName === 'BUTTON') stage.addEventListener('click', happy);
    if ('{state}' === 'happy') happy();
    </script></body></html>'''
    height = int(pixels * 1.05) + (65 if line else 30)
    if hasattr(st, 'iframe'):
        st.iframe(document, height=height, alt=t('tracey_mascot'), tab_index=0 if interactive else -1)
    else:
        # Compatibility with the project's older supported Streamlit versions.
        components.html(document, height=height, scrolling=False)
