import os

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate, Manager, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
import yaml


db = SQLAlchemy()
migrate = Migrate()
app = Flask(__name__)


# init SQLAlchemy so we can use it later in our models
def create_app():
    db_info = yaml.load(open(os.path.join(os.getcwd(), 'db.yaml')), Loader=yaml.BaseLoader)
    host = db_info['mysql_host']
    user = db_info['mysql_user']
    password = db_info['mysql_password']
    db_db = db_info['mysql_db']
    port = db_info['mysql_port']

    app.config['SECRET_KEY'] = db_info['secret']
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_db}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    db.init_app(app)
    db.metadata.clear()
    migrate.init_app(app, db)

    # manager = Manager(app)
    # manager.add_command('db', MigrateCommand)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from models import User, Project, Task, Reminder
    from main import main as main_blueprint
    from controllers.auth import auth as auth_blueprint
    from controllers.projects_controller import projects_controller as projects_blueprint
    from controllers.tasks_controller import tasks_controller as tasks_blueprint
    from controllers.reminders_controller import reminders_controller

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.User.query.get(int(user_id))

    # blueprint for auth routes in our app
    app.register_blueprint(auth_blueprint)

    # blueprint for main parts of app
    app.register_blueprint(main_blueprint)

    # register projects controller app
    app.register_blueprint(projects_blueprint)

    # register tasks controller app
    app.register_blueprint(tasks_blueprint)

    # register reminders controller app
    app.register_blueprint(reminders_controller)

    # db.drop_all(app)
    with app.app_context():
        db.create_all()
        db.session.commit()

    with app.app_context():
        db.create_all()

        return app
