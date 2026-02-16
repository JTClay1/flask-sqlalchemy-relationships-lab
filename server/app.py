from flask import Flask, jsonify
from flask_migrate import Migrate
from models import db, Event, Session, Speaker, Bio

app = Flask(__name__)

# Basic SQLite config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

# =========================
# GET ALL EVENTS
# =========================
@app.route("/events")
def get_events():
    # Pull everything from the table
    events = Event.query.all()

    # Convert SQLAlchemy objects into plain dictionaries
    # because Flask can only JSONify serializable data
    data = [
        {"id": e.id, "name": e.name, "location": e.location}
        for e in events
    ]

    return jsonify(data), 200


# =========================
# GET SESSIONS FOR ONE EVENT
# =========================
@app.route("/events/<int:id>/sessions")
def get_event_sessions(id):

    # Fetch event by primary key
    event = db.session.get(Event, id)

    # If it doesn't exist, return proper error + 404
    if event is None:
        return jsonify({"error": "Event not found"}), 404

    # event.sessions works because of the relationship
    sessions = [
        {
            "id": s.id,
            "title": s.title,
            # datetime objects can't be JSON'd directly
            "start_time": s.start_time.isoformat() if s.start_time else None,
        }
        for s in event.sessions
    ]

    return jsonify(sessions), 200


# =========================
# GET ALL SPEAKERS
# =========================
@app.route("/speakers")
def get_speakers():
    speakers = Speaker.query.all()

    data = [{"id": s.id, "name": s.name} for s in speakers]

    return jsonify(data), 200


# =========================
# GET ONE SPEAKER + THEIR BIO
# =========================
@app.route("/speakers/<int:id>")
def get_speaker(id):

    speaker = db.session.get(Speaker, id)

    if speaker is None:
        return jsonify({"error": "Speaker not found"}), 404

    # Handle case where speaker has no bio
    bio_text = speaker.bio.bio_text if speaker.bio else "No bio available"

    data = {
        "id": speaker.id,
        "name": speaker.name,
        "bio_text": bio_text
    }

    return jsonify(data), 200


# =========================
# GET SPEAKERS FOR A SESSION
# =========================
@app.route("/sessions/<int:id>/speakers")
def get_session_speakers(id):

    session = db.session.get(Session, id)

    if session is None:
        return jsonify({"error": "Session not found"}), 404

    # session.speakers works because of many-to-many relationship
    data = []
    for sp in session.speakers:
        bio_text = sp.bio.bio_text if sp.bio else "No bio available"

        data.append({
            "id": sp.id,
            "name": sp.name,
            "bio_text": bio_text
        })

    return jsonify(data), 200


if __name__ == "__main__":
    app.run(port=5555, debug=True)
