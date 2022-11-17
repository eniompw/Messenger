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
        cur.execute(""" CREATE TABLE contacts(
            user VARCHAR(20) NOT NULL,
	        contact VARCHAR(20) NOT NULL)
                    """)
    except sqlite3.OperationalError as e:
        return str(e)
    return "table created"

@app.route('/insert')
def insert():
	con = sqlite3.connect('messenger.db')
	cur = con.cursor()
	cur.execute("""	INSERT INTO users (username, password)
                    VALUES ("bob", "123")
                """)
	con.commit()
	return 'INSERT'

@app.route('/login', methods=['POST'])
def login():
    con = sqlite3.connect('messenger.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?",
		            (request.form['un'],request.form['pw']))
    result = cur.fetchall()
    if len(result) == 0:
        return 'username / password not recognised'
    else:
        session.permanent = True
        session['username'] = request.form['un']
        session['chat'] = None
        return redirect(url_for('menu'))

@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    if request.method == 'GET':
        return render_template('contact.html')
    else:
        con = sqlite3.connect('messenger.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username=?",
            (request.form['usr'],))
        result = cur.fetchall()
        if len(result) == 0:
            return 'username not recognised'
        else:
            cur.execute("INSERT INTO contacts (user, contact) VALUES (?,?)",
                (session['username'],request.form['usr']))
            con.commit()
            return 'contact added'

@app.route('/outbox')
def outbox():
    con = sqlite3.connect('messenger.db')
    cur = con.cursor()
    cur.execute("SELECT contact FROM contacts WHERE user=?", (session['username'],))
    result = [item[0] for item in cur.fetchall()]
    return render_template('msgs.html', contacts=result)

@app.route('/send', methods=['POST'])
def send():
    con = sqlite3.connect('messenger.db')
    cur = con.cursor()
    cur.execute("INSERT INTO messages (sender, receiver, msg) VALUES (?,?,?)",
    	       		(session['username'],request.form['to'],request.form['msg']))
    con.commit()
    return redirect(url_for('outbox'))

@app.route('/getMsgs', methods=['GET'])
def getMsgs():
    session['chat'] = request.args.get("name")
    con = sqlite3.connect('messenger.db')
    cur = con.cursor()
    cur.execute("SELECT sender, msg FROM messages WHERE receiver=? OR sender=?", (session['username'],session['username']))
    rows = cur.fetchall()
    return rows

@app.route('/menu')
def menu():
    return render_template('menu.html', user=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('menu'))
