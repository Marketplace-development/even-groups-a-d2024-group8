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
        try:
            # Collect form data
            email = request.form['email']
            profile_type = request.form.get('profile_type')
            musician_role = request.form.get('musician_role') if profile_type == 'musician' else None
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name', None)
            price_per_hour = float(request.form.get('price_per_hour', 0.0))
            genre = request.form.get('genre', None)

            # Check if email is already registered
            existing_user = Profile.query.filter_by(email=email).first()
            if existing_user:
                flash("Email already registered. Please use a different email.", "error")
                return redirect(url_for('main.register'))

            # Create and commit new Profile
            new_user = Profile(
                email=email,
                first_name=first_name,
                last_name=last_name,
                profile_type=profile_type,
                musician_type=musician_role
            )
            db.session.add(new_user)
            db.session.commit()

            # Add musician-specific data if needed
            if profile_type == 'musician':
                musician = Musician(profile_id=new_user.profile_id, genre=genre, price_per_hour=price_per_hour)
                db.session.add(musician)
                db.session.commit()

            # Save session and redirect
            session['user_id'] = new_user.profile_id
            session['profile_type'] = new_user.profile_type
            flash("Registration successful! Please upload your profile picture.", "success")
            return redirect(url_for('main.upload_picture'))

        except Exception as e:
            # Catch unexpected errors and rollback changes
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('main.register'))

    # Render registration page for GET request
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
        flash("You must be logged in to access this page.", "error")
        return redirect(url_for('main.login'))  # Redirect to login if user isn't logged in

    user = Profile.query.get(session['user_id'])

    if request.method == 'POST':
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            if profile_picture:
                user.profile_picture = profile_picture.read()  # Save the binary data
                db.session.commit()
                flash("Profile picture uploaded successfully!", "success")

        # Handle "Skip" action or after upload
        return redirect(url_for('main.website'))

    return render_template('upload_picture.html')
