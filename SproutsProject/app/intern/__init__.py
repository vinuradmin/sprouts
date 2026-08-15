from flask import Blueprint

bp = Blueprint('intern', __name__)

from app.intern import routes
