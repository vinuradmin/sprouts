from datetime import datetime
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Boolean, DateTime, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, backref

from app import db
from .base_model import BaseModel

# Association table for many-to-many relationship between users and roles
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(BaseModel):
    """Role model for user authorization."""
    __tablename__ = 'role'
    
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Role {self.name}>'

class User(BaseModel, UserMixin):
    """User account model."""
    __tablename__ = 'user'
    
    # Authentication
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    confirmed_at = db.Column(db.DateTime())
    
    # User information
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(20))
    
    # Relationships
    roles = db.relationship('Role', secondary=roles_users,
                           backref=db.backref('users', lazy='dynamic'))
    
    # User type (intern, restaurant_owner, admin)
    user_type = db.Column(db.String(20), nullable=False, default='intern')
    
    # One-to-one relationships with specific user types
    intern = db.relationship('Intern', backref='user', uselist=False, lazy=True)
    restaurant_owner = db.relationship('RestaurantOwner', backref='user', uselist=False, lazy=True)
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.roles is None or not self.roles:
            # Assign default role based on user_type
            default_role = Role.query.filter_by(name=self.user_type).first()
            if default_role:
                self.roles = [default_role]
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def has_role(self, role_name):
        """Check if user has the specified role."""
        return role_name in [role.name for role in self.roles]
    
    def __repr__(self):
        return f'<User {self.email}>'
