# ⚾ MLB American League Data Explorer

This project scrapes, stores, and explores MLB player, pitcher, and team data across the last 15 seasons.

## 📂 Project Structure

- `scraping/` → Scraper for Baseball Almanac tables
- `data/raw/` → Raw CSVs
- `db/` → SQLite DBs and import script
- `queries/` → CLI tool to query data interactively
- `dashboard/app.py` → Streamlit dashboard
- `assets/img/` → Screenshots of the Streamlit dashboard

## 🚀 Live Dashboard

👉 [Click to View on Streamlit.io](https://ctd-web-scraping-and-dashboard-project-r5owgddeamjhpkwu4gaepm.streamlit.app/)

## 💻 Local Setup
```bash
git clone https://github.com/henzbori/CTD-Web-Scraping-and-Dashboard-Project.git
pip install -r requirements.txt
streamlit run dashboard/app.py
