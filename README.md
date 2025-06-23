# ⚾ MLB American League Data Explorer

This project scrapes, stores, and explores MLB player, pitcher, and team data across the last 15 seasons.

## 📂 Project Structure

- `scraping/` → Scraper for Baseball Almanac tables
- `data/raw/` → Raw CSVs
- `db/` → SQLite DBs and import script
- `queries/` → CLI tool to query data interactively
- `dashboard/app.py` → Streamlit dashboard

## 🚀 Live Dashboard

👉 [Click to View on Streamlit.io](https://<your-streamlit-link>)

## 💻 Local Setup

```bash
git clone https://github.com/yourname/mlb-dashboard.git
cd mlb-dashboard
pip install -r requirements.txt
streamlit run dashboard/app.py

![example of the daashboard top players](/assets/img/dashboard%20screenshort%20top%20players.png) ![example of the dashboard win %](/assets/img/dashboard%20screenshort%20win%20percentage.png)