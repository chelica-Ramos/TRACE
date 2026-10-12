"""T.R.A.C.E. Run with: python -m streamlit run app.py"""
from pathlib import Path
import os
import re
import math

# Keep plotting caches in the writable project directory.
os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".cache" / "matplotlib"))

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_squared_error, accuracy_score

st.set_page_config(page_title="T.R.A.C.E.", page_icon="🇵🇭", layout="wide")
sns.set_theme(style="whitegrid")
ROOT = Path(__file__).resolve().parent


@st.cache_data
def load_data(path, modified_time):
    """File modification time invalidates cached data after CSV edits."""
    df = pd.read_csv(path, dtype={"Contract ID": "string"})
    df.columns = df.columns.str.strip()
    required = {"Contract ID", "Description", "Category", "Contractor", "Region",
                "Province", "Budget", "Year", "Progress", "Status", "Start Date", "Completion Date"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
    df = df.drop(columns="Amount Paid", errors="ignore")
    for col in ["Budget", "Year", "Progress"]:
        values = df[col].astype("string").str.replace(r"[₱,%\s]|(?i:PHP)", "", regex=True)
        df[col] = pd.to_numeric(values, errors="coerce").replace([np.inf, -np.inf], np.nan)
    for col in ["Description", "Category", "Contractor", "Province", "Region", "Status"]:
        df[col] = df[col].fillna("").astype(str).str.strip()
    df["Region"] = df["Region"].replace("", "Unknown")
    keys = df["Status"].str.lower().str.replace(r"[\s_-]+", "", regex=True)
    df["Status"] = keys.map({"completed": "Completed", "complete": "Completed",
                             "ongoing": "On-Going", "inprogress": "On-Going"}).fillna(df["Status"])
    df["Status"] = df["Status"].replace("", "Unknown")
    df["Start Date"] = pd.to_datetime(df["Start Date"], format="mixed", errors="coerce")
    raw = df["Completion Date"].astype("string").str.strip()
    absent = raw.isna() | raw.str.lower().isin(["", "on-going", "ongoing", "nat", "none", "n/a"])
    parsed = pd.to_datetime(raw.mask(absent), format="mixed", errors="coerce")
    # Preserve datetime values separately: a date column cannot hold On-Going.
    df["Completion Date Parsed"] = parsed
    df["Completion Date"] = parsed.dt.strftime("%Y-%m-%d").fillna("Invalid Date")
    df.loc[absent, "Completion Date"] = "On-Going"
    return df


@st.cache_resource
def stopwords():
    try:
        words = set(nltk.corpus.stopwords.words("english"))
    except LookupError:
        words = set(ENGLISH_STOP_WORDS)
    return words | {"ang", "ng", "mga", "sa", "at", "ay", "na", "ni", "si", "po", "opo", "para", "ito", "isang"}


def tokenize(text):
    # Regex tokenization works offline without NLTK corpus downloads.
    return [word for word in nltk.tokenize.RegexpTokenizer(r"[^\W\d_]+").tokenize(str(text).lower())
            if len(word) > 1 and word not in stopwords()]


def keywords(documents):
    vectorizer = TfidfVectorizer(tokenizer=tokenize, token_pattern=None, lowercase=False, max_features=5000)
    matrix = vectorizer.fit_transform(documents)
    terms = vectorizer.get_feature_names_out()
    def rank(values):
        return [(terms[i], float(values[i])) for i in np.argsort(-values, kind="stable") if values[i] > 0][:5]
    overall = pd.DataFrame(rank(np.asarray(matrix.mean(axis=0)).ravel()), columns=["Keyword", "TF-IDF score"])
    rows = [rank(matrix.getrow(i).toarray().ravel()) for i in range(matrix.shape[0])]
    return overall, rows


@st.cache_resource
def regression(data):
    x, y = data[["Budget", "Year"]], data["Progress"]
    train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.2, random_state=42)
    model = Pipeline([("scale", StandardScaler()), ("model", LinearRegression())])
    model.fit(train_x, train_y)
    mse = mean_squared_error(test_y, model.predict(test_x))
    model.fit(x, y)
    return model, mse


@st.cache_resource
def classification(data):
    x, y = data[["Budget", "Region"]], data["Status"]
    encoder = ColumnTransformer([("region", OneHotEncoder(handle_unknown="ignore"), ["Region"]),
                                 ("budget", "passthrough", ["Budget"])])
    model = Pipeline([("encode", encoder), ("model", RandomForestClassifier(
        n_estimators=100, max_depth=12, min_samples_leaf=2,
        class_weight="balanced", random_state=42, n_jobs=1))])
    accuracy = None
    test_count = max(2, math.ceil(len(data) * 0.2))
    if y.value_counts().min() >= 2 and len(data) - test_count >= 2:
        train_x, test_x, train_y, test_y = train_test_split(
            x, y, test_size=test_count, stratify=y, random_state=42)
        model.fit(train_x, train_y)
        accuracy = accuracy_score(test_y, model.predict(test_x))
    model.fit(x, y)
    return model, accuracy


