import os
import sqlite3
import pandas as pd

# Define the directories
data_dirs = {
    "data/raw/player_review": "player_review.db",
    "data/raw/pitcher_review": "pitcher_review.db",
    "data/raw/team_standings": "team_standings.db"
}

# Create the 'db'
db_dir = "db"
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

for data_dir, db_file in data_dirs.items():
    print(f"Processing directory: {data_dir}")

    # full path to the database file 
    db_path = os.path.join(db_dir, db_file)

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all CSV files in the directory
    csv_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]

    if not csv_files:
        print(f"No CSV files found in {data_dir}")
    else:
        for file in csv_files:
            file_path = os.path.join(data_dir, file)
            # File name without the extension
            table_name = os.path.splitext(file)[0]

            try:
                print(f"Loading CSV: {file}")
                df = pd.read_csv(file_path)

                # Write DataFrame to SQLite table
                df.to_sql(table_name, conn, if_exists='replace', index=False)

                print(f"Imported into table '{table_name}' with {len(df)} rows.")
            except Exception as e:
                print(f"Error importing {file}: {e}")

    conn.close()
    print(f"Done importing all CSV files from {data_dir} into the SQLite database: {db_path}.")

print("Done importing all CSV files.")
