import dateutil.parser
import babel
from flask import( 
  Flask, 
  render_template,
  request, 
  flash,
  redirect,
  url_for
 )
import logging
from logging import Formatter, FileHandler
from models import db, Venue, Artist, Show
from flask_migrate import Migrate
from forms import VenueForm, ShowForm, ArtistForm, datetime



app = Flask(__name__)
app.config.from_object("config")
db.init_app(app)
migrate = Migrate(app, db)


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime


@app.route("/")
def index():
    return render_template("pages/home.html")


@app.route("/venues")
def venues():

    # initialize an empty list
    data = list()

    # initialize set
    city_states = set()

    all_venue = Venue.query.all()

    for venue in all_venue:
        # add elements to set
        city_states.add((venue.city, venue.state))

    for area in city_states:
        # getting tuple item at index
        data.append({"city": area[0], "state": area[1], "venues": list()})

    for venue in all_venue:
        future_shows = 0

        shows = Show.query.filter_by(venue_id=venue.id).all()

        # get number of upcoming shows
        for show in shows:
            if show.start_time > datetime.now():
                future_shows += 1

        for detail in data:
            if venue.city == detail["city"] and venue.state == detail["state"]:
                detail["venues"].append(
                    {"id": venue.id, "name": venue.name, "upcoming_show": future_shows}
                )

    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():

    venue_details = list()

    # Get search item from form
    search_term = request.form.get("search_term", " ")

    # select match of search item using ilike statement to make match case insensitive
    venues = Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all()

    upcoming_shows = (
        Show.query.join(Venue, Artist)
        .filter(Show.venue_id == Venue.id, Show.start_time > datetime.now())
        .all()
    )

    for venue in venues:
        venue_details.append(
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(upcoming_shows),
            }
        )

    response = {"count": len(venues), "data": venue_details}
    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):

    venue = Venue.query.get(venue_id)

    past_shows = list()
    upcoming_shows = list()

    # Get past and future shows
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
                "artist_id": show.artist_id,
                "artist_name": show.Artist.name,
                "artist_image_link": show.Artist.image_link,
                "start_time": format_datetime(str(show.start_time)),
            }
        )

    for shows in future_shows:
        upcoming_shows.append(
            {
                "artist_id": shows.artist_id,
                "artist_name": shows.Artist.name,
                "artist_image_link": shows.Artist.image_link,
                "start_time": format_datetime(str(shows.start_time)),
            }
        )

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
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(shows_past),
        "upcoming_shows_count": len(future_shows),
    }

    # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
    return render_template("pages/show_venue.html", venue=data)


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm(request.form)
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

    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():

    try:
        # collect form datas
        name = request.form.get("name", " ")
        state = request.form.get("state", " ")
        city = request.form.get("city", " ")
        address = request.form.get("address", " ")
        phone = request.form.get("phone", " ")
        genres = request.form.get("genres", " ")
        facebook_link = request.form.get("facebook_link", " ")
        image_link = request.form.get("image_link", " ")
        website_link = request.form.get("website_link", " ")
        # convert form data from seeking_talent to boolean
        seeking_talent = True if "seeking_talent" in request.form else False
        seeking_description = request.form.get("seeking_description", " ")

        venue = Venue(
            name=name,
            state=state,
            city=city,
            address=address,
            phone=phone,
            genres=genres,
            facebook_link=facebook_link,
            image_link=image_link,
            website_link=website_link,
            seeking_talent=seeking_talent,
            seeking_description=seeking_description,
        )
        db.session.add(venue)
        db.session.commit()
        flash("Venue " + request.form["name"] + " was successfully listed!")
    except:
        flash("Venue " + request.form["name"] + " was successfully listed!")
        db.session.rollback()
    finally:
        db.session.close()
    return render_template("pages/home.html")


# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):

    try:
        # Get venue by id
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash("Venue " + venue.name + " was successfully deleted")
    except:
        flash("Venue " + venue.name + " was successfully deleted")
        db.session.rollback()
    finally:
        db.session.close()

    return None


