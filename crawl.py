import json
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup

from config import BASE_LINK
from parser import AdvertisementPageParser


class CrawlerBase(ABC):

    @abstractmethod
    def start(self, store=False):
        pass

    @abstractmethod
    def store(self, data, filename=None):
        pass

    @staticmethod
    def get(link):
        try:
            response = requests.get(link)
        except requests.HTTPError:
            return None
        return response


class LinkCrawler(CrawlerBase):

    def __init__(self, cities, link=BASE_LINK):
        self.cities = cities
        self.link = link

    @staticmethod
    def find_links(html_doc):
        soup = BeautifulSoup(html_doc, features='html.parser')
        return soup.find_all('a', attrs={'class': 'result-title hdrlnk'})

    def start_crawl_city(self, url):
        start_page = 0
        crawl = True
        adv_links = list()
        while crawl:
            res = self.get(url + str(start_page))
            new_links = self.find_links(res.text)
            adv_links.extend(new_links)
            start_page += 120
            crawl = bool(len(new_links))
        # for lnk in links:
        #     print(lnk.get('href'))
        return adv_links

    def start(self, store=False):
        adv_links = list()
        for city in self.cities:
            links = self.start_crawl_city(self.link.format(city))
            print(f'{city}total:', len(links))
            adv_links.extend(links)
        if store:
            self.store([li.get('href') for li in adv_links])
        return adv_links

    def store(self, data, *args):
        with open('data/links.json', 'w') as f:
            """ change list to string"""
            f.write(json.dumps(data))


class DataCrawler(CrawlerBase):

    def __init__(self):
        self.links = self.__load_links()
        self.parser = AdvertisementPageParser()

    @staticmethod
    def __load_links():
        with open('data/links.json', 'r') as f:
            """ we should to load json data """
            links = json.loads(f.read())
        return links

    def start(self, store=False):
        for link in self.links:
            response = self.get(link)
            data = self.parser.parse(response.text)
            if store:
                self.store(data=data, filename=data.get('post_id', 'sample'))

    def store(self, data, filename):
        with open(f'data/adv/{filename}.json', 'w') as f:
            f.write(json.dumps(data))
        print(f'data/adv/{filename}.json')
