from flask import Flask, jsonify, request, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__, static_folder="static", template_folder="templates")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "app.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---- Models ----
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    body = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "body": self.body, "created_at": self.created_at.isoformat()}

# ---- Routes ----
@app.route("/")
def index():
    return render_template("index.html")

# API: list messages
@app.route("/api/messages", methods=["GET"])
def list_messages():
    messages = Message.query.order_by(Message.created_at.desc()).all()
    return jsonify([m.to_dict() for m in messages])

# API: create message
@app.route("/api/messages", methods=["POST"])
def create_message():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    body = data.get("body", "").strip()
    if not name or not body:
        return jsonify({"error":"name and body are required"}), 400
    m = Message(name=name, body=body)
    db.session.add(m)
    db.session.commit()
    return jsonify(m.to_dict()), 201

# API: get single
@app.route("/api/messages/<int:msg_id>", methods=["GET"])
def get_message(msg_id):
    m = Message.query.get_or_404(msg_id)
    return jsonify(m.to_dict())

# API: update
@app.route("/api/messages/<int:msg_id>", methods=["PUT"])
def update_message(msg_id):
    m = Message.query.get_or_404(msg_id)
    data = request.get_json() or {}
    name = data.get("name")
    body = data.get("body")
    if name is not None:
        m.name = name.strip()
    if body is not None:
        m.body = body.strip()
    db.session.commit()
    return jsonify(m.to_dict())

# API: delete
@app.route("/api/messages/<int:msg_id>", methods=["DELETE"])
def delete_message(msg_id):
    m = Message.query.get_or_404(msg_id)
    db.session.delete(m)
    db.session.commit()
    return jsonify({"result":"deleted"})

# ---- CLI helper to create DB ----
@app.cli.command("init-db")
def init_db():
    """Initialize the database (run: flask init-db)."""
    db.create_all()
    print("Initialized the database.")

if __name__ == "__main__":
    # create DB automatically if missing
    if not os.path.exists(db_path):
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
