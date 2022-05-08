import requests
from bs4 import BeautifulSoup
import concurrent.futures
import re

pages = [f'https://www.olx.ro/imobiliare/?page={i}' for i in range(1, 26)]
apartments=[]
singleRooms=[]
houses=[]
land=[]

def isLand(title, description):
    regex=re.compile('teren', re.IGNORECASE)
    if re.search(regex, title) or re.search(regex, description):
        return True
    return False


def getSurface(title, description):
    regexMp=re.compile(r'\d+\s*m(p|\^?2|²|p[aă]tra[tţ]i*|etr[iu]+\s*p|etr[iu]+\s*p[aă]tra[tţ]i*)', re.IGNORECASE)
    regexHa=re.compile(r'\d+\s*h(a|ectar[ie]*)', re.IGNORECASE)
    number = re.compile('\d+')

    if regexMp.search(title):
        value=int(number.search(regexMp.search(title).group()).group())
        return f'{value} m²'
    elif regexMp.search(description):
        value = int(number.search(regexMp.search(description).group()).group())
        return f'{value} m²'
    elif regexHa.search(title):
        value = int(number.search(regexHa.search(title).group()).group())
        return f'{value} ha'
    elif regexHa.search(description):
        value = int(number.search(regexHa.search(description).group()).group())
        return f'{value} ha'

    return ''

def getTransactionType(title,description):
    rental = isForRental(title, description
    sale = isForSale(title, description)
    exchange = isForExchange(title, description)

    result=''
    if (rental and sale) or (rental and exchange) or (sale and exchange):
        result = ''
    elif rental:
        result = 'For rent'
    elif sale:
        result = 'For sale'
    elif exchange:
        result = 'For exchange'

    return result


def filters(ad, title, description):
    global apartments
    global singleRooms
    global houses
    global land

    if isApartment(title, description):
        result=getTransactionType(title, description)

        surface=getSurface(title, description)
        if surface and result:
            result+=f' - surface: {surface}'
        elif surface:
            result+=f'Surface: {surface}'

        year=getYearOfConstruction(title, description)
        if year and result:
            result+=f' - year of construction: {year}'
        elif year:
            result+=f'Year of construction: {year}'

        rooms=getRooms(title, description)
        if rooms==1 and result:
            singleRooms.append(f'{ad}\n\t{result}')
        elif rooms==1:
            singleRooms.append(f'{ad}\n\tNo further information could be extracted!')
        elif rooms>1 and result:
            apartments.append(f'{ad}\n\t{result} - {rooms} rooms')
        elif rooms>1:
            apartments.append(f'{ad}\n\t{rooms} rooms')
        else:
            apartments.append(f'{ad}\n\tNo further information could be extracted!')


    elif isSingleRoom(title, description):
        result = getTransactionType(title, description)

        surface = getSurface(title, description)
        if surface and result:
            result += f' - surface: {surface}'
        elif surface:
            result += f'Surface: {surface}'

        year = getYearOfConstruction(title, description)
        if year and result:
            result += f' - year of construction: {year}'
        elif year:
            result += f'Year of construction: {year}'

        if result:
            singleRooms.append(f'{ad}\n\t{result}')
        else:
            singleRooms.append(f'{ad}\n\tNo further information could be extracted!')


    elif isHouse(title, description):
        result = getTransactionType(title, description)

        surface = getSurface(title, description)
        if surface and result:
            result += f' - surface: {surface}'
        elif surface:
            result += f'Surface: {surface}'

        year = getYearOfConstruction(title, description)
        if year and result:
            result += f' - year of construction: {year}'
        elif year:
            result += f'Year of construction: {year}'

        rooms=getRooms(title, description)
        if rooms and result:
            result+=f' - {rooms} rooms'
        elif rooms:
            result+=f'{rooms} rooms'

        floors=getFloors(title, description)
        if floors and result:
            result+=f' - {floors} floors'
        elif floors:
            result+=f'{floors} floors'

        if result:
            houses.append(f'{ad}\n\t{result}')
        else:
            houses.append(f'{ad}\n\tNo further information could be extracted!')


    elif isLand(title, description):
        result = getTransactionType(title, description)

        surface = getSurface(title, description)
        if surface and result:
            result += f' - surface: {surface}'
        elif surface:
            result += f'Surface: {surface}'

        if result:
            land.append(f'{ad}\n\t{result}')
        else:
            land.append(f'{ad}\n\tNo further information could be extracted!')


def adScraper(ad):
    # global counter
    adPage = BeautifulSoup(requests.get(ad).content, 'lxml')
    try:
        title = adPage.select('h1.css-r9zjja-Text.eu5v0x0')[0].text
        description = adPage.select('div.css-g5mtbi-Text')[0].text
        filters(ad, title, description)
        # counter += 1
    except:
        title = adPage.select('h1.css-11kn46p.eu6swcv17')[0].text
        description = adPage.select('section.css-1vfwbw8.e1r1048u3')[0]
        description = description.find(class_='e1r1048u1').text
        filters(ad, title, description)
        # print(description)
        # counter += 1

    # if rooms(title, description)==1:
    #     singleRooms.append(ad)




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
