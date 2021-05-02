from flask_wtf import FlaskForm
from sqlalchemy import Column, Integer, ForeignKey, text
from sqlalchemy.orm import relationship
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms.widgets import TextArea


from flask_app import db
from models.Reminder import Reminder
from models.Task import Task


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100), unique=True, nullable=False)
    notes = db.Column(db.Text, nullable=False, default="")

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all,delete")

    is_active = db.Column(db.Boolean, default=True)

    @staticmethod
    def get_active_and_inactive_projects(current_user):
        active_projects = []
        inactive_projects = []
        for project in current_user.projects:
            if project.is_active:
                project.task = None
                project.reminder = None
                # get next task
                project.task = Task.query.filter_by(project_id=project.id).order_by(Task.date.desc()).first()

                if project.task:
                    # get next reminder - join sqlalchemy for requirement
                    project.reminder = Reminder.query.join(
                        Task, Task.project_id == project.task.id).order_by(Task.date.desc()).first()

                active_projects.append(project)
            else:
                inactive_projects.append(project)

        return active_projects, inactive_projects


class ProjectForm(FlaskForm):
    class Meta:
        model = Project

    name = StringField('name', validators=[DataRequired(), Length(min=2, max=100)])
    notes = StringField('Notes', widget=TextArea())
    submit = SubmitField('Sign Up')
