import dateutil.parser
import babel
from flask import Blueprint, render_template, request, flash, redirect, url_for

from models import db, Venue, Artist, Show
from forms import ArtistForm, datetime


artist = Blueprint(
    "artist", __name__, static_folder="static", template_folder="templates"
)


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


@artist.route("/artists")
def artists():

    data = list()

    artists = Artist.query.group_by(Artist.id, Artist.name).all()

    for artist in artists:

        data.append({"id": artist.id, "name": artist.name})
    return render_template("pages/artists.html", artists=data)


@artist.route("/artists/search", methods=["POST"])
def search_artists():

    artist_details = list()
    # Get search item from form
    search_term = request.form.get("search_term", " ")
    # select match of search item using ilike statement to make match case insensitive
    artists = Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).all()
    upcoming_shows = (
        Show.query.join(Venue, Artist)
        .filter(Show.artist_id == Artist.id, Show.start_time > datetime.now())
        .all()
    )
    for artist in artists:
        artist_details.append(
            {
                "id": artist.id,
                "name": artist.name,
                # Get number of up future shows using len
                "num_upcoming_shows": len(upcoming_shows),
            }
        )

    response = {
        # Get number of match search item
        "count": len(artists),
        "data": artist_details,
    }
    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@artist.route("/artists/<int:artist_id>")
def show_artist(artist_id):

    past_shows = list()
    upcoming_shows = list()

    artist = Artist.query.get(artist_id)

    shows_past = (
        Show.query.join(Venue, Artist)
        .filter(Show.venue_id == Venue.id, Show.start_time < datetime.now())
        .all()
    )

    future_shows = (
        Show.query.join(Venue, Artist)
        .filter(Show.venue_id == Venue.id, Show.start_time > datetime.now())
        .all()
    )

    for show in shows_past:
        past_shows.append(
            {
                "venue_id": show.venue_id,
                "venue_name": show.Venue.name,
                "Venue_image_link": show.Venue.image_link,
                "start_time": format_datetime(str(show.start_time)),
            }
        )

    for shows in future_shows:
        upcoming_shows.append(
            {
                "venue_id": shows.venue_id,
                "venue_name": shows.Venue.name,
                "venue_image_link": shows.Venue.image_link,
                "start_time": format_datetime(str(shows.start_time)),
            }
        )

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(shows_past),
        "upcoming_shows_count": len(future_shows),
    }

    return render_template("pages/show_artist.html", artist=data)


@artist.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = ArtistForm()

    artist = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    }

    # Get artist by id
    artist = Artist.query.get(artist_id)
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@artist.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):

    form = ArtistForm(request.form)
    artist = Artist.query.get(artist_id)

    try:
        artist.name = form.name.data
        artist.state = form.state.data
        artist.city = form.city.data
        artist.phone = form.phone.data
        artist.genres = form.genres.data
        artist.facebook_link = form.facebook_link.data
        artist.image_link = form.image_link.data
        artist.website_link = form.website_link.data
        # convert form data from seeking_talent to boolean
        artist.seeking_venue = True if form.seeking_venue.data == "Yes" else False
        artist.seeking_description = form.seeking_description.data

        db.session.commit()
        flash("Artist " + artist.name + " was successfully updated")
    except:
        flash("Artist " + artist.name + "  not successfully updated")
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for("show_artist", artist_id=artist_id))


@artist.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm(request.form)
    try:
        venue = Venue()
        form.populate_obj(venue)
        db.session.add(venue)
        db.session.commit()
        flash("Form input is valid")
    except:
        flash("Form input is invalid")
        db.session.rollback()
    finally:
        db.session.close()
    return render_template("forms/new_artist.html", form=form)


@artist.route("/artists/create", methods=["POST"])
def create_artist_submission():

    form = ArtistForm(request.form)

    try:

        name = form.name.data
        state = form.state.data
        city = form.city.data
        phone = form.phone.data
        genres = form.genres.data
        facebook_link = form.facebook_link.data
        image_link = form.image_link.data
        website_link = form.website_link.data
        # convert form data from seeking_talent to boolean
        seeking_venue = True if form.seeking_venue.data == "Yes" else False
        seeking_description = form.seeking_description.data

        venue = Venue(
            name=name,
            state=state,
            city=city,
            phone=phone,
            genres=genres,
            facebook_link=facebook_link,
            image_link=image_link,
            website_link=website_link,
            seeking_talent=seeking_venue,
            seeking_description=seeking_description,
        )
        db.session.add(venue)
        db.session.commit()
        flash("Venue " + request.form["name"] + " was successfully listed!")
        return render_template("pages/home.html")
    except:
        flash("An error occurred creating the " + request.form["name"])
        db.session.rollback()
    finally:
        db.session.close()
    return render_template("pages/home.html")
