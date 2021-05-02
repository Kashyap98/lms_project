from flask import Blueprint, redirect, url_for, flash, render_template, request
from flask_login import login_required, current_user

from flask_app import db
from models import Task
from models.Reminder import ReminderForm, Reminder
from models.Task import TaskForm

reminders_controller = Blueprint('reminders_controller', __name__)


@reminders_controller.route('/reminders/new', methods=['POST'])
@login_required
def new_reminder_post():
    form = ReminderForm()

    if form.validate_on_submit():
        flash(f'Reminder created!', 'success')
        reminder = Reminder()
        form.populate_obj(reminder)

        db.session.add(reminder)
        db.session.commit()
        task = reminder.task
        return render_template('task/edit.html', name=current_user.name, title=f"{task.name} | Edit", form=TaskForm(),
                               project=task.project, task=task, reminder_form=form)

    else:
        for error_field, error_message in form.errors.items():
            flash(str(error_message), 'error')
        task = Task.query.filter(Task.id == form.task_id.data).first()
        return render_template('task/edit.html', name=current_user.name, title=f"{task.name} | Edit", form=TaskForm(),
                               project=task.project, task=task, reminder_form=form)


@reminders_controller.route('/reminders/delete', methods=['GET'])
@login_required
def delete_reminder():
    reminder_id = request.args.get('reminder_id')

    reminder = Reminder.query.filter(Reminder.id == reminder_id)
    task_id = reminder.first().task.id
    if reminder:
        reminder.delete()
    db.session.commit()
    flash(f'Reminder deleted!', 'success')

    return redirect(url_for('tasks_controller.edit_task', task_id=task_id))