def plot(fig):
    st.pyplot(fig)
    plt.close(fig)


def overview(df):
    st.title("🇵🇭 T.R.A.C.E.")
    st.subheader("Taxpayer Resource Allocation & Expenditure Oversight")
    st.write("Explore Philippine infrastructure allocations, extract themes from budget hearings, "
             "estimate project progress, and review inconsistent records.")
    st.write("**SDG 9:** Infrastructure · **SDG 16:** Accountable institutions · **SDG 17:** Partnerships")
    a, b, c = st.columns(3)
    a.metric("Projects", f"{len(df):,}")
    b.metric("Recorded budget", f"₱{df['Budget'].sum(min_count=1):,.2f}")
    c.metric("Regions", df["Region"].nunique())
    st.caption("Progress measures physical completion. Financial utilization cannot be estimated from zero-valued payment records.")
    st.dataframe(df.drop(columns="Completion Date Parsed"), use_container_width=True, hide_index=True)
    st.caption("Amount Paid removed; missing completion dates display as On-Going. Invalid dates are labeled separately.")
    st.subheader("Data consistency review")
    rules = pd.DataFrame({
        "Missing or negative budget": df["Budget"].isna() | df["Budget"].lt(0),
        "Missing or invalid progress": df["Progress"].isna() | ~df["Progress"].between(0, 100),
        "Completed with progress below 100": df["Status"].eq("Completed") & df["Progress"].lt(100),
        "Completion precedes start": df["Completion Date Parsed"].lt(df["Start Date"]),
        "Invalid completion date": df["Completion Date"].eq("Invalid Date"),
    })
    selected = rules.any(axis=1)
    flagged = df.loc[selected, ["Contract ID", "Description", "Budget", "Progress", "Status"]].copy()
    flagged["Review reason"] = rules.loc[selected].apply(lambda row: "; ".join(row.index[row]), axis=1)
    st.metric("Flagged records", len(flagged))
    st.caption("These explicit rules identify possible data inconsistencies, not evidence of wrongdoing.")
    if not flagged.empty:
        st.dataframe(flagged, hide_index=True, use_container_width=True)


def eda(df):
    st.title("EDA & Visualizations")
    st.subheader("Total Budget per Region")
    totals = df.groupby("Region")["Budget"].sum(min_count=1).dropna().sort_values(ascending=False)
    if not totals.empty:
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(x=totals.index, y=totals.values / 1e9, color="#2874A6", ax=ax)
        ax.set_ylabel("Total budget (PHP billions)")
        ax.tick_params(axis="x", rotation=65)
        fig.tight_layout()
        plot(fig)
    else:
        st.info("No numeric budgets available.")
    st.subheader("Project Status")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.countplot(data=df, x="Status", order=df["Status"].value_counts().index, color="#148F77", ax=ax)
    ax.set_ylabel("Projects")
    fig.tight_layout()
    plot(fig)
    st.subheader("Budget vs Progress")
    points = df.dropna(subset=["Budget", "Progress"]).copy()
    if points.empty:
        st.info("No valid budget-progress pairs.")
        return
    if len(points) > 10000:
        points = points.sample(10000, random_state=42)
        st.caption("Showing a reproducible 10,000-project sample.")
    points["Budget (PHP millions)"] = points["Budget"] / 1e6
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.scatterplot(data=points, x="Budget (PHP millions)", y="Progress", hue="Status", alpha=0.5, ax=ax)
    ax.set_ylabel("Progress (%)")
    fig.tight_layout()
    plot(fig)


def nlp(df):
    st.title("NLP Analysis Module")
    text = st.text_area("Budget hearing transcript", height=220)
    if st.button("Extract top 5 TF-IDF keywords", type="primary"):
        documents = [part for part in re.split(r"[.!?\n]+", text) if tokenize(part)]
        if not documents:
            st.warning("Enter text with usable words beyond stopwords.")
        else:
            scores, _ = keywords(documents)
            st.dataframe(scores, hide_index=True)
            st.caption("Mean TF-IDF across sentence/line segments. With one segment, IDF has no cross-document distinction.")
            with st.expander("Tokens after stopword removal"):
                st.write(", ".join(tokenize(text)))
    st.subheader("First 10 project descriptions")
    sample = df.head(10)[["Contract ID", "Description"]].copy()
    try:
        scores, rows = keywords(sample["Description"].tolist())
        st.dataframe(scores, hide_index=True)
        sample["Top keywords"] = [", ".join(f"{word} ({score:.3f})" for word, score in row) for row in rows]
        st.dataframe(sample, hide_index=True, use_container_width=True)
    except ValueError:
        st.info("Sample descriptions contain no usable keywords.")
    st.caption("NLTK tokenization; installed English stopwords or an offline fallback, plus a small Filipino stopword list.")


