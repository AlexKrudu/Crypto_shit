import pymongo


client = pymongo.MongoClient("localhost", 27017)

coin = client.database.coins
log = client.database.logs


