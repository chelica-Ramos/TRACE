# TRACE Budget Tracker

Executive Streamlit dashboard with custom metric cards and four tabs:
Executive Dashboard, Project Explorer, AI Insights, and Tracey. Region/Year filters apply
globally. Plotly provides interactive status donuts, grouped regional budget bars,
unfinished-project TF-IDF keyword charts, and a prediction gauge. Linear regression
predicts progress from Budget alone and trains dynamically without saved models.

Run the installed Python 3.13 environment:

```powershell
.\.runtime\Scripts\python.exe -m streamlit run app.py
```

For a fresh environment, use Python 3.11–3.14 and install requirements.txt.
Place dpwh-projects-2026-10-06.csv beside app.py.

Utilized Budget = Budget × Progress / 100 is an estimate based on physical
progress, not measured payments. Amount Paid is dropped. On-Going means
unfinished; delay cannot be established without planned deadlines and a reporting
date. The dashboard tabs and regression model follow the Region/Year filters.

The earlier four-page version is preserved in app.previous.py.

Tracey uses local Ollama and llama3. Start Ollama before chatting. The app
automatically downloads the model on the first prompt if missing; this requires
internet. Subsequent conversations run offline. Tracey receives chat history,
not the dashboard dataset or filters.
