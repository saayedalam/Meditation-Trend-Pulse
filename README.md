# 🧘 Meditation Trend Pulse  

**Meditation Trend Pulse** is a full-stack data project that tracks global interest in meditation, mindfulness, breathwork, yoga nidra, and guided meditation. It combines **Google Trends data**, automated pipelines, and an interactive **Streamlit dashboard** to explore how interest evolves across time and geography.  

## ✨ Key Features  
- **Automated data pipeline** (Python + Pytrends)  
  - Daily cron job updates Google Trends datasets  
  - GitHub auto-commits new data only if changes occur  
- **Clean, structured datasets** for analysis and visualization  
  - Global weekly interest (5 years)  
  - Country-level interest + top-5 country counts  
  - Related queries (Top, Rising, Shared)  
- **Streamlit dashboard** with consistent UI components  
  - 📊 Global Trends (line charts, % change, top peaks)  
  - 🌍 Country Trends (rankings, breakdowns, flags)  
  - 🔍 Related Queries (top, rising, and shared queries)  
  - 🧩 Final Insights (reflection journal with save/clear)  
- **Professional UI/UX**  
  - Chakra-inspired theme, responsive cards, smooth animations  
  - Shared UI utilities for consistent layout and styling  

## 🛠️ Tech Stack  
- **Python** (Pandas, Pytrends, Prophet [for forecasting])  
- **Streamlit** (interactive app, custom CSS/HTML)  
- **GitHub Actions / Cron** (automation + version control)  
- **Shell scripting** for scheduled updates  
- **Data wrangling & cleaning** with Pandas  

## 📂 Data Pipeline  
1. Pulls **5-year weekly data** for all keywords in a single Pytrends call  
2. Updates derived datasets:  
   - `trend_pct_change.csv` (5-year % change)  
   - `trend_top_peaks.csv` (top 3 peaks per keyword)  
   - `country_interest_summary.csv` (long format)  
   - `country_total_interest_by_keyword.csv`  
   - `country_top5_appearance_counts.csv`  
   - `related_queries_top10.csv`, `related_queries_rising10.csv`, `related_queries_shared.csv`  
3. Runs **once per day**; skips if no new weekly data  

## 🚧 Next Steps  
- Add **forecasting module** with Facebook Prophet  
- Expand dashboard with forward-looking trend insights  

---

👉 This project demonstrates **real-world data engineering, automation, and visualization skills** — built for portfolio use but deployable as a public dashboard.  