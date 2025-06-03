import requests
from bs4 import BeautifulSoup
import csv
import time

# Base URL for PhishTank's browsing page
base_url = "https://phishtank.org/phish_search.php?page={}&valid=y&active=y"

# Initialize CSV file to save the URLs
with open('phishtank_phishing_scraped.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['URL'])  # Column header

    url_count = 0
    max_urls = 100000
    page = 1

    # Loop through pages until we reach the desired number of URLs
    while url_count < max_urls:
        print(f"Scraping page {page}...")
        # Get the page content
        response = requests.get(base_url.format(page))
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all URL entries on the page
        url_cells = soup.find_all('td', class_='url')  # Adjust selector if needed

        # Extract URLs and write them to the CSV
        for cell in url_cells:
            url = cell.get_text(strip=True)
            writer.writerow([url])
            url_count += 1

            # Stop if we've reached the limit
            if url_count >= max_urls:
                print(f"Reached limit of {max_urls} URLs.")
                break

        # Move to the next page and add a delay to avoid rate limiting
        page += 1
        time.sleep(2)  # Adjust sleep duration as needed

    print(f"Saved {url_count} URLs to 'phishtank_phishing_scraped.csv'")