def machine_learning(df):
    st.title("Machine Learning: Regression & Classification")
    st.caption("Models estimate recorded project patterns. Random holdout performance does not establish future forecasting accuracy.")
    st.subheader("Regression: project progress")
    data = df[["Budget", "Year", "Progress"]].dropna()
    data = data.loc[data["Budget"].ge(0) & data["Year"].between(1900, 2100) & data["Progress"].between(0, 100)]
    if len(data) < 5:
        st.warning("At least five valid records are required for regression.")
    else:
        model, mse = regression(data)
        st.metric("Holdout Mean Squared Error", f"{mse:,.3f}")
        st.caption("MSE is in squared percentage points. Evaluation uses a 20% holdout; the final model uses all valid rows.")
        with st.form("regression"):
            budget = st.number_input("Budget (PHP)", min_value=0.0, value=float(data["Budget"].median()), key="reg_budget")
            year = st.number_input("Year", min_value=1900, max_value=2100, value=int(data["Year"].median()))
            submit = st.form_submit_button("Predict Progress")
        if submit:
            raw = float(model.predict(pd.DataFrame({"Budget": [budget], "Year": [year]}))[0])
            prediction = float(np.clip(raw, 0, 100))
            st.success(f"Predicted Progress: {prediction:.2f}%")
            st.progress(prediction / 100)
            if raw != prediction:
                st.caption(f"Raw prediction {raw:.2f}% capped to the valid 0–100% range.")
            if not data["Budget"].min() <= budget <= data["Budget"].max() or not data["Year"].min() <= year <= data["Year"].max():
                st.info("Input lies outside the observed training range.")
    st.divider()
    st.subheader("Classification: Completed or On-Going")
    data = df.loc[df["Status"].isin(["Completed", "On-Going"]), ["Budget", "Region", "Status"]].dropna()
    data = data.loc[data["Budget"].ge(0)]
    st.caption(f"Excluded {len(df) - len(data):,} records with other statuses or invalid budgets. Regions are one-hot encoded.")
    if data["Status"].nunique() < 2:
        st.warning("Both Completed and On-Going examples are required.")
        return
    model, accuracy = classification(data)
    if accuracy is not None:
        st.metric("Stratified holdout accuracy", f"{accuracy:.1%}")
    else:
        st.info("Too few examples per class for stratified holdout evaluation; model fitted on available records.")
    st.dataframe(data["Status"].value_counts().rename_axis("Status").reset_index(name="Records"), hide_index=True)
    with st.form("classification"):
        budget = st.number_input("Budget (PHP)", min_value=0.0, value=float(data["Budget"].median()), key="cls_budget")
        region = st.selectbox("Region", sorted(data["Region"].unique()))
        submit = st.form_submit_button("Predict Status")
    if submit:
        inputs = pd.DataFrame({"Budget": [budget], "Region": [region]})
        st.success(f"Predicted Status: {model.predict(inputs)[0]}")
        st.dataframe(pd.DataFrame({"Status": model.named_steps["model"].classes_,
                                   "Model probability": model.predict_proba(inputs)[0]}), hide_index=True)
        st.caption("Probabilities are uncalibrated model estimates, not guaranteed completion probabilities.")


def main():
    st.sidebar.title("T.R.A.C.E.")
    pages = {"Home & Dataset Overview": overview, "EDA & Visualizations": eda,
             "NLP Analysis Module": nlp, "Machine Learning": machine_learning}
    page = st.sidebar.radio("Navigation", list(pages))
    candidates = [ROOT / "dpwh-projects-2026-10-06_2.csv", ROOT / "dpwh-projects-2026-10-06.csv"]
    default = next((path for path in candidates if path.is_file()), candidates[0])
    path = Path(st.sidebar.text_input("CSV path", str(default))).expanduser()
    if not path.is_absolute():
        path = ROOT / path
    try:
        df = load_data(str(path), path.stat().st_mtime_ns)
    except (OSError, ValueError, UnicodeError) as error:
        st.error(f"Unable to load dataset: {error}")
        st.stop()
    if df.empty:
        st.warning("Dataset contains no project records.")
        st.stop()
    st.sidebar.caption(f"{len(df):,} records · {path.name}")
    pages[page](df)


if __name__ == "__main__":
    main()
