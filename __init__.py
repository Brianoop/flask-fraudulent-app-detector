from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask.json import JSONEncoder
from enum import Enum
import os
from os.path import join, dirname, realpath
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

dotenv_path = join(dirname(__file__), '.env')  # Address of your .env file
load_dotenv(dotenv_path)


config_name = os.getenv('FLASK_CONFIG')
mysql_server = os.getenv('MYSQL_SERVER')
mysql_user = os.getenv('MYSQL_USER')
mysql_database = os.getenv('MYSQL_DATABASE')
mysql_password = os.getenv('MYSQL_PASSWORD')
mysql_port = os.getenv('MYSQL_PORT')



# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
UPLOAD_FOLDER = "dashboard/uploads"

UPLOAD_PATH = join(dirname(realpath(__file__)), "static\\dashboard\\uploads")

MODEL_PATH = join(dirname(realpath(__file__)), "models")
WORDS_PATH = join(dirname(realpath(__file__)), "models")


ALLOWED_EXTENSIONS = set(["txt", "pdf", "png", "jpg", "jpeg", "gif"])


# Custom JSON Encoder
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)

def seed_database(db):
     from .models import User
    
     admin_name= os.getenv('ADMIN_NAME')
     admin_email = os.getenv('ADMIN_EMAIL')
     admin_password = os.getenv('ADMIN_PASSWORD')
     admin_role = os.getenv('ADMIN_ROLE')

     user = User.query.filter_by(
        email=admin_email
     ).first()  # if this returns a user, then the email already exists in database

     if(user):  # if a user is found, we want to redirect back to signup page so user can try again
        print("Admin already exists in database!")
        return 
     new_user = User(
        email=admin_email,
        name=admin_name,
        role=admin_role,
        password= generate_password_hash(admin_password, method="sha256"),
     )

     db.session.add(new_user)
     db.session.commit()

def create_app():
    app = Flask(__name__)

    app.json_encoder = CustomJSONEncoder

    app.config["SECRET_KEY"] = "123456"
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "mysql+pymysql://" + mysql_user+":" + mysql_password + "@"+ mysql_server +":"+ mysql_port +"/" + mysql_database
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["UPLOAD_PATH"] = UPLOAD_PATH
    app.config["MODEL_PATH"] = MODEL_PATH
    app.config["WORDS_PATH"] = WORDS_PATH

    db.init_app(app)

    app.app_context().push()

    seed_database(db)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    from .routes import routes as routes_blueprint

    app.register_blueprint(routes_blueprint)

    return app
