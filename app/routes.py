from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from app.models import db, Profile, Musician, Soloist, Band, Venue  # Import db and models from app.models
import uuid
from datetime import datetime
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import base64
main = Blueprint('main', __name__)


@main.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main.main_page'))  # Redirect to main page if already logged in
    return render_template('index.html')  # Show the index page if not logged in

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
            return redirect(url_for('main.main_page'))  # Redirect to main_page.html after login
        else:
            flash('Invalid email. Please try again.', 'error')
            return redirect(url_for('main.login'))
    return render_template('login.html')

@main.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_id', None)
    session.pop('profile_type', None)
    flash("You have been logged out.", "success")
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

    if request.method == 'POST':
        if 'profile_picture' in request.files and request.files['profile_picture'].filename != '':
            profile_picture = request.files['profile_picture']
            user = Profile.query.get(uuid.UUID(session['user_id']))
            user.profile_picture = profile_picture.read()
            db.session.commit()
            flash("Profile picture uploaded successfully!", "success")
        else:
            flash("No profile picture uploaded. Proceeding without it.", "info")
        return redirect(url_for('main.main_page'))  # Redirect to main_page.html after uploading
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

@main.route('/search_musicians', methods=['POST'])
def search_musicians():
    data = request.get_json()
    query = db.session.query(Musician)
    
    if data.get('musician_type'):
        query = query.filter(Musician.type == data['musician_type'])
    if data.get('city'):
        query = query.filter(Musician.city == data['city'])
    if data.get('style'):
        query = query.filter(Musician.style == data['style'])
    if data.get('rating'):
        query = query.filter(Musician.rating >= int(data['rating']))
    if data.get('max_price'):
        query = query.filter(Musician.price_per_hour <= float(data['max_price']))
    if 'equipment' in data:
        equipment_needed = True if data['equipment'] == 'Yes' else False
        query = query.filter(Musician.equipment_needed == equipment_needed)

    results = query.all()
    return jsonify([{
        'first_name': musician.first_name,
        'last_name': musician.last_name,
        'style': musician.style,
        'city': musician.city,
        'rating': musician.rating,
        'price_per_hour': musician.price_per_hour,
        'equipment_needed': musician.equipment_needed
    } for musician in results])


@main.route('/profile')
@main.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user_id = session['user_id']
    user = Profile.query.get(user_id)

    if not user:
        return redirect(url_for('main.main_page'))

    if user.profile_type == 'musician':
        if user.musician_type == 'soloist':
            return render_template('soloist_profile.html', user=user)
        elif user.musician_type == 'band':
            return redirect(url_for('main.band_profile', user_id=user_id))
    elif user.profile_type == 'venue':
        return redirect(url_for('main.venue_profile', user_id=user_id))

    return redirect(url_for('main.main_page'))

@main.route('/band_profile/<user_id>')
def band_profile(user_id):
    user = Profile.query.get(user_id)
    band = Band.query.get(user_id)

    # Convert profile picture to Base64 if it exists
    profile_picture = None
    if user and user.profile_picture:
        profile_picture = base64.b64encode(user.profile_picture).decode('utf-8')

    return render_template('band_profile.html', user=user, band=band, profile_picture=profile_picture)

    return render_template('venue_profile.html', user=user, venue=venue, profile_picture=profile_picture)
@main.route('/edit_band_profile/<user_id>')
def edit_band_profile(user_id):
    # Fetch user and band data
    user = Profile.query.get(user_id)
    band = Band.query.get(user_id)

    # Handle cases where the user or band is not found
    if not user or not band:
        flash("Profile not found", "error")
        return redirect(url_for('main.main_page'))

    # Convert the profile picture to Base64 if it exists
    profile_picture = None
    if user.profile_picture:
        profile_picture = base64.b64encode(user.profile_picture).decode('utf-8')

    # Render the edit_band_profile.html with all necessary data
    return render_template('edit_band_profile.html', user=user, band=band, profile_picture=profile_picture)


