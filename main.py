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

        if not error:
            db.coin.insert_one(
                {
                    "string": rest,
                    "time": datetime.utcnow(),
                    "user": uid,
                }
            )
        result.append((h, error))


    return result

@app.route("/", methods=["GET", "POST"])
def index():
    result = []
    if request.method == "POST":
        hashes = request.form["hashes"].strip().split()
        result = check_hashes(hashes)


    # Сделать функцию check_hashes

    return render_template("index.html", res=result)

if __name__ == "__main__":
    app.run(port=8080,host="localhost")
    print("Smth")