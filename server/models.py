from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

# Naming convention just keeps FK names predictable in migrations.
# Not functionally required for relationships, just cleaner database structure.
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

# =========================
# MANY-TO-MANY JOIN TABLE
# =========================
# This table does NOT get its own model class.
# It exists purely to connect Sessions and Speakers.
# Think of it like:
#   "Which speaker is speaking at which session?"
session_speakers = db.Table(
    "session_speakers",
    db.Column("session_id", db.Integer, db.ForeignKey("sessions.id"), primary_key=True),
    db.Column("speaker_id", db.Integer, db.ForeignKey("speakers.id"), primary_key=True),
)

# =========================
# EVENT MODEL
# =========================
class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)

    # ONE-TO-MANY
    # One Event -> many Sessions
    # back_populates connects the relationship both ways.
    # cascade means:
    #   If Event gets deleted, delete all its Sessions automatically.
    sessions = db.relationship(
        "Session",
        back_populates="event",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Event {self.id}, {self.name}, {self.location}>"

# =========================
# SESSION MODEL
# =========================
class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    start_time = db.Column(db.DateTime)

    # FOREIGN KEY side of Event relationship
    # This is the actual column stored in the database.
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))

    # Relationship back to Event object
    # Allows: session.event
    event = db.relationship("Event", back_populates="sessions")

    # MANY-TO-MANY
    # A session can have many speakers.
    # secondary tells SQLAlchemy which table connects them.
    speakers = db.relationship(
        "Speaker",
        secondary=session_speakers,
        back_populates="sessions",
    )

    def __repr__(self):
        return f"<Session {self.id}, {self.title}, {self.start_time}>"

# =========================
# SPEAKER MODEL
# =========================
class Speaker(db.Model):
    __tablename__ = "speakers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    # ONE-TO-ONE
    # Each speaker has exactly ONE bio.
    # uselist=False makes it one-to-one instead of one-to-many.
    # cascade ensures deleting a speaker deletes their bio.
    bio = db.relationship(
        "Bio",
        back_populates="speaker",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # MANY-TO-MANY (other side)
    # A speaker can speak at multiple sessions.
    sessions = db.relationship(
        "Session",
        secondary=session_speakers,
        back_populates="speakers",
    )

    def __repr__(self):
        return f"<Speaker {self.id}, {self.name}>"

# =========================
# BIO MODEL
# =========================
class Bio(db.Model):
    __tablename__ = "bios"

    id = db.Column(db.Integer, primary_key=True)
    bio_text = db.Column(db.Text, nullable=False)

    # FK column (actual stored value)
    # unique=True enforces one-to-one at database level.
    speaker_id = db.Column(db.Integer, db.ForeignKey("speakers.id"), unique=True)

    # Relationship back to Speaker
    speaker = db.relationship("Speaker", back_populates="bio")

    def __repr__(self):
        return f"<Bio {self.id}>"
