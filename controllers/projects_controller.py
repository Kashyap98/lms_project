from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from sqlalchemy import and_, text

from models import Task, User
from models.Project import ProjectForm, Project
from flask_app import db
from models.Task import _convert_results_to_tasks

projects_controller = Blueprint('projects_controller', __name__)


@projects_controller.route('/projects/index', methods=['GET'])
@login_required
def index():
    form = ProjectForm()
    active_projects, inactive_projects = Project.get_active_and_inactive_projects(current_user)
    return render_template('project/index.html', name=current_user.name, title="Projects", form=form,
                           projects=active_projects, inactive_projects=inactive_projects)


@projects_controller.route('/projects/upcoming', methods=['GET'])
@login_required
def upcoming():
    # join regular sql requirement
    tasks_sql = text('SELECT task.id AS task_id, task.name AS task_name, task.notes AS task_notes, task.date AS task_date,'
                     ' task.start_time AS task_start_time, task.end_time AS task_end_time, task.project_id AS task_project_id,'
                     ' task.is_completed AS task_is_completed FROM task JOIN project ON project.id = task.project_id JOIN '
                     'user ON user.id = project.user_id')
    tasks_results = db.engine.execute(tasks_sql)
    tasks = _convert_results_to_tasks(tasks_results)

    return render_template('project/upcoming.html', title="Upcoming", tasks=tasks)


@projects_controller.route('/projects/new', methods=['POST'])
@login_required
def new_project_post():
    form = ProjectForm()
    active_projects, inactive_projects = Project.get_active_and_inactive_projects(current_user)

    if form.validate_on_submit():
        flash(f'Project {form.name.data} created!', 'success')
        project = Project()
        form.populate_obj(project)
        project.user = current_user
        project.user_id = current_user.id

        db.session.add(project)
        db.session.commit()
        return redirect(url_for('projects_controller.index'))
    else:
        if "email" in form.errors:
            flash('Email must be unique.')
        return render_template('project/index.html', name=current_user.name, title="Projects", form=form,
                               projects=active_projects, inactive_projects=inactive_projects)


@projects_controller.route('/projects/deactivate', methods=['GET'])
@login_required
def deactivate_project():
    project_id = request.args.get('project_id')

    # compound sql condition using sqlalchemy for requirement
    project = Project.query.filter(and_(Project.user_id == current_user.id, Project.id == project_id)).first()
    project.is_active = 0
    db.session.commit()
    flash(f'Project {project.name} deactivated!', 'success')

    return redirect(url_for('projects_controller.index'))


@projects_controller.route('/projects/activate', methods=['GET'])
@login_required
def activate_project():
    project_id = request.args.get('project_id')

    project = Project.query.filter(and_(Project.user_id == current_user.id, Project.id == project_id)).first()
    project.is_active = 1
    db.session.commit()
    flash(f'Project {project.name} activated!', 'success')

    return redirect(url_for('projects_controller.index'))


@projects_controller.route('/projects/delete', methods=['GET'])
@login_required
def delete_project():
    project_id = request.args.get('project_id')

    project = Project.query.filter(and_(Project.user_id == current_user.id, Project.id == project_id))
    if project:
        project.delete()
    db.session.commit()
    flash(f'Project deleted!', 'success')

    return redirect(url_for('projects_controller.index'))


@projects_controller.route('/projects/edit', methods=['GET'])
@login_required
def edit_project():
    project_id = request.args.get('project_id')
    project = Project.query.filter(and_(Project.user_id == current_user.id, Project.id == project_id)).first()

    if project:
        form = ProjectForm(obj=project)
        return render_template('project/edit.html', name=current_user.name, title=f"{project.name} | Edit", form=form,
                               project_id=project_id, tasks=Task.get_tasks_regular_sql(project_id))
    else:
        flash(f'Project does not exist.', 'error')
        return redirect(url_for('projects_controller.index'))


@projects_controller.route('/projects/edit', methods=['POST'])
@login_required
def edit_project_post():
    form = ProjectForm()
    project_id = request.args.get('project_id')
    project = Project.query.filter(and_(Project.user_id == current_user.id, Project.id == project_id)).first()

    if project:
        if form.validate_on_submit():
            form.populate_obj(project)
            db.session.add(project)
            db.session.commit()

            flash(f'Successfully updated project.', 'success')
            return render_template('project/edit.html', name=current_user.name, title=f"{project.name} | Edit",
                                   form=form, tasks=Task.get_tasks_regular_sql(project_id))
        else:
            flash(f'Error updating project.', 'error')
            return render_template('project/edit.html', name=current_user.name, title=f"{project.name} | Edit",
                                   form=form, tasks=Task.get_tasks_regular_sql(project_id))
    else:
        flash(f'Project does not exist.', 'error')
        return redirect(url_for('projects_controller.index'))
