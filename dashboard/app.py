import streamlit as st
import pandas as pd
import sqlite3
import os
import altair as alt

st.set_page_config(page_title="MLB Dashboard", layout="wide")
st.title("⚾ MLB American League Stats Dashboard")

# Setup DB Paths
DB_PATHS = {
    "Team Standings": os.path.abspath(os.path.join(".", "db", "team_standings.db")),
    "Player Review": os.path.abspath(os.path.join(".", "db", "player_review.db")),
    "Pitcher Review": os.path.abspath(os.path.join(".", "db", "pitcher_review.db"))
}

@st.cache_data
def get_tables(db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return sorted([row[0] for row in cursor.fetchall()])

@st.cache_data
def load_table(db_path, table_name):
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql(f"SELECT * FROM '{table_name}'", conn)

# Sidebar selections
data_type = st.sidebar.selectbox("Select Data Type", list(DB_PATHS.keys()))
db_path = DB_PATHS[data_type]

if not os.path.exists(db_path):
    st.error(f"Database for {data_type} not found.")
    st.stop()

all_tables = get_tables(db_path)
year_options = sorted({t.split("_")[0] for t in all_tables}, reverse=True)
selected_year = st.sidebar.selectbox("Select Year", year_options)
matched_table = next((t for t in all_tables if t.startswith(selected_year)), None)

if not matched_table:
    st.error(f"No table found for year {selected_year}")
    st.stop()

df = load_table(db_path, matched_table)

def deduplicate_columns(columns):
    seen = {}
    new_cols = []
    for col in columns:
        col = col.strip()
        if col in seen:
            seen[col] += 1
            new_cols.append(f"{col}.{seen[col]}")
        else:
            seen[col] = 0
            new_cols.append(col)
    return new_cols

df.columns = deduplicate_columns(df.columns)

# Render by Data Type
if data_type == "Team Standings":
    df.rename(columns={df.columns[0]: "Team"}, inplace=True)
    df["Wins"] = pd.to_numeric(df.get("Wins"), errors="coerce")
    df["Losses"] = pd.to_numeric(df.get("Losses"), errors="coerce")
    df["WP"] = pd.to_numeric(df.get("WP"), errors="coerce")

    if "Payroll" in df.columns:
        try:
            df["Payroll ($M)"] = (
                df["Payroll"]
                  .replace('[\$,]', '', regex=True)
                  .replace(',', '', regex=True)
                  .astype(float) / 1e6
            )
        except Exception as e:
            st.warning(f"Could not parse payroll column: {e}")
            df["Payroll ($M)"] = None

    # Filter and chart
    wp_min = st.sidebar.slider("Min Win %", 0.3, 0.8, 0.5, step=0.01)
    filtered_df = df[df["WP"] >= wp_min]

    st.subheader(f"🏆 Win Percentage — {selected_year}")
    st.bar_chart(filtered_df.set_index("Team")["WP"])

    if "Payroll ($M)" in filtered_df.columns and filtered_df["Payroll ($M)"].notnull().any():
        st.subheader("💰 Payroll vs Wins")
        st.scatter_chart(filtered_df.set_index("Team")[["Payroll ($M)", "Wins"]])

    # show the standings table
    st.subheader("📋 Filtered Standings")
    columns_to_show = ["Team", "Wins", "Losses", "WP"]
    if "Payroll ($M)" in filtered_df.columns:
        columns_to_show.append("Payroll ($M)")

    st.dataframe(filtered_df[columns_to_show].sort_values("WP", ascending=False))

elif data_type == "Player Review":
    df.rename(columns={df.columns[0]: "Statistic"}, inplace=True)
    df.columns = [col.strip() for col in df.columns]
    df["#"] = pd.to_numeric(df["#"], errors="coerce")

    st.subheader(f"📊 Player Leaderboard — {selected_year}")

    # Only include stats where "#" is not null
    valid_stats = (
        df.dropna(subset=["#", "Statistic"])
          .groupby("Statistic")
          .filter(lambda g: g["#"].notna().any())["Statistic"]
          .unique()
          .tolist()
    )

    if not valid_stats:
        st.warning("No valid statistics found in the player review data.")
        st.stop()

    selected_stat = st.selectbox("Choose a Statistic", sorted(valid_stats))

    stat_df = df[df["Statistic"] == selected_stat]
    stat_df = stat_df.dropna(subset=["#", "Name"])

    if not stat_df.empty:
        top_n = stat_df.sort_values("#", ascending=False).head(10)

        st.markdown(f"### 🏅 Top 10 in {selected_stat}")

        chart = (
            alt.Chart(top_n)
            .mark_bar(color='steelblue')
            .encode(
                x=alt.X("#:Q", title=selected_stat),
                y=alt.Y("Name:N", sort='-x'),
                tooltip=["Name", "Team", "#"]
            )
            .properties(height=400)
        )
        st.altair_chart(chart, use_container_width=True)

        st.markdown("### 📋 Full Stat Table")
        st.dataframe(stat_df[["Name", "Team", "#"]].sort_values("#", ascending=False))
    else:
        st.warning(f"No data available for {selected_stat}.")

elif data_type == "Pitcher Review":
    df.rename(columns={df.columns[0]: "Statistic"}, inplace=True)
    df.columns = [col.strip() for col in df.columns]
    df["#"] = pd.to_numeric(df["#"], errors="coerce")

    st.subheader(f"⚾ Pitching Performance — {selected_year}")

    # Only include stats that have at least one numeric "#" value
    valid_stats = (
        df.dropna(subset=["#", "Statistic"])
          .groupby("Statistic")
          .filter(lambda g: g["#"].notna().any())["Statistic"]
          .unique()
          .tolist()
    )

    if not valid_stats:
        st.warning("No valid pitching statistics available for this year.")
        st.stop()

    selected_stat = st.selectbox("Select a Stat", sorted(valid_stats))

    stat_df = df[df["Statistic"] == selected_stat].dropna(subset=["#", "Name"])

    if not stat_df.empty:
        top10 = stat_df.sort_values("#", ascending=False).head(10)

        st.markdown(f"### 🔵 Bubble Chart — Top in {selected_stat}")

        chart = (
            alt.Chart(top10)
            .mark_circle(opacity=0.8)
            .encode(
                x=alt.X("#:Q", title=f"{selected_stat} Value"),
                y=alt.Y("Team:N", title="Team"),
                size=alt.Size("#:Q", title="Magnitude", scale=alt.Scale(range=[100, 1000])),
                color=alt.Color("Name:N", legend=None),
                tooltip=["Name", "Team", "#"]
            )
            .properties(height=400)
        )

        st.altair_chart(chart, use_container_width=True)

        st.subheader("📋 Full Pitcher Data")
        st.dataframe(stat_df[["Name", "Team", "#"]].sort_values("#", ascending=False))

    else:
        st.warning(f"No data available for {selected_stat}.")

else:
    st.warning("Unsupported data type.")
