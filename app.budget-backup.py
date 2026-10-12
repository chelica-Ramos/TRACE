"""T.R.A.C.E. — run with: streamlit run app.py"""
from pathlib import Path
import os

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".cache" / "matplotlib"))
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error

st.set_page_config(page_title="T.R.A.C.E. Budget Tracker", page_icon="🇵🇭", layout="wide")
sns.set_theme(style="whitegrid")
ROOT = Path(__file__).resolve().parent


@st.cache_data
def load_data(path, modified_time):
    # Modification time invalidates the cache when the CSV changes.
    df = pd.read_csv(path, encoding="utf-8-sig", dtype={"Contract ID": "string"})
    df.columns = df.columns.str.strip()
    required = {"Contract ID", "Description", "Category", "Contractor", "Region", "Province", "Budget", "Year", "Progress", "Status", "Start Date", "Completion Date"}
    if required - set(df.columns):
        raise ValueError("Missing columns: " + ", ".join(sorted(required - set(df.columns))))
    df = df.drop(columns="Amount Paid", errors="ignore")
    for col in ["Budget", "Progress", "Year"]:
        values = df[col].astype("string").str.replace(r"[₱,%\s]|(?i:PHP)", "", regex=True)
        df[col] = pd.to_numeric(values, errors="coerce").replace([np.inf, -np.inf], np.nan)
    # Invalid values stay missing; do not manufacture utilization estimates.
    df.loc[df["Budget"].lt(0), "Budget"] = np.nan
    df.loc[~df["Progress"].between(0, 100), "Progress"] = np.nan
    valid_year = df["Year"].between(1900, 2100) & df["Year"].mod(1).eq(0)
    df["Year"] = df["Year"].where(valid_year).astype("Int64")
    for col in ["Contract ID", "Description", "Category", "Contractor", "Region", "Province", "Status"]:
        df[col] = df[col].fillna("").astype(str).str.strip()
    for col in ["Category", "Contractor", "Region", "Province", "Status"]:
        df[col] = df[col].replace("", "Unknown")
    keys = df["Status"].str.lower().str.replace(r"[\s_-]+", "", regex=True)
    df["Status"] = keys.map({"completed": "Completed", "complete": "Completed", "ongoing": "On-Going", "inprogress": "On-Going"}).fillna(df["Status"])
    for col in ["Start Date", "Completion Date"]:
        df[col] = pd.to_datetime(df[col], format="mixed", errors="coerce")
    df["Utilized Budget"] = df["Budget"] * (df["Progress"] / 100)
    df["Estimated Remaining Budget"] = df["Budget"] - df["Utilized Budget"]
    return df


@st.cache_resource
def train_model(data):
    x, y = data[["Budget", "Year"]].astype(float), data["Progress"]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    model = make_pipeline(StandardScaler(), LinearRegression())
    model.fit(x_train, y_train)
    mse = mean_squared_error(y_test, model.predict(x_test))
    model.fit(x, y)  # Refit only after evaluating unseen rows.
    return model, mse


def money(value):
    return "Unavailable" if pd.isna(value) else f"₱{value:,.2f}"


