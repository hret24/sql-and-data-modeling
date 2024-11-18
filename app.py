#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import Venue, Artist, Show, db
import os
from sqlalchemy import func
from flask_migrate import Migrate


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database DONE


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

with app.app_context():
    db.create_all()

#  Venues 
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  # get all venues
  venues = Venue.query.all()

  # Use set so there are no duplicate venues
  locations = set()

  for venue in venues:
    # add city / state tuples
    locations.add((venue.city, venue.state))

  # for each unique city / state, add veneus
  for location in locations:
    data.append({
      "city": location[0],
      "state": location[1],
      "venues": []
    })

  for venue in venues:
    num_upcoming_shows = 0

    shows = Show.query.filter_by(venue_id=venue.id).all()
    # get current date to filter num_upcoming_shows
    current_date = datetime.now()

    for show in shows:
      if show.start_time > current_date:
        num_upcoming_shows += 1
    

    for venue_location in data:
      if venue.state == venue_location['state'] and venue.city == venue_location['city']:
        venue_location['venues'].append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": num_upcoming_shows
        })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # Retrieve the search term from the form input
    search_term = request.form.get('search_term', '').strip()

    # Perform a case-insensitive search for venues
    matching_venues = (
        db.session.query(Venue)
        .filter(func.lower(Venue.name).contains(func.lower(search_term)))
        .all()
    )

    # Prepare the response dictionary
    response = {
        "count": len(matching_venues),
        "data": []
    }

    for venue in matching_venues:
        # Count upcoming shows for the venue
        upcoming_shows_count = db.session.query(Show).filter(
            Show.venue_id == venue.id,
            Show.start_time > datetime.utcnow()
        ).count()

        # Add venue information to the response
        response["data"].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": upcoming_shows_count
        })

    # Render the search results in the template
    return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
# Fetch venue details from the database
    venue = Venue.query.get_or_404(venue_id)

    # Query for past and upcoming shows
    past_shows_query = db.session.query(Show, Artist).join(Artist).filter(
        Show.venue_id == venue_id,
        Show.start_time < datetime.utcnow()
    ).all()

    upcoming_shows_query = db.session.query(Show, Artist).join(Artist).filter(
        Show.venue_id == venue_id,
        Show.start_time >= datetime.utcnow()
    ).all()

    # Format past shows
    past_shows = [
        {
            "artist_id": show.Artist.id,
            "artist_name": show.Artist.name,
            "artist_image_link": show.Artist.image_link,
            "start_time": show.Show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        }
        for show in past_shows_query
    ]

    # Format upcoming shows
    upcoming_shows = [
        {
            "artist_id": show.Artist.id,
            "artist_name": show.Artist.name,
            "artist_image_link": show.Artist.image_link,
            "start_time": show.Show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        }
        for show in upcoming_shows_query
    ]

    # Prepare venue data for rendering
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,  
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_for_artist,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    # Render the venue page
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

# @app.route('/venues/create', methods=['POST'])
# def create_venue_submission():
#   # TODO: insert form data as a new Venue record in the db, instead
#   # TODO: modify data to be the data object returned from db insertion

#   # on successful db insert, flash success
#   flash('Venue ' + request.form['name'] + ' was successfully listed!')
#   # TODO: on unsuccessful db insert, flash an error instead.
#   # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
#   # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
#   return render_template('pages/home.html')

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        # Create a new Venue instance without specifying the id
        new_venue = Venue(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            address=request.form['address'],
            phone=request.form['phone'],
            image_link=request.form['image_link'],
            facebook_link=request.form['facebook_link'],
            website_link=request.form['website_link'],
            genres=request.form.getlist('genres'),  # Assuming genres are passed as a list
            seeking_for_artist=bool(request.form.get('seeking_for_artist')),  # Convert to boolean
            seeking_description=request.form.get('seeking_description', '')  # Default to empty string
        )
        
        db.session.add(new_venue)
        db.session.commit()
        flash(f'Venue {new_venue.name} was successfully listed!')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred. Venue {request.form["name"]} could not be listed. Error: {e}')
    finally:
        db.session.close()
        
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # Query the database to get all artists
    data = Artist.query.all()

    # Convert the result into a list of dictionaries with the necessary details
    artists_data = [{
        "id": artist.id,
        "name": artist.name,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "genres": ', '.join(artist.genres) if artist.genres else '',
        "facebook_link": artist.facebook_link,
        "image_link": artist.image_link,
        "website_link": artist.website_link,
        "seeking_for_venue": artist.seeking_for_venue,
        "seeking_description": artist.seeking_description
    } for artist in data]

    # Return the artists data to the template
    return render_template('pages/artists.html', artists=artists_data)

