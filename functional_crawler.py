import sys

import requests
from bs4 import BeautifulSoup


# ------------------- start of functional crawler ------------------

def get_page(url, start=0):
    try:
        response = requests.get(url + str(start))
    except:
        return None
    print(response.status_code, response.url)
    return response


def find_links(html_doc):
    soup = BeautifulSoup(html_doc, features='html.parser')

    return soup.find_all('a', attrs={'class': 'result-title hdrlnk'})


def start_crawl_city(url):
    start_page = 0
    crawl = True
    adv_links = list()
    while crawl:
        res = get_page(url, start_page)
        print(res)
        new_links = find_links(res.text)
        adv_links.extend(new_links)
        start_page += 120
        crawl = bool(len(new_links))
    # for lnk in links:
    #     print(lnk.get('href'))
    return adv_links


def start_crawl():
    cities = ['paris', 'berlin', 'amsterdam', 'munich']
    link = 'https://{}.craigslist.org/search/hhh?availabilityMode=0&' \
           'sale_date=all+data&s='
    for city in cities:
        links = start_crawl_city(link.format(city))
        print(f'{city}total:', len(links))


def get_page_data():
    raise NotImplementedError


# ------------------- end of functional crawler ------------------

if __name__ == '__main__':
    switch = sys.argv[1]
    if switch == 'find_links':
        start_crawl()
    elif switch == 'extract_pages':
        get_page_data()
