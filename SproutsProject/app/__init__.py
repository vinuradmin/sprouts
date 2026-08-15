from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.intern import bp as intern_bp
    app.register_blueprint(intern_bp, url_prefix='/intern')

    from app.restaurant import bp as restaurant_bp
    app.register_blueprint(restaurant_bp, url_prefix='/restaurant')

    return app

# Import models to ensure they are registered with SQLAlchemy
from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
