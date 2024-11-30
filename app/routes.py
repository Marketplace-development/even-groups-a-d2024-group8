from flask import Blueprint, request, redirect, url_for, render_template, session, flash, jsonify
from app.models import db, Profile, Musician, Soloist, Band, Venue, Booking, Review  # Import db and models from app.models
import uuid
from datetime import datetime
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import base64
import random
from datetime import datetime, timedelta

main = Blueprint('main', __name__)


@main.route('/')
def index():
    # Check if the user is logged in
    if 'user_id' in session:
        try:
            user_id = uuid.UUID(session['user_id'])
            user = Profile.query.get(user_id)

            # If the user exists, redirect to the main page
            if user:
                return redirect(url_for('main.main_page'))
        except Exception as e:
            # Clear invalid session data if there's an issue
            session.pop('user_id', None)

    # Render the index.html for guests
    return render_template('index.html')


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
                        artist_name=artist_name
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

                # Update musician type and commit
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

            # Redirect to upload_picture for both musicians and venues
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
            return redirect(url_for('main.register'))

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

    user = Profile.query.get(uuid.UUID(session['user_id']))

    if request.method == 'POST':
        if 'submit' in request.form:  # Submit button was pressed
            if 'profile_picture' in request.files and request.files['profile_picture'].filename != '':
                profile_picture = request.files['profile_picture']
                user.profile_picture = profile_picture.read()  # Save the image to the database
                db.session.commit()
                flash("Profile picture uploaded successfully!", "success")
            else:
                flash("No profile picture uploaded.", "error")
        elif 'skip' in request.form:  # Skip button was pressed
            flash("Skipped uploading profile picture.", "info")
        
        return redirect(url_for('main.main_page'))  # Redirect to the main page

    return render_template('upload_picture.html')

@main.route('/main_page')
def main_page():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user_id = uuid.UUID(session['user_id'])
    user = Profile.query.get(user_id)

    if user.profile_type == 'venue':
        # Show profiles of soloists and bands
        musician_profiles = db.session.query(Musician).join(Profile).order_by(db.func.random()).all()
        return render_template('main_page.html', user=user, profiles=musician_profiles)
    elif user.profile_type == 'musician':
        # Fetch bookings where the musician is the logged-in user and status is 'Requested'
        bookings = Booking.query.filter_by(musician_id=user_id, status='Requested').all()
        return render_template('main_page.html', user=user, bookings=bookings)
    else:
        return render_template('main_page.html', user=user)


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
def profile():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user_id = session['user_id']
    user = Profile.query.get(user_id)

    if not user:
        return redirect(url_for('main.main_page'))

    if user.profile_type == 'musician':
        if user.musician_type == 'soloist':
            return redirect(url_for('main.soloist_profile', user_id=user_id))
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
    user = Profile.query.get(user_id)
    band = Band.query.get(user_id)

    if not user or not band:
        flash("Profile not found", "error")
        return redirect(url_for('main.main_page'))

    # Update fields
    band.band_name = request.form.get('band_name', band.band_name)
    user.musician.genre = request.form.get('genre', user.musician.genre)
    user.musician.price_per_hour = request.form.get('price_per_hour', user.musician.price_per_hour)
    user.musician.link_to_songs = request.form.get('link_to_songs', user.musician.link_to_songs)
    user.musician.equipment = request.form.get('equipment', 'false') == 'true'
    user.bio = request.form.get('bio', user.bio)  # Added bio to be updated
    user.country = request.form.get('country', user.country)
    user.city = request.form.get('city', user.city)
    user.street_name = request.form.get('street_name', user.street_name)
    user.house_number = request.form.get('house_number', user.house_number)
    user.first_name = request.form.get('first_name', user.first_name)
    user.last_name = request.form.get('last_name', user.last_name)
    user.phone_number = request.form.get('phone_number', user.phone_number)
    user.email = request.form.get('email', user.email)

    # Handle profile picture
    if 'profile_picture' in request.files:
        profile_picture = request.files['profile_picture']
        if profile_picture:
            user.profile_picture = profile_picture.read()

    # Commit changes to the database
    db.session.commit()

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

