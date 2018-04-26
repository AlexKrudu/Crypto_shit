from flask import Flask
from flask import render_template, request
from hashlib import md5
from datetime import datetime
import db

app = Flask(__name__)


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

        if not db.check_exists(rest):
            error = False

        if error:
            db.coin.insert_one(
                {
                    "string": rest,
                    "time": datetime.utcnow(),
                    "user": uid,
                }
            )
        result.append((h, error))
        print(list(db.coin.find()))

    return result

@app.route("/", methods=["GET", "POST"])
def index():
    result = []
    if request.method == "POST":
        hashes = request.form["hashes"].strip().split()
        result = check_hashes(hashes)


    # Сделать функцию check_hashes

    return render_template("index.html", res=result)

@app.route("/wallet", methods=["GET", "POST"])
def wallet():
    score = 0
    if request.method == "POST":
        id = request.form["id"].strip()
        score = db.calculate(id)

    return render_template("wallet.html", score = score)

@app.route("/pay", methods=["GET", "POST"])
def pay():
    result = ""
    if request.method == "POST":
        sender = request.form["id_send"].strip()
        amount = request.form["amount"].strip()
        getter = request.form["id_get"].strip()
        if not sender or not amount or not getter:
            result = "Заполните все поля ввода"

        if sender == getter and not result:
            result = "Нельзя отправлять монеты самому себе"

        try:
            amount = int(amount)
        except ValueError:
            amount = 0
            result = "Некорректная сумма"

        if not result and amount <= 0:
            result = "Некорректная сумма"

        result = db.handle_transaction(sender, getter, amount, datetime.utcnow())

    return render_template("pay.html", res=result)

@app.route("/top", methods=["GET"])
def top():
    return render_template("top.html", res = db.build_top())




if __name__ == "__main__":
    app.run(port=8080,host="localhost")
    print("Smth")