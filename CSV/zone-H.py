import os
import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

# Current date for output filename
today = datetime.now()
year, month, day = today.year, today.month, today.day
output_path = f'output/zoneH-{year}-{month}-{day}-urls.csv'

# Cookies and headers, update with your valid Zone-H cookies
cookies = {
    'ZHE': '43e7d686af657175b6bfc71884a1d70d',
    'PHPSESSID': 'a3t0go4aj68em8ng56n7rmlqb0'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
    'Referer': 'http://www.zone-h.org/archive/special=1',
}

def get_total_pages():
    # Check the number of pages in the archive
    response = requests.get('http://www.zone-h.org/archive', headers=headers, cookies=cookies)
    soup = BeautifulSoup(response.text, "html.parser")
    total_text = soup.find('b')
    try:
        total = int(total_text.text.replace(",", ""))
        return (total // 25) + 1  # Calculate total pages
    except:
        print("Total pages not found; defaulting to 1 page.")
        return 1

def scrape_urls_from_page(page_number):
    # Scrape URLs from a single page of Zone-H
    page_url = f"http://www.zone-h.org/archive/page={page_number}"
    response = requests.get(page_url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find table rows that contain the URLs
    rows = soup.find_all('tr')[1:-2]  # Skip header/footer rows

    urls = []
    for row in rows:
        cells = row.find_all('td')
        if len(cells) > 9:  # Verify cell count to access URL
            url_cell = cells[1].text.strip()  # Adjust index if necessary
            if url_cell:
                urls.append(url_cell)

    return urls

def main():
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)

    # Write CSV header if file does not exist
    if not os.path.exists(output_path):
        with open(output_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['URL'])

    # Get total pages to scrape
    num_pages = get_total_pages()

    for page in range(1, num_pages + 1):
        print(f"Scraping page {page}/{num_pages}...")
        urls = scrape_urls_from_page(page)

        if urls:
            with open(output_path, 'a', newline='') as csv_file:
                writer = csv.writer(csv_file)
                for url in urls:
                    writer.writerow([url])
        else:
            print(f"No URLs found on page {page}.")

        time.sleep(2)  # Delay to avoid getting blocked

    print(f"Scraping complete. URLs saved to {output_path}")

if __name__ == "__main__":
    main()