@main.route('/soloist_profile/<user_id>')
def soloist_profile(user_id):
    # Fetch the user profile and soloist details
    user = Profile.query.get(user_id)
    soloist = Soloist.query.get(user_id)

    # Handle cases where the user or soloist is not found
    if not user or not soloist:
        flash("Soloist profile not found", "error")
        return redirect(url_for('main.main_page'))

    # Convert profile picture to Base64 if it exists
    profile_picture = None
    if user.profile_picture:
        profile_picture = base64.b64encode(user.profile_picture).decode('utf-8')

    # Render the soloist_profile.html template with necessary data
    return render_template('soloist_profile.html', user=user, soloist=soloist, profile_picture=profile_picture)


@main.route('/edit_soloist_profile/<user_id>')
def edit_soloist_profile(user_id):
    """
    Route to display the edit page for soloist profiles.
    """
    user = Profile.query.get(user_id)
    soloist = Soloist.query.get(user_id)

    if not user or not soloist:
        flash("Soloist profile not found", "error")
        return redirect(url_for('main.main_page'))

    # Convert profile picture to Base64 if it exists
    profile_picture = None
    if user.profile_picture:
        profile_picture = base64.b64encode(user.profile_picture).decode('utf-8')

    # Render edit_soloist_profile.html
    return render_template('edit_soloist_profile.html', user=user, soloist=soloist, profile_picture=profile_picture)


@main.route('/update_soloist_profile/<user_id>', methods=['POST'])
def update_soloist_profile(user_id):
    """
    Route to handle updating the soloist profile with consistent backend processing.
    """
    user = Profile.query.get(user_id)
    soloist = Soloist.query.get(user_id)

    # Handle cases where the user or soloist is not found
    if not user or not soloist:
        flash("Profile not found", "error")
        return redirect(url_for('main.main_page'))

    # Update soloist-specific fields
    soloist.artist_name = request.form.get('artist_name', soloist.artist_name)

    # Parse and validate the date of birth
    date_of_birth = request.form.get('date_of_birth')
    if date_of_birth:
        try:
            soloist.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format for Date of Birth. Please use YYYY-MM-DD.", "error")
            return redirect(url_for('main.edit_soloist_profile', user_id=user_id))

    # Update musician-specific fields
    musician = getattr(user, 'musician', None)
    if not musician:
        flash("Musician details are missing. Please contact support.", "error")
        return redirect(url_for('main.edit_soloist_profile', user_id=user.profile_id))

# Update musician-specific fields
    musician.genre = request.form.get('genre', musician.genre)  # Ensure form field name matches
    price_per_hour = request.form.get('price_per_hour', None)
    if price_per_hour:
        try:
            musician.price_per_hour = float(price_per_hour)  # Convert to float for numeric columns
        except ValueError:
            flash("Invalid value for Price per Hour. Please enter a valid number.", "error")
            return redirect(url_for('main.edit_soloist_profile', user_id=user.profile_id))
    musician.link_to_songs = request.form.get('link_to_songs', musician.link_to_songs)
    musician.equipment = request.form.get('equipment', 'false').lower() == 'true'  # Convert to boolean
    user.bio = request.form.get('bio', user.bio)
    user.country = request.form.get('country', user.country)
    user.city = request.form.get('city', user.city)
    user.street_name = request.form.get('street_name', user.street_name)
    user.house_number = request.form.get('house_number', user.house_number)
    user.first_name = request.form.get('first_name', user.first_name)
    user.last_name = request.form.get('last_name', user.last_name)
    user.phone_number = request.form.get('phone_number', user.phone_number)
    user.email = request.form.get('email', user.email)

    # Handle profile picture if uploaded
    if 'profile_picture' in request.files:
        profile_picture = request.files['profile_picture']
        if profile_picture:
            user.profile_picture = profile_picture.read()

    # Commit changes to the database
    db.session.commit()

    flash("Profile updated successfully!", "success")
    return redirect(url_for('main.soloist_profile', user_id=user_id))

from sqlalchemy.orm import aliased

