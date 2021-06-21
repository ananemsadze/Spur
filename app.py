from flask import Flask, render_template, redirect, url_for, request, session
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

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


all_user_dict = {}
all_users = Users.query.all()
for un in all_users:
    all_user_dict[un.email] = un.username


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/Motivation')
def motivation():
    return render_template("motivation.html")


@app.route('/Login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        if email in all_user_dict.keys():
            session.permanent = True
            session['email'] = email
            session['username'] = all_user_dict[email]
            return redirect(url_for('home'))

    return render_template("login.html")


@app.route('/SignUp', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        repeat_password = request.form['repeatPassword']
        if(username not in all_user_dict.values() and email not in all_user_dict.keys()) and password == repeat_password:
            session.permanent = True
            session['email'] = email
            session['username'] = username
            user = Users(username=username, email=email)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('home'))
    return render_template("signup.html")


@app.route('/Advices')
def advices():
    return render_template("advices.html")


@app.route('/Bored')
def bored():
    return render_template("bored.html")


@app.route('/AboutUs')
def about():
    return render_template("aboutus.html")


@app.route('/MyProfile')
def profile():
    return render_template("myprofile.html")


@app.route('/signout')
def signout():
    session.pop('email')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
