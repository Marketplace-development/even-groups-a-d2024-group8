# app/routes.py

from flask import Blueprint, request, redirect, url_for, render_template, session
from .models import db, Profile

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if 'user_id' in session:
        user = Profile.query.get(session['user_id'])
        return render_template('index.html', username=user.name)
    return render_template('index.html', username=None)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        if Profile.query.filter_by(name=username).first() is None:
            new_user = Profile(name=username)
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.profile_id
            return redirect(url_for('main.index'))
        return 'Username already registered'
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = Profile.query.filter_by(name=username).first()
        if user:
            session['user_id'] = user.profile_id
            return redirect(url_for('main.index'))
        return 'User not found'
    return render_template('login.html')

@main.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.index'))
