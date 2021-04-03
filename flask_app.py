import os

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate, Manager, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
import yaml


db = SQLAlchemy()


# init SQLAlchemy so we can use it later in our models
def create_app():
    app = Flask(__name__)
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
    migrate = Migrate(app, db)
    migrate.init_app(app, db)

    # manager = Manager(app)
    # manager.add_command('db', MigrateCommand)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from models import User
    from main import main as main_blueprint
    from auth import auth as auth_blueprint

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.User.query.get(int(user_id))

    # blueprint for auth routes in our app
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    app.register_blueprint(main_blueprint)

    # db.create_all(app)
    # db.session.commit()
    #
    # guest = User.User('guest', 'guest@example.com')
    # db.session.add(guest)
    # db.session.commit()

    with app.app_context():
        db.create_all()

        return app
