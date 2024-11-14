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
        profile_type = request.form.get('profile_type')
        musician_type = request.form.get('musician_type') if profile_type == 'musician' else None
        first_name = request.form['first_name']
        last_name = request.form['last_name'] if 'last_name' in request.form else None
        band_name = request.form['band_name'] if 'band_name' in request.form else None
        email = request.form['email']
        address = request.form['address']
        phone_number = request.form['phone_number']
        bio = request.form['bio']
        profile_picture = request.files['profile_picture']

        # Check if username already exists
        if Profile.query.filter_by(username=username).first() is None:
            new_user = Profile(
                first_name=first_name,
                last_name=last_name,
                band_name=band_name,
                email=email,
                address=address,
                phone_number=phone_number,
                bio=bio,
                profile_picture=profile_picture.read() if profile_picture else None,  # Or save the image file path as needed
                profile_type=profile_type,
                musician_type=musician_type
            )
            db.session.add(new_user)
            db.session.commit()

            # If the profile type is 'musician', create an entry in Musician table
            if profile_type == 'musician':
                new_musician = Musician(profile_id=new_user.profile_id)
                db.session.add(new_musician)
                db.session.commit()

                if musician_type == 'soloist':
                    new_soloist = Soloist(profile_id=new_user.profile_id, age=request.form['age'])
                    db.session.add(new_soloist)
                elif musician_type == 'band':
                    new_band_member = BandMember(profile_id=new_user.profile_id, num_members_in_band=request.form['num_members'])
                    db.session.add(new_band_member)
                db.session.commit()

            elif profile_type == 'venue':
                new_venue = Venue(profile_id=new_user.profile_id, seating_capacity=request.form['seating_capacity'])
                db.session.add(new_venue)
                db.session.commit()

            session['user_id'] = new_user.profile_id
            session['username'] = new_user.username
            session['profile_type'] = new_user.profile_type 
             
            if profile_type == 'venue':
                return redirect(url_for('websitevenue'))
            else:
                return redirect(url_for('websitemusician'))

        return 'Username already registered'

    return render_template('register.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = Profile.query.filter_by(username=username).first()
        if user:
            session['user_id'] = user.profile_id
            session['username'] = user.username
            session['profile_type'] = user.profile_type  # 'venue' or 'musician'
            
            # Redirect based on profile type
            if user.profile_type == 'venue':
                return redirect(url_for('websitevenue'))
            else:
                return redirect(url_for('websitemusician'))
        else:
            flash('User not found', 'error')

    return render_template('login.html')

@main.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.index'))

@main.route('/website')
def website():
    # Check if the user is logged in
    if 'user_id' in session:
        user_id = session['user_id']
        user = Profile.query.filter_by(profile_id=user_id).first()

        if user:
            if user.profile_type == 'venue':
                # Venue user should see musician profiles
                musicians = Musician.query.all()  # Get all musicians
                return render_template('websitevenue.html', user=user, musicians=musicians)
            elif user.profile_type == 'musician':
                # Musician user should see venue profiles
                venues = Venue.query.all()  # Get all venues
                return render_template('websitemusician.html', user=user, venues=venues)
        else:
            return redirect(url_for('login'))  # Redirect to login if user not found
    else:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    
@main.route('/book_musician/<musician_id>')
def book_musician(musician_id):
    # Your booking logic for musicians here
    return f"Booking musician with ID: {musician_id}"

@main.route('/book_venue/<venue_id>')
def book_venue(venue_id):
    # Your booking logic for venues here
    return f"Booking venue with ID: {venue_id}"


