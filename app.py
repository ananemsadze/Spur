from flask import Flask, render_template, redirect, url_for, request, session
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
import requests
import json

app = Flask(__name__)
app.secret_key = "getYourLifeTogether"
app.permanent_session_lifetime = timedelta(days=2)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(12), nullable=False)

class Quotes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    quote = db.Column(db.String(1200), unique=False, nullable=False)

db.create_all()

def get_all_user_dict():
    all_user_dict = {}

    all_users = Users.query.all()
    for un in all_users:
        all_user_dict[un.email] = {un.username: un.password}

    return  all_user_dict

def get_all_usenames():
    all_username = []
    for email in get_all_user_dict():
        username = list(get_all_user_dict()[email].keys())[0]
        all_username.append(username)

    return all_username


# </ ------------------------------------------------------------------------------------------------------------------

url_bored = "http://www.boredapi.com/api/activity/"
url_affirmation = "https://www.affirmations.dev/"
url_advice = "https://api.adviceslip.com/advice"

BORED = "activity"
AFFIRMATION = "affirmation"
ADVICE_ONE = "slip"
ADVICE_TWO = "advice"

def api_service(url, key, second_key=None):
    r = requests.get(url)
    json_api = r.text
    dict_api = json.loads(json_api)
    if second_key is None:
        return dict_api[key]
    else:
        return dict_api[key][second_key]


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/addQuote/<string:quote>/<string:page>',methods=['POST'])
def addQuote(quote,page):
    quote = Quotes(username=session["username"],  quote=quote)
    db.session.add(quote)
    db.session.commit()
    return redirect('/'+str(page))

@app.route('/removeQuote/<string:quote>',methods=['POST'])
def removeQuote(quote):
    all_quotes = Quotes.query.all()
    for un in all_quotes:
        if un.username == session["username"] and un.quote == quote:
            db.session.delete(un)
            db.session.commit()

    return redirect('/Profile/'+session["username"])

@app.route('/Motivation',methods=['GET'])
def motivation():
    quote = api_service(url_affirmation, AFFIRMATION)
    return render_template("motivation.html", quote=quote)


@app.route('/Login', methods=['POST', 'GET'])
def login():
    all_user_dict = get_all_user_dict()

    if request.method == 'POST':
        email = request.form['email']
        if email in all_user_dict.keys():
            password = request.form["password"]
            if password == all_user_dict[email][list(all_user_dict[email])[0]]:
                session.permanent = True
                session['email'] = email

                session['username'] = list(all_user_dict[email].keys())[0]
                return redirect(url_for('home'))
            else:
                return redirect("/Login")
        else:
            return redirect("/Login")

    return render_template("login.html")


@app.route('/SignUp', methods=['POST', 'GET'])
def register():
    all_username = get_all_usenames()
    all_user_dict = get_all_user_dict()
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        repeat_password = request.form['repeatPassword']
        if(username not in all_username and email not in all_user_dict.keys()) and password == repeat_password:
            session.permanent = True
            session['email'] = email
            session['username'] = username
            user = Users(username=username, email=email,password=password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            return redirect("/SignUp")

    elif request.method == 'GET':
        return render_template("signup.html")


@app.route('/Advices',methods=['GET'])
def advices():
    advice = api_service(url_advice, ADVICE_ONE, ADVICE_TWO)
    return render_template("advices.html",advice=advice)


@app.route('/Bored',methods=['GET'])
def bored():
    quote = api_service(url_bored, BORED)
    return render_template("bored.html", quote=quote)


@app.route('/AboutUs')
def about():
    return render_template("aboutus.html")

@app.route('/Search',methods=['POST'])
def search():
    username = request.form['search']

    return redirect('/Profile/'+str(username))


@app.route('/Profile/<username>')
def profile(username):
    all_username = get_all_usenames()
    all_quotes = Quotes.query.all()
    set_of_quotes = set()
    for un in all_quotes:
        if un.username == username:
            set_of_quotes.add(un.quote)
    if not username in all_username:
        return redirect("/")
    return render_template("myprofile.html", set_of_quotes=set_of_quotes,username=username)


@app.route('/signout')
def signout():
    session.pop('email')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
