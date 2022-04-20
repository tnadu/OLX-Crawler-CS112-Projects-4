import requests
import concurrent.futures
import re
from bs4 import BeautifulSoup

pages = [f'https://www.olx.ro/imobiliare/?page={i}' for i in range(1, 26)]
hm = 0


def adScraper(ad):
    # global counter
    adPage = BeautifulSoup(requests.get(ad).content, 'lxml')
    try:
        title = adPage.select('h1.css-r9zjja-Text.eu5v0x0')[0].text
        description = adPage.select('div.css-g5mtbi-Text')[0].text
        # counter += 1
    except:
        title = adPage.select('h1.css-11kn46p.eu6swcv17')[0].text
        description = adPage.select('section.css-1vfwbw8.e1r1048u3')[0]
        description = description.find(class_='e1r1048u1').text
        # print(description)
        # counter += 1


for page in pages:
    # global counter
    # print(page)
    links = BeautifulSoup(requests.get(page).content, 'lxml')
    # 'ads' contains all '<a>' tags which have a 'href' attribute linking pages which begin with either of the two link formats
    ads = links.find_all('a', attrs={'href': re.compile('^https://www.storia.ro/ro/oferta/|^https://www.olx.ro/d/oferta')})
    ads = [ad['href'] for ad in ads]
    ads = list(set(ads))[5:]

    # counter = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(ads)) as executor:
        executor.map(adScraper, ads)
    # print(counter)
