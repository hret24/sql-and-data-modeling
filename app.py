#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import (
  Flask, render_template, 
  request, 
  Response, 
  flash, 
  redirect, 
  url_for, 
  jsonify
)
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
  venues = Venue.query.all()
  locations = set()

  for venue in venues:
    locations.add((venue.city, venue.state))

  for location in locations:
    data.append({
      "city": location[0],
      "state": location[1],
      "venues": []
    })

  for venue in venues:
    num_upcoming_shows = 0

    shows = Show.query.filter_by(venue_id=venue.id).all()
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
    search_term = request.form.get('search_term', '').strip()

    matching_venues = (
        db.session.query(Venue)
        .filter(func.lower(Venue.name).contains(func.lower(search_term)))
        .all()
    )

    response = {
        "count": len(matching_venues),
        "data": []
    }

    for venue in matching_venues:
        upcoming_shows_count = db.session.query(Show).filter(
            Show.venue_id == venue.id,
            Show.start_time > datetime.utcnow()
        ).count()

        response["data"].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": upcoming_shows_count
        })

    return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)

    past_shows = []
    upcoming_shows = []

    for show in venue.shows:
      show_info = {
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
      }
      if show.start_time <= datetime.now():
        past_shows.append(show_info)
      else:
        upcoming_shows.append(show_info)

    data = venue.__dict__
    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form, meta={'csrf': False})
    if form.validate():
        try:
            new_venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                website_link=form.website_link.data,
                genres=form.genres.data,  # Retrieve the list of selected genres
                seeking_talent=form.seeking_talent.data,  # Boolean
                seeking_description=form.seeking_description.data or ''  # Default to empty string if no data
            )
            db.session.add(new_venue)
            db.session.commit()
            flash(f'Venue {new_venue.name} was successfully listed!')
            return redirect(url_for('venues'))  # Redirect to the venues page after success
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred. Venue {form.name.data} could not be listed. Error: {e}')
            return render_template('forms/new_venue.html', form=form)  # Re-render the form with errors
        finally:
            db.session.close()
    else:
        # Collect errors from form validation
        errors = ", ".join([f"{field}: {', '.join(errs)}" for field, errs in form.errors.items()])
        flash(f'Please fix the following errors: {errors}')
        return render_template('forms/new_venue.html', form=form)  # Re-render the form with validation errors

    # Fallback return to ensure response is always provided
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if error:
        return jsonify({'success': False, 'message': 'Venue was not successfully deleted!'}), 500
    else:
        return jsonify({'success': True, 'message': 'Venue was successfully deleted!'}), 200

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = Artist.query.all()

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
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description
    } for artist in data]

    return render_template('pages/artists.html', artists=artists_data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    
    artists_query = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

    results = []
    for artist in artists_query:
        num_upcoming_shows = Show.query.filter(Show.artist_id == artist.id, Show.start_time > datetime.utcnow()).count()

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
    artist = Artist.query.get_or_404(artist_id)

    past_shows = []
    upcoming_shows = []

    for show in artist.shows:
        show_info = {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        }
        if show.start_time <= datetime.now():
            past_shows.append(show_info)
        else:
            upcoming_shows.append(show_info)

    artist_data = artist.__dict__.copy()  
    artist_data['past_shows'] = past_shows
    artist_data['upcoming_shows'] = upcoming_shows
    artist_data['past_shows_count'] = len(past_shows)
    artist_data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    artist = Artist.query.get(artist_id)

    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website_link.data = artist.website_link
    form.facebook_link.data = artist.facebook_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    form.image_link.data = artist.image_link
    form.genres.data = artist.genres

    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
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
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    db.session.commit()
  except: 
    error = True
    db.session.rollback()     
  finally:
    db.session.close()
  if error: 
    flash('An error occurred. Artist ' + form.name.data + ' could not be updated.')
    return render_template('forms/new_artist.html', form=form)
  else:
    flash('Artist ' + form.name.data + ' was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

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
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
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
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    db.session.commit()
  except: 
    error = True
    db.session.rollback()     
  finally:
    db.session.close()
  if error: 
    flash('An error occurred. Venue ' + form.name.data + ' could not be updated.')
    return render_template('forms/new_venue.html', form=form)
  else:
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
    form = ArtistForm(request.form, meta={'csrf': False})  # Load form with CSRF disabled for simplicity
  
    if form.validate():
        try:
            new_artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres=form.genres.data,
                facebook_link=form.facebook_link.data,
                image_link=form.image_link.data,
                website_link=form.website_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data
            )
            db.session.add(new_artist)
            db.session.commit()
            flash(f"Artist '{new_artist.name}' was successfully listed!")
            return redirect(url_for('index'))  
        except Exception as e:
            db.session.rollback() 
            flash(f"An error occurred. Artist '{form.name.data}' could not be listed. Error: {e}")
            return render_template('forms/new_artist.html', form=form)  
        finally:
            db.session.close()
    else:
      errors = ", ".join([f"{field}: {error}" for field, errs in form.errors.items() for error in errs])
      flash(f'Please fix the following errors: {errors}') 
      return render_template('forms/new_artist.html', form=form)

#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
    shows = Show.query.join(Venue).join(Artist).all()

    data = []
    for show in shows:
        show_data = {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,  
            "artist_id": show.artist_id,
            "artist_name": show.artist.name, 
            "artist_image_link": show.artist.image_link,  
            "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')  
        }
        data.append(show_data)

    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form, meta={'csrf': False})
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
        flash('An error occurred. Show could not be listed.', category='error')
        return render_template('forms/new_show.html', form=form)
      else:
        flash('Show was successfully listed!')
        return render_template('pages/home.html')
    else:
      for field, errors in form.errors.items():
          for error in errors:
              flash(f"Error in {field}: {error}", category='error')
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

