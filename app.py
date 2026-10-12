"""TRACE executive dashboard. Run: streamlit run app.py"""
from pathlib import Path
import html
import os
import shutil
import subprocess
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from i18n import t, language, language_switcher, column_config, chart_labels, chart_config, LANGUAGE_POLICY
from tracey_component import Tracey, avatar as tracey_avatar, install_tab_avatar
try:
    import ollama
except ImportError:
    ollama = None
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

st.set_page_config(page_title=t("page_title"), page_icon="🇵🇭", layout="wide")
ROOT = Path(__file__).resolve().parent
COLORS = {"Completed": "#14b8a6", "On-Going": "#f59e0b", "Terminated": "#f43f5e"}
st.markdown("""
<style>
.stApp {background:var(--background-color);}
.block-container {max-width:1600px;padding-top:2rem;padding-bottom:3rem;}
[data-testid="stMetric"] {background:var(--secondary-background-color);border:1px solid rgba(128,145,165,.22);border-radius:18px;padding:22px 20px;box-shadow:0 6px 24px rgba(15,23,42,.06);min-height:125px;}
[data-testid="stMetricLabel"] {font-size:.82rem;letter-spacing:.035em;}
[data-testid="stMetricValue"] {font-size:clamp(1.35rem,2vw,2.1rem);font-weight:700;}
[data-testid="stSidebar"] {border-right:1px solid rgba(128,145,165,.18);}
.stTabs [data-baseweb="tab-list"] {gap:24px;border-bottom:1px solid rgba(128,145,165,.2);}
.stTabs [data-baseweb="tab"] {padding:12px 4px;font-weight:600;}
.stTabs [aria-selected="true"] {color:#14b8a6;}
.trace-hero {background:linear-gradient(120deg,#0f172a,#12324a);border-radius:22px;padding:30px 34px;margin-bottom:24px;color:#f8fafc;}
.trace-hero h1 {color:#f8fafc;font-size:2.8rem;margin:0;padding:0;letter-spacing:.06em;}
.trace-hero p {color:#cbd5e1;margin:8px 0 0;}
.trace-eyebrow {color:#5eead4;font-size:.73rem;font-weight:700;letter-spacing:.18em;margin-bottom:10px;}
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_data(path, modified_time):
    # Modification time keeps the cache synchronized with file changes.
    df = pd.read_csv(path, encoding="utf-8-sig", dtype={"Contract ID": "string"})
    df.columns = df.columns.str.strip()
    required = {"Contract ID", "Description", "Category", "Contractor", "Region", "Province", "Budget", "Year", "Progress", "Status", "Start Date", "Completion Date"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(t("missing_columns", columns=", ".join(sorted(missing))))
    df = df.drop(columns="Amount Paid", errors="ignore")
    for col in ["Budget", "Progress", "Year"]:
        values = df[col].astype("string").str.replace(r"[₱,%\s]|(?i:PHP)", "", regex=True)
        df[col] = pd.to_numeric(values, errors="coerce").replace([np.inf, -np.inf], np.nan)
    df.loc[df["Budget"].lt(0), "Budget"] = np.nan
    df.loc[~df["Progress"].between(0, 100), "Progress"] = np.nan
    df["Year"] = df["Year"].where(df["Year"].between(1900, 2100) & df["Year"].mod(1).eq(0)).astype("Int64")
    for col in ["Contract ID", "Description", "Category", "Contractor", "Region", "Province", "Status"]:
        df[col] = df[col].fillna("").astype(str).str.strip()
    for col in ["Category", "Contractor", "Region", "Province", "Status"]:
        df[col] = df[col].replace("", "Unknown")
    keys = df["Status"].str.lower().str.replace(r"[\s_-]+", "", regex=True)
    df["Status"] = keys.map({"completed": "Completed", "complete": "Completed", "ongoing": "On-Going", "inprogress": "On-Going", "terminated": "Terminated"}).fillna(df["Status"])
    for col in ["Start Date", "Completion Date"]:
        df[col] = pd.to_datetime(df[col], format="mixed", errors="coerce")
    df["Utilized Budget"] = df["Budget"] * (df["Progress"] / 100)
    df["Estimated Remaining Budget"] = df["Budget"] - df["Utilized Budget"]
    return df


@st.cache_resource(show_spinner=False)
def train_model(data):
    # Use PHP millions for numerical stability; Budget is the only feature.
    x = data[["Budget"]] / 1e6
    y = data["Progress"]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.2, random_state=42)
    model = LinearRegression().fit(x_train, y_train)
    mse = mean_squared_error(y_test, model.predict(x_test))
    model.fit(x, y)
    return model, float(mse)


def money(value, compact=False):
    if pd.isna(value):
        return t("unavailable")
    if compact:
        for size, suffix in [(1e12, "T"), (1e9, "B"), (1e6, "M")]:
            if abs(value) >= size:
                return f"₱{value / size:,.2f}{suffix}"
    return f"₱{value:,.2f}"


def chart(fig):
    fig.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Arial", color="#64748b"), margin=dict(l=10, r=10, t=30, b=10), legend_title_text="")
    st.plotly_chart(fig, width="stretch", config=chart_config())


TRACEY_PERSONA = (
    'You are Tracey, the official offline AI Assistant for the TRACE '
    '(Taxpayer Resource Allocation & Expenditure Oversight) project. '
    'You help explain government budget data, fund utilization, '
    'linear regression, and NLP insights.'
)

@st.cache_resource
def get_tracey_client():
    return ollama.Client(host='http://127.0.0.1:11434', trust_env=False, timeout=300.0)


def ensure_tracey_model(client):
    try:
        client.show('llama3')
        return
    except ollama.ResponseError as error:
        if error.status_code != 404:
            raise
    if os.environ.get('TRACE_OFFLINE') == '1':
        raise RuntimeError(t('tracey_offline_missing_model'))
    executable = shutil.which('ollama')
    if executable is None:
        raise RuntimeError(t("tracey_missing_path"))
    pull_environment = os.environ.copy()
    pull_environment['OLLAMA_HOST'] = 'http://127.0.0.1:11434'
    with st.spinner(t("tracey_downloading")):
        result = subprocess.run(
            [executable, 'pull', 'llama3'], env=pull_environment,
            capture_output=True, text=True, encoding='utf-8', errors='replace',
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
        )
        if result.returncode != 0:
            details = (result.stderr or result.stdout).strip()
            raise RuntimeError(t('tracey_download_error') + '\n' + details[-2000:])
        client.show('llama3')


def render_tracey_tab():
    if ollama is None:
        st.subheader(t("tracey_title"))
        st.error(t("tracey_missing_package"))
        return
    st.subheader(t("tracey_title"))
    st.caption(t("tracey_local"))
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    st.session_state.messages = [
        {'role': 'system', 'content': TRACEY_PERSONA + '\n' + LANGUAGE_POLICY + '\nCurrent selected language: ' + ('Tagalog (TL).' if language() == 'tl' else 'English (EN).')},
        *[message for message in st.session_state.messages if message['role'] != 'system'],
    ]
    if len(st.session_state.messages) > 1 and st.session_state.messages[1]['role'] == 'assistant':
        st.session_state.messages[1]['content'] = t('tracey_greeting')
    if len(st.session_state.messages) == 1:
        st.session_state.messages.append({'role': 'assistant', 'content': t('tracey_greeting')})
    if not any(message['role'] == 'user' for message in st.session_state.messages):
        Tracey(size='lg', line=t('tracey_greeting'))
    suggested_prompt = None
    if not any(message['role'] == 'user' for message in st.session_state.messages):
        with st.container(horizontal=True):
            for chip in ('chip_project', 'chip_data', 'chip_flags', 'chip_limits', 'chip_tfidf'):
                if st.button(t(chip), key=chip):
                    suggested_prompt = t(chip)
    for message in st.session_state.messages:
        if message['role'] in ('user', 'assistant'):
            with st.chat_message(message['role'], avatar=tracey_avatar() if message['role'] == 'assistant' else None):
                st.write(message['content'])
    entered_prompt = st.chat_input(t("tracey_placeholder"), key='tracey_chat_input')
    if prompt := entered_prompt or suggested_prompt:
        st.session_state.messages.append({'role': 'user', 'content': prompt})
        with st.chat_message('user'):
            st.write(prompt)
        with st.chat_message('assistant', avatar=tracey_avatar()):
            mascot_state = st.empty()
            mascot_state.markdown('<span class="tracey-response-thinking" aria-hidden="true">...</span>', unsafe_allow_html=True)
            try:
                client = get_tracey_client()
                ensure_tracey_model(client)
                with st.spinner(t("tracey_thinking")):
                    response = iter(client.chat(model='llama3', messages=st.session_state.messages, stream=True))
                    first_chunk = next(response, None)
                mascot_state.markdown('<span class="tracey-response-talking" aria-hidden="true"></span>', unsafe_allow_html=True)
                def reply_chunks():
                    if first_chunk is not None:
                        yield first_chunk['message']['content']
                    for chunk in response:
                        yield chunk['message']['content']
                answer = st.write_stream(reply_chunks())
                if not answer or not answer.strip():
                    raise RuntimeError(t("tracey_empty_response"))
                st.session_state.messages.append({'role': 'assistant', 'content': answer})
            except ConnectionError:
                st.error(t("tracey_connection_error"))
                st.session_state.messages.pop()
            except ollama.ResponseError as error:
                st.error(t('tracey_ollama_error', error=error.error))
                st.session_state.messages.pop()
            except Exception as error:
                st.error(t('tracey_request_error', error=error))
                st.session_state.messages.pop()
            finally:
                mascot_state.markdown('<span class="tracey-response-idle" aria-hidden="true"></span>', unsafe_allow_html=True)


def main():
    language_switcher()
    path = ROOT / "dpwh-projects-2026-10-06.csv"
    loading_mascot = st.empty()
    try:
        with loading_mascot.container():
            Tracey(size='md', state='thinking', line=t("tracey_loading"))
        with st.spinner(t('preparing')):
            source = load_data(str(path), path.stat().st_mtime_ns)
    except (OSError, ValueError, UnicodeError) as error:
        st.error(t('dataset_error', error=error))
        st.stop()
    finally:
        loading_mascot.empty()
    st.sidebar.title("TRACE")
    st.sidebar.caption(t("sidebar_caption"))
    st.sidebar.divider()
    regions = st.sidebar.multiselect(t('region'), sorted(source["Region"].unique()), key='region_filter', placeholder=t('choose_options'))
    years = st.sidebar.multiselect(t('year'), sorted(source["Year"].dropna().astype(int).unique().tolist()), key='year_filter', placeholder=t('choose_options'))
    st.sidebar.caption(t("filter_note"))
    df = source.copy()
    if regions:
        df = df.loc[df["Region"].isin(regions)]
    if years:
        df = df.loc[df["Year"].isin(years)]
    st.sidebar.metric(t("scope_projects"), f"{len(df):,}")
    st.markdown(f'<div class="trace-hero"><div class="trace-eyebrow">{html.escape(t("hero_eyebrow"))}</div><h1>TRACE</h1><p>{html.escape(t("project_full_name"))}</p><p>{html.escape(t("hero_tagline"))}</p></div>', unsafe_allow_html=True)
    st.caption(t("methodology"))
    if df.empty:
        Tracey(size='md', line=t("tracey_find_projects"))
        st.info(t("no_filter_matches"))
        st.stop()
    install_tab_avatar()
    overview, explorer, insights, tracey = st.tabs([t("tab_overview"), t("tab_explorer"), t("tab_insights"), t("tab_tracey")], key='trace_tabs', on_change='rerun')
    with overview:
        a, b, c, d = st.columns(4)
        a.metric(t("total_projects"), f"{len(df):,}")
        a.caption(t("scope_records"))
        allocated = df["Budget"].sum(min_count=1)
        utilized = df["Utilized Budget"].sum(min_count=1)
        b.metric(t("total_allocated"), money(allocated, True))
        b.caption(money(allocated))
        c.metric(t("total_utilized"), money(utilized, True))
        c.caption(t("estimated_prefix") + money(utilized))
        avg = df["Progress"].mean()
        d.metric(t("average_progress"), t('unavailable') if pd.isna(avg) else f"{avg:.1f}%")
        d.caption(t("unweighted_average"))
        st.write("")
        left, right = st.columns([1, 1.6])
        with left:
            st.subheader(t("portfolio_status"))
            counts = df["Status"].value_counts().rename_axis("Status").reset_index(name="Projects")
            fig = px.pie(counts, names="Status", values="Projects", hole=.68, color="Status", color_discrete_map=COLORS, labels=chart_labels())
            fig.update_traces(textinfo="percent", hovertemplate=t("pie_hover"))
            fig.update_layout(height=440, legend=dict(orientation="h", y=-.1))
            chart(fig)
        with right:
            st.subheader(t("regional_comparison"))
            totals = df.dropna(subset=["Budget", "Utilized Budget"]).groupby("Region")[["Budget", "Utilized Budget"]].sum().sort_values("Budget").reset_index()
            if totals.empty:
                Tracey(size='md', line=t("tracey_budget_empty"))
                st.info(t("no_budget_pairs"))
            else:
                melted = totals.melt(id_vars="Region", var_name="Measure", value_name="PHP")
                melted["Measure"] = melted["Measure"].replace({"Budget": "Allocated", "Utilized Budget": "Estimated utilized"})
                fig = px.bar(melted, x="PHP", y="Region", color="Measure", orientation="h", barmode="group", color_discrete_map={"Allocated": "#3b82f6", "Estimated utilized": "#14b8a6"}, labels=chart_labels())
                for trace in fig.data:
                    trace.name = t('allocated') if trace.name == 'Allocated' else t('estimated_utilized')
                fig.update_traces(hovertemplate="%{y}<br>₱%{x:,.2f}<extra>%{fullData.name}</extra>")
                fig.update_layout(height=max(440, len(totals) * 36), legend=dict(orientation="h", y=1.12))
                chart(fig)
        st.subheader(t("funding_gaps"))
        st.caption(t("ongoing_note"))
        st.dataframe(df.loc[df["Status"].eq("On-Going")].sort_values("Estimated Remaining Budget", ascending=False).head(10)[["Contract ID", "Region", "Description", "Budget", "Utilized Budget", "Estimated Remaining Budget", "Progress"]], width="stretch", hide_index=True, column_config=column_config())
    with explorer:
        st.subheader(t("explore_title"))
        query = st.text_input(t("search_label"), placeholder=t("search_placeholder"), key='project_search')
        matches = df
        if query.strip():
            matches = df.loc[df["Contract ID"].str.contains(query.strip(), case=False, regex=False) | df["Description"].str.contains(query.strip(), case=False, regex=False)]
        matches = matches.reset_index(drop=True)
        st.caption(t('matching_records', count=len(matches)))
        st.dataframe(matches, width="stretch", hide_index=True, column_config=column_config())
        if matches.empty:
            Tracey(size='md', line=t("tracey_search_empty"))
            st.info(t("no_search_matches"))
        else:
            selected = st.selectbox(t("select_project"), range(len(matches)), index=None, placeholder=t("choose_project"), key='project_selection', format_func=lambda i: f"{matches.iloc[i]['Contract ID']} · {matches.iloc[i]['Description'][:85]} · {t('record_number', number=i + 1)}")
            if selected is None and query.strip() and len(matches) == 1:
                selected = 0
            if selected is not None:
                row = matches.iloc[selected]
                with st.container(border=True):
                    st.subheader(t('contract_title', contract=row['Contract ID']))
                    st.write(row["Description"])
                    # Escape dataset text before embedding in HTML.
                    st.markdown(f"<strong>{html.escape(t('contractor_label'))}</strong> {html.escape(row['Contractor'])}", unsafe_allow_html=True)
                    st.write(f"**{t('location_label')}**", row["Region"], " / ", row["Province"])
                    a, b, c = st.columns(3)
                    a.metric(t('allocated'), money(row["Budget"], True))
                    a.caption(money(row["Budget"]))
                    b.metric(t('estimated_utilized'), money(row["Utilized Budget"], True))
                    c.metric(t('status'), row["Status"])
                    def date(value):
                        return t("not_recorded") if pd.isna(value) else value.strftime("%d %b %Y")
                    st.write(f"**{t('start_date_label')}**", date(row["Start Date"]), f" · **{t('completion_date_label')}**", date(row["Completion Date"]))
                    if pd.notna(row["Progress"]):
                        st.write(f"**{t('physical_progress', progress=row['Progress'])}**")
                        st.progress(float(row["Progress"]) / 100)
                    else:
                        st.info(t("invalid_progress"))
    with insights:
        left, right = st.columns([1.2, 1])
        with left:
            st.subheader(t("themes_title"))
            st.caption(t("tfidf_note"))
            descriptions = df.loc[df["Status"].eq("On-Going"), "Description"]
            descriptions = descriptions.loc[descriptions.str.strip().ne("")]
            if descriptions.empty:
                Tracey(size='md', line=t("tracey_descriptions_empty"))
                st.info(t("no_ongoing_descriptions"))
            else:
                try:
                    vectorizer = TfidfVectorizer(stop_words="english", max_features=10000)
                    matrix = vectorizer.fit_transform(descriptions)
                    scores = np.asarray(matrix.mean(axis=0)).ravel()
                    top = np.argsort(-scores, kind="stable")[:15]
                    terms = pd.DataFrame({"Keyword": vectorizer.get_feature_names_out()[top], "Mean TF-IDF": scores[top]}).sort_values("Mean TF-IDF")
                    fig = px.bar(terms, x="Mean TF-IDF", y="Keyword", orientation="h", color_discrete_sequence=["#14b8a6"], labels=chart_labels())
                    fig.update_layout(height=520)
                    chart(fig)
                    st.caption(t('tfidf_count', count=len(descriptions)))
                except ValueError:
                    st.info(t("no_terms"))
        with right:
            st.subheader(t("prediction_title"))
            st.caption(t("prediction_note"))
            data = df[["Budget", "Progress"]].dropna()
            if len(data) < 5:
                st.info(t("prediction_minimum"))
            else:
                with st.spinner(t('training')):
                    model, mse = train_model(data)
                with st.form("prediction"):
                    budget = st.number_input(t("hypothetical_budget"), min_value=0.0, value=float(data["Budget"].median()), step=100000.0, key='hypothetical_budget_input')
                    submitted = st.form_submit_button(t("estimate_progress"), type="primary", width="stretch")
                if submitted:
                    raw = float(model.predict(pd.DataFrame({"Budget": [budget / 1e6]}))[0])
                    predicted = float(np.clip(raw, 0, 100))
                    st.metric(t("predicted_progress"), f"{predicted:.1f}%")
                    gauge = go.Figure(go.Indicator(mode="gauge+number", value=predicted, number={"suffix": "%", "font": {"size": 40}}, gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#14b8a6"}, "steps": [{"range": [0, 40], "color": "#ffe4e6"}, {"range": [40, 75], "color": "#fef3c7"}, {"range": [75, 100], "color": "#ccfbf1"}]}))
                    gauge.update_layout(height=260)
                    chart(gauge)
                    st.progress(predicted / 100)
                    if raw != predicted:
                        st.caption(t('raw_prediction', raw=raw))
                    if not data["Budget"].min() <= budget <= data["Budget"].max():
                        st.info(t("outside_range"))
                st.caption(t('mse_note', mse=mse, count=len(data)))
    with tracey:
        render_tracey_tab()

    st.divider()
    st.caption(t("footer"))


if __name__ == "__main__":
    main()

