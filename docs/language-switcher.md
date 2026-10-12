# TRACE language switcher

The header offers EN and TL on every tab, with English as the first-visit default.
The built-in Streamlit v2 component stores the choice in `localStorage` under
`trace.ui.language`. If browser storage is blocked, switching still works within
the current visit. Language changes use Streamlit's WebSocket rerun, without
reloading the browser document. Stable widget keys retain the filters, search,
project selection, and submitted prediction input. Tracked tab labels are mapped
to the new language before the tabs render.

Streamlit 1.65 or newer is required; this is the version already installed in
the project's `.runtime` environment. No additional library is needed.

## Translation review

[translations-review.md](translations-review.md) lists every dictionary string,
including identical English/Tagalog terms retained intentionally. The source
files are `locales/en.json` and `locales/tl.json`. Keep their keys and formatting
placeholders identical. `t()` falls back to English for missing Tagalog keys.
Development mode logs server and browser console warnings; set
`TRACE_ENV=production` to disable development warnings.

Dataframe column labels change through `column_config`, not dataframe renaming.
Chart axis labels, legend captions, and modebar tooltips change only for display.
Dataset values, status labels, numeric formatting, date formatting, calculations,
cleaning, chart series, and filtering rules retain their existing behavior.
Historical user messages and model replies retain their original text; Tracey's
UI welcome and system language instruction follow the selected language.

## Source audit

The search covered the root Python and HTML files and the live mascot component.
`app.py`, `tracey_component.py`, and the header component are the running app's
UI paths. `app.previous.py` and `app.budget-backup.py` are archived versions.
`Tracey, the T.R.A.C.E. helper.html` is the standalone reference chatbot and is
not imported or served by the Streamlit app. Those references were left intact.
Proper names, internal dataframe keys, status/data values, developer-only
validation errors, external error details, and archived research text were not
translated. Streamlit's application-management toolbar remains framework-owned.

## Checks

```powershell
.\.runtime\Scripts\python.exe scripts\check_translations.py
.\.runtime\Scripts\python.exe scripts\test_language.py
```

The first script checks dictionary keys, formatting placeholders, and literal
Python lookups, then regenerates the review table. The second checks fallback,
filters, selection, prediction input, metrics, dataframe values, chart values,
chat history, language policy, and all four tabs, using mocked Ollama replies.

`scripts/browser_language_test.mjs` uses Node's built-in WebSocket client and
Chrome DevTools Protocol, without a test library. Start a separate hidden
headless Edge/Chrome with a disposable profile and remote debugging on port
9223, run Streamlit on port 8502, then run:

```powershell
node scripts\browser_language_test.mjs
```

It checks switching without a browser reload, active tab, region/search
preservation, localStorage on revisit, the document language, mobile fit, and
JavaScript exceptions. It writes a mobile screenshot under `.cache`.
