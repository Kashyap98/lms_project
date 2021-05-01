from flask_wtf import FlaskForm
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms.widgets import TextArea


from flask_app import db


class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100), unique=False, nullable=False)
    date_time = db.Column(db.Text, nullable=False, default="")

    task_id = Column(Integer, ForeignKey('task.id'))
    task = relationship("Task", back_populates="reminders")
    has_expired = db.Column(db.Boolean, default=False)