def plot(fig):
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def main():
    path = ROOT / "dpwh-projects-2026-10-06.csv"
    try:
        df = load_data(str(path), path.stat().st_mtime_ns)
    except (OSError, ValueError, UnicodeError) as error:
        st.error(f"Cannot load dataset: {error}")
        st.stop()
    st.sidebar.title("Budget filters")
    regions = st.sidebar.multiselect("Region", sorted(df["Region"].unique()))
    years = st.sidebar.multiselect("Year", sorted(df["Year"].dropna().astype(int).unique().tolist()))
    st.sidebar.caption("Empty selections include all values. Filters apply to every tab and the model.")
    if regions:
        df = df.loc[df["Region"].isin(regions)]
    if years:
        df = df.loc[df["Year"].isin(years)]
    st.title("🇵🇭 T.R.A.C.E.")
    st.subheader("Taxpayer Resource Allocation & Expenditure Oversight")
    st.write("Track allocations, estimated utilization, and unfinished projects across regions and years.")
    st.caption("Utilized Budget = Budget × Progress / 100. This proxy assumes spending proportional to physical progress; actual payments are unavailable.")
    if df.empty:
        st.info("No matching projects. Adjust Region or Year.")
        st.stop()
    a, b, c = st.columns(3)
    a.metric("Total Budget Allocated", money(df["Budget"].sum(min_count=1)))
    b.metric("Total Estimated Utilized Budget", money(df["Utilized Budget"].sum(min_count=1)))
    average = df["Progress"].mean()
    c.metric("Overall Average Progress", "Unavailable" if pd.isna(average) else f"{average:.1f}%")
    st.caption(f"{len(df):,} filtered projects. Average progress is unweighted.")
    invalid = df[["Budget", "Progress"]].isna().any(axis=1).sum()
    if invalid:
        st.warning(f"{invalid:,} records lack valid Budget or Progress. Totals omit missing values; utilization comparisons use complete pairs.")
    charts, projects, analysis = st.tabs(["Where Did The Money Go?", "Project-Level Tracker", "NLP & Machine Learning"])
    with charts:
        st.subheader("Budget by Category")
        totals = df.groupby("Category")["Budget"].sum(min_count=1).dropna().sort_values()
        if not totals.empty:
            fig, ax = plt.subplots(figsize=(11, max(4, len(totals) * 0.4)))
            ax.barh(totals.index, totals.values / 1e6, color="#2874A6")
            ax.set_xlabel("Allocated budget (PHP millions)")
            plot(fig)
        st.subheader("Utilization Gap by Region")
        totals = df.dropna(subset=["Budget", "Utilized Budget"]).groupby("Region")[["Budget", "Utilized Budget"]].sum().sort_values("Budget", ascending=False)
        if totals.empty:
            st.info("No valid allocation-utilization pairs.")
        else:
            fig, ax = plt.subplots(figsize=(12, 6))
            (totals / 1e6).plot.bar(ax=ax, color=["#2874A6", "#148F77"])
            ax.set_ylabel("Budget (PHP millions)")
            ax.tick_params(axis="x", rotation=65)
            ax.legend(["Allocated", "Estimated utilized"])
            plot(fig)
            totals["Estimated gap"] = totals["Budget"] - totals["Utilized Budget"]
            totals["Estimated utilization (%)"] = totals["Utilized Budget"].div(totals["Budget"].replace(0, np.nan)) * 100
            st.dataframe(totals)
        st.subheader("Status Breakdown")
        counts = df["Status"].value_counts()  # Include other statuses in the denominator.
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90, wedgeprops={"width": 0.45})
        ax.set_aspect("equal")
        plot(fig)
        st.subheader("Largest estimated remaining budgets: On-Going projects")
        st.caption("On-Going means unfinished. Delay requires a planned deadline and reporting date.")
        columns = ["Contract ID", "Description", "Region", "Budget", "Utilized Budget", "Estimated Remaining Budget", "Progress"]
        st.dataframe(df.loc[df["Status"].eq("On-Going")].sort_values("Estimated Remaining Budget", ascending=False).head(20)[columns], hide_index=True)
    with projects:
        query = st.text_input("Search Contract ID or Description", placeholder="Contract number or keyword")
        if query.strip():
            mask = df["Contract ID"].str.contains(query.strip(), case=False, regex=False) | df["Description"].str.contains(query.strip(), case=False, regex=False)
            matches = df.loc[mask].reset_index(drop=True)
            if matches.empty:
                st.info("No matching projects within the current filters.")
            else:
                st.caption(f"{len(matches):,} matching records")
                selected = st.selectbox("Select a project", range(len(matches)), format_func=lambda i: f"{matches.iloc[i]['Contract ID']} · {matches.iloc[i]['Description'][:90]} · result {i + 1}")
                row = matches.iloc[selected]
                with st.container(border=True):
                    st.subheader(f"Contract {row['Contract ID']}")
                    st.write(row["Description"])
                    x, y, z = st.columns(3)
                    x.metric("Exact allocated budget", money(row["Budget"]))
                    y.metric("Progress", "Unavailable" if pd.isna(row["Progress"]) else f"{row['Progress']:.2f}%")
                    z.metric("Status", row["Status"])
                    st.write("**Contractor:**", row["Contractor"])
                    st.write("**Region / Province:**", row["Region"], "/", row["Province"])
                    st.write("**Estimated utilized:**", money(row["Utilized Budget"]))
                    st.write("**Estimated remaining:**", money(row["Estimated Remaining Budget"]))
        st.subheader("Filtered project records")
        st.dataframe(df, hide_index=True)
    with analysis:
        st.subheader("Common terms in On-Going descriptions")
        descriptions = df.loc[df["Status"].eq("On-Going"), "Description"]
        descriptions = descriptions.loc[descriptions.str.strip().ne("")]
        if descriptions.empty:
            st.info("No On-Going descriptions within these filters.")
        else:
            try:
                vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
                matrix = vectorizer.fit_transform(descriptions)
                scores = np.asarray(matrix.mean(axis=0)).ravel()
                top = np.argsort(-scores, kind="stable")[:10]
                st.dataframe(pd.DataFrame({"Keyword": vectorizer.get_feature_names_out()[top], "Mean TF-IDF": scores[top]}), hide_index=True)
                st.caption(f"Across {len(descriptions):,} unfinished descriptions. Keywords do not prove or explain delays.")
            except ValueError:
                st.info("Descriptions contain no usable terms after preprocessing.")
        st.divider()
        st.subheader("Predict expected Progress")
        data = df[["Budget", "Year", "Progress"]].dropna()
        if len(data) < 5:
            st.info("At least five valid filtered records are needed. Select broader filters.")
        else:
            model, mse = train_model(data)
            st.metric("Holdout Mean Squared Error", f"{mse:,.3f}")
            st.caption(f"Model uses {len(data):,} filtered records. MSE uses a 20% holdout and squared percentage points; accuracy for future projects is not established.")
            with st.form("predict_progress"):
                budget = st.number_input("Hypothetical Budget (PHP)", min_value=0.0, value=float(data["Budget"].median()), step=100000.0)
                year = st.number_input("Project Year", min_value=1900, max_value=2100, value=int(data["Year"].median()), step=1)
                submitted = st.form_submit_button("Predict Progress")
            if submitted:
                raw = float(model.predict(pd.DataFrame({"Budget": [budget], "Year": [year]}))[0])
                prediction = float(np.clip(raw, 0, 100))
                st.success(f"Expected Progress: {prediction:.2f}%")
                st.progress(prediction / 100)
                if raw != prediction:
                    st.caption(f"Raw prediction {raw:.2f}% capped to 0–100% for display.")
                if not data["Budget"].min() <= budget <= data["Budget"].max() or not data["Year"].min() <= year <= data["Year"].max():
                    st.info("Input is outside the filtered training range; this prediction extrapolates.")


if __name__ == "__main__":
    main()
