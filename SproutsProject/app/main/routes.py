from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.main import bp
from app.models import Internship, Restaurant, Intern, Application
from app import db

@bp.route('/')
@bp.route('/index')
def index():
    """Home page showing featured internships and stats."""
    featured_internships = Internship.query.filter_by(is_featured=True, is_active=True).limit(6).all()
    total_internships = Internship.query.filter_by(is_active=True).count()
    total_restaurants = Restaurant.query.filter_by(is_active=True).count()
    total_interns = Intern.query.count()
    
    return render_template('main/index.html',
                         featured_internships=featured_internships,
                         total_internships=total_internships,
                         total_restaurants=total_restaurants,
                         total_interns=total_interns)

@bp.route('/about')
def about():
    """About page."""
    return render_template('main/about.html')

@bp.route('/contact')
def contact():
    """Contact page."""
    return render_template('main/contact.html')

@bp.route('/search')
def search():
    """Search internships page."""
    query = request.args.get('q', '')
    location = request.args.get('location', '')
    cuisine_type = request.args.get('cuisine_type', '')
    department = request.args.get('department', '')
    is_paid = request.args.get('is_paid', '')
    
    # Build search query
    internships_query = Internship.query.filter_by(is_active=True)
    
    if query:
        internships_query = internships_query.filter(
            db.or_(
                Internship.title.contains(query),
                Internship.description.contains(query)
            )
        )
    
    if location:
        internships_query = internships_query.join(Restaurant).filter(
            db.or_(
                Restaurant.city.contains(location),
                Restaurant.address.contains(location)
            )
        )
    
    if cuisine_type:
        internships_query = internships_query.join(Restaurant).filter(
            Restaurant.cuisine_type == cuisine_type
        )
    
    if department:
        internships_query = internships_query.filter(
            Internship.department == department
        )
    
    if is_paid == 'true':
        internships_query = internships_query.filter(Internship.is_paid == True)
    elif is_paid == 'false':
        internships_query = internships_query.filter(Internship.is_paid == False)
    
    page = request.args.get('page', 1, type=int)
    internships = internships_query.paginate(
        page=page, per_page=12, error_out=False
    )
    
    # Get filter options for the form
    cuisine_types = db.session.query(Restaurant.cuisine_type).distinct().all()
    departments = db.session.query(Internship.department).distinct().all()
    
    return render_template('main/search.html',
                         internships=internships,
                         cuisine_types=[ct[0] for ct in cuisine_types if ct[0]],
                         departments=[d[0] for d in departments if d[0]],
                         query=query,
                         location=location,
                         cuisine_type=cuisine_type,
                         department=department,
                         is_paid=is_paid)

@bp.route('/internship/<int:id>')
def internship_detail(id):
    """Internship detail page."""
    internship = Internship.query.get_or_404(id)
    
    # Check if current user has applied (if logged in)
    has_applied = False
    if current_user.is_authenticated and current_user.intern:
        application = Application.query.filter_by(
            intern_id=current_user.intern.id,
            internship_id=internship.id
        ).first()
        has_applied = application is not None
    
    return render_template('main/internship_detail.html',
                         internship=internship,
                         has_applied=has_applied)

@bp.route('/restaurant/<int:id>')
def restaurant_profile(id):
    """Restaurant profile page."""
    restaurant = Restaurant.query.get_or_404(id)
    active_internships = restaurant.internships.filter_by(is_active=True).all()
    
    return render_template('main/restaurant_profile.html',
                         restaurant=restaurant,
                         active_internships=active_internships)
