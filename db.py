import pymongo
import requests
from hashlib import md5
from datetime import datetime


client = pymongo.MongoClient("localhost", 27017)

coin = client.database.coins
log = client.database.logs


def calculate(user_id):
    result = coin.find({"user": {"$eq": user_id}}).count()
    return result if result else False


def check_exists(rest):
    if coin.find_one({"string": {"$eq": rest}}) is None:
        return True

    return False


def handle_transaction(sender, getter, amount, time):
    if not sender or not amount or not getter:
        return "Убедитесь в корректности введенных данных"

    if sender == getter:
        return "Нельзя отправлять монеты самому себе"
    if amount <= 0:
        return "Некорректная сумма"
    if coin.find({"user": {"$eq": sender}}).count() < amount:
        return "Недостаточно средств!"

    coins_id = [i["_id"] for i in coin.find({"user": {"$eq": sender}})[:amount]]

    for i in coins_id:
        coin.update({"_id": i}, {"$set": {"user": getter}})

        log.insert_one(
            {
                "coin": i,
                "from": sender,
                "to": getter,
                "time": time
            })

    return "Перевод успешно состоялся!"


def get_vk_name(id):
    server = "https://api.vk.com/method/users.get"
    params = {"user_ids": str(id),
              "v": "5.74"}
    try:
        answer = requests.get(server, params=params).json()["response"][0]
        return " ".join((answer["first_name"], answer["last_name"]))
    except:
        return "Не удалось найти информацию"


def build_top(num):
    res = coin.aggregate([{'$group': {'_id': '$user', 'total': {'$sum': 1}}}, {'$sort': {'total': -1}}])
    res = list(res)[:num]
    return [(get_vk_name(res[i]["_id"]), res[i]["total"]) for i in range(len(res))]


def check_hashes(hashes):
    result = []
    error = True
    uid = ""
    rest = ""
    for h in hashes:
        if md5(h.encode('utf8')).hexdigest()[:5] == '00000':  # нашли хеш (здесь проверка для 4-х нулей)
            try:
                uid, rest = h.split('-', maxsplit=1)
            except Exception:
                error = False
            if not uid.isdigit():
                error = False
        else:
            error = False

        if not check_exists(rest):
            error = False

        if error:
            coin.insert_one(
                {
                    "string": rest,
                    "time": datetime.utcnow(),
                    "user": uid,
                }
            )
        result.append((h, error))
        print(list(coin.find()))

    return result
