import requests
from bs4 import BeautifulSoup
import concurrent.futures
import re
import time

# Hard-coded list of OLX URLs
pages = [f'https://www.olx.ro/imobiliare/?page={i}' for i in range(1, 6)]

# Lists which will store ads corresponding to each category
apartments = []
singleRooms = []
houses = []
land = []


# Modular functions for each and every regex search performed
# Category REGEX
def isHouse(title, description):
    regex = re.compile('vil[aă]|cas[aă]|duplex|house', re.IGNORECASE)
    if regex.search(title) or regex.search(description):
        return True
    return False


def isApartment(title, description):
    regex = re.compile(r'apart[ae]*ment|\bap(art)?\b', re.IGNORECASE)
    if re.search(regex, title) or re.search(regex, description):
        return True
    return False


def isSingleRoom(title, description):
    regex = re.compile(r'garsonier[aăe]|studio', re.IGNORECASE)
    if regex.search(title) or regex.search(description):
        return True
    return False


def isLand(title, description):
    regex = re.compile('teren', re.IGNORECASE)
    if re.search(regex, title) or re.search(regex, description):
        return True
    return False


# Transaction type REGEX
def isForSale(title, description):
    regex = re.compile(r'v[aîăâ]nzare|v[aîăâ]nd|sale|achizi[tț]i(e|on[ăa]r[ei])', re.IGNORECASE)
    if re.search(regex, title) or re.search(regex, description):
        return True
    return False


def isForRental(title, description):
    regex = re.compile(r'([iîâ]n)?\s*chiri(e|ez|at|[aă]m|ere)', re.IGNORECASE)
    if regex.search(title) or regex.search(description):
        return True
    return False


def isForExchange(title, description):
    regex = re.compile('schimb|troc', re.IGNORECASE)
    if regex.search(title) or regex.search(description):
        return True
    return False


# Sub-filtering REGEX
def getRooms(title, description):
    regex = re.compile(r'[\do]+\s*camer[eăa]|[\do]+\s*cam|[\do]+\s*[iâî]nc[aă]per[ei]', re.IGNORECASE)

    if re.search(regex, title):
        return int("".join([x for x in regex.findall(title)[0] if x.isdigit()]))
    elif re.search(regex, description):
        return int("".join([x for x in regex.findall(description)[0] if x.isdigit()]))

    return False


def getYearOfConstruction(title, description):
    regex = re.compile(r'an(ul)?\s*(20[12]\d|19\d{2})', re.IGNORECASE)
    number = re.compile('\d+')

    if regex.search(title):
        # the string which is found is parsed again using the 'number' regex variable,
        # in order to extract the year as a string, which is then converted to an integer
        return int(number.search(regex.search(title).group()).group())
    elif re.search(regex, description):
        return int(number.search(regex.search(description).group()).group())

    return False


def getSurface(title, description):
    regexMp = re.compile(r'\d+\s*m(p|\^?2|²|p[aă]tra[tţ]i*|etr[iu]+\s*p|etr[iu]+\s*p[aă]tra[tţ]i*)', re.IGNORECASE)
    regexHa = re.compile(r'\d+\s*h(a|ectar[ie]*)', re.IGNORECASE)
    number = re.compile('\d+')

    if regexMp.search(title):
        value = int(number.search(regexMp.search(title).group()).group())
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


# returns a properly formatted string, using all transaction type regex functions
def getTransactionType(title, description):
    rental = isForRental(title, description)
    sale = isForSale(title, description)
    exchange = isForExchange(title, description)

    if (rental and sale) or (rental and exchange) or (sale and exchange):
        # Multiple transaction types found (conflict), so transaction type is considered undecidable
        return ''
    if rental:
        return 'For rent'
    if sale:
        return 'For sale'
    if exchange:
        return 'For exchange'


# Main filtering function
# - receives source ad URL, extracted title and description
# - appends formatted result, based on source ad URL and regex filters, to corresponding category list
def filters(ad, title, description):
    global apartments
    global singleRooms
    global houses
    global land

    if isApartment(title, description):
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

        rooms = getRooms(title, description)
        # if apartment has only one room, it is considered a single room
        if rooms == 1 and result:
            singleRooms.append(f'{ad}\n\t{result}')
        elif rooms == 1:
            singleRooms.append(f'{ad}\n\tNo further information could be extracted!')
        # else it is considered a regular apartment
        elif rooms > 1 and result:
            apartments.append(f'{ad}\n\t{result} - {rooms} rooms')
        elif rooms > 1:
            apartments.append(f'{ad}\n\t{rooms} rooms')
        elif result:
            apartments.append(f'{ad}\n\t{result}')
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

        rooms = getRooms(title, description)
        if rooms and result:
            result += f' - {rooms} rooms'
        elif rooms:
            result += f'{rooms} rooms'

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


# Function used for extracting individual ad pages from parent ad-listing pages
# - is separate for multi-threading optimization
def adScraper(ad):
    # request.get(URL).content returns the html file of the URL link, which is then transformed
    # into a BeautifulSoup object, using the LXML processor (for better performance)
    adPage = BeautifulSoup(requests.get(ad).content, 'lxml')
    try:  # OLX page structure
        title = adPage.select('h1.css-r9zjja-Text.eu5v0x0')[0].text
        description = adPage.select('div.css-g5mtbi-Text')[0].text
        filters(ad, title, description)
    except:  # 'Storia' page structure
        title = adPage.select('h1.css-11kn46p.eu6swcv19')[0].text
        description = adPage.select('section.css-1vfwbw8.e1r1048u3')[0]
        description = description.find(class_='e1r1048u1').text
        filters(ad, title, description)


print('Crawling and filtering initiated.')
time.sleep(1)
print('The process is expected to take a few minutes.')
time.sleep(1)
print('Please wait...')

for page in pages:
    # request.get(URL).content returns the html file of the URL link, which is then transformed
    # into a BeautifulSoup object, using the LXML processor (for better performance)
    links = BeautifulSoup(requests.get(page).content, 'lxml')
    # 'ads' contains all '<a>' tags which have a 'href' attribute linking pages which begin with either of the two link formats
    ads = links.find_all('a', attrs={'href': re.compile('^https://www.storia.ro/ro/oferta/|^https://www.olx.ro/d/oferta')})
    # at this point, ads contains a list of BeautifulSoup objects
    # to extract the attribute info (ad links), ['href'] is performed on said objects
    ads = [ad['href'] for ad in ads]
    # set() removes duplicate ad links;
    # list() turns the set back into a list;
    # [5:] because the first 5 ads are always promoted (and can show up on other ad-listing pages)
    ads = list(set(ads))[5:]

    # spawning threads for each ad URL found on current ad-listing page (improves performance by 12 times)
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(ads)) as executor:
        executor.map(adScraper, ads)

print('Done!')
time.sleep(1)

print(f'\nApartments - {len(apartments)} result(s):\n')
time.sleep(2)
for apartment in apartments:
    print(f'\t{apartment}')

print(f'\nSingle Rooms - {len(singleRooms)} result(s):\n')
time.sleep(2)
for singleRoom in singleRooms:
    print(f'\t{singleRoom}')

print(f'\nHouses - {len(houses)} result(s):\n')
time.sleep(2)
for house in houses:
    print(f'\t{house}')

print(f'\nLand - {len(land)} result(s):\n')
time.sleep(2)
for pieceOfLand in land:
    print(f'\t{pieceOfLand}')