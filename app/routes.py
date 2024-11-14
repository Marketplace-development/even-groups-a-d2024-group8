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
        profile_type = request.form.get('profile_type')  # Get profile type from form
        artist_type = request.form.get('artist_type') if profile_type == 'artist' else None  # Only get artist type if profile_type is "artist"
        name = request.form['name']
        address = request.form['address']
        email = request.form['email']
        phone_number = request.form['phone_number']
        bio = request.form['bio']
        profile_picture = request.files['profile_picture']

        # Check if username already exists
        if Profile.query.filter_by(name=username).first() is None:
            new_user = Profile(
                name=name,
                email=email,
                address=address,
                phone_number=phone_number,
                bio=bio,
                profile_picture=profile_picture.read() if profile_picture else None,
                profile_type=profile_type,
                artist_type=artist_type
            )
            db.session.add(new_user)
            db.session.commit()

            # If the profile type is 'artist', create an entry in Musician table
            if profile_type == 'artist':
                new_musician = Musician(profile_id=new_user.profile_id)
                db.session.add(new_musician)
                db.session.commit()

                # Add artist type specifics
                if artist_type == 'soloist':
                    new_soloist = Soloist(profile_id=new_user.profile_id, age=request.form['age'])
                    db.session.add(new_soloist)
                elif artist_type == 'band':
                    new_band_member = BandMember(profile_id=new_user.profile_id, num_members_in_band=request.form['num_members'])
                    db.session.add(new_band_member)
                db.session.commit()

            # If the profile type is 'venue', create an entry in Venue table
            elif profile_type == 'venue':
                new_venue = Venue(profile_id=new_user.profile_id, seating_capacity=request.form['seating_capacity'])
                db.session.add(new_venue)
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
