from flask import Blueprint, request, redirect, url_for, render_template, session, flash, jsonify
from app.models import db, Profile, Musician, Soloist, Band, Venue, Booking, Review, Payment  # Import db and models from app.models
import uuid
from datetime import datetime
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import base64
import random
from datetime import datetime, timedelta
from app import db
from sqlalchemy import func
from decimal import Decimal

main = Blueprint('main', __name__)


@main.route('/')
def index():
    if 'user_id' in session:
        try:
            user_id = uuid.UUID(session['user_id'])
            user = Profile.query.get(user_id)

            if user:
                return redirect(url_for('main.main_page'))
        except Exception as e:
            session.pop('user_id', None)

    return render_template('index.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = None  
        try:
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

            if not email or not profile_type or not first_name or not last_name:
                flash("Please fill out all required fields.", "error")
                return redirect(url_for('main.register'))

            existing_user = Profile.query.filter_by(email=email).first()
            if existing_user:
                flash("Email already registered. Please use a different email.", "error")
                return redirect(url_for('main.register'))

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

            if profile_type == 'musician':
                musician_role = request.form.get('musician_role')
                genre = request.form.get('genre')
                price_per_hour = request.form.get('price_per_hour')
                link_to_songs = request.form.get('link_to_songs')
                equipment = request.form.get('equipment')

                if not musician_role or price_per_hour is None or equipment is None:
                    flash("Please fill out all required musician fields.", "error")
                    return redirect(url_for('main.register'))

                has_equipment = equipment.lower() == 'yes'

                try:
                    price_per_hour = float(price_per_hour)
                except ValueError:
                    flash("Invalid price per hour.", "error")
                    return redirect(url_for('main.register'))

                musician = Musician(
                    profile_id=new_user.profile_id,
                    genre=genre,
                    price_per_hour=price_per_hour,
                    link_to_songs=link_to_songs,
                    equipment=has_equipment
                )
                db.session.add(musician)
                db.session.commit()

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

                new_user.musician_type = musician_role
                db.session.commit()

            elif profile_type == 'venue':
                venue_name = request.form.get('venue_name')
                venue_style = request.form.get('venue_style', 'Not specified')

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

            session['user_id'] = str(new_user.profile_id)
            session['profile_type'] = new_user.profile_type

            flash("Registration successful! Please upload your profile picture.", "success")
            return redirect(url_for('main.upload_picture'))

        except IntegrityError as e:
            db.session.rollback()
            flash("This email has already been registered. Please use a different email.", "error")
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("A database error occurred. Please try again.", "error")
            print(f"SQLAlchemy error: {e}")  
        except Exception as e:
            db.session.rollback()
            flash(f"An unexpected error occurred: {str(e)}. Please try again.", "error")
            print(f"Unexpected error: {e}")
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
            return redirect(url_for('main.main_page'))  
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
        if 'submit' in request.form:  
            if 'profile_picture' in request.files and request.files['profile_picture'].filename != '':
                profile_picture = request.files['profile_picture']
                user.profile_picture = profile_picture.read() 
                db.session.commit()
                flash("Profile picture uploaded successfully!", "success")
                return redirect(url_for('main.main_page')) 
            else:
                flash("No profile picture uploaded.", "error")
                return render_template('upload_picture.html')
        elif 'skip' in request.form:  
            flash("Skipped uploading profile picture.", "info")
            return redirect(url_for('main.main_page'))

    return render_template('upload_picture.html')

import base64

@main.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user_id = session['user_id']
    user = Profile.query.get(user_id)

    reviews_count = Review.query.filter_by(reviewee_id=user.profile_id).count()

    if not user:
        return redirect(url_for('main.main_page'))

    if user.profile_type == 'musician':
        if user.musician_type == 'soloist':
            return redirect(url_for('main.soloist_profile', user_id=user_id, reviews_count=reviews_count))
        elif user.musician_type == 'band':
            return redirect(url_for('main.band_profile', user_id=user_id, reviews_count=reviews_count))
    elif user.profile_type == 'venue':
        return redirect(url_for('main.venue_profile', user_id=user_id, reviews_count=reviews_count))

    return redirect(url_for('main.main_page'))


@main.route('/band_profile/<user_id>')
def band_profile(user_id):
    if 'user_id' not in session:
        flash("You must be logged in to view this page.", "error")
        return redirect(url_for('main.login'))

    logged_in_user_id = session['user_id']

    user = Profile.query.get(user_id)
    band = Band.query.get(user_id)

    reviews_count = Review.query.filter_by(reviewee_id=user.profile_id).count()

    
    if not user or not band:
        flash("Profile not found", "error")
        return redirect(url_for('main.main_page'))

    is_own_profile = (str(user_id) == logged_in_user_id)

    profile_picture = None
    if user.profile_picture:
        profile_picture = base64.b64encode(user.profile_picture).decode('utf-8')


    return render_template(
        'band_profile.html',
        user=user,
        band=band,
        profile_picture=profile_picture,
        is_own_profile=is_own_profile,
        reviews_count=reviews_count 
    )



@main.route('/edit_band_profile/<user_id>')
def edit_band_profile(user_id):
    user = Profile.query.get(user_id)
    band = Band.query.get(user_id)

    if not user or not band:
        flash("Profile not found", "error")
        return redirect(url_for('main.main_page'))

    profile_picture = None
    if user.profile_picture:
        profile_picture = base64.b64encode(user.profile_picture).decode('utf-8')

    return render_template('edit_band_profile.html', user=user, band=band, profile_picture=profile_picture)


@main.route('/update_band_profile/<user_id>', methods=['POST'])
def update_band_profile(user_id):
    user = Profile.query.get(user_id)
    band = Band.query.get(user_id)

    if not user or not band:
        flash("Profile not found", "error")
        return redirect(url_for('main.main_page'))


    band.band_name = request.form.get('band_name', band.band_name)
    num_members = request.form.get('num_members_in_band', band.num_members_in_band)
    try:
        band.num_members_in_band = int(num_members) if num_members else band.num_members_in_band
    except ValueError:
        flash("Invalid value for number of band members. Please enter a valid integer.", "error")
        return redirect(url_for('main.edit_band_profile', user_id=user_id))


    musician = getattr(user, 'musician', None)
    if musician:
        musician.genre = request.form.get('genre', musician.genre)
        price_per_hour = request.form.get('price_per_hour', None)
        if price_per_hour:
            try:
                musician.price_per_hour = float(price_per_hour)  
            except ValueError:
                flash("Invalid value for Price per Hour. Please enter a valid number.", "error")
                return redirect(url_for('main.edit_band_profile', user_id=user_id))
        musician.link_to_songs = request.form.get('link_to_songs', musician.link_to_songs)
        musician.equipment = request.form.get('equipment', 'false').lower() == 'true'

    user.bio = request.form.get('bio', user.bio)
    user.country = request.form.get('country', user.country)
    user.city = request.form.get('city', user.city)
    user.street_name = request.form.get('street_name', user.street_name)
    user.house_number = request.form.get('house_number', user.house_number)
    user.first_name = request.form.get('first_name', user.first_name)
    user.last_name = request.form.get('last_name', user.last_name)
    user.phone_number = request.form.get('phone_number', user.phone_number)
    user.email = request.form.get('email', user.email)

    if 'profile_picture' in request.files:
        profile_picture = request.files['profile_picture']
        if profile_picture:
            user.profile_picture = profile_picture.read()

    db.session.commit()

    flash("Profile updated successfully!", "success")
    return redirect(url_for('main.band_profile', user_id=user_id))


@main.route('/venue_profile/<user_id>')
def venue_profile(user_id):
    if 'user_id' not in session:
        flash("You must be logged in to view this page.", "error")
        return redirect(url_for('main.login'))

    logged_in_user_id = session['user_id']

    user = Profile.query.get(user_id)
    venue = Venue.query.get(user_id)

    reviews_count = Review.query.filter_by(reviewee_id=user.profile_id).count()

    if not user or not venue:
        flash("Venue profile not found", "error")
        return redirect(url_for('main.main_page'))

    is_own_profile = (str(user_id) == logged_in_user_id)

    profile_picture = None
    if user.profile_picture:
        profile_picture = base64.b64encode(user.profile_picture).decode('utf-8')

    return render_template(
        'venue_profile.html',
        user=user,
        venue=venue,
        profile_picture=profile_picture,
        is_own_profile=is_own_profile,
        reviews_count= reviews_count
    )



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


    profile_picture = None
    if user.profile_picture:
        profile_picture = base64.b64encode(user.profile_picture).decode('utf-8')


    return render_template('edit_venue_profile.html', user=user, venue=venue, profile_picture=profile_picture)


@main.route('/update_venue_profile/<user_id>', methods=['POST'])
def update_venue_profile(user_id):
    user = Profile.query.get(user_id)
    venue = Venue.query.get(user_id)

    if not user or not venue:
        flash("Profile not found", "error")
        return redirect(url_for('main.main_page'))

    venue.name_event = request.form.get('name_event', venue.name_event) 
    venue.style = request.form.get('venue_style', venue.style) 

    user.bio = request.form.get('bio', user.bio)
    user.country = request.form.get('country', user.country)
    user.city = request.form.get('city', user.city)
    user.street_name = request.form.get('street_name', user.street_name)
    user.house_number = request.form.get('house_number', user.house_number)
    user.first_name = request.form.get('first_name', user.first_name)
    user.last_name = request.form.get('last_name', user.last_name)
    user.phone_number = request.form.get('phone_number', user.phone_number)
    user.email = request.form.get('email', user.email)

    if 'profile_picture' in request.files:
        profile_picture = request.files['profile_picture']
        if profile_picture:
            user.profile_picture = profile_picture.read()

    db.session.commit()

    flash("Profile updated successfully!", "success")
    return redirect(url_for('main.venue_profile', user_id=user_id))


@main.route('/soloist_profile/<user_id>')
def soloist_profile(user_id):
    if 'user_id' not in session:
        flash("You must be logged in to view this page.", "error")
        return redirect(url_for('main.login'))

    logged_in_user_id = session['user_id']

    user = Profile.query.get(user_id)
    soloist = Soloist.query.get(user_id)

    reviews_count = Review.query.filter_by(reviewee_id=user.profile_id).count()

    if not user or not soloist:
        flash("Soloist profile not found", "error")
        return redirect(url_for('main.main_page'))

    is_own_profile = (str(user_id) == logged_in_user_id)

    show_book_button = (
        logged_in_user_id != user_id and 
        Profile.query.get(logged_in_user_id).profile_type == 'venue'
    )

    profile_picture = None
    if user.profile_picture:
        profile_picture = base64.b64encode(user.profile_picture).decode('utf-8')

    return render_template(
        'soloist_profile.html',
        user=user,
        soloist=soloist,
        profile_picture=profile_picture,
        is_own_profile=is_own_profile,
        show_book_button=show_book_button,
        reviews_count = reviews_count
    )


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

    profile_picture = None
    if user.profile_picture:
        profile_picture = base64.b64encode(user.profile_picture).decode('utf-8')

    return render_template('edit_soloist_profile.html', user=user, soloist=soloist, profile_picture=profile_picture)


@main.route('/update_soloist_profile/<user_id>', methods=['POST'])
def update_soloist_profile(user_id):
    """
    Route to handle updating the soloist profile with consistent backend processing.
    """
    user = Profile.query.get(user_id)
    soloist = Soloist.query.get(user_id)

    if not user or not soloist:
        flash("Profile not found", "error")
        return redirect(url_for('main.main_page'))

    soloist.artist_name = request.form.get('artist_name', soloist.artist_name)

    date_of_birth = request.form.get('date_of_birth')
    if date_of_birth:
        try:
            soloist.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format for Date of Birth. Please use YYYY-MM-DD.", "error")
            return redirect(url_for('main.edit_soloist_profile', user_id=user_id))

    musician = getattr(user, 'musician', None)
    if not musician:
        flash("Musician details are missing. Please contact support.", "error")
        return redirect(url_for('main.edit_soloist_profile', user_id=user.profile_id))

    musician.genre = request.form.get('genre', musician.genre) 
    price_per_hour = request.form.get('price_per_hour', None)
    if price_per_hour:
        try:
            musician.price_per_hour = float(price_per_hour)  
        except ValueError:
            flash("Invalid value for Price per Hour. Please enter a valid number.", "error")
            return redirect(url_for('main.edit_soloist_profile', user_id=user.profile_id))
    musician.link_to_songs = request.form.get('link_to_songs', musician.link_to_songs)
    musician.equipment = request.form.get('equipment', 'false').lower() == 'true' 
    user.bio = request.form.get('bio', user.bio)
    user.country = request.form.get('country', user.country)
    user.city = request.form.get('city', user.city)
    user.street_name = request.form.get('street_name', user.street_name)
    user.house_number = request.form.get('house_number', user.house_number)
    user.first_name = request.form.get('first_name', user.first_name)
    user.last_name = request.form.get('last_name', user.last_name)
    user.phone_number = request.form.get('phone_number', user.phone_number)
    user.email = request.form.get('email', user.email)

    if 'profile_picture' in request.files:
        profile_picture = request.files['profile_picture']
        if profile_picture:
            user.profile_picture = profile_picture.read()

    db.session.commit()

    flash("Profile updated successfully!", "success")
    return redirect(url_for('main.soloist_profile', user_id=user_id))

from sqlalchemy.orm import aliased

@main.route('/main_page')
def main_page():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user_id = uuid.UUID(session['user_id'])
    user = Profile.query.get(user_id)

    if user.profile_type == 'venue':
        musician_profiles = db.session.query(Musician).join(Profile).order_by(db.func.random()).all()

        processed_profiles = []
        for musician in musician_profiles:
            profile = musician.profile

            display_name = None
            if profile.musician_type == 'band':
                if musician.band:
                    display_name = musician.band.band_name
            elif profile.musician_type == 'soloist':
                if musician.soloist:
                    display_name = musician.soloist.artist_name

            if not display_name:
                display_name = f"{profile.first_name} {profile.last_name}"

            encoded_image = None
            if profile.profile_picture:
                encoded_image = base64.b64encode(profile.profile_picture).decode('utf-8')

            rating_val = float(profile.rating) if profile.rating else 0.0

            processed_profiles.append({
                'id': str(musician.profile_id),
                'display_name': display_name,
                'genre': musician.genre,
                'price_per_hour': float(musician.price_per_hour),
                'equipment': musician.equipment,  
                'rating': rating_val,
                'encoded_image': encoded_image,
            })

        return render_template('main_page.html', user=user, profiles=processed_profiles)
    elif user.profile_type == 'musician':
        bookings = Booking.query.filter_by(musician_id=user_id, status='Requested').all()
        return render_template('main_page.html', user=user, bookings=bookings, base64=base64)
    else:
        return render_template('main_page.html', user=user)


@main.route('/search_profiles', methods=['POST'])
def search_profiles():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized access'}), 401

    data = request.get_json()
    user = Profile.query.get(uuid.UUID(session['user_id']))

    if not user:
        return jsonify({'error': 'User not found'}), 404

    if user.profile_type == 'venue':

        soloist_alias = aliased(Soloist)
        band_alias = aliased(Band)

        query = query.outerjoin(soloist_alias, Musician.profile_id == soloist_alias.profile_id)
        query = query.outerjoin(band_alias, Musician.profile_id == band_alias.profile_id)

        filters_applied = False
        musician_type = data.get('musician_type')
        if musician_type:
            query = query.filter(Profile.musician_type == musician_type)
            filters_applied = True

        name = data.get('name')
        if name:
            name = f"%{name}%"
            query = query.filter(
                db.or_(
                    Profile.first_name.ilike(name),
                    Profile.last_name.ilike(name),
                    (Profile.first_name + " " + Profile.last_name).ilike(name)
                )
            )
            filters_applied = True

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
                pass

        equipment = data.get('equipment')
        if equipment:
            needs_equipment = equipment.lower() == 'yes'
            query = query.filter(Musician.equipment == needs_equipment)
            filters_applied = True

        min_rating = data.get('min_rating')
        if min_rating:
            try:
                min_rating_value = float(min_rating)
                query = query.filter(func.coalesce(Profile.rating, 0) >= min_rating_value)
                filters_applied = True
            except ValueError:
                pass

        results = query.all()

        if not filters_applied:
            results = db.session.query(Musician).join(Profile).order_by(db.func.random()).limit(5).all()

        output = []
        for musician in results:
            profile = musician.profile
            display_name = None
            if profile.musician_type == 'band' and musician.band:
                display_name = musician.band.band_name
            elif profile.musician_type == 'soloist' and musician.soloist:
                display_name = musician.soloist.artist_name
            if not display_name:
                display_name = f"{profile.first_name} {profile.last_name}"

            encoded_image = None
            if profile.profile_picture:
                encoded_image = base64.b64encode(profile.profile_picture).decode('utf-8')

            rating_val = float(profile.rating) if profile.rating else 0.0

            genre = musician.genre
            price_per_hour = float(musician.price_per_hour)
            equipment_bool = musician.equipment 

            output.append({
                'id': str(musician.profile_id),
                'display_name': display_name,
                'genre': genre,
                'price_per_hour': price_per_hour,
                'equipment': equipment_bool,
                'rating': rating_val,
                'encoded_image': encoded_image
            })

        return jsonify(output)

    return jsonify([])  

@main.route('/profile/<user_id>')
def view_profile(user_id):
    user = Profile.query.get(uuid.UUID(user_id))

    if not user:
        flash("Profile not found", "error")
        return redirect(url_for('main.main_page'))

    logged_in_user_id = uuid.UUID(session['user_id'])
    logged_in_user = Profile.query.get(logged_in_user_id)

    reviews_count = Review.query.filter_by(reviewee_id=user.profile_id).count()

    is_own_profile = (logged_in_user_id == uuid.UUID(user_id)) 

    profile_picture = None
    if user.profile_picture:
        profile_picture = base64.b64encode(user.profile_picture).decode('utf-8')

    if user.profile_type == 'musician':
        show_book_button = logged_in_user.profile_type == 'venue' and not is_own_profile

        if user.musician_type == 'soloist':
            soloist = Soloist.query.get(user.profile_id)
            return render_template(
                'soloist_profile.html',
                user=user,
                soloist=soloist,
                show_book_button=show_book_button,
                is_own_profile=is_own_profile,
                profile_picture=profile_picture,
                reviews_count=reviews_count
            )
        elif user.musician_type == 'band':
            band = Band.query.get(user.profile_id)
            return render_template(
                'band_profile.html',
                user=user,
                band=band,
                show_book_button=show_book_button,
                is_own_profile=is_own_profile,
                profile_picture=profile_picture,
                reviews_count=reviews_count
            )

    elif user.profile_type == 'venue':
   

        return render_template(
            'venue_profile.html',
            user=user,
            venue=user.venue,
            is_own_profile=is_own_profile,
            profile_picture=profile_picture,
            reviews_count = reviews_count
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
        date_booking_str = request.form.get('date_booking')
        duration_str = request.form.get('duration')
        method_str = request.form.get('payment_method')
        note_str = request.form.get('note')

        print(f"Received form data: date_booking={date_booking_str}, duration={duration_str}, payment_method={method_str}")

        try:
            date_booking = datetime.strptime(date_booking_str, '%Y-%m-%dT%H:%M')
            print(f"Parsed date_booking: {date_booking}")

            if not duration_str or ':' not in duration_str:
                raise ValueError("Invalid duration format. Please use HH:MM.")

            hours, minutes = map(int, duration_str.split(':'))
            if hours < 0 or minutes < 0 or minutes >= 60:
                raise ValueError("Invalid duration values. Hours must be >= 0, and minutes between 0 and 59.")

            duration = timedelta(hours=hours, minutes=minutes)
            if duration.total_seconds() <= 0:
                raise ValueError("Duration must be greater than zero.")
            print(f"Duration validated: {duration}")

            total_hours = hours + minutes / 60
            total_price = Decimal(total_hours) * Decimal(musician.price_per_hour) 

        except ValueError as e:
            print(f"ValueError: {e}")
            flash(str(e), "error")
            return render_template('booking.html', musician=musician)

        
        status = 'Requested'
        new_booking = Booking(
            musician_id=uuid.UUID(musician_id),
            venue_id=logged_in_user_id,
            status=status,
            date_booking=date_booking,
            duration=duration,
            booked_by=logged_in_user_id,
            booked_in=logged_in_user_id,
            note=note_str
        )

        print(f"New booking object created: {new_booking}")
 
        total_hours = hours + minutes / 60
        total_price = Decimal(total_hours) * Decimal(musician.price_per_hour)
        new_payment = Payment(
            method=method_str,
            amount= total_price  
        )

        try:
            print("Attempting to commit booking and payment...")
            db.session.add(new_booking)
            db.session.flush()  
            new_payment.booking_id = new_booking.booking_id  
            db.session.add(new_payment)
            db.session.commit()
            flash("Booking request sent successfully!", "success")
            print("Booking and payment successfully committed.")
            return redirect(url_for('main.main_page'))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while requesting the booking: {e}", "error")
            print(f"Error during commit: {e}")
            return render_template('booking.html', musician=musician)


    else:
        print("Rendering booking.html")
        return render_template('booking.html', musician=musician)      


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

    if booking.musician_id != user_id:
        flash("You are not authorized to respond to this booking.", "error")
        return redirect(url_for('main.main_page'))

    response = request.form.get('response')
    if response not in ['Accepted', 'Denied']:
        flash("Invalid response.", "error")
        return redirect(url_for('main.main_page'))

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
        flash("You must be logged in to view your bookings.", "error")
        return redirect(url_for('main.login'))

    user_id = uuid.UUID(session['user_id'])
    user = Profile.query.get(user_id)

    if user.profile_type == 'venue':
        bookings = Booking.query.filter_by(venue_id=user_id).order_by(Booking.date_booking.desc()).all()
    elif user.profile_type == 'musician':
        bookings = Booking.query.filter_by(musician_id=user_id).order_by(Booking.date_booking.desc()).all()
    else:
        flash("Invalid user type.", "error")
        return redirect(url_for('main.main_page'))

    return render_template('mybooking.html', bookings=bookings, user=user)

genre_to_style = {
    'Pop': ['Dance Club', 'Wine Bar'],
    'Rock': ['Beach Bar', 'Dance Club'],
    'Hip-Hop/Rap': ['Dance Club', 'Bar'],
    'Jazz': ['Jazz Lounge', 'Restaurant'],
    'Classical': ['Restaurant', 'Jazz Lounge'],
    'EDM': ['Dance Club', 'Bar'],
    'Blues': ['Jazz Lounge', 'Art Café'],
    'Reggae': ['Beach Bar', 'Restaurant'],
    'R&B': ['Wine Bar', 'Dance Club'],
    'Country': ['Restaurant', 'Art Café'],
    'Other': ['Dance Club', 'Wine Bar', 'Beach Bar', 'Restaurant', 'Jazz Lounge', 'Art Café', 'Dance Club', 'Modern Cocktailbar']
}
import base64

import base64

@main.route('/recommended')
def recommended_page():
    if 'user_id' not in session:
        flash("You must be logged in to respond to bookings.", "error")
        return redirect(url_for('main.login'))

    logged_in_user_id = uuid.UUID(session['user_id'])
    user = Profile.query.get(logged_in_user_id)  

    recommendations = get_recommendations(logged_in_user_id)

    processed_recommendations = []
    for musician in recommendations:
        if musician.profile.profile_picture:
            encoded_image = base64.b64encode(musician.profile.profile_picture).decode('utf-8')
            musician.encoded_picture = f"data:image/jpeg;base64,{encoded_image}"
        else:
            musician.encoded_picture = None
        processed_recommendations.append(musician)

    print(f"Recommendations for User ID {user.profile_id}: {recommendations}")

    return render_template('my_recommendations.html', user=user, recommendations=processed_recommendations)

def get_recommendations(user_profile_id):
    """
    Verkrijg muzikantaanbevelingen op basis van genre-naar-venue stijl matching en hoogste rating.
    
    1. Als er geen eerdere boekingen zijn, wordt er aanbevolen op basis van genre en venue stijlen.
    2. Als er eerdere boekingen zijn, wordt er aanbevolen op basis van de meest geboekte genres, gesorteerd op rating.
    """

    bookings = Booking.query.filter(Booking.booked_by == user_profile_id).all()
    
    print(f"User ID: {user_profile_id}, Bookings Found: {len(bookings)}")

    if not bookings:
        recommended_musicians = []
        

        venues = Venue.query.all()
        
        print(f"Total Venues Found: {len(venues)}")
        
        for venue in venues:
            for genre, styles in genre_to_style.items():
                if venue.style in styles:
                    musicians = Musician.query.filter(Musician.genre == genre).all()
                    recommended_musicians.extend(musicians)

        unique_musicians = {m.profile_id: m for m in recommended_musicians}.values()

        recommended_musicians = sorted(unique_musicians, key=lambda m: m.profile.rating, reverse=True)[:3]
        print(f"Recommended Musicians (no bookings): {len(recommended_musicians)}")
        return recommended_musicians

    else:
        genre_count = {}

        for booking in bookings:
            musician = Musician.query.get(booking.musician_id)
            if musician:
                genre = musician.genre
                genre_count[genre] = genre_count.get(genre, 0) + 1

        print(f"Genre Count from Previous Bookings: {genre_count}")

        if not genre_count:
            print("No genres found from previous bookings.")
            return []

        most_booked_genre = max(genre_count, key=genre_count.get)
        print(f"Most Booked Genre: {most_booked_genre}")

        recommended_musicians = Musician.query.filter(Musician.genre == most_booked_genre).all()

        unique_musicians = {m.profile_id: m for m in recommended_musicians}.values()

        recommended_musicians = sorted(unique_musicians, key=lambda m: m.profile.rating, reverse=True)[:3]
        
        print(f"Recommended Musicians (based on most booked genre): {len(recommended_musicians)}")
        
        return recommended_musicians

@main.route('/bookings/<uuid:booking_id>/review', methods=['GET', 'POST'])
def submit_review(booking_id):
    if 'user_id' not in session:
        flash("You must be logged in to submit a review.", "error")
        return redirect(url_for('main.login'))

    current_user_id = uuid.UUID(session['user_id'])
    current_user = Profile.query.get(current_user_id)
    booking = Booking.query.get_or_404(booking_id)

    if booking.booked_by != current_user_id and booking.musician_id != current_user_id:
        flash('You are not authorized to review this booking.', 'error')
        return redirect(url_for('main.bookings'))

    existing_review = Review.query.filter_by(
        booking_id=booking_id,
        reviewer_id=current_user_id
    ).first()
    if existing_review:
        flash('You have already submitted a review for this booking.', 'error')
        return redirect(url_for('main.bookings'))

    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment')

        try:
            rating = float(rating)
            if rating < 0.0 or rating > 5.0:
                raise ValueError
        except ValueError:
            flash('Invalid rating. Please select a rating between 0 and 5.', 'error')
            return render_template('submit_review.html', booking=booking)

        if current_user.profile_type == 'venue':
            role_reviewer = 'Venue'
            reviewee_id = booking.musician_id
        elif current_user.profile_type == 'musician':
            role_reviewer = 'Musician'
            reviewee_id = booking.venue_id
        else:
            flash('Invalid profile type for reviewing.', 'error')
            return redirect(url_for('main.bookings'))

        review = Review(
            booking_id=booking_id,
            reviewer_id=current_user_id,
            reviewee_id=reviewee_id,
            rating=rating,
            comment=comment,
            role_reviewer=role_reviewer
        )
        db.session.add(review)
        db.session.commit()

        reviewee_profile = Profile.query.get(reviewee_id)
        if reviewee_profile:
            all_reviews = Review.query.filter_by(reviewee_id=reviewee_id).all()
            if all_reviews:
                avg_rating = sum(float(r.rating) for r in all_reviews) / len(all_reviews)
                reviewee_profile.rating = round(avg_rating, 1)
                db.session.commit()

        flash('Your review has been submitted.', 'success')
        return redirect(url_for('main.bookings'))

    return render_template('submit_review.html', booking=booking)

@main.route('/reviews')
def reviews():
    if 'user_id' not in session:
        flash("You must be logged in to view your reviews.", "error")
        return redirect(url_for('main.login'))

    current_user_id = uuid.UUID(session['user_id'])
    current_user = Profile.query.get(current_user_id)

    reviews = Review.query.filter_by(reviewee_id=current_user_id).all()

    total_rating = sum(float(review.rating) for review in reviews)
    average_rating = round(total_rating / len(reviews), 2) if reviews else 0.0

    rating_counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for rev in reviews:
        rating_counts[int(rev.rating)] += 1

    total_reviews = len(reviews) if reviews else 0
    rating_percentages = {}
    for star in rating_counts:
        rating_percentages[star] = (rating_counts[star] / total_reviews * 100) if total_reviews > 0 else 0

    return render_template('reviews.html', 
                           user=current_user, 
                           reviews=reviews, 
                           average_rating=average_rating,
                           rating_counts=rating_counts,
                           rating_percentages=rating_percentages)

@main.route('/reviews/<uuid:musician_id>')
def view_reviews(musician_id):
    if 'user_id' not in session:
        flash("You must be logged in to view reviews.", "error")
        return redirect(url_for('main.login'))

    show_all_param = request.args.get('show_all', 'false').lower()
    show_all = (show_all_param == 'true')

    current_user_id = uuid.UUID(session['user_id'])
    current_user = Profile.query.get(current_user_id)

    reviews = Review.query.filter_by(reviewee_id=musician_id).all()

    total_rating = sum(float(review.rating) for review in reviews)
    average_rating = round(total_rating / len(reviews), 2) if reviews else 0.0

    rating_counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for rev in reviews:
        rating_counts[int(rev.rating)] += 1

    total_reviews = len(reviews)
    rating_percentages = {}
    for star in rating_counts:
        rating_percentages[star] = (rating_counts[star] / total_reviews * 100) if total_reviews > 0 else 0

    five_stars = rating_counts[5]
    four_stars = rating_counts[4]
    three_stars = rating_counts[3]
    two_stars = rating_counts[2]
    one_star = rating_counts[1]
    total_counts = five_stars + four_stars + three_stars + two_stars + one_star

    musician = Profile.query.get(musician_id)

    return render_template(
        'view_reviews.html',
        logged_in_user=current_user,
        reviews=reviews,
        average_rating=average_rating,
        musician=musician,
        show_all=show_all,
        rating_counts=rating_counts,
        rating_percentages=rating_percentages,
        total_reviews=total_reviews,
        five_stars=five_stars,
        four_stars=four_stars,
        three_stars=three_stars,
        two_stars=two_stars,
        one_star=one_star,
        total_counts=total_counts,
    )