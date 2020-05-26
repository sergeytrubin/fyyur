#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import json
import dateutil.parser
from datetime import datetime
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

from models import *

migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # Shows all venues per area
    # Queries
    all_venues = db.session.query(Venue).order_by(
        Venue.city, Venue.state).all()

    # Variables
    data = []
    area = ''

    # Formating data
    for venue in all_venues:
        num_upcoming_shows = len(db.session.query(Show).filter(
            Show.venue_id==venue.id).filter(
            Show.show_time>datetime.now()).all())

        if area == venue.city + venue.state:
            data[len(data) - 1]['venues'].append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': num_upcoming_shows
            })
        else:
            data.append({
                'city': venue.city,
                'state': venue.state,
                'venues': [{
                    'id': venue.id,
                    'name': venue.name,
                    'num_upcoming_shows': num_upcoming_shows
                }]
            })
            area = venue.city + venue.state
    return render_template('pages/venues.html', areas=data)


# Search a venue
@app.route('/venues/search', methods=['POST'])
def search_venues():
    # Searches for a venue by a given search term
    # Queries
    search_query = db.session.query(Venue).filter(
        Venue.name.ilike(f'%{search_term}%')).all()

    search_term = request.form.get('search_term', '')

    upcoming_shows = db.session.query(Show).filter(
        Show.venue_id==1).filter(Show.show_time>datetime.now()).all()

    # Variables
    data = []
    response = {}

    # Formating data
    for _row in search_query:
        venue_shows = db.session.query(Show).filter_by(
            venue_id=_row.id).all()
        data.append({
            'id': _row.id,
            'name': _row.name,
            'num_upcomming_shows': len(upcoming_shows)
        })

    response = {
        'count': len(search_query),
        'data': data
    }
    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the artist page with the given venue_id
    # Queries
    venue = db.session.query(Venue).filter_by(
        id=venue_id).first()

    venue_shows = db.session.query(Show).filter_by(
        venue_id=venue_id).all()

    past_shows_query = db.session.query(Show).join(Artist).filter(
        Show.venue_id==venue_id).filter(
        Show.show_time<=datetime.now()).all()

    upcoming_shows_query = db.session.query(Show).join(Artist).filter(
        Show.venue_id==venue_id).filter(
        Show.show_time>datetime.now()).all()

    # Variables
    past_shows = []
    upcoming_shows = []
    data = {}

    # Formating data
    for show in past_shows_query:
        past_shows.append({
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.show_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    for show in upcoming_shows_query:
        upcoming_shows.append({
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.show_time.strftime("%Y-%m-%d %H:%M:%S")
        })

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres":  venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # Creates new venue
    # Variables
    error = False
    form = VenueForm(request.form)

    # Formating data
    new_venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        website=form.website.data,
        image_link=form.image_link.data,
        seeking_talent=form.seeking_talent.data == 'True',
        seeking_description=form.seeking_description.data,
    )

    # Updating database
    try:
        db.session.add(new_venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    # Show result message
    if not error:
        flash(f"Venue {request.form['name']} was successfully listed!")
        return render_template('pages/home.html')
    else:
        flash(f"An error occurred. Venue {request.form['name']} could not be listed.")
        return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # Edits existing venue data
    # Query
    venue = db.session.query(Venue).filter_by(id=venue_id).first()

    # Redirect to error page if nothing found
    if not venue:
        return render_template('errors/404.html')

    # Variables
    form = VenueForm()

    # Formating data
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    #Queries
    venue = db.session.query(Venue).filter_by(id=venue_id).first()

    if not venue:
        return render_template('errors/404.html')
    
    # Variables
    form = VenueForm()

    # Updating database
    try:
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.genres = form.genres.data
        venue.facebook_link = form.facebook_link.data
        venue.website = form.website.data
        venue.image_link = form.image_link.data
        venue.seeking_talent = form.seeking_talent.data == 'True'
        venue.seeking_description = form.seeking_description.data
        db.session.commit()

    except:
        flash(f"An error occurred. Venue {request.form['name']} could not be updated.")
        db.session.rollback()
        return redirect(url_for('show_venue', venue_id=venue_id))

    finally:
        flash(f"Venue {request.form['name']} was successfully updated.")
        db.session.close()
        return redirect(url_for('show_venue', venue_id=venue_id))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # Deletes a venue
    # Variables
    error = False

    # Updating database
    try:
        db.session.query(Venue).filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    # Show result message
    if not error:
        flash(f'Venue {venue_id} was successfully deleted.')
        return redirect(url_for('index'))
    else:
        flash(f'An error occurred. Venue {venue_id} could not be deleted.')
        return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # Shows all artists
    # Queries
    all_artists = db.session.query(Artist).all()

    # Variables
    data = []

    # Formating data
    for _row in all_artists:
        data.append({
            "id": _row.id,
            "name": _row.name
        })
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # Seraches for an artist per search term
    # Queries
    search_term = request.form.get('search_term', '')
    search_query = db.session.query(Artist).filter(
        Artist.name.ilike(f'%{search_term}%')).all()

    # Variables
    data = []
    response = {}

    # Formating data
    for _row in search_query:
        artist_shows = db.session.query(Show).filter_by(
            artist_id=_row.id).all()
        data.append({
            'id': _row.id,
            'name': _row.name,
            'num_upcomming_shows': len(db.session.query(Show).filter(
                Show.artist_id == result.id).filter(
                Show.start_time > datetime.now()).all())
        })

    response = {
        'count': len(search_query),
        'data': data
    }

    return render_template(
        'pages/search_artists.html',
        results=response,
        search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given venue_id
    # Queries
    artist = db.session.query(Artist).filter_by(id=artist_id).first()

    past_shows_query = db.session.query(Show).join(Venue).filter(
        Show.artist_id==artist_id).filter(
        Show.show_time<=datetime.now()).all()

    upcoming_shows_query = db.session.query(Show).join(Venue).filter(
        Show.artist_id==artist_id).filter(
        Show.show_time>datetime.now()).all()

    # Variables
    past_shows = []
    upcoming_shows = []
    data = {}

    # Past shows data
    for show in past_shows_query:
        past_shows.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.show_time.strftime('%Y-%m-%d %H:%M:%S')
            })

    # Upcoming shows data
    for show in upcoming_shows_query:
        upcoming_shows.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.show_time.strftime('%Y-%m-%d %H:%M:%S')
            })

    # Artist data
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }
    return render_template('pages/show_artist.html', artist=data)



