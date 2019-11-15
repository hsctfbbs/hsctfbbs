#!/usr/bin/env python
# coding: utf8
import sys
import logging
import os
from datetime import datetime, timedelta
from flask import Flask, request, session, redirect, url_for, render_template
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

admin_username = "hsctfadmin"
admin_password = "K~nQpqpHC2hA'K7h"

flag = "HSCTF{dummyflag}"
if os.path.exists('flag.txt'):
    with open("flag.txt") as f:
        flag = f.read()

db = SQLAlchemy()

class BBSUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    password = db.Column(db.String(64))

    def __init__(self, username, password, id=None):
        self.username = username
        self.password = password
        if id != None:
            self.id = id

class BBSThread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    userid = db.Column(db.Integer, default=-1)
    username = db.Column(db.String(64))
    date = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, title, creator):
        self.title = title
        self.userid = creator.id
        self.username = creator.username

class BBSMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    threadid = db.Column(db.Integer, default=-1)
    userid = db.Column(db.Integer, default=-1)
    username = db.Column(db.String(64))
    message = db.Column(db.String(1024))
    date = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, thread, user, message):
        self.threadid = thread.id
        self.userid = user.id
        self.message = message
        self.username = user.username

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/hsctfbbs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = 'sessions'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
#app.config[''] = ''
db.init_app(app)
app.app_context().push()
sess = Session()
sess.init_app(app)

if not os.path.exists('hsctfbbs.db'):
    db.create_all()

def get_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    if user_id == -1:
        return BBSUser(admin_username, "", -1)
    return BBSUser.query.filter_by(id=user_id).first()

@app.route('/', methods=['GET'])
def index():
    user = get_user()
    if not user:
        return redirect(url_for('login'))
    
    threads = BBSThread.query.order_by(BBSThread.date.desc()).all()
    return render_template('index.html', threads=threads, username=user.username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if "username" in request.form and "password" in request.form:
            username = request.form["username"]
            password = request.form["password"]
            if admin_username == username and admin_password == password:
                session["user_id"] = -1
                return redirect(url_for('index'))
            user = BBSUser.query.filter_by(username=username).first()
            if user and user.username == username and user.password == password:
                session["user_id"] = user.id
                return redirect(url_for('index'))
        return render_template('login.html', message='failed to login...')
    return render_template('login.html', message='')

@app.route('/logout', methods=['GET'])
def logout():
    if get_user():
        session.pop('user_id')
    return redirect(url_for('index'))

@app.route('/thread/<int:thread_id>', methods=['GET'])
def get_thread(thread_id):
    user = get_user()
    if not user:
        return redirect(url_for('login'))
    
    thread = BBSThread.query.filter_by(id = thread_id).first()
    if not thread:
        return render_template('thread_not_found.html')
    
    messages = BBSMessage.query.filter_by(threadid = thread_id).order_by(BBSMessage.date)

    return render_template('thread.html', thread=thread, messages=messages, user=user)

@app.route('/post/<int:thread_id>', methods=['POST'])
def post_thread(thread_id):
    user = get_user()
    if not user:
        return redirect(url_for('login'))
    
    if not "message" in request.form:
        return render_template('post.html', message="failed", thread=None)
    
    thread = BBSThread.query.filter_by(id = thread_id).first()
    if not thread:
        return render_template('thread_not_found.html')
    
    message = BBSMessage(thread, user, request.form["message"])
    thread.date = datetime.now()
    db.session.add(message)
    db.session.commit()

    return render_template('post.html', message="success", thread=thread)

@app.route('/mkthread', methods=['POST'])
def mkthread():
    user = get_user()
    if not user:
        return redirect(url_for('login'))
    
    if "title" in request.form:
        title = request.form["title"]
        thread = BBSThread(title, user)
        db.session.add(thread)
        db.session.commit()
        return render_template('mkthread.html', message='success', thread=thread)
        
    return render_template('mkthread.html', message='failed', thread=None)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if "username" in request.form and "password" in request.form:
            username = request.form["username"]
            password = request.form["password"]
            if admin_username == username:
                return render_template('register.html', message='failed (already exist)', form=True)
            if BBSUser.query.filter_by(username=username).first():
                return render_template('register.html', message='failed (already exist)', form=True)
            user = BBSUser(username, password)
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            return render_template('register.html', message='success', form=False)
        return render_template('register.html', message='failed', form=True)
    else:
        return render_template('register.html', message='', form=True)

@app.route('/profile', methods=['GET'])
def myprofile():
    user = get_user()
    if not user:
        return redirect(url_for('login'))
    
    return render_template('profile.html', user=user, flag=flag)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3333, debug=True)
