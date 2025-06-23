import sqlite3
import os
import sys

# Define the directories
data_dirs = {
    "data/raw/player_review": "player_review.db",
    "data/raw/pitcher_review": "pitcher_review.db",
    "data/raw/team_standings": "team_standings.db"
}

def list_tables(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    return [t[0] for t in tables]

def preview_table(conn, table_name, limit=5):
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        print("\n Preview of", table_name)
        print("-" * 50)
        print("	".join(cols))
        for row in rows:
            print("	".join(str(val) for val in row))
    except Exception as e:
        print(f"Error previewing table '{table_name}': {e}")


def run_query(conn, query):
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        print("\n Query Result")
        print("-" * 60)
        print("	".join(cols))
        for row in rows:
            print("	".join(str(val) for val in row))
    except Exception as e:
        print(f"Query error: {e}")


def main():
    print("Welcome to the MLB History Database Explorer!")

    for data_dir, db_file in data_dirs.items():
        db_path = os.path.join("db", db_file)
        if not os.path.exists(db_path):
            print(f"Database file '{db_path}' not found. Please run the data import script first.")
            continue

        print(f"\nConnected to database: {db_file}")
        conn = sqlite3.connect(db_path)

        print("Available tables:")
        tables = list_tables(conn)
        for t in tables:
            print("  -", t)

        print("\nYou can enter SQL queries below.")
        print("Type `preview <table>` to see sample rows.")
        print("Type `exit` to switch to the next database or quit if all databases are processed.\n")

        while True:
            user_input = input(f"SQL ({db_file})> ").strip()

            if user_input.lower() in ("exit", "quit"):
                conn.close()
                print(f"Closing connection to {db_file}.")
                break
            elif user_input.lower().startswith("preview "):
                table = user_input.split(" ", 1)[1]
                preview_table(conn, table)
            elif user_input:
                run_query(conn, user_input)

        print("Moving to the next database (if any).")

    print("\nDone exploring all available databases. Goodbye!")


if __name__ == "__main__":
    main()

# Example Query for player_review.db ---- SELECT * FROM "2024_american_league_player_review" WHERE "AVG" != '' ORDER BY CAST("AVG" AS FLOAT) DESC LIMIT 5;

# Example Query for pitcher_review.db ---- SELECT * FROM "2024_american_league_pitcher_review" WHERE "ERA" != '' ORDER BY CAST("ERA" AS FLOAT) ASC LIMIT 5;

# Query for team_standings.db ---- SELECT * FROM "2024_american_league_team_standings" WHERE "Pct" != '' ORDER BY CAST("Pct" AS FLOAT) DESC;
