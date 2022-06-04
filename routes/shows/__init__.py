import dateutil.parser
import babel
from flask import (
    Blueprint,
    render_template,
    request,
    flash,
)


from models import db, Venue, Artist, Show
from forms import ShowForm


show = Blueprint("show", __name__, static_folder="static", template_folder="templates")


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


@show.route("/shows")
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


@show.route("/shows/create")
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


@show.route("/shows/create", methods=["POST"])
def create_show_submission():
    form = ShowForm(request.form)
    try:
        artist_id = form.artist_id.data
        venue_id = form.venue_id.data
        start_time = form.start_time.data

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