# @app.route('/artists/search', methods=['POST'])
# def search_artists():
#   # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
#   # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
#   # search for "band" should return "The Wild Sax Band".
#   response={
#     "count": 1,
#     "data": [{
#       "id": 4,
#       "name": "Guns N Petals",
#       "num_upcoming_shows": 0,
#     }]
#   }
#   return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    
    # Perform case-insensitive search for artists based on the search term
    artists_query = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

    # Prepare the list of artists with the number of upcoming shows
    results = []
    for artist in artists_query:
        # Count the number of upcoming shows for the artist (shows that are after the current date)
        num_upcoming_shows = Show.query.filter(Show.artist_id == artist.id, Show.start_time > datetime.utcnow()).count()

        # Add the artist's data and upcoming shows count to the result
        results.append({
            'id': artist.id,
            'name': artist.name,
            'num_upcoming_shows': num_upcoming_shows,
        })

    response = {
        'count': len(results),
        'data': results,
    }

    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # Get the artist details from the database
    artist = Artist.query.get(artist_id)

    if not artist:
        return render_template('errors/404.html')  # or some error handling page
    
    # Get past shows (shows that have already passed)
    past_shows = Show.query.filter(Show.artist_id == artist.id, Show.start_time < datetime.utcnow()).all()

    # Get upcoming shows (shows that are in the future)
    upcoming_shows = Show.query.filter(Show.artist_id == artist.id, Show.start_time > datetime.utcnow()).all()

    # Convert the shows data into the required format for rendering
    past_shows_data = [{
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,  # Assuming there's an 'image_link' field in the 'venue' model
        "start_time": show.start_time.isoformat(),
    } for show in past_shows]

    upcoming_shows_data = [{
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": show.start_time.isoformat(),
    } for show in upcoming_shows]

    # Prepare the artist data
    artist_data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "facebook_link": artist.facebook_link,
        "image_link": artist.image_link,
        "website": artist.website_link,
        "seeking_venue": artist.seeking_for_venue,
        "seeking_description": artist.seeking_description,
        "past_shows": past_shows_data,
        "upcoming_shows": upcoming_shows_data,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    # Fetch the artist details from the database (or use the mock `artist` data)
    # You would typically query the database for the artist like this:
    artist = Artist.query.get(artist_id)


    # Populate the form with the artist's current data
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website_link.data = artist.website_link
    form.facebook_link.data = artist.facebook_link
    form.seeking_venue.data = artist.seeking_for_venue
    form.seeking_description.data = artist.seeking_description
    form.image_link.data = artist.image_link
    form.genres.data = artist.genres  # This should be a list, which SelectMultipleField expects

    return render_template('forms/edit_artist.html', form=form, artist=artist)


# @app.route('/artists/<int:artist_id>/edit', methods=['POST'])
# def edit_artist_submission(artist_id):
#     form = ArtistForm(request.form)

#     artist = Artist.query.get(artist_id)


#     if form.validate_on_submit():

      
#         # Update artist data based on the form input
#         artist['name'] = form.name.data
#         artist['city'] = form.city.data
#         artist['state'] = form.state.data
#         artist['phone'] = form.phone.data
#         artist['website'] = form.website_link.data
#         artist['facebook_link'] = form.facebook_link.data
#         artist['seeking_venue'] = form.seeking_venue.data
#         artist['seeking_description'] = form.seeking_description.data
#         artist['image_link'] = form.image_link.data
#         artist['genres'] = form.genres.data  # This will update the list of genres

#         # Save the updated artist to the database (replace with your actual database logic)
#         db.session.commit()

#         # After updating the artist, redirect to the artist's page
#         return redirect(url_for('show_artist', artist_id=artist_id))

