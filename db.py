import pymongo


client = pymongo.MongoClient("localhost", 27017)

coin = client.database.coins
log = client.database.logs


def calculate(user_id):
    result = coin.find({"user": {"$eq": user_id}}).count()
    return result if result else "0"


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