@main.route('/update_band_profile/<user_id>', methods=['POST'])
def update_band_profile(user_id):
    # Fetch user and band data
    user = Profile.query.get(user_id)
    band = Band.query.get(user_id)

    # Handle cases where the user or band is not found
    if not user or not band:
        flash("Profile not found", "error")
        return redirect(url_for('main.main_page'))

    # Update text fields from the form
    user.bio = request.form.get('bio', user.bio)
    user.musician.genre = request.form.get('genre', user.musician.genre)
    user.musician.price_per_hour = request.form.get('price_per_hour', user.musician.price_per_hour)
    user.musician.link_to_songs = request.form.get('link_to_songs', user.musician.link_to_songs)
    user.musician.equipment = request.form.get('equipment', 'false') == 'true'
    user.country = request.form.get('country', user.country)
    user.city = request.form.get('city', user.city)
    user.street_name = request.form.get('street_name', user.street_name)
    user.house_number = request.form.get('house_number', user.house_number)
    user.first_name = request.form.get('first_name', user.first_name)
    user.last_name = request.form.get('last_name', user.last_name)
    user.phone_number = request.form.get('phone_number', user.phone_number)
    user.email = request.form.get('email', user.email)

    # Update profile picture if a new one is uploaded
    if 'profile_picture' in request.files:
        profile_picture = request.files['profile_picture']
        if profile_picture:
            user.profile_picture = profile_picture.read()

    # Commit changes to the database
    db.session.commit()

    # Provide feedback and redirect to the updated profile page
    flash("Profile updated successfully!", "success")
    return redirect(url_for('main.band_profile', user_id=user_id))

@main.route('/venue_profile/<user_id>')
def venue_profile(user_id):
    user = Profile.query.get(user_id)
    venue = Venue.query.get(user_id)

    # Validate if user and venue exist
    if not user or not venue:
        flash("Venue profile not found", "error")
        return redirect(url_for('main.main_page'))

    # Convert profile picture to Base64 if it exists
    profile_picture = None
    if user.profile_picture:
        profile_picture = base64.b64encode(user.profile_picture).decode('utf-8')

    # Render the venue_profile template
    return render_template('venue_profile.html', user=user, venue=venue, profile_picture=profile_picture)


@main.route('/edit_venue_profile/<user_id>')
def edit_venue_profile(user_id):
    """
    Route to display the edit page for venue profiles.
    """
    user = Profile.query.get(user_id)
    venue = Venue.query.get(user_id)

    if not user or not venue:
        flash("Venue profile not found", "error")
        return redirect(url_for('main.main_page'))

    # Convert profile picture to Base64 if it exists
    profile_picture = None
    if user.profile_picture:
        profile_picture = base64.b64encode(user.profile_picture).decode('utf-8')

    # Render edit_venue_profile.html
    return render_template('edit_venue_profile.html', user=user, venue=venue, profile_picture=profile_picture)


@main.route('/update_venue_profile/<user_id>', methods=['POST'])
def update_venue_profile(user_id):
    # Fetch user and venue data
    user = Profile.query.get(user_id)
    venue = Venue.query.get(user_id)

    # Handle cases where the user or venue is not found
    if not user or not venue:
        flash("Profile not found", "error")
        return redirect(url_for('main.main_page'))

    # Update text fields from the form
    venue.style = request.form.get('venue_style', venue.style)  # Update style
    user.bio = request.form.get('bio', user.bio)
    user.country = request.form.get('country', user.country)
    user.city = request.form.get('city', user.city)
    user.street_name = request.form.get('street_name', user.street_name)
    user.house_number = request.form.get('house_number', user.house_number)
    user.first_name = request.form.get('first_name', user.first_name)
    user.last_name = request.form.get('last_name', user.last_name)
    user.phone_number = request.form.get('phone_number', user.phone_number)
    user.email = request.form.get('email', user.email)

    # Update profile picture if a new one is uploaded
    if 'profile_picture' in request.files:
        profile_picture = request.files['profile_picture']
        if profile_picture:
            user.profile_picture = profile_picture.read()

    # Commit changes to the database
    db.session.commit()

    # Provide feedback and redirect to the updated profile page
    flash("Profile updated successfully!", "success")
    return redirect(url_for('main.venue_profile', user_id=user_id))