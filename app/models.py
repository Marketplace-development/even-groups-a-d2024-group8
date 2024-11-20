from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Profile(db.Model):
    __tablename__ = 'profile'

    profile_id = db.Column(db.String(7), primary_key=True)  # Char(7)
    first_name = db.Column(db.String, nullable=True)  # Nullable for bands/venues
    last_name = db.Column(db.String, nullable=True)  # Nullable for bands/venues
    address = db.Column(db.String)  # Optional
    email = db.Column(db.String, nullable=False, unique=True)  # Unique email for login
    phone_number = db.Column(db.String)  # Optional
    bio = db.Column(db.String)  # Optional
    profile_picture = db.Column(db.LargeBinary)  # Optional
    pictures = db.Column(db.LargeBinary)  # Optional
    rating = db.Column(db.Numeric(2, 1), default=0.0, nullable=True)  # Default rating
    profile_type = db.Column(db.String, nullable=False)  # 'musician' or 'venue'
    musician_type = db.Column(db.String, nullable=True)  # 'soloist' or 'band', only for musicians
    band_name = db.Column(db.String, nullable=True)  # Only for bands

    __table_args__ = (
        db.CheckConstraint('rating >= 0.0 AND rating <= 5.0', name='check_rating_range'),
        db.CheckConstraint("profile_type IN ('musician', 'venue')", name='check_profile_type_valid'),
    )

    def __repr__(self):
        return f'<Profile {self.profile_id}, {self.email}>'


class Musician(db.Model):
    __tablename__ = 'musician'

    profile_id = db.Column(db.String(7), db.ForeignKey('profile.profile_id', ondelete='SET NULL', onupdate='CASCADE'), primary_key=True)
    genre = db.Column(db.String, nullable=False)  # Genre is now required
    price_per_hour = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)  # Default value for price
    link_to_songs = db.Column(db.String)  # Optional (changed from LargeBinary to String for better URL support)
    availability = db.Column(db.String)  # Optional
    equipment = db.Column(db.Boolean, default=False)  # Optional

    profile = db.relationship('Profile', backref=db.backref('musician', uselist=False))

    def __repr__(self):
        return f'<Musician {self.profile_id}, Genre: {self.genre}>'


class Soloist(db.Model):
    __tablename__ = 'soloist'

    profile_id = db.Column(db.String(7), db.ForeignKey('musician.profile_id', ondelete='SET NULL', onupdate='CASCADE'), primary_key=True)
    date_of_birth = db.Column(db.Date, nullable=False)  # Required field for soloists

    musician = db.relationship('Musician', backref=db.backref('soloist', uselist=False))

    def __repr__(self):
        return f'<Soloist {self.profile_id}, DOB: {self.date_of_birth}>'


class BandMember(db.Model):
    __tablename__ = 'band_member'

    profile_id = db.Column(db.String(7), db.ForeignKey('musician.profile_id', ondelete='SET NULL', onupdate='CASCADE'), primary_key=True)
    num_members_in_band = db.Column(db.Integer, nullable=False, default=1)  # Default is 1

    musician = db.relationship('Musician', backref=db.backref('band_member', uselist=False))

    def __repr__(self):
        return f'<BandMember {self.profile_id}, Members: {self.num_members_in_band}>'


class Venue(db.Model):
    __tablename__ = 'venue'

    profile_id = db.Column(db.String(7), db.ForeignKey('profile.profile_id', ondelete='SET NULL', onupdate='CASCADE'), primary_key=True)
    seating_capacity = db.Column(db.Integer, nullable=True)  # Optional
    name_event = db.Column(db.String)  # Optional
    style = db.Column(
        db.String,
        nullable=False,
        default='Not specified',
        check_constraint=db.CheckConstraint(
            "style IN ('Traditional Pub', 'Modern Cocktailbar', 'Jazz Lounge', 'Industrial Bar', 'Beach Bar', 'Art Café', 'Dance Club', 'Restaurant', 'Wine Bar', 'Other', 'Not specified')"
        )
    )

    profile = db.relationship('Profile', backref=db.backref('venue', uselist=False))

    def __repr__(self):
        return f'<Venue {self.profile_id}, Style: {self.style}>'


class Booking(db.Model):
    __tablename__ = 'booking'

    booking_id = db.Column(db.String(7), primary_key=True)
    musician_id = db.Column(db.String(7), db.ForeignKey('musician.profile_id', ondelete='SET NULL', onupdate='CASCADE'), nullable=False)
    venue_id = db.Column(db.String(7), db.ForeignKey('venue.profile_id', ondelete='SET NULL', onupdate='CASCADE'), nullable=False)
    status = db.Column(db.String, nullable=False)
    duration = db.Column(db.Interval)
    date_booking = db.Column(db.TIMESTAMP(timezone=True))
    booked_by = db.Column(db.String(7), db.ForeignKey('profile.profile_id', ondelete='SET NULL', onupdate='CASCADE'))
    booked_in = db.Column(db.String(7), db.ForeignKey('venue.profile_id', ondelete='SET NULL', onupdate='CASCADE'))

    # Relationships with explicit foreign_keys
    musician = db.relationship('Musician', backref=db.backref('bookings', lazy=True))
    venue = db.relationship('Venue', backref=db.backref('venue_bookings', lazy=True), foreign_keys=[venue_id])
    venue_booking = db.relationship('Venue', backref=db.backref('booked_venues', lazy=True), foreign_keys=[booked_in])
    profile_booked_by = db.relationship('Profile', foreign_keys=[booked_by], backref=db.backref('bookings_made', lazy=True))

    __table_args__ = (
        db.CheckConstraint("status IN ('Completed', 'Processing', 'Failed')", name='check_status_valid'),
    )

    def __repr__(self):
        return f'<Booking {self.booking_id}, Status: {self.status}>'


class Payment(db.Model):
    __tablename__ = 'payment'

    payment_id = db.Column(db.String(7), primary_key=True)
    booking_id = db.Column(db.String(7), db.ForeignKey('booking.booking_id', ondelete='SET NULL', onupdate='CASCADE'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    method = db.Column(db.String, nullable=False)
    date_payment = db.Column(db.TIMESTAMP(timezone=True), default=db.func.current_timestamp())
    status = db.Column(db.String, nullable=False, default='Processing')

    booking = db.relationship('Booking', backref=db.backref('payments', lazy=True))

    __table_args__ = (
        db.CheckConstraint("method IN ('Cash', 'Mobile payment', 'Credit card', 'Bancontact', 'Other')", name='check_method_valid'),
        db.CheckConstraint("status IN ('Completed', 'Processing', 'Failed')", name='check_status_valid_payment'),
    )

    def __repr__(self):
        return f'<Payment {self.payment_id}, Amount: {self.amount}>'


class Review(db.Model):
    __tablename__ = 'review'

    review_id = db.Column(db.String(7), primary_key=True)
    booking_id = db.Column(db.String(7), db.ForeignKey('booking.booking_id', ondelete='SET NULL', onupdate='CASCADE'), nullable=False)
    rating = db.Column(db.Numeric(2, 1), nullable=False)
    comment = db.Column(db.String, nullable=True)  # Optional
    role_reviewer = db.Column(db.String, nullable=False)

    booking = db.relationship('Booking', backref=db.backref('reviews', lazy=True))

    __table_args__ = (
        db.CheckConstraint('rating >= 0.0 AND rating <= 5.0', name='check_rating_range_review'),
        db.CheckConstraint("role_reviewer IN ('Musician', 'Venue Owner')", name='check_role_reviewer_valid'),
    )

    def __repr__(self):
        return f'<Review {self.review_id}, Rating: {self.rating}>'

