import dateutil.parser
import babel
from flask import Blueprint, render_template, request, flash, redirect, url_for

from models import db, Venue, Artist, Show
from forms import VenueForm, datetime

venue = Blueprint(
    "venue", __name__, static_folder="static", template_folder="templates"
)


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


@venue.route("/venues")
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


@venue.route("/venues/search", methods=["POST"])
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


@venue.route("/venues/<int:venue_id>")
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

    return render_template("pages/show_venue.html", venue=data)


@venue.route("/venues/create", methods=["GET"])
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


@venue.route("/venues/create", methods=["POST"])
def create_venue_submission():
    form = VenueForm(request.form)

    try:

        name = form.name.data
        state = form.state.data
        city = form.city.data
        address = form.address.data
        phone = form.phone.data
        genres = form.genres.data
        facebook_link = form.facebook_link.data
        image_link = form.image_link.data
        website_link = form.website_link.data
        # convert form data from seeking_talent to boolean
        seeking_talent = True if form.seeking_talent.data == "Yes" else False
        seeking_description = form.seeking_description.data

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
        flash("Venue " + request.form["name"] + " was created successfully")
        return render_template("pages/home.html")
    except:
        flash("An error occurred creating the " + request.form["name"])
        db.session.rollback()
    finally:
        db.session.close()
    return render_template("pages/home.html")


@venue.route("/venues/<venue_id>", methods=["DELETE"])
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


@venue.route("/venues/<int:venue_id>/edit", methods=["GET"])
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


@venue.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):

    form = VenueForm(request.form)
    venue = Venue.query.get(venue_id)
    try:
        venue.name = form.name.data
        venue.state = form.state.data
        venue.city = form.city.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.genres = form.genres.data
        venue.facebook_link = form.facebook_link.data
        venue.image_link = form.image_link.data
        venue.website_link = form.website_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data

        db.session.commit()
        flash("Venue " + venue.name + " was successfully updated")
    except:
        flash("Venue " + venue.name + " can not be updated")
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for("show_venue", venue_id=venue_id))
