from email.policy import default
# from app import db
from datetime import datetime
from sqlalchemy.dialects import postgresql
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Association table to link Venue and Artist
# venue_artist_association = db.Table('venue_artist_association',
#     db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), primary_key=True),
#     db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True)
# )

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
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)


    # Many-to-many relationship to Artist using the association table
    # artists = db.relationship('Artist', secondary=venue_artist_association, lazy=True)
    shows = db.relationship('Show', backref='venue', lazy='joined', cascade='all, delete')

    def __repr__(self):
        return f'<Venue {self.name}>'

    # artists = db.relationship('Artist', secondary='Show', backref=db.backref('venues', lazy=True), viewonly=True)
    # shows = db.relationship('Show', backref='venues', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate DONE

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String)
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)

    # Many-to-many relationship to Venue using the association table
    # venues = db.relationship('Venue', secondary=venue_artist_association, lazy=True)
    shows = db.relationship('Show', backref='artist', lazy='joined', cascade='all, delete')

    def __repr__(self):
        return f'<Artist {self.name}>'

    # venues = db.relationship('Venue', backref=db.backref('artists', lazy=True)) 
    # shows = db.relationship('Show', backref='artists',lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate DONE

class Show(db.Model):
    __tablename__ = 'show'

    show_id = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Define relationships to Venue and Artist
    # venue = db.relationship('Venue')
    # artist = db.relationship('Artist')

    def __repr__(self):
        return f'<Show {self.show_id} - {self.venue_id} - {self.artist_id} - {self.start_time}>'

    # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. DONE
