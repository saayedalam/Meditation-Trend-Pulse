# 🧘 Meditation Trend Pulse

**Interactive dashboard + automation pipeline** tracking global and country-level interest in meditation, mindfulness, and breathwork.  
Built with **Python, PyTrends, Prophet, and Streamlit** to demonstrate end-to-end data workflows: ingestion, automation, analysis, forecasting, and dashboarding.

🌐 **Live App:** [Streamlit Dashboard](https://your-streamlit-link-here)  
📂 **Repo Highlights:** `/automation` · `/data` · `/notebooks` · `/streamlit`  

---

## 📖 Project Overview
Meditation and mindfulness practices have gained global popularity, but which ones are rising, steady, or fading?  
This project answers that by combining **Google Trends data** with automated pipelines, statistical forecasting, and a polished **multi-page Streamlit app**.  

The project was designed as part of my portfolio to showcase skills in **data engineering, automation, analysis, and stakeholder-ready visualization**.

---

## 🛠️ Tech Stack
- **Data ingestion:** [PyTrends](https://github.com/GeneralMills/pytrends) (Google Trends unofficial API)  
- **Automation:** Python scripts + daily update scheduling  
- **Analysis & Notebooks:** Pandas, NumPy, Matplotlib, scikit-learn metrics  
- **Forecasting:** Prophet (CmdStan backend) for time-series forecasting  
- **Dashboard:** Streamlit + Altair (custom UI components, multi-page layout)  

---

## 📂 Repository Structure
```
meditation-trend-pulse/
│
├── automation/        # update_all_datasets.py and cron-ready run_update.sh
├── data/              # 9 cleaned datasets (global, country, related queries)
├── notebooks/         # EDA + transformation notebooks for each Streamlit page
├── forecasting/       # Prophet forecasting notebook (polished, error-free)
├── streamlit/         # Streamlit app: Home + 4 pages + utils (UI components)
│   ├── pages/
│   ├── utils/
│   └── .streamlit/config.toml
├── requirements.txt   # clean dependency list
├── .gitignore
└── README.md
```

---

## 📊 Dashboard Features
- **Global Trends** → 5-year search interest, % change table, peak interest dates  
- **Country Trends** → top countries by practice, cross-keyword comparisons  
- **Related Queries** → top & rising search queries, shared interest signals  
- **Forecasting** → Prophet-based projections with uncertainty intervals  

Each page uses custom UI components (chakra-themed cards, headers, footers) for a professional look.

---

## 🔄 Automation
- Daily update script pulls new Google Trends data.  
- Only overwrites datasets if fresh data is available.  
- Keeps repo lightweight and reproducible.  

---

## 📈 Forecasting
- Prophet models project future global search interest.  
- Visuals highlight uncertainty intervals and trend direction.  
- Complements descriptive dashboards with predictive insights.  

---

## 🎯 Why This Project Matters
This project demonstrates:  
- **End-to-end ownership** → from raw API pulls to a polished dashboard  
- **Breadth of skills** → automation, time series forecasting, dashboarding  
- **Stakeholder readiness** → insights framed for business & non-technical audiences  

Together with my other portfolio projects (Loan Default Prediction + CMS Hospital SQL/BI), this completes a **well-rounded, job-ready data portfolio**.

---

## 🚀 Next Steps
- Add more keywords (e.g., yoga, meditation apps) for broader analysis.  
- Connect to YouTube API for multimedia trend comparison.  
- Deploy continuous integration for dataset + dashboard updates.  

---

## 👤 Author
**Saayed Alam**  
🔗 [Portfolio Website](https://your-website-link-here) | [LinkedIn](https://www.linkedin.com/in/saayedalam) | [GitHub](https://github.com/saayedalam)
