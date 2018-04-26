import pymongo


client = pymongo.MongoClient("localhost", 27017)

coin = client.database.coins
log = client.database.logs

def calculate(user_id):
    result = coin.find({"user": {"$eq": user_id}}).count()
    return result if result else "0"

