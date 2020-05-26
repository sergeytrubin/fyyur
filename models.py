from app import db
from datetime import datetime

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String()))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(250))
    seeking_talent = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(), default='')
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __init__(
            self, name, genres, city, state, address, phone, image_link,
            facebook_link, website, seeking_talent, seeking_description):

        self.name = name
        self.genres = genres
        self.city = city
        self.state = state
        self.address = address
        self.phone = phone
        self.image_link = image_link
        self.facebook_link = facebook_link
        self.website = website
        self.seeking_talent = False
        self.seeking_description = seeking_description

    def __repr__(self):
        return f'<Venue {self.id}: {self.name}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(250))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(), default='')
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __init__(
            self, name, genres, city, state, phone, website, facebook_link,
            seeking_venue, seeking_description, image_link):

        self.name = name
        self.genres = genres
        self.city = city
        self.state = state
        self.phone = phone
        self.website = website
        self.facebook_link = facebook_link
        self.seeking_venue = False
        self.seeking_description = seeking_description
        self.image_link = image_link

    def __repr__(self):
        return f'<Artist {self.id}: {self.name}>'


class Show(db.Model):
    __tablename__ = 'Show'

    id = id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    show_time = db.Column(db.DateTime, default=datetime.utcnow())

    def __init__(self, venue_id, artist_id, show_time):
        self.venue_id = venue_id
        self.artist_id = artist_id
        self.show_time = show_time

    def __repr__(self):
        return f'<Show {self.id}>'
