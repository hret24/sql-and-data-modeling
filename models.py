from email.policy import default
# from app import db
from datetime import datetime
from sqlalchemy.dialects import postgresql
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String)
    genres = db.Column(postgresql.ARRAY(db.String))
    seeking_for_artist = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)
    artists = db.relationship('Artist', secondary='Show', backref=db.backref('venues', lazy=True), viewonly=True)
    shows = db.relationship('Show', backref='venues', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate DONE

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(postgresql.ARRAY(db.String))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String)
    seeking_for_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)
    venues = db.relationship('Venue', backref=db.backref('artists', lazy=True)) 
    shows = db.relationship('Show', backref='artists',lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate DONE

# class Show(db.Model):
#     __tablename__ = 'show'

#     venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), primary_key=True)
#     artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), primary_key=True)
#     start_time = db.Column(db.DateTime, nullable=False, default=datetime.now())

# # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. DONE

# class Show(db.Model):
#     __tablename__ = 'show'

#     venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), primary_key=True)
#     artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), primary_key=True)
#     start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

#     # Define relationships to Venue and Artist
#     venue = db.relationship('Venue', backref=db.backref('shows', lazy=True))
#     artist = db.relationship('Artist', backref=db.backref('shows', lazy=True))

#     # Composite key now includes 'start_time'
#     __table_args__ = (
#         db.PrimaryKeyConstraint('venue_id', 'artist_id', 'start_time'),
#     )

#     def __repr__(self):
#         return f'<Show {self.venue_id} - {self.artist_id} - {self.start_time}>'

class Show(db.Model):
    __tablename__ = 'show'

    show_id = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Define relationships to Venue and Artist
    venue = db.relationship('Venue', backref=db.backref('shows', lazy=True))
    artist = db.relationship('Artist', backref=db.backref('shows', lazy=True))

    def __repr__(self):
        return f'<Show {self.show_id} - {self.venue_id} - {self.artist_id} - {self.start_time}>'