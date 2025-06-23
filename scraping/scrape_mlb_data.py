import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import os

# Setup Selenium WebDriver with options
options = webdriver.ChromeOptions()
options.add_argument('--headless') 
options.add_argument('--disable-gpu')  
options.add_argument('--window-size=1920x1080') 

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

# Make sure output folder exists
os.makedirs("data/raw", exist_ok=True)

driver.get("https://www.baseball-almanac.com/yearmenu.shtml")
time.sleep(2)

# Find all year links
year_links = driver.find_elements(By.CSS_SELECTOR, "td a")
links = [link.get_attribute("href") for link in year_links if "yearly/yr" in link.get_attribute("href")]

# Limit to recent 15 years
links = [link for link in links if "202" in link or "201" in link][-15:]

player_review_xpath = '//*[@id="wrapper"]/div[2]/div[3]/table'
pitcher_review_xpath = '//*[@id="wrapper"]/div[2]/div[4]/table'
team_standings_xpath = '/html/body/div[2]/div[2]/div[5]/table'


def extract_table_data(driver, xpath):
    table = driver.find_element(By.XPATH, xpath)
    header_row = table.find_elements(By.TAG_NAME, "tr")[1]
    headers = [th.text.strip() for th in header_row.find_elements(By.TAG_NAME, "th")]
    if not headers:
        headers = [th.text.strip() for th in header_row.find_elements(By.TAG_NAME, "td")]

    # Filter out headers 
    headers = [header for header in headers if "East" not in header and "West" not in header and "Central" not in header]

    data = []
    for row in table.find_elements(By.TAG_NAME, "tr")[2:]:  # Start from the second row
        cells = row.find_elements(By.TAG_NAME, "td")

        # Skip rows with class "banner"
        if cells and len(cells) > 0 and "banner" in cells[0].get_attribute("class").split():
            continue

        row_data = {}
        cell_index = 0  # Keep valid header index
        for i, cell in enumerate(cells):
            if cell_index < len(headers):

                row_data[headers[cell_index]] = cell.text.strip()
                cell_index+=1

            else:
                row_data[f'Column_{i}'] = cell.text.strip()  # Handle tables where number of cells exceed number of header
        data.append(row_data)
    return headers, data


def scrape_table_to_csv(driver, xpath, filename, year):
    try:
        headers, table_data = extract_table_data(driver, xpath)

        if table_data:

            df = pd.DataFrame(table_data)

            os.makedirs(os.path.dirname(filename), exist_ok=True)
            df.to_csv(filename.format(year=year), index=False)
            print(f"Saved {filename.format(year=year)}")
        else:
            print(f"No data found for table at {xpath} in {year}")
    except Exception as e:
        print(f"Error extracting table at {xpath} in {year}: {e}")


for link in links:
    try:
        driver.get(link)
        time.sleep(2)

        year = link.split("yr")[-1][:4]

        player_review_filename = "data/raw/player_review/{year}_american_league_player_review.csv"
        pitcher_review_filename = "data//raw/pitcher_review/{year}_american_league_pitcher_review.csv"
        team_standings_filename = "data//raw/team_standings/{year}_american_league_team_standings.csv"

        # Scrape and save each table
        scrape_table_to_csv(driver, player_review_xpath, player_review_filename, year)
        scrape_table_to_csv(driver, pitcher_review_xpath, pitcher_review_filename, year)
        scrape_table_to_csv(driver, team_standings_xpath, team_standings_filename, year)

    except Exception as e:
        print(f"Error with {link}: {e}")

driver.quit()

print("Done! CSVs saved.")