@app.route("/artists")
def artists():

    data = list()

    artists = Artist.query.group_by(Artist.id, Artist.name).all()

    for artist in artists:

        data.append({"id": artist.id, "name": artist.name})
    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():

    artist_details = list()
    search_term = request.form.get("search_term", " ")
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


@app.route("/artists/<int:artist_id>")
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

    # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
    return render_template("pages/show_artist.html", artist=data)


@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
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


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):

    artist = Artist.query.get(artist_id)

    try:
        # Get updated details from artist
        artist.name = request.form.get("name", " ")
        artist.state = request.form.get("state", " ")
        artist.city = request.form.get("city", " ")
        artist.phone = request.form.get("phone", " ")
        artist.genres = request.form.get("genres", " ")
        artist.facebook_link = request.form.get("facebook_link", " ")
        artist.image_link = request.form.get("image_link", " ")
        artist.website_link = request.form.get("website_link", " ")
        # convert form data from seeking_venue to boolean
        artist.seeking_venue = True if "seeking_venue" in request.form else False
        artist.seeking_description = request.form.get("seeking_description", " ")
        db.session.commit()
        flash("Artist " + artist.name + " was successfully updated")
    except:
        flash("Artist " + artist.name + "  not successfully updated")
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()

    venue = {
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    }

    venue = Venue.query.get(venue_id)
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):

    venue = Venue.query.get(venue_id)
    try:
        venue.name = request.form.get("name", " ")
        venue.state = request.form.get("state", " ")
        venue.city = request.form.get("city", " ")
        venue.address = request.form.get("address", " ")
        venue.phone = request.form.get("phone", " ")
        venue.genres = request.form.get("genres", " ")
        venue.facebook_link = request.form.get("facebook_link", " ")
        venue.image_link = request.form.get("image_link", " ")
        venue.website_link = request.form.get("website_link", " ")
        venue.seeking_talent = True if "seeking_talent" in request.form else False
        venue.seeking_description = request.form.get("seeking_description", " ")

        db.session.commit()
        flash("Venue " + venue.name + " was successfully updated")
    except:
        flash("Venue " + venue.name + " can not be updated")
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for("show_venue", venue_id=venue_id))


@app.route("/artists/create", methods=["GET"])
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


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():

    try:
        name = request.form.get("name", " ")
        state = request.form.get("state", " ")
        city = request.form.get("city", " ")
        phone = request.form.get("phone", " ")
        genres = request.form.get("genres", " ")
        facebook_link = request.form.get("facebook_link", " ")
        image_link = request.form.get("image_link", " ")
        website_link = request.form.get("website_link", " ")
        seeking_venue = True if "seeking_venue" in request.form else False
        seeking_description = request.form.get("seeking_description", " ")

        artist = Artist(
            name=name,
            state=state,
            city=city,
            phone=phone,
            genres=genres,
            facebook_link=facebook_link,
            image_link=image_link,
            website_link=website_link,
            seeking_venue=seeking_venue,
            seeking_description=seeking_description,
        )

        db.session.add(artist)
        db.session.commit()
        flash("Artist " + request.form["name"] + " was successfully listed!")
    except:
        flash(
            "An error occurred. Artist "
            + request.form["name"]
            + " could not be listed."
        )
        db.session.rollback()
    finally:
        db.session.close()
    return render_template("pages/home.html")


@app.route("/shows")
def shows():
    data = list()

    # join tables
    shows = Show.query.join(Artist, Venue).all()

    for show in shows:
        data.append(
            {
                "id": show.venue_id,
                "name": show.Venue.name,
                "artist_id": show.artist_id,
                "artist_name": show.Artist.name,
                "artist_image_link": show.Artist.image_link,
                "start_time": format_datetime(str(show.start_time)),
            }
        )

    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    form = ShowForm(request.form)
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
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():

    try:
        artist_id = request.form.get("artist_id", " ")
        venue_id = request.form.get("venue_id", " ")
        start_time = request.form.get("start_time", " ")

        show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)

        db.session.add(show)
        db.session.commit()
        flash("Show was successfully listed!")
    except:
        flash("An error occurred. Show could not be listed.")
        db.session.rollback()
    finally:
        db.session.close()
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")


# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
