from pymongo import MongoClient


class MongoDatabase:
    _instance = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(*args,**kwargs)
        return cls._instance


    def __init__(self):
        self.client = MongoClient()
        self.database = self.client['crawler2']
