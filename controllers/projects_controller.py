from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import and_
from werkzeug.security import generate_password_hash, check_password_hash

from models.Project import ProjectForm, Project
from models.User import User, RegistrationForm, LoginForm
from flask_app import db

projects_controller = Blueprint('projects_controller', __name__)


@projects_controller.route('/projects/index', methods=['GET'])
@login_required
def index():
    form = ProjectForm()
    active_projects, inactive_projects = Project.get_active_and_inactive_projects(current_user)
    return render_template('project/index.html', name=current_user.name, title="Projects", form=form,
                           projects=active_projects, inactive_projects=inactive_projects)


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
