from flask import Flask, render_template, url_for

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/Motivation')
def motivation():
    return render_template("motivation.html")


@app.route('/Login')
def login():
    return render_template("login.html")

@app.route('/Advices')
def advices():
    return render_template("advices.html")

@app.route('/Bored')
def bored():
    return render_template("bored.html")

if __name__ == '__main__':
    app.run()
