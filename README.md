# 🏛️ T.R.A.C.E. (Taxpayer Resource Allocation & Expenditure Oversight)
*Public Finance Intelligence & Local Bilingual AI Assistant Dashboard*

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit_Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com/)

---

## 📌 Project Overview
**T.R.A.C.E.** is an offline-capable data science dashboard and public finance intelligence tool designed to monitor and evaluate Department of Public Works and Highways (DPWH) project allocations and expenditures. By integrating advanced data cleaning, Natural Language Processing (NLP), and Machine Learning regression/classification models, the platform promotes transparent governance and data-driven oversight.

It features **"Tracey"**, a localized, offline bilingual AI assistant (capable of conversing in both English and Tagalog) powered by Ollama, allowing users to seamlessly query project data and discuss analytical insights without requiring an active internet connection.

---

## 🚀 Key Features
* **Executive Dashboard & Project Explorer:** Interactive filters for regional data, budget tracking, and physical progress metrics with a clean, professional user interface.
* **NLP Preprocessing Pipeline:** Automated text cleaning, tokenization, stopword removal, lemmatization, POS tagging, and feature extraction (Binary, Count, and TF-IDF vectorization).
* **Exploratory Data Analysis (EDA):** Visual insights including Word Clouds of project descriptions, budget distributions, allocated vs. actual expenditures, and status trends.
* **Predictive Machine Learning Models:**
  * *Regression:* Simple and Multiple Linear Regression to analyze budget allocations against physical and financial progress ($R^2$, MAE, RMSE).
  * *Classification:* Logistic Regression, Random Forest, and Naive Bayes models to categorize projects and identify top descriptive keywords driving "Flagged for Review" statuses.
* **Tracey Bilingual AI Chatbot:** Fully offline LLM assistant supporting contextual English and Tagalog interaction for friendly project navigation and insight explanation.

---

## 🛠️ Tech Stack
* **Frontend/UI:** Streamlit
* **Data Processing & ML:** Pandas, NumPy, Scikit-Learn
* **NLP & Text Analysis:** NLTK, spaCy, WordCloud, Matplotlib, Seaborn
* **Local AI / LLM:** Ollama (Local LLM Integration)

---

## 📂 Project Structure
```text
T.R.A.C.E./
│
├── app.py                     # Main Streamlit application
├── requirements.txt           # Python package dependencies
├── dpwh-projects-2026.csv     # Cleaned dataset
└── README.md                  # Project documentation
