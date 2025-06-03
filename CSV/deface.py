from bs4 import BeautifulSoup
import requests
import math
import csv
import os
import json
from datetime import datetime
import smtplib

senderEmail = ''
senderPassword = ''
today = datetime.now()
year = today.year
month = today.month
day = today.day
defaced = []

cookies = {
    'ZHE': '43e7d686af657175b6bfc71884a1d70d',
    'PHPSESSID': 'a3t0go4aj68em8ng56n7rmlqb0'
}

headers = {
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Referer': 'http://www.zone-h.org/archive/special=1',
    'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
}

def getEmail(domain):
    url = "https://api.hunter.io/v2/domain-search?domain=" + domain + "&api_key=a435c665ca5965b46151a3b40b5e6729efd450e1"
    response = requests.get(url)
    data = response.json()
    emails = data.get('data', {}).get("emails", [])
    if emails:
        return emails[0]["value"]
    return None

def send_mail(senderEmail, senderPassword, receiverEmail, message):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(senderEmail, senderPassword)
    server.sendmail(senderEmail, receiverEmail, message.encode("utf8"))
    server.quit()

def crawlEachPage(pageNumber):
    urlPage = f"http://www.zone-h.org/archive/page={pageNumber}"
    response = requests.get(urlPage, headers=headers, cookies=cookies)
    soup = BeautifulSoup(response.text, "html.parser")
    
    rowAll = soup.find_all('tr')
    if not rowAll:
        print(f"No rows found on page {pageNumber}.")
        return
    
    for row in rowAll[1:-2]:  # Skip the header and footer rows
        tdAll = row.find_all('td')
        if len(tdAll) < 10:
            print(f"Unexpected row structure on page {pageNumber}: {row}")
            continue
        
        try:
            location = tdAll[5].find('img')['title'] if tdAll[5].find('img') else ""
        except Exception as e:
            location = ""
        
        i = "yes" if tdAll[6].find('img') else ""
        view = "http://www.zone-h.org" + tdAll[9].find('a')['href'] if tdAll[9].find('a') else ""
        
        if location == "Viet Nam":
            r = (tdAll[0].text, tdAll[1].text, tdAll[2].text, tdAll[3].text, tdAll[4].text,
                 location, i, tdAll[7].text.strip(), tdAll[8].text, view)
            if r not in defaced:
                with open(f'output/zoneH-{year}-{month}-{day}-output.csv', 'a', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(r)
                
                receiverEmail = getEmail(tdAll[7].text.strip())
                if receiverEmail:
                    message = 'Alert: New defacement detected.'
                    send_mail(senderEmail, senderPassword, receiverEmail, message)

def crawlPageInRange(startPage, endPage):
    for page in range(startPage, endPage + 1):
        print(f"Crawling page {page}...")
        crawlEachPage(page)

if __name__ == "__main__":
    originUrl = 'http://www.zone-h.org'
    url = 'http://www.zone-h.org/archive'
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    soup = BeautifulSoup(response.text, "html.parser")
    total = soup.find('b')
    
    if total and total.text.isdigit():
        totalPage = int(total.text.replace(",", ""))
        numOfPage = math.ceil(totalPage / 25)
    else:
        print("Could not find total page count. Defaulting to 1 page.")
        numOfPage = 1
    
    output_path = f'output/zoneH-{year}-{month}-{day}-output.csv'
    if not os.path.exists(output_path):
        os.makedirs('output', exist_ok=True)
        with open(output_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Date', 'Notifier', 'H', 'M', 'R', 'L', 'Special defacement', 'Domain', 'OS', 'View'])
    else:
        with open(output_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            for row in reader:
                if row:
                    defaced.append(tuple(row))
    
    crawlPageInRange(1, numOfPage + 1)
