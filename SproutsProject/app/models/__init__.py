from .user import User, Role, roles_users
from .intern import Intern, InternAvailability, InternSkill, WorkExperience
from .restaurant import Restaurant, RestaurantOwner
from .internship import Internship
from .application import Application
from .base_model import BaseModel

# Import all models to ensure they are registered with SQLAlchemy
__all__ = [
    'User', 'Role', 'roles_users',
    'Intern', 'InternAvailability', 'InternSkill', 'WorkExperience',
    'Restaurant', 'RestaurantOwner',
    'Internship',
    'Application',
    'BaseModel'
]
