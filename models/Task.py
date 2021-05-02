import datetime

from flask_wtf import FlaskForm
from sqlalchemy import Column, Integer, ForeignKey, text
from sqlalchemy.orm import relationship, validates
from wtforms import StringField, SubmitField, HiddenField, validators
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import DataRequired, Length, ValidationError
from wtforms.widgets import TextArea


from flask_app import db


def _convert_results_to_tasks(result):
    # aggregate regular sql requirement
    aggregate_sql = text("SELECT task_id, COUNT(*) FROM reminder WHERE has_expired = 0 GROUP BY task_id;")
    aggregate_result = db.engine.execute(aggregate_sql)

    reminder_counts = {}
    for row in aggregate_result:
        reminder_counts[row[0]] = row[1]

    tasks = []
    # get name for user from result
    for row in result:
        if row[4]:
            start_time = (datetime.datetime.min + row[4]).time()
            end_time = (datetime.datetime.min + row[5]).time()
        else:
            start_time = None
            end_time = None

        task = Task(id=row[0], name=row[1], notes=row[2], date=row[3],
                    start_time=start_time,
                    end_time=end_time,
                    project_id=row[6], is_completed=row[7])

        if task.id in reminder_counts:
            task.reminder_count = reminder_counts[task.id]
        else:
            task.reminder_count = 0
        tasks.append(task)

    return tasks


def get_tasks_regular_sql(project_id):
    # compound regular sql requirement
    sql = text(f'select * from task WHERE project_id = {project_id} AND is_completed = 0;')
    result = db.engine.execute(sql)

    tasks = _convert_results_to_tasks(result)

    return tasks


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100), unique=False, nullable=False)
    notes = db.Column(db.Text, nullable=False, default="")

    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", back_populates="tasks")
    reminders = relationship("Reminder", back_populates="task", cascade="all,delete")
    is_completed = db.Column(db.Boolean, default=False)


class TaskForm(FlaskForm):
    class Meta:
        model = Task

    name = StringField('name', validators=[DataRequired(), Length(min=2, max=100)])
    project_id = HiddenField('project_id', validators=[DataRequired()])
    notes = StringField('Notes', widget=TextArea())
    date = DateField('DatePicker', format='%Y-%m-%d', validators=[DataRequired()])
    start_time = TimeField('Start time', validators=(validators.Optional(),))
    end_time = TimeField('End time', validators=(validators.Optional(),))
    submit = SubmitField('Sign Up')

    # def validate_date(self, field):
    #     today = datetime.datetime.now().date()
    #     value = field.data
    #     if value < today:
    #         raise ValidationError('Date must be later than today')