@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # Edit artist existing data
    # Query
    artist = db.session.query(Artist).filter_by(id=artist_id).first()

    # Redirect to error page if nothing found
    if not artist:
        return render_template('errors/404.html')

    # Variables
    form = ArtistForm()

    # Formating data
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    #Queries
    artist = db.session.query(Artist).filter_by(id=artist_id).first()

    if not artist:
        return render_template('errors/404.html')
    
    # Variables
    form = ArtistForm()

    # Updating database
    try:
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.genres = form.genres.data
        artist.facebook_link = form.facebook_link.data
        artist.website = form.website.data
        artist.image_link = form.image_link.data
        artist.seeking_venue = form.seeking_venue.data == 'True'
        artist.seeking_description = form.seeking_description.data

        db.session.commit()

    except:
        flash(f"An error occurred. Artist {request.form['name']} could not be updated.")
        db.session.rollback()
        return redirect(url_for('show_artist', artist_id=artist_id))

    finally:
        db.session.close()
        flash(f"Artist {request.form['name']} was succesfully updated.")
        return redirect(url_for('show_artist', artist_id=artist_id))


    return redirect(url_for('show_artist', artist_id=artist_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
# Creates new artist
def create_artist_submission():
     # Variables
    error = False
    form = ArtistForm(request.form)
    print(form.seeking_venue.data)
    # Formating data
    new_artist = Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        website=form.website.data,
        image_link=form.image_link.data,
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data,
    )

    # Updating database
    try:
        db.session.add(new_artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    # Show result message
    if not error:
        flash(f"Artist {request.form['name']} was successfully created!")
        return render_template('pages/home.html')
    else:
        flash(f"An error occurred. Artist {request.form['name']} could not be created.")
        return render_template('pages/home.html')


@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    # Detetes artist
    # Variables
    error = False

    # Updating database
    try:
        db.session.query(Artist).filter_by(id=artist_id).delete()
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    # Show result message
    if not error:
        flash(f'Artist {artist_id} was successfully deleted.')
        return redirect(url_for('index'))
    else:
        flash(f'An error occurred. Venue {artist_id} could not be deleted.')
        return redirect(url_for('index'))    

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # Query
    shows = db.session.query(Show).join(Artist).join(Venue).all()

    # Variables
    data = []

    # Formating data
    for show in shows:
        data.append({
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_image_link": show.artist.image_link,
            "start_time": show.show_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['GET', 'POST'])
def create_show_submission():

    # Varables
    error = False
    form = ShowForm(request.form)

    #Formating data
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                new_show = Show(
                    form.venue_id.data,
                    form.artist_id.data,
                    form.start_time.data
                )
                db.session.add(new_show)
                db.session.commit()
            except:
                error = True

                db.session.rollback()
                print(sys.exc_info())
            finally:
                db.session.close()
    if not error:
         flash('Show was successfully created!')
         return render_template('pages/home.html')
    else:
        flash('An error occurred. Show could not be listed.')
        return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(host='192.168.1.173', port=8000)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
