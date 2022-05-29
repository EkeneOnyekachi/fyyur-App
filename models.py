from flask_sqlalchemy import SQLAlchemy



db = SQLAlchemy()




class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,  nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    website_link = db.Column(db.String(), nullable=False)
    seeking_talent = db.Column(db.Boolean,  default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship("Show", backref="Venue", lazy=True)



def __repr__(self):
    return f'<Venue Id: {self.id}, name: {self.name}, city: {self.city}, state: {self.state},\
       address: {self.address}, phone: {self.phone}, genres: {self.genres},\
          image_link: {self.image_link},facebook_link: {self.facebook_link},\
             website_link: {self.website_link}, seekin_talent: {self.seeking_talent},\
                seeking_description:{self.seeking_description}>' 



class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    website_link = db.Column(db.String(), nullable=False)
    seeking_venue  = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship("Show", backref="Artist", lazy=True)


def __repr__(self):
    return f'<Artist Id: {self.id}, name: {self.name}, city: {self.city}, state: {self.state},\
       phone: {self.phone}, genres: {self.genres},image_link: {self.image_link},\
         facebook_link: {self.facebook_link},website_link: {self.website_link}, \
           seekin_talent: {self.seeking_venue},seeking_description: {self.seeking_description}>' 


class Show(db.Model):
  __tablename__ = "Show"
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False )


def __repr__(self):
  return f'<Show id: {self.id}, venue_id {self.venue_id},\
     artist_id: {self.artist_id},start_time: {self.start_time}>'

#db.create_all()

