from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL, ValidationError
from enum import Enum
from custom_enums import Genre, State, FacebookURL

def validate_genres(form, field):
    for genre in field.data:
        if genre not in [g.value for g in Genre]:
            raise ValidationError(f"'{genre}' is not a valid genre.")

def validate_state(form, field):
    if field.data not in [state.value for state in State]:
        raise ValidationError(f"'{field.data}' is not a valid state.")

def validate_phone(form, field):
    phone_pattern = r"^\d{3}-?\d{3}-?\d{4}$"
    if not re.match(phone_pattern, field.data):
        raise ValidationError(
            f"'{field.data}' is not a valid phone number. Use the format XXX-XXX-XXXX."
        )

def validate_facebook_link(form, field):
    if not any(field.data.startswith(url.value) for url in FacebookURL):
        raise ValidationError(
            f"'{field.data}' is not a valid Facebook URL. It must start with one of the following: "
            f"{', '.join([url.value for url in FacebookURL])}"
        )
        
class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

def validate_genres(form, field):
    for genre in field.data:
        if genre not in [g.value for g in Genre]:
            raise ValidationError(f"'{genre}' is not a valid genre.")

class VenueForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(), validate_state],
        choices=State.choices()
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone', validators=[DataRequired(), validate_phone]
    ) 

    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired(), validate_genres],
        choices=Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL(), validate_facebook_link]
    )
    
    website_link = StringField(
        'website_link'
    )

    seeking_talent = BooleanField( 'seeking_talent' )

    seeking_description = StringField(
        'seeking_description'
    )

class ArtistForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(), validate_state],
        choices=State.choices()
    )
    phone = StringField(
        'phone', validators=[DataRequired(), validate_phone]
    ) 
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired(), validate_genres],
        choices=Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL(), validate_facebook_link]
    )

    website_link = StringField(
        'website_link'
    )

    seeking_venue = BooleanField( 'seeking_venue' )

    seeking_description = StringField(
            'seeking_description'
    )

