from flask import Flask, render_template, redirect, url_for, request, session, flash
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


# Database is created for the users, so the registered users are saved.
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(12), nullable=False)


# Database is created for the quotes, so saved ones would show on users' profile later.
class Quotes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    quote = db.Column(db.String(1200), unique=False, nullable=False)


db.create_all()

'''This function returns the users' dictionary where 
the email is the main key, value is another dictionary of username and password, where 
username is the key.'''


def get_all_user_dict():
    all_user_dict = {}

    all_users = Users.query.all()
    for un in all_users:
        all_user_dict[un.email] = {un.username: un.password}

    return all_user_dict


# This function returns the list of all the users' usernames who're registered.
def get_all_usernames():
    all_username = []
    for email in get_all_user_dict():
        username = list(get_all_user_dict()[email].keys())[0]
        all_username.append(username)

    return all_username


# At this point all the actions associated with the database are done.
# </ ------------------------------------------------------------------------------------------------------------------

# These are the static variables of APIs' urls and the keys required for searching quotes.
url_bored = "http://www.boredapi.com/api/activity/"
url_affirmation = "https://www.affirmations.dev/"
url_advice = "https://api.adviceslip.com/advice"

BORED = "activity"
AFFIRMATION = "affirmation"
ADVICE_ONE = "slip"
ADVICE_TWO = "advice"


# This function returns the quotes based on the url and key which are passed to the called function.
def api_service(url, key, second_key=None):
    r = requests.get(url)
    json_api = r.text
    dict_api = json.loads(json_api)
    if second_key is None:
        return dict_api[key]
    else:
        return dict_api[key][second_key]


# At this point all the actions associated with the APIs are done.
# </ ------------------------------------------------------------------------------------------------------------------

# This route is written for the home page.
@app.route('/')
def home():
    return render_template("index.html")


'''
This route is mainly written for function use, when the user saves the displayed quote, this function 
is called. string:quote - is for the quote, string:page - is for the page the user is on at the moment.
These parameters are passed in the current page's html file and the quote is saved in the Quotes database.
The return statement redirects on the same page, so the user stays on the same page and the new
quote is generated.
'''


@app.route('/addQuote/<string:quote>/<string:page>', methods=['POST'])
def addQuote(quote, page):
    quote = Quotes(username=session["username"], quote=quote)
    db.session.add(quote)
    db.session.commit()
    return redirect('/' + str(page))


'''
This route is mainly written for function use, when the user goes to their profile page,
they have the option to remove the saved quotes. When user clicks the 'SAVED' button quote is removed
from the database.  The removable quote is passed as the parameter.  This process is done in realtime, the 
user stays on the same page, the quote is removed.
'''


@app.route('/removeQuote/<string:quote>', methods=['POST'])
def removeQuote(quote):
    all_quotes = Quotes.query.all()
    for un in all_quotes:
        if un.username == session["username"] and un.quote == quote:
            db.session.delete(un)
            db.session.commit()

    return redirect('/Profile/' + session["username"])


# </ ------------------------------------------------------------------------------------------------------------------
'''
Previously written function api_service is called in these routes' functions so that
the quotes are generated from the APIs. If the session is empty these pages are not accessible. 
'''


@app.route('/Motivation', methods=['GET'])
def motivation():
    if session.get("username") is not None:
        quote = api_service(url_affirmation, AFFIRMATION)
        return render_template("motivation.html", quote=quote)
    else:
        return redirect(url_for('home'))


@app.route('/Advices', methods=['GET'])
def advices():
    if session.get("username") is not None:
        advice = api_service(url_advice, ADVICE_ONE, ADVICE_TWO)
        return render_template("advices.html", advice=advice)
    else:
        return redirect(url_for('home'))


@app.route('/Bored', methods=['GET'])
def bored():
    if session.get("username") is not None:
        quote = api_service(url_bored, BORED)
        return render_template("bored.html", quote=quote)
    else:
        return redirect(url_for('home'))


# </ ------------------------------------------------------------------------------------------------------------------

# This route is written for the about us page.
@app.route('/AboutUs')
def about():
    return render_template("aboutus.html")


# </ ------------------------------------------------------------------------------------------------------------------


# If session is not empty, these following pages are not accessible.


'''
Firstly, we get the list of usernames and dictionary of all the registered users, then we check
whether the session is empty or not, if the method is POST, the entered credentials are filled in the 
database, if the user already exists the flash message is displayed on the screen.
'''


@app.route('/SignUp', methods=['POST', 'GET'])
def register():
    all_username = get_all_usernames()
    all_user_dict = get_all_user_dict()
    if session.get("username") is None:
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            repeat_password = request.form['repeatPassword']
            if (username not in all_username and email not in all_user_dict.keys()) and password == repeat_password:
                session.permanent = True
                session['username'] = username
                user = Users(username=username, email=email, password=password)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('home'))
            elif email in all_user_dict.keys() or username in all_username:
                flash("User already exists")
                return redirect("/SignUp")
            else:
                flash("You made an error, retype the fields")
                return redirect("/SignUp")

        elif request.method == 'GET':
            return render_template("signup.html")
    else:
        return redirect(url_for('home'))


'''
Firstly, we get the dictionary of all the registered users, then we check
whether the session is empty or not, if the method is POST, we check whether
the user is already has an account or not. If not flash message is displayed. Otherwise, 
user logs in successfully. 
'''


@app.route('/Login', methods=['POST', 'GET'])
def login():
    if session.get("username") is None:
        all_user_dict = get_all_user_dict()

        if request.method == 'POST':
            email = request.form['email']
            if email in all_user_dict.keys():
                password = request.form["password"]
                if password == all_user_dict[email][list(all_user_dict[email])[0]]:
                    session.permanent = True
                    session['username'] = list(all_user_dict[email].keys())[0]
                    return redirect(url_for('home'))
                else:
                    flash("Wrong password")
                    return redirect("/Login")
            else:
                flash("Account doesn't exist")
                return redirect("/Login")
        return render_template("login.html")
    else:
        return redirect(url_for('home'))


# </ ------------------------------------------------------------------------------------------------------------------

''' 
The search takes the text from the request form of the search bar and checks if the user exists,
if not the user gets redirected on the home page, otherwise the user can visit the searched
user's profile.'''


@app.route('/Search', methods=['POST'])
def search():
    username = request.form['search']

    return redirect('/Profile/' + str(username))


'''
This route is for generated unique url for each user. It takes usernames and saved quotes,
it iterates in all_quotes and checks if the quotes' associated username matches the
any of the database's usernames, if not the user gets redirected to home page. If it matches,
it get redirected to registered user's Profile page.
'''


@app.route('/Profile/<username>')
def profile(username):
    all_username = get_all_usernames()
    all_quotes = Quotes.query.all()
    set_of_quotes = set()
    for un in all_quotes:
        if un.username == username:
            set_of_quotes.add(un.quote)
    if not username in all_username:
        return redirect("/")
    return render_template("myprofile.html", set_of_quotes=set_of_quotes, username=username)


# The user sign outs of the website. We username, to pop them from the session.


@app.route('/signout')
def signout():
    session.pop('username', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
