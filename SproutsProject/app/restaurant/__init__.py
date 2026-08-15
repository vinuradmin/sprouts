from flask import Blueprint

bp = Blueprint('restaurant', __name__)

from app.restaurant import routes
