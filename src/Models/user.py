from enum import unique
from sqlalchemy.sql.schema import PrimaryKeyConstraint
from src.config.dbConfig import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String, unique=True)
