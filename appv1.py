from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
import os
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16)

@app.route("/")
def home():
    return render_template('login.html')

@app.route("/create")
def create():
    con = sqlite3.connect("messenger.db")
    cur = con.cursor()
    try:
        cur.execute(""" CREATE TABLE messages(
            		sender VARCHAR(20) NOT NULL,
	    		receiver VARCHAR(20) NOT NULL,
            		msg VARCHAR(20) NOT NULL)
                    """)
    except sqlite3.OperationalError as e:
        return str(e)
    return "table created"

@app.route('/insert')
def insert():
    con = sqlite3.connect('messenger.db')
    cur = con.cursor()
    cur.execute(""" INSERT INTO users (username, password)
                    VALUES ("bob", "123")
                """)
    con.commit()
    return 'INSERT'

@app.route('/login', methods=['POST'])
def login():
    con = sqlite3.connect('messenger.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM Users WHERE Username=? AND Password=?",
			(request.form['un'],request.form['pw']))
    result = cur.fetchall()
    if len(result) == 0:
        return 'username / password not recognised'
    else:
        session.permanent = True
        session['username'] = request.form['un']
        return redirect(url_for('inbox'))

@app.route('/inbox')
def inbox():
    con = sqlite3.connect('messenger.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM messages WHERE receiver=? OR sender=?", (session['username'],session['username']))
    rows = cur.fetchall()
    return render_template('inbox.html', user=session['username'] , msgs=rows)

@app.route('/outbox')
def outbox():
    return render_template('send.html')

@app.route('/send', methods=['POST'])
def send():
    con = sqlite3.connect('messenger.db')
    cur = con.cursor()
    cur.execute("INSERT INTO messages (sender, receiver, msg) VALUES (?,?,?)",
			(session['username'],request.form['to'],request.form['msg']))
    con.commit()
    return redirect(url_for('inbox'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))
