from flask import Flask
import os
from flask import render_template, request, send_from_directory
from datetime import datetime
import db

app = Flask(__name__)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/", methods=["GET", "POST"])
def index():
    result = []
    if request.method == "POST":
        hashes = request.form["hashes"].strip().split()
        result = db.check_hashes(hashes)

    return render_template("index.html", res=result)


@app.route("/wallet", methods=["GET", "POST"])
def wallet():
    score = 0
    if request.method == "POST":
        id = request.form["id"].strip()
        score = db.calculate(id)

    return render_template("wallet.html", score=score)


@app.route("/pay", methods=["GET", "POST"])
def pay():
    result = ""
    if request.method == "POST":
        sender = request.form["id_send"].strip()
        amount = request.form["amount"].strip()
        getter = request.form["id_get"].strip()
        result = db.handle_transaction(sender, getter, amount, datetime.utcnow())

    return render_template("pay.html", res=result)


@app.route("/top", methods=["GET"])
def top():
    return render_template("top.html", res=db.build_top())


if __name__ == "__main__":
    app.run(port=8080, host="localhost")
    print("Smth")
