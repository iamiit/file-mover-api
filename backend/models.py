# models.py
from app import db
from datetime import datetime

class FileRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128), nullable=False)
    src_folder = db.Column(db.String(256), nullable=False)
    dest_folder = db.Column(db.String(256), nullable=False)
    moved_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    isMoved = db.Column(db.Boolean, nullable=False, default=True)
