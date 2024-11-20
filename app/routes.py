from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from .models import db, Profile, Musician, Soloist, BandMember, Venue

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if 'user_id' in session:
        user = Profile.query.get(session['user_id'])
        return render_template('index.html', username=user.first_name)
    return render_template('index.html', username=None)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        profile_type = request.form.get('profile_type')
        musician_role = request.form.get('musician_role') if profile_type == 'musician' else None
        email = request.form['email']
        address = request.form['address']
        phone_number = request.form['phone_number']
        bio = request.form['bio']

        # For soloist
        artist_name = request.form.get('artist_name') if musician_role == 'soloist' else None
        first_name = request.form.get('first_name') if musician_role == 'soloist' else None
        last_name = request.form.get('last_name') if musician_role == 'soloist' else None

        # For band
        band_name = request.form.get('band_name') if musician_role == 'band' else None
        leader_first_name = request.form.get('leader_first_name') if musician_role == 'band' else None
        leader_last_name = request.form.get('leader_last_name') if musician_role == 'band' else None

        # For venue
        venue_name = request.form.get('venue_name') if profile_type == 'venue' else None
        owner_first_name = request.form.get('first_name') if profile_type == 'venue' else None
        owner_last_name = request.form.get('last_name') if profile_type == 'venue' else None

        # Ensure email is unique
        if Profile.query.filter_by(email=email).first():
            flash('Email is already registered.', 'error')
            return redirect(url_for('main.register'))

        # Create profile
        new_profile = Profile(
            email=email,
            address=address,
            phone_number=phone_number,
            bio=bio,
            profile_type=profile_type
        )

        if profile_type == 'musician':
            new_profile.musician_type = musician_role
            if musician_role == 'soloist':
                new_profile.first_name = first_name
                new_profile.last_name = last_name
            elif musician_role == 'band':
                new_profile.band_name = band_name
                new_profile.first_name = leader_first_name
                new_profile.last_name = leader_last_name
        elif profile_type == 'venue':
            new_profile.first_name = owner_first_name
            new_profile.last_name = owner_last_name

        db.session.add(new_profile)
        db.session.commit()

        # Add musician or venue details
        if profile_type == 'musician':
            musician = Musician(profile_id=new_profile.profile_id)
            db.session.add(musician)
            if musician_role == 'soloist':
                soloist = Soloist(profile_id=new_profile.profile_id, age=request.form.get('age'))
                db.session.add(soloist)
            elif musician_role == 'band':
                band_member = BandMember(profile_id=new_profile.profile_id, num_members_in_band=request.form.get('num_members'))
                db.session.add(band_member)
        elif profile_type == 'venue':
            venue = Venue(profile_id=new_profile.profile_id, seating_capacity=request.form.get('seating_capacity'))
            db.session.add(venue)

        db.session.commit()

        # Log in the user after successful registration
        session['user_id'] = new_profile.profile_id
        session['profile_type'] = new_profile.profile_type

        if profile_type == 'venue':
            return redirect(url_for('main.website'))
        else:
            return redirect(url_for('main.website'))

    return render_template('register.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        user = Profile.query.filter_by(email=email).first()

        if user:
            session['user_id'] = user.profile_id
            session['profile_type'] = user.profile_type

            if user.profile_type == 'venue':
                return redirect(url_for('main.website'))
            else:
                return redirect(url_for('main.website'))
        else:
            flash('Invalid email. Please try again.', 'error')
            return redirect(url_for('main.login'))

    return render_template('login.html')


@main.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('profile_type', None)
    return redirect(url_for('main.index'))


@main.route('/website')
def website():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user = Profile.query.get(session['user_id'])

    if user.profile_type == 'venue':
        musicians = Musician.query.all()
        return render_template('websitevenue.html', user=user, musicians=musicians)
    elif user.profile_type == 'musician':
        venues = Venue.query.all()
        return render_template('websitemusician.html', user=user, venues=venues)

    return redirect(url_for('main.index'))


