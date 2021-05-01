import datetime

from flask_wtf import FlaskForm
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, validates
from wtforms import StringField, SubmitField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import DataRequired, Length
from wtforms.widgets import TextArea


from flask_app import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100), unique=False, nullable=False)
    notes = db.Column(db.Text, nullable=False, default="")

    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", back_populates="tasks")
    reminders = relationship("Reminder", back_populates="task")
    is_completed = db.Column(db.Boolean, default=False)


class TaskForm(FlaskForm):
    class Meta:
        model = Task

    name = StringField('name', validators=[DataRequired(), Length(min=2, max=100)])
    notes = StringField('Notes', widget=TextArea())
    date = DateField('DatePicker', format='%Y-%m-%d')
    start_time = TimeField('Start time')
    end_time = TimeField('End time')
    submit = SubmitField('Sign Up')

