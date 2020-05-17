from collections import defaultdict

from pymongo import MongoClient
client = MongoClient('localhost', 27017)

db = client['bot-test-database']
collection = db['bot-test-collection']

MAX_NAME_LENGTH = 25

jobs = defaultdict(list)