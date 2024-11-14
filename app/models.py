from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Profile(db.Model):
    __tablename__ = 'profile'

    profile_id = db.Column(db.String(7), primary_key=True)  # Char(7)
    name = db.Column(db.String, nullable=False)  # Text
    address = db.Column(db.String)  # Text
    email = db.Column(db.String, nullable=False, unique=True)  # Text
    phone_number = db.Column(db.String)  # Text
    bio = db.Column(db.String)  # Text
    profile_picture = db.Column(db.LargeBinary)  # BYTEA
    pictures = db.Column(db.LargeBinary)  # BYTEA
    rating = db.Column(db.Numeric(2, 1))  # Decimal(2,1)

    # Define the check constraint separately using __table_args__
    __table_args__ = (
        db.CheckConstraint('rating >= 0.0 AND rating <= 5.0', name='check_rating_range'),
    )

    def __repr__(self):
        return f'<Profile {self.profile_id}, {self.name}>'
    
class Musician(db.Model):
    __tablename__ = 'musician'

    profile_id = db.Column(db.String(7), db.ForeignKey('profile.profile_id'), primary_key=True)
    genre = db.Column(db.String)  # Text
    price_per_hour = db.Column(db.Numeric(10, 2))  # Decimal(10, 2)
    link_to_songs = db.Column(db.LargeBinary)  # BYTEA
    availability = db.Column(db.LargeBinary)  # BYTEA
    equipment = db.Column(db.String)  # Text

    # Relationship back to Profile (Profile is a parent of Musician)
    profile = db.relationship('Profile', backref=db.backref('musician', uselist=False))

    def __repr__(self):
        return f'<Musician {self.profile_id}, {self.genre}>'
    
class Soloist(db.Model):
    __tablename__ = 'soloist'

    profile_id = db.Column(db.String(7), db.ForeignKey('musician.profile_id'), primary_key=True)
    age = db.Column(db.Integer)  # Integer column without 'check' argument here

    # Define the check constraint in __table_args__
    __table_args__ = (
        db.CheckConstraint('age > 0', name='check_age_positive'),
    )

    # Relationship back to Musician
    musician = db.relationship('Musician', backref=db.backref('soloist', uselist=False))

    def __repr__(self):
        return f'<Soloist {self.profile_id}, Age: {self.age}>'

class BandMember(db.Model):
    __tablename__ = 'band_member'

    profile_id = db.Column(db.String(7), db.ForeignKey('musician.profile_id'), primary_key=True)
    num_members_in_band = db.Column(db.Integer, check=db.CheckConstraint('num_members_in_band > 0'))  # Integer with check constraint

    # Relationship back to Musician
    musician = db.relationship('Musician', backref=db.backref('band_member', uselist=False))

    def __repr__(self):
        return f'<BandMember {self.profile_id}, Members: {self.num_members_in_band}>'

class Venue(db.Model):
    __tablename__ = 'venue'

    profile_id = db.Column(db.String(7), db.ForeignKey('profile.profile_id'), primary_key=True)
    seating_capacity = db.Column(db.Integer, check=db.CheckConstraint('seating_capacity > 0'))  # Integer with check constraint
    name_event = db.Column(db.String)  # Text

    # Relationship back to Profile (Profile is a parent of Venue)
    profile = db.relationship('Profile', backref=db.backref('venue', uselist=False))

    def __repr__(self):
        return f'<Venue {self.profile_id}, Event: {self.name_event}>'
    
class Booking(db.Model):
    __tablename__ = 'booking'

    booking_id = db.Column(db.String(7), primary_key=True)
    musician_id = db.Column(db.String(7), db.ForeignKey('musician.profile_id'), nullable=False)
    venue_id = db.Column(db.String(7), db.ForeignKey('venue.profile_id'), nullable=False)
    status = db.Column(db.String, nullable=False, check=db.CheckConstraint("status IN ('Completed', 'Processing', 'Failed')"))
    duration = db.Column(db.Interval)  # Interval
    date_booking = db.Column(db.TIMESTAMP(timezone=True))  # Timestamp with timezone
    booked_by = db.Column(db.String(7), db.ForeignKey('profile.profile_id'))
    booked_in = db.Column(db.String(7), db.ForeignKey('venue.profile_id'))

    #Relationships
    musician = db.relationship('Musician', backref=db.backref('booking'))
    venue = db.relationship('Venue', backref=db.backref('booking'))
    profile_booked_by = db.relationship('Profile', foreign_keys=[booked_by], backref=db.backref('booked_by', uselist=False))
    profile_booked_in = db.relationship('Profile', foreign_keys=[booked_in], backref=db.backref('booked_in', uselist=False))

    def __repr__(self):
        return f'<Booking {self.booking_id}, Status: {self.status}>'
    
class Payment(db.Model):
    __tablename__ = 'payment'

    payment_id = db.Column(db.String(7), primary_key=True)
    booking_id = db.Column(db.String(7), db.ForeignKey('booking.booking_id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    method = db.Column(db.String, nullable=False, check=db.CheckConstraint("method IN ('Cash', 'Mobile payment', 'Credit card', 'Bancontact', 'Other')"))
    date_payment = db.Column(db.TIMESTAMP(timezone=True), default=db.func.current_timestamp())  # Timestamp with timezone
    status = db.Column(db.String, nullable=False, check=db.CheckConstraint("status IN ('Completed', 'Processing', 'Failed')"))

    # Relationship
    booking = db.relationship('Booking', backref=db.backref('payment'))

    def __repr__(self):
        return f'<Payment {self.payment_id}, Amount: {self.amount}>'
    
class Review(db.Model):
    __tablename__ = 'review'

    review_id = db.Column(db.String(7), primary_key=True)
    booking_id = db.Column(db.String(7), db.ForeignKey('booking.booking_id'), nullable=False)
    rating = db.Column(db.Numeric(2, 1), nullable=False, check=db.CheckConstraint('rating >= 0.0 AND rating <= 5.0'))
    comment = db.Column(db.String)  # Text
    role_reviewer = db.Column(db.String, nullable=False, check=db.CheckConstraint("role_reviewer IN ('Musician', 'Venue Owner')"))
    date = db.Column(db.TIMESTAMP(timezone=True), default=db.func.current_timestamp())  # Timestamp with timezone
    pictures = db.Column(db.LargeBinary)  # BYTEA

    # Relationship
    booking = db.relationship('Booking', backref=db.backref('review'))

    def __repr__(self):
        return f'<Review {self.review_id}, Rating: {self.rating}>'


    
    