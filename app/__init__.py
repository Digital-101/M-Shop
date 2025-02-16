from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

import os

# Configure the upload folder
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'app\static\images')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

from app import routes
from app import db
from app.models import Role

def create_manager_role():
    """Function to create the manager role in the database."""
    manager_role = Role(name='Manager')
    
    if not Role.query.filter_by(name='Manager').first():  # Check if it exists
        db.session.add(manager_role)
        db.session.commit()

def create_app():
    # Add any necessary app configurations here
    with app.app_context():
        db.create_all()
        create_manager_role()  # Call the function to create roles

    return app
