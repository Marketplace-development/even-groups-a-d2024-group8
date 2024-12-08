from sqlalchemy.dialects.postgresql import UUID
from . import db
import uuid

class Profile(db.Model):
    __tablename__ = 'profile'
    profile_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable= False)
    city = db.Column(db.String, nullable=False)     
    street_name = db.Column(db.String)  
    house_number = db.Column(db.String)  
    phone_number = db.Column(db.String)
    email = db.Column(db.String, nullable=False, unique=True)
    bio = db.Column(db.String)
    profile_picture = db.Column(db.LargeBinary)
    rating = db.Column(db.Numeric(2, 1), default=0.0, nullable=True)
    profile_type = db.Column(db.String, nullable=False)
    musician_type = db.Column(db.String, nullable=True)

    __table_args__ = (
        db.CheckConstraint('rating >= 0.0 AND rating <= 5.0', name='check_rating_range'),
        db.CheckConstraint("profile_type IN ('musician', 'venue')", name='check_profile_type_valid'),
    )

    def __repr__(self):
        return f'<Profile {self.profile_id}, {self.email}>'

class Musician(db.Model):
    __tablename__ = 'musician'
    profile_id = db.Column(UUID(as_uuid=True), db.ForeignKey('profile.profile_id', ondelete='SET NULL', onupdate='CASCADE'), primary_key=True)
    genre = db.Column(db.String, nullable=False)
    price_per_hour = db.Column(db.Numeric(10, 2), nullable=False)
    link_to_songs = db.Column(db.String)
    equipment = db.Column(db.Boolean, nullable=False)

    profile = db.relationship('Profile', backref=db.backref('musician', uselist=False))

    __table_args__ = (
        db.CheckConstraint(
            "genre IN ('Pop', 'Rock', 'Hip-Hop/Rap', 'Jazz', 'Electronic Dance Music (EDM)', 'Classical', 'Reggae', 'Blues', 'Country', 'R&B', 'Other')", 
            name='check_genre_valid'
        ),
    )

    
    def __repr__(self):
        return f'<Musician {self.profile_id}, Genre: {self.genre}>'

class Soloist(db.Model):
    __tablename__ = 'soloist'
    profile_id = db.Column(UUID(as_uuid=True), db.ForeignKey('musician.profile_id', ondelete='SET NULL', onupdate='CASCADE'), primary_key=True)
    date_of_birth = db.Column(db.Date, nullable=False)
    artist_name = db.Column(db.String, nullable=False)  # Optional

    musician = db.relationship('Musician', backref=db.backref('soloist', uselist=False))

    def __repr__(self):
        return f"<Soloist {self.profile_id}, Artist Name: {self.artist_name}>"

class Band(db.Model):
    __tablename__ = 'band'
    profile_id = db.Column(UUID(as_uuid=True), db.ForeignKey('musician.profile_id', ondelete='SET NULL', onupdate='CASCADE'), primary_key=True)
    band_name = db.Column(db.String, nullable=False)
    num_members_in_band = db.Column(db.Integer, nullable=False, default=1)

    musician = db.relationship('Musician', backref=db.backref('band', uselist=False))

    def __repr__(self):
        return f'<Band {self.profile_id}, Members: {self.num_members_in_band}>'


class Venue(db.Model):
    __tablename__ = 'venue'

    profile_id = db.Column(UUID(as_uuid=True), db.ForeignKey('profile.profile_id', ondelete='SET NULL', onupdate='CASCADE'), primary_key=True)
    name_event = db.Column(db.String)
    style = db.Column(db.String, nullable=False, default='Not specified')

    __table_args__ = (
        db.CheckConstraint(
            "style IN ('Traditional Pub', 'Modern Cocktailbar', 'Jazz Lounge', 'Industrial Bar', 'Beach Bar', 'Art Café', 'Dance Club', 'Restaurant', 'Wine Bar', 'Other', 'Not specified')",
            name='check_style_valid'
        ),
    )

    profile = db.relationship('Profile', backref=db.backref('venue', uselist=False))

    def __repr__(self):
        return f'<Venue {self.profile_id}, Style: {self.style}>'


class Booking(db.Model):
    __tablename__ = 'booking'

    booking_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    musician_id = db.Column(UUID(as_uuid=True), db.ForeignKey('musician.profile_id', ondelete='SET NULL', onupdate='CASCADE'), nullable=False)
    venue_id = db.Column(UUID(as_uuid=True), db.ForeignKey('venue.profile_id', ondelete='SET NULL', onupdate='CASCADE'), nullable=False)
    status = db.Column(db.String, nullable=False)
    duration = db.Column(db.Interval)
    date_booking = db.Column(db.TIMESTAMP(timezone=True))
    booked_by = db.Column(UUID(as_uuid=True), db.ForeignKey('profile.profile_id', ondelete='SET NULL', onupdate='CASCADE'))
    booked_in = db.Column(UUID(as_uuid=True), db.ForeignKey('venue.profile_id', ondelete='SET NULL', onupdate='CASCADE'))

    musician = db.relationship('Musician', backref=db.backref('bookings', lazy=True))
    venue = db.relationship('Venue', backref=db.backref('venue_bookings', lazy=True), foreign_keys=[venue_id])
    venue_booking = db.relationship('Venue', backref=db.backref('booked_venues', lazy=True), foreign_keys=[booked_in])
    profile_booked_by = db.relationship('Profile', foreign_keys=[booked_by], backref=db.backref('bookings_made', lazy=True))

    __table_args__ = (
        db.CheckConstraint("status IN ('Requested', 'Accepted', 'Denied')", name='check_status_valid'),
    )

    def __repr__(self):
        return f'<Booking {self.booking_id}, Status: {self.status}>'


class Payment(db.Model):
    __tablename__ = 'payment'

    payment_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = db.Column(UUID(as_uuid=True), db.ForeignKey('booking.booking_id', ondelete='SET NULL', onupdate='CASCADE'), nullable=False)
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

    review_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = db.Column(UUID(as_uuid=True), db.ForeignKey('booking.booking_id', ondelete='SET NULL', onupdate='CASCADE'), nullable=False)
    reviewer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('profile.profile_id', ondelete='SET NULL', onupdate='CASCADE'), nullable=False)
    reviewee_id = db.Column(UUID(as_uuid=True), db.ForeignKey('profile.profile_id', ondelete='SET NULL', onupdate='CASCADE'), nullable=False)
    rating = db.Column(db.Numeric(2, 1), nullable=False)
    comment = db.Column(db.String, nullable=True)
    role_reviewer = db.Column(db.String, nullable=False)

    # Relationships
    booking = db.relationship('Booking', backref=db.backref('reviews', lazy=True))
    reviewer = db.relationship('Profile', foreign_keys=[reviewer_id], backref='reviews_given')
    reviewee = db.relationship('Profile', foreign_keys=[reviewee_id], backref='reviews_received')

    __table_args__ = (
        db.CheckConstraint('rating >= 0.0 AND rating <= 5.0', name='check_rating_range_review'),
        db.CheckConstraint("role_reviewer IN ('Musician', 'Venue')", name='check_role_reviewer_valid'),
    )

    def __repr__(self):
        return f'<Review {self.review_id}, Rating: {self.rating}>'
