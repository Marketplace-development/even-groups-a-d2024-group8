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

            # Add musician-specific or venue-specific data
            if profile_type == 'musician':
                musician = Musician(profile_id=new_user.profile_id, genre=genre, price_per_hour=price_per_hour)
                db.session.add(musician)
                if musician_role == 'soloist':
                    date_of_birth = request.form.get('date_of_birth')
                    if date_of_birth:
                        soloist = Soloist(profile_id=new_user.profile_id, date_of_birth=date_of_birth)
                        db.session.add(soloist)
                elif musician_role == 'band':
                    band_name = request.form.get('band_name')
                    if band_name:
                        band_member = BandMember(profile_id=new_user.profile_id)
                        db.session.add(band_member)

            elif profile_type == 'venue':
                venue_name = request.form.get('venue_name')
                venue_style = request.form.get('venue_style', 'Not specified')
                venue = Venue(profile_id=new_user.profile_id, name_event=venue_name, style=venue_style)
                db.session.add(venue)

            db.session.commit()

            # Save session and redirect to upload_picture
            session['user_id'] = new_user.profile_id
            session['profile_type'] = new_user.profile_type

            # Conditional redirection
            if profile_type == 'musician':
                if musician_role == 'soloist':
                    flash("Welcome, Soloist! Please upload your profile picture.", "success")
                elif musician_role == 'band':
                    flash("Welcome, Band! Please upload your profile picture.", "success")
            elif profile_type == 'venue':
                flash("Welcome, Venue! Please upload your profile picture.", "success")

            return redirect(url_for('main.upload_picture'))

        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {e}")  # Debugging line
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
        if 'profile_picture' in request.files and request.files['profile_picture'].filename != '':
            profile_picture = request.files['profile_picture']
            # Save the binary data to the user profile
            user.profile_picture = profile_picture.read()
            db.session.commit()
            flash("Profile picture uploaded successfully!", "success")
        else:
            # Handle the "Skip" action or empty upload
            flash("No profile picture uploaded. Proceeding without it.", "info")

        return redirect(url_for('main.website'))  # Redirect to main website after upload or skip

    return render_template('upload_picture.html')