@main.route('/search_profiles', methods=['POST'])
def search_profiles():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized access'}), 401

    data = request.get_json()
    user = Profile.query.get(uuid.UUID(session['user_id']))

    if not user:
        return jsonify({'error': 'User not found'}), 404

    if user.profile_type == 'venue':
        # Start the query with Musician joined with Profile
        query = db.session.query(Musician).join(Profile)

        # Create aliases for Soloist and Band models
        soloist_alias = aliased(Soloist)
        band_alias = aliased(Band)

        # Outer join to Soloist and Band
        query = query.outerjoin(soloist_alias, Musician.profile_id == soloist_alias.profile_id)
        query = query.outerjoin(band_alias, Musician.profile_id == band_alias.profile_id)

        # Initialize a flag to check if any filters are applied
        filters_applied = False

        # Filter by musician type if provided
        musician_type = data.get('musician_type')
        if musician_type:
            query = query.filter(Profile.musician_type == musician_type)
            filters_applied = True

        # Filter by first name or last name
        name = data.get('name')
        if name:
            name = f"%{name}%"
            query = query.filter(
                (Profile.first_name.ilike(name)) |
                (Profile.last_name.ilike(name))
            )
            filters_applied = True

        # Apply other filters
        city = data.get('city')
        if city:
            query = query.filter(Profile.city.ilike(f"%{city}%"))
            filters_applied = True

        style = data.get('style')
        if style:
            query = query.filter(Musician.genre == style)
            filters_applied = True

        max_price = data.get('max_price')
        if max_price:
            try:
                max_price_float = float(max_price)
                query = query.filter(Musician.price_per_hour <= max_price_float)
                filters_applied = True
            except ValueError:
                pass  # Ignore invalid price input

        equipment = data.get('equipment')
        if equipment:
            needs_equipment = equipment.lower() == 'yes'
            # If musician needs equipment, they do NOT have equipment
            query = query.filter(Musician.equipment != needs_equipment)
            filters_applied = True

        # Fetch results based on filters
        results = query.all()

        if not filters_applied:
            # No filters applied, show random profiles
            results = db.session.query(Musician).join(Profile).order_by(db.func.random()).limit(5).all()
        # Else, if filters are applied and results are empty, we return an empty list
        # This allows the frontend to display the "No Soloists Or Bands Satisfy Your Requirements" message

        # Prepare the results
        output = []
        for musician in results:
            profile = musician.profile
            artist_or_band_name = None
            if profile.musician_type == 'soloist' and musician.soloist:
                artist_or_band_name = musician.soloist.artist_name
            elif profile.musician_type == 'band' and musician.band:
                artist_or_band_name = musician.band.band_name
            else:
                artist_or_band_name = f"{profile.first_name} {profile.last_name}"

            output.append({
                'id': str(musician.profile_id),
                'name': artist_or_band_name,
                'details': f"Genre: {musician.genre}, Price: €{musician.price_per_hour}/hour",
            })

        return jsonify(output)

    # Handle other profile types if needed
    return jsonify([])  # Default empty result


@main.route('/profile/<user_id>')
def view_profile(user_id):
    user = Profile.query.get(uuid.UUID(user_id))

    if not user:
        flash("Profile not found", "error")
        return redirect(url_for('main.main_page'))

    logged_in_user_id = uuid.UUID(session['user_id'])
    is_own_profile = (logged_in_user_id == uuid.UUID(user_id))
    logged_in_user = Profile.query.get(logged_in_user_id)

    if user.profile_type == 'musician':
        # Show "Book Here" button only if the logged-in user is a venue and not viewing their own profile
        show_book_button = logged_in_user and logged_in_user.profile_type == 'venue' and not is_own_profile

        # Convert profile picture to Base64 if it exists
        profile_picture = None
        if user.profile_picture:
            profile_picture = base64.b64encode(user.profile_picture).decode('utf-8')

        if user.musician_type == 'soloist':
            # Fetch the soloist data
            soloist = Soloist.query.get(user.profile_id)
            return render_template(
                'soloist_profile.html',
                user=user,
                soloist=soloist,
                show_book_button=show_book_button,
                is_own_profile=is_own_profile,
                profile_picture=profile_picture
            )

        elif user.musician_type == 'band':
            # Fetch the band data
            band = Band.query.get(user.profile_id)
            return render_template(
                'band_profile.html',
                user=user,
                band=band,
                show_book_button=show_book_button,
                is_own_profile=is_own_profile,
                profile_picture=profile_picture
            )

    elif user.profile_type == 'venue':
        # For venues
        profile_picture = None
        if user.profile_picture:
            profile_picture = base64.b64encode(user.profile_picture).decode('utf-8')

        is_own_profile = (logged_in_user_id == uuid.UUID(user_id))
        return render_template(
            'venue_profile.html',
            user=user,
            venue=user.venue,
            is_own_profile=is_own_profile,
            profile_picture=profile_picture
        )

    flash("Invalid profile type", "error")
    return redirect(url_for('main.main_page'))

