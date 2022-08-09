#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)


# TODO: connect to a local postgresql database
# ANS => i have added a local database called fyyur
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))
    # ANS => most missing fields are without nullable being set to false

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(120), nullable=False)
    website_link = db.Column(db.String(120))
    talent = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)
    no_of_upcoming_shows = db.Column(db.Integer, default=0)
    no_of_past_shows = db.Column(db.Integer, default=0)
    shows = db.relationship('Show', backref='venue', lazy=True,
                        cascade="save-update, merge, delete")


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)

    # ANS: => most missing fields are without nullable being set to false
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(120))
    venue = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)
    no_of_upcoming_shows = db.Column(db.Integer, default=0)
    no_of_past_shows = db.Column(db.Integer, default=0)
    shows = db.relationship('Show', backref='artist', lazy=True,
                        cascade="save-update, merge, delete")

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    upcoming = db.Column(db.Boolean, nullable=False, default=True)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    availableVenues = Venue.query.order_by(db.desc(Venue.id)).limit(10).all()
    availableArtists = Artist.query.order_by(
        db.desc(Artist.id)).limit(10).all()
    return render_template('pages/home.html', venues=availableVenues, artists=availableArtists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    venue_areas = db.session.query(Venue.city, Venue.state).group_by(Venue.state,
    Venue.city).all()
    data = []
    for area in venue_areas:
        venues = db.session.query(Venue.id, Venue.name,
        Venue.no_of_upcoming_shows).filter(Venue.city == area[0], Venue.state == area[1]).all()
        data.append({
            "city": area[0],
            "state": area[1],
            "venues": []
        })
        for venue in venues:
            data[-1]["venues"].append({
                "id": venue[0],
                "name": venue[1],
                "num_upcoming_shows": venue[2]
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    results = Venue.query.filter(Venue.name.ilike('%{}%'.format(request.form['search_term']))).all()
    response={
        "count": len(results),
        "data": []
        }
    for venue in results:
        response["data"].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": venue.no_of_upcoming_shows
        })
    
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    past_shows = []
    upcoming_shows = []
    shows = venue.shows
    for show in shows:
        show_info ={
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": str(show.start_time)
        }
        now = datetime.now()
        if(show.start_time > now):
            upcoming_shows.append(show_info)
        else:
            past_shows.append(show_info)

    data={
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres.split(','),
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.talent,
        "seeking_description": venue.description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "no_of_past_shows": len(past_shows),
        "no_of_upcoming_shows": len(upcoming_shows)
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
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    formData = request.form
    new_venue = Venue(
        name = formData['name'],
        city = formData['city'],
        state = formData['state'],
        address = formData['address'],
        phone = formData['phone'],
        genres = formData.getlist('genres'),
        facebook_link = formData['facebook_link'],
        website_link = formData['website_link'],
        image_link = formData['image_link'],
        talent = bool(formData.getlist('seeking_talent')),
        description = formData['seeking_description']
    )
    try:
        db.session.add(new_venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
        db.session.close()
    return redirect(url_for('index'))


@app.route('/venues/delete', methods=['POST'])
def delete_venue():
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    # this will get the data coming from the venue page for delete
    venue_id = request.get_json()['delete']
    # this will get the venue using the id on the venue table 
    venue = Venue.query.get(venue_id)
    venueName = venue.name
    try:
        # then we call db.sesion.delete to delete the row with the ID
        db.session.delete(venue)
        # this wont delete the data until we commit it
        db.session.commit()
        # this will flash a message 
        flash('Venue ' + venueName + ' was successfully deleted!')
    except:
        db.session.rollback()
        # this will flash a message
        flash('please try again. Venue ' + venueName + ' could not be deleted.')
    finally:
        db.session.close()
        # this will return to the home page using redirect and url_for
    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = Artist.query.with_entities(Artist.id, Artist.name).all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    results = Artist.query.filter(Artist.name.ilike('%{}%'.format(request.form['search_term']))).all()

    response={
        "count": len(results),
        "data": []
    }
    for artist in results:
        response['data'].append({
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": artist.no_of_upcoming_shows,
        })
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get(artist_id)
    shows = artist.shows
    past_shows = []
    upcoming_shows = []
    for show in shows:
        show_info = {
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": str(show.start_time)
        }
        now = datetime.now()
        if(show.start_time > now):
            upcoming_shows.append(show_info)
        else:
            past_shows.append(show_info)
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres.split(','), 
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "venue": artist.venue,
        "description":artist.description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    artist_info = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres.split(','),
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "website_link": artist.website_link,
        "image_link": artist.image_link,
        "seeking_venue": artist.venue,
        "seeking_description": artist.description,
        "image_link": artist.image_link
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist_info)


@app.route('/artists/<artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.facebook_link = request.form['facebook_link']
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form['image_link']
    artist.website_link = request.form['website_link']
    artist.talent = bool(request.form.getlist('seeking_talent'))
    artist.description = request.form['seeking_description']
    try:
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully edited!')
    except:
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist' + request.form['name'] + ' could not be edited.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    venue_info={
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres.split(','),
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website_link": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.talent,
        "seeking_description": venue.description,
        "image_link": venue.image_link
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue_info)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.facebook_link = request.form['facebook_link']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.website_link = request.form['website_link']
    venue.talent = bool(request.form.getlist('seeking_talent'))
    venue.description = request.form['seeking_description']
    try:
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully edited!')
    except:
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue' + request.form['name'] + ' could not be edited.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    formData = request.form
    new_artist = Artist(
        name = formData['name'],
        city = formData['city'],
        state = formData['state'],
        phone = formData['phone'],
        genres = formData.getlist('genres'),
        facebook_link = formData['facebook_link'],
        website_link = formData['website_link'],
        image_link = formData['image_link'],
        venue = bool(formData.getlist('seeking_venue')),
        description = formData['seeking_description']
    )
    try:
        db.session.add(new_artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist' + request.form['name'] + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
        db.session.close()
    return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    shows_list = Show.query.all()
    data = []
    for show in shows_list:
        if(show.upcoming):
            data.append({
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": str(show.start_time)
            })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    formData = request.form
    dateAndTime = formData['start_time']
    artistId = formData['artist_id']
    venueId = formData['venue_id']
    upcoming = True
    new_show = Show(
        artist_id = artistId,
        venue_id = venueId,
        start_time =  dateAndTime,
        upcoming = upcoming
    )
    try:
        db.session.add(new_show)
        # update venue and artist table
        updated_artist = Artist.query.get(artistId)
        updated_venue = Venue.query.get(venueId)
        if(upcoming):
            updated_artist.no_of_upcoming_shows += 1
            updated_venue.no_of_upcoming_shows += 1
        else:
            updated_artist.no_of_past_shows += 1
            updated_venue.no_of_past_showsSS += 1
        # on successful db insert, flash success
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('Show could not be listed. please make sure that your ids are correct')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
        db.session.close()
    return redirect(url_for('index'))


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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
