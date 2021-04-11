import json
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup

from config import BASE_LINK, STORAGE_TYPE
from parser import AdvertisementPageParser
from storage import MongoStorage, FileStorage


class CrawlerBase(ABC):
    def __init__(self):
        self.storage = self.__set_storage()

    @abstractmethod
    def start(self, store=False):
        pass

    @staticmethod
    def __set_storage():
        if STORAGE_TYPE == 'mongo':
            return MongoStorage()
        return FileStorage()

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
        super().__init__()
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
            self.store(
                [{"url": li.get('href'), 'flag': False} for li in adv_links])
        return adv_links

    def store(self, data, *args):
        self.storage.store(data, 'advertisements_links')


class DataCrawler(CrawlerBase):

    def __init__(self):
        super().__init__()
        self.links = self.__load_links()
        self.parser = AdvertisementPageParser()

    def __load_links(self):
        return self.storage.load('advertisements_links', {'flag': False})

    def start(self, store=False):
        for link in self.links:
            response = self.get(link['url'])
            data = self.parser.parse(response.text)
            if store:
                self.store(data=data, filename=data.get('post_id', 'sample'))
            self.storage.update_flag(link)

    def store(self, data, filename=None):
        self.storage.store(data, 'advertisements_data')
        print(data['post_id'])


class ImageDownloader(CrawlerBase):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.advertisements = self.__load_advertisements()

    def __load_advertisements(self):
        return self.storage.load('advertisements_data')

    @staticmethod
    def get(link):
        try:
            response = requests.get(link, stream=True)
        except requests.HTTPError:
            return None
        return response

    def start(self, store=True):
        for advertisement in self.advertisements:
            counter = 1
            for image in advertisement['images']:
                response = self.get(image['url'])
                if store:
                    self.store(response, advertisement['post_id'], counter)
                counter += 1

    def store(self, data, adv_id, image_number):
        filename = f'{adv_id}-{image_number}'
        return self.save_to_disk(data, filename)

    def save_to_disk(self, response, filename):
        with open(f'data/images/{filename}.jpg', 'ab') as f:
            f.write(response.content)
            for _ in response.iter_content():
                f.write(response.content)

        print(filename)
        return filename
