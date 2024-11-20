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
        email = request.form['email']
        profile_type = request.form.get('profile_type')
        musician_role = request.form.get('musician_role') if profile_type == 'musician' else None
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name', None)
        band_name = request.form.get('band_name', None)
        address = request.form.get('address', None)
        phone_number = request.form.get('phone_number', None)
        bio = request.form.get('bio', None)

        # Data type conversions
        try:
            age = int(request.form.get('age', 0)) if musician_role == 'soloist' else None
            num_members = int(request.form.get('num_members', 0)) if musician_role == 'band' else None
            seating_capacity = int(request.form.get('seating_capacity', 0)) if profile_type == 'venue' else None
        except ValueError:
            flash("Invalid numeric value for one of the fields.", "error")
            return redirect(url_for('main.register'))

        # Check if email already exists
        if Profile.query.filter_by(email=email).first() is None:
            new_user = Profile(
                email=email,
                first_name=first_name,
                last_name=last_name,
                band_name=band_name,
                address=address,
                phone_number=phone_number,
                bio=bio,
                profile_type=profile_type,
                musician_type=musician_role
            )
            db.session.add(new_user)
            db.session.commit()

            # Add musician-specific or venue-specific records
            if profile_type == 'musician':
                musician = Musician(profile_id=new_user.profile_id)
                db.session.add(musician)
                if musician_role == 'soloist':
                    soloist = Soloist(profile_id=new_user.profile_id, age=age)
                    db.session.add(soloist)
                elif musician_role == 'band':
                    band_member = BandMember(profile_id=new_user.profile_id, num_members_in_band=num_members)
                    db.session.add(band_member)
            elif profile_type == 'venue':
                venue = Venue(profile_id=new_user.profile_id, seating_capacity=seating_capacity)
                db.session.add(venue)

            db.session.commit()

            # Save user session and redirect to upload picture
            session['user_id'] = new_user.profile_id
            session['profile_type'] = new_user.profile_type
            flash("Registration successful! Please upload your profile picture.", "success")
            return redirect(url_for('main.upload_picture'))

        flash("Email already registered. Please use a different email.", "error")
        return redirect(url_for('main.register'))

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
    flash("You have been logged out.", "success")
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


@main.route('/upload_picture', methods=['GET', 'POST'])
def upload_picture():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Redirect to login if user isn't logged in

    if request.method == 'POST':
        # Handle the case where a picture is uploaded
        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            if profile_picture:
                user = Profile.query.get(session['user_id'])
                user.profile_picture = profile_picture.read()  # Save the binary data
                db.session.commit()
                flash("Profile picture uploaded successfully!", "success")
        
        # Redirect to the appropriate dashboard after uploading or skipping
        if session.get('profile_type') == 'musician':
            return redirect(url_for('main.website'))
        else:
            return redirect(url_for('main.website'))

    return render_template('upload_picture.html')

