from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import login_required, current_user
from sqlalchemy import and_, text

from flask_app import db
from models.Project import Project
from models.Reminder import ReminderForm
from models.Task import TaskForm, Task

tasks_controller = Blueprint('tasks_controller', __name__)


@tasks_controller.route('/tasks/new', methods=['GET'])
@login_required
def index():
    form = TaskForm()
    project_id = request.args.get('project_id')
    project = Project.query.filter(and_(Project.user_id == current_user.id, Project.id == project_id)).first()

    if project:
        form.project_id.data = project_id
        return render_template('task/index.html', project=project, title="New Task", form=form)
    else:
        flash(f'Project does not exist.', 'error')
        return redirect(url_for('projects_controller.index'))


@tasks_controller.route('/tasks/new', methods=['POST'])
@login_required
def new_task_post():
    form = TaskForm()
    project = Project.query.filter(and_(Project.user_id == current_user.id, Project.id == form.project_id.data)).first()

    if project:
        if form.validate_on_submit():
            flash(f'Task {form.name.data} created!', 'success')
            task = Task()
            form.populate_obj(task)
            task.project = project
            project.project_id = project.id

            db.session.add(project)
            db.session.commit()
            return redirect(url_for('projects_controller.edit_project', project_id=project.id))

        else:
            for error_field, error_message in form.errors.items():
                flash(str(error_message), 'error')
            return render_template('task/index.html', project=project, title="New Task", form=form)
    else:
        flash(f'Project does not exist.', 'error')
        return redirect(url_for('projects_controller.index'))


@tasks_controller.route('/tasks/edit', methods=['GET'])
@login_required
def edit_task():
    task_id = request.args.get('task_id')
    # filter using sqlalchemy requirement
    task = Task.query.filter(Task.id == task_id).first()

    # update subquery regular sql for requirement
    update_query = text("UPDATE reminder SET has_expired=1 WHERE id = (SELECT id FROM reminder WHERE date_time <= NOW());")
    db.engine.execute(update_query)
    db.session.commit()

    if task:
        form = TaskForm(obj=task)
        return render_template('task/edit.html', name=current_user.name, title=f"{task.name} | Edit", form=form,
                               task=task, project=task.project, reminder_form=ReminderForm(task_id=task.id))
    else:
        flash(f'Task does not exist.', 'error')
        return redirect(url_for('projects_controller.index'))


@tasks_controller.route('/tasks/edit', methods=['POST'])
@login_required
def edit_task_post():
    form = TaskForm()
    task_id = request.args.get('task_id')
    task = Task.query.filter(Project.id == task_id).first()

    if task:
        if form.validate_on_submit():
            form.populate_obj(task)
            db.session.add(task)
            db.session.commit()

            flash(f'Successfully updated task.', 'success')
            return render_template('task/edit.html', name=current_user.name, title=f"{task.name} | Edit", form=form,
                                   project=task.project, task=task, reminder_form=ReminderForm(task_id=task.id))
        else:
            flash(f'Error updating task.', 'error')
            return render_template('task/edit.html', name=current_user.name, title=f"{task.name} | Edit", form=form,
                                   project=task.project, task=task, reminder_form=ReminderForm(task_id=task.id))
    else:
        flash(f'Task does not exist.', 'error')
        return redirect(url_for('projects_controller.index'))


@tasks_controller.route('/tasks/delete', methods=['GET'])
@login_required
def delete_task():
    task_id = request.args.get('task_id')

    task = Task.query.filter(Task.id == task_id)
    project_id = task.first().project.id
    if task:
        task.delete()
    db.session.commit()
    flash(f'Task deleted!', 'success')

    return redirect(url_for('projects_controller.edit_project', project_id=project_id))