@main.route('/request_booking/<musician_id>', methods=['GET', 'POST'])
def request_booking(musician_id):
    if 'user_id' not in session:
        flash("You must be logged in to book a musician.", "error")
        return redirect(url_for('main.login'))

    logged_in_user_id = uuid.UUID(session['user_id'])
    logged_in_user = Profile.query.get(logged_in_user_id)

    if not logged_in_user or logged_in_user.profile_type != 'venue':
        flash("Only venues can request bookings.", "error")
        return redirect(url_for('main.main_page'))

    musician = Musician.query.get(uuid.UUID(musician_id))
    if not musician:
        flash("Musician not found.", "error")
        return redirect(url_for('main.main_page'))

    if request.method == 'POST':
        # Get form data
        date_booking_str = request.form.get('date_booking')
        duration_str = request.form.get('duration')  # Get the unified duration field

        print(f"Received form data: date_booking={date_booking_str}, duration={duration_str}")

        # Validate and parse form data
        try:
            # Parse date_booking
            date_booking = datetime.strptime(date_booking_str, '%Y-%m-%dT%H:%M')
            print(f"Parsed date_booking: {date_booking}")

            # Parse and validate duration
            if not duration_str or ':' not in duration_str:
                raise ValueError("Invalid duration format. Please use HH:MM.")

            hours, minutes = map(int, duration_str.split(':'))
            if hours < 0 or minutes < 0 or minutes >= 60:
                raise ValueError("Invalid duration values. Hours must be >= 0, and minutes between 0 and 59.")

            duration = timedelta(hours=hours, minutes=minutes)
            if duration.total_seconds() <= 0:
                raise ValueError("Duration must be greater than zero.")
            print(f"Duration validated: {duration}")

        except ValueError as e:
            print(f"ValueError: {e}")
            flash(str(e), "error")
            return redirect(url_for('main.request_booking', musician_id=musician_id))
        
        status = 'Requested'
        # Create a new booking with status 'Requested'
        new_booking = Booking(
            musician_id=uuid.UUID(musician_id),
            venue_id=logged_in_user_id,
            status=status,
            date_booking=date_booking,
            duration=duration,
            booked_by=logged_in_user_id,
            booked_in=logged_in_user_id
        )
        
        print(f"New booking object created: {new_booking}")

        try:
            print("Attempting to commit booking...")
            db.session.add(new_booking)
            db.session.commit()
            flash("Booking request sent successfully!", "success")
            print("Booking successfully committed.")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while requesting the booking: {e}", "error")
            print(f"Error during commit: {e}")

        return redirect(url_for('main.main_page'))

    else:
        # GET request, render booking.html
        print("Rendering booking.html")
        return render_template('booking.html', musician=musician)

# routes.py
@main.route('/respond_booking/<uuid:booking_id>', methods=['POST'])
def respond_booking(booking_id):
    if 'user_id' not in session:
        flash("You must be logged in to respond to bookings.", "error")
        return redirect(url_for('main.login'))

    user_id = uuid.UUID(session['user_id'])
    user = Profile.query.get(user_id)

    booking = Booking.query.get(booking_id)
    if not booking:
        flash("Booking not found.", "error")
        return redirect(url_for('main.main_page'))

    # Ensure that only the musician associated with the booking can respond
    if booking.musician_id != user_id:
        flash("You are not authorized to respond to this booking.", "error")
        return redirect(url_for('main.main_page'))

    # Get the response from the form
    response = request.form.get('response')
    if response not in ['Accepted', 'Denied']:
        flash("Invalid response.", "error")
        return redirect(url_for('main.main_page'))

    # Update the booking status
    try:
        booking.status = response
        db.session.commit()
        flash(f"Booking has been {response.lower()}.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while updating the booking: {e}", "error")

    return redirect(url_for('main.main_page'))

@main.route('/bookings')
def bookings():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user_id = uuid.UUID(session['user_id'])
    user = Profile.query.get(user_id)

    if user.profile_type == 'venue':
        # Get bookings requested by this venue
        bookings = Booking.query.filter_by(venue_id=user_id).order_by(Booking.date_booking.desc()).all()
        return render_template('mybooking.html', bookings=bookings, user=user)
    else:
        flash("Only venues can view this page.", "error")
        return redirect(url_for('main.main_page'))



@main.route('/recommended')
def recommended_page():
    return render_template('my_recommendations.html', username=Profile.first_name)

