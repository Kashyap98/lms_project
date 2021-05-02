from flask_wtf import FlaskForm
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from wtforms import SubmitField, HiddenField
from wtforms.fields.html5 import DateTimeLocalField


from flask_app import db


class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    date_time = db.Column(db.DateTime, nullable=False, default="")

    task_id = Column(Integer, ForeignKey('task.id'))
    task = relationship("Task", back_populates="reminders")
    has_expired = db.Column(db.Boolean, default=False)


class ReminderForm(FlaskForm):
    class Meta:
        model = Reminder

    task_id = HiddenField('task_id')
    date_time = DateTimeLocalField('Reminder', format='%Y-%m-%dT%H:%M')
    submit = SubmitField('Sign Up')