#     # If the form wasn't valid, re-render the form with validation errors
#     return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  form = ArtistForm()
  try: 
    artist = Artist.query.get(artist_id)
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.image_link = form.image_link.data
    artist.facebook_link = form.facebook_link.data
    artist.website_link = form.website_link.data
    artist.genres = form.genres.data
    artist.seeking_for_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    db.session.commit()
  except: 
    error = True
    db.session.rollback()     
  finally:
    db.session.close()
  if error: 
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Artist ' + form.name.data + ' could not be updated.')
    return render_template('forms/new_artist.html', form=form)
  else:
    # on successful db insert, flash success
    flash('Artist ' + form.name.data + ' was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))


# @app.route('/venues/<int:venue_id>/edit', methods=['GET'])
# def edit_venue(venue_id):
#   form = VenueForm()
#   venue={
#     "id": 1,
#     "name": "The Musical Hop",
#     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
#     "address": "1015 Folsom Street",
#     "city": "San Francisco",
#     "state": "CA",
#     "phone": "123-123-1234",
#     "website": "https://www.themusicalhop.com",
#     "facebook_link": "https://www.facebook.com/TheMusicalHop",
#     "seeking_talent": True,
#     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
#     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
#   }
#   # TODO: populate form with values from venue with ID <venue_id>
#   return render_template('forms/edit_venue.html', form=form, venue=venue)

# @app.route('/venues/<int:venue_id>/edit', methods=['POST'])
# def edit_venue_submission(venue_id):
#   # TODO: take values from the form submitted, and update existing
#   # venue record with ID <venue_id> using the new attributes
#   return redirect(url_for('show_venue', venue_id=venue_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # venue_1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name 
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.image_link.data = venue.image_link
  form.facebook_link.data =  venue.facebook_link
  form.website_link.data = venue.website_link
  form.genres.data = venue.genres
  form.seeking_talent.data = venue.seeking_for_artist
  form.seeking_description.data = venue.seeking_description
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  error = False
  try: 
    venue = Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.image_link = form.image_link.data
    venue.facebook_link = form.facebook_link.data
    venue.website_link = form.website_link.data
    venue.genres = form.genres.data
    venue.seeking_for_artist = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    db.session.commit()
  except: 
    error = True
    db.session.rollback()     
  finally:
    db.session.close()
  if error: 
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Venue ' + form.name.data + ' could not be updated.')
    return render_template('forms/new_venue.html', form=form)
  else:
    # on successful db insert, flash success
    flash('Venue ' + form.name.data + ' was successfully updated!')
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
  error = False
  form = ArtistForm(request.form)  # Create the form object with the submitted data
  try: 
    artist = Artist(
      name=form.name.data, 
      city=form.city.data, 
      state=form.state.data, 
      phone=form.phone.data, 
      image_link=form.image_link.data, 
      facebook_link=form.facebook_link.data, 
      website_link=form.website_link.data, 
      genres=form.genres.data, 
      seeking_for_venue=form.seeking_venue.data, 
      seeking_description=form.seeking_description.data)

    db.session.add(artist)
    db.session.commit()
  except: 
    error = True
    db.session.rollback()     
  finally:
    db.session.close()
  if error: 
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    return render_template('forms/new_artist.html', form=form)
  else:
    # on successful db insert, flash success
    flash('Artist ' + form.name.data + ' was successfully listed!')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # Query the database for all shows, join with venue and artist tables
    shows = Show.query.join(Venue).join(Artist).all()

    # Create a list of show data to pass to the template
    data = []
    for show in shows:
        show_data = {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,  # Accessing venue name through the relationship
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,  # Accessing artist name through the relationship
            "artist_image_link": show.artist.image_link,  # Accessing artist image link
            "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')  # Formatting start_time
        }
        data.append(show_data)

    # Pass the list of shows data to the template
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

# @app.route('/shows/create', methods=['POST'])
# def create_show_submission():
#   # called to create new shows in the db, upon submitting new show listing form
#   # TODO: insert form data as a new Show record in the db, instead

#   # on successful db insert, flash success
#   flash('Show was successfully listed!')
#   # TODO: on unsuccessful db insert, flash an error instead.
#   # e.g., flash('An error occurred. Show could not be listed.')
#   # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
#   return render_template('pages/home.html')

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm()
    error = False
    if form.validate_on_submit():
      try: 
        show = Show(
          artist_id=form.artist_id.data, 
          venue_id=form.venue_id.data, 
          start_time=form.start_time.data
        )
        db.session.add(show)
        db.session.commit()
      except: 
        error = True
        db.session.rollback()     
      finally:
        db.session.close()
      if error: 
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred. Show could not be listed.', category='error')
        return render_template('forms/new_show.html', form=form)
      else:
        # on successful db insert, flash success
        flash('Show was successfully listed!')
        return render_template('pages/home.html')
    else:
    # Handle form validation errors
      for field, errors in form.errors.items():
          for error in errors:
              flash(f"Error in {field}: {error}", category='error')
      # Re-render the form with validation errors
      return render_template('forms/new_show.html', form=form)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)

