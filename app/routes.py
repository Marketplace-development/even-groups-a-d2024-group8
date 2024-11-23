from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from app.models import db, Profile, Musician, Soloist, Band, Venue  # Import db and models from app.models
import uuid
from datetime import datetime
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if 'user_id' in session:
        # Redirect to the main page if user is logged in
        return redirect(url_for('main.main_page'))
    # If not logged in, show the welcome page
    return render_template('index.html', username=None)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = None  # Initialize new_user to avoid linter warnings
        try:
            # Collect common form data
            email = request.form.get('email')
            profile_type = request.form.get('profile_type')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            country = request.form.get('country')
            city = request.form.get('city')
            street_name = request.form.get('street_name')
            house_number = request.form.get('house_number')
            phone_number = request.form.get('phone_number')
            bio = request.form.get('bio')

            # Validate required common fields
            if not email or not profile_type or not first_name or not last_name:
                flash("Please fill out all required fields.", "error")
                return redirect(url_for('main.register'))

            # Check if email is already registered
            existing_user = Profile.query.filter_by(email=email).first()
            if existing_user:
                flash("Email already registered. Please use a different email.", "error")
                return redirect(url_for('main.register'))

            # Create new user
            new_user = Profile(
                email=email,
                first_name=first_name,
                last_name=last_name,
                country=country,
                city=city,
                street_name=street_name,
                house_number=house_number,
                phone_number=phone_number,
                bio=bio,
                profile_type=profile_type
            )
            db.session.add(new_user)
            db.session.commit()

            # Add musician-specific or venue-specific data
            if profile_type == 'musician':
                musician_role = request.form.get('musician_role')
                genre = request.form.get('genre')
                price_per_hour = request.form.get('price_per_hour')
                link_to_songs = request.form.get('link_to_songs')
                equipment = request.form.get('equipment')

                # Validate musician-specific fields
                if not musician_role or price_per_hour is None or equipment is None:
                    flash("Please fill out all required musician fields.", "error")
                    return redirect(url_for('main.register'))

                has_equipment = equipment.lower() == 'yes'

                try:
                    price_per_hour = float(price_per_hour)
                except ValueError:
                    flash("Invalid price per hour.", "error")
                    return redirect(url_for('main.register'))

                # Create musician record
                musician = Musician(
                    profile_id=new_user.profile_id,
                    genre=genre,  # Genre is optional
                    price_per_hour=price_per_hour,
                    link_to_songs=link_to_songs,
                    equipment=has_equipment
                )
                db.session.add(musician)
                db.session.commit()

                # Create role-specific record
                if musician_role == 'soloist':
                    artist_name = request.form.get('artist_name')
                    date_of_birth = request.form.get('date_of_birth')

                    if not date_of_birth:
                        flash("Date of birth is required for soloists.", "error")
                        return redirect(url_for('main.register'))

                    try:
                        date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
                    except ValueError:
                        flash("Invalid date format for date of birth.", "error")
                        return redirect(url_for('main.register'))

                    soloist = Soloist(
                        profile_id=new_user.profile_id,
                        date_of_birth=date_of_birth,
                        artist_name=artist_name  # This can be None (optional)
                    )
                    db.session.add(soloist)
                elif musician_role == 'band':
                    band_name = request.form.get('band_name')
                    num_members_in_band = request.form.get('num_members_in_band')

                    if not band_name or not num_members_in_band:
                        flash("Band name and number of members are required for bands.", "error")
                        return redirect(url_for('main.register'))

                    try:
                        num_members_in_band = int(num_members_in_band)
                    except ValueError:
                        flash("Invalid number of members in band.", "error")
                        return redirect(url_for('main.register'))

                    band = Band(
                        profile_id=new_user.profile_id,
                        band_name=band_name,
                        num_members_in_band=num_members_in_band
                    )
                    db.session.add(band)
                else:
                    flash("Invalid musician role selected.", "error")
                    return redirect(url_for('main.register'))

                # Update the musician_type
                new_user.musician_type = musician_role
                db.session.commit()

            elif profile_type == 'venue':
                venue_name = request.form.get('venue_name')
                venue_style = request.form.get('venue_style', 'Not specified')

                # Validate venue-specific fields
                if not venue_name:
                    flash("Venue name is required.", "error")
                    return redirect(url_for('main.register'))

                venue = Venue(
                    profile_id=new_user.profile_id,
                    name_event=venue_name,
                    style=venue_style
                )
                db.session.add(venue)
                db.session.commit()
            else:
                flash("Invalid profile type selected.", "error")
                return redirect(url_for('main.register'))

            # Save session and redirect to upload_picture
            session['user_id'] = str(new_user.profile_id)
            session['profile_type'] = new_user.profile_type

            # Redirect to upload_picture
            flash("Registration successful! Please upload your profile picture.", "success")
            return redirect(url_for('main.upload_picture'))

        except IntegrityError as e:
            db.session.rollback()
            flash("This email has already been registered. Please use a different email.", "error")
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("A database error occurred. Please try again.", "error")
            print(f"SQLAlchemy error: {e}")  # This will print the error to your server logs, which can help in debugging.
        except Exception as e:
            db.session.rollback()
            flash(f"An unexpected error occurred: {str(e)}. Please try again.", "error")
            print(f"Unexpected error: {e}")  # Debugging line

    # Render registration page for GET request
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        user = Profile.query.filter_by(email=email).first()

        if user:
            session['user_id'] = str(user.profile_id)
            session['profile_type'] = user.profile_type

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
    # Redirect to the index which will take them to the login page if not logged in
    return redirect(url_for('main.index'))

@main.route('/website')
def website():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user_id = uuid.UUID(session['user_id'])
    user = Profile.query.get(user_id)

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
        return redirect(url_for('main.login'))

    user_id = uuid.UUID(session['user_id'])
    user = Profile.query.get(user_id)

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

        return redirect(url_for('main.website'))

    return render_template('upload_picture.html')

@main.route('/main_page')
def main_page():
    if 'user_id' not in session:
        # If user is not logged in, redirect to login page
        return redirect(url_for('main.login'))
    # If logged in, render the main page
    user_id = uuid.UUID(session['user_id'])
    user = Profile.query.get(user_id)
    return render_template('main_page.html', username=user.first_name)