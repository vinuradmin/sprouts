from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.restaurant import bp
from app.models import Restaurant, Internship, Application, RestaurantOwner
from app.restaurant.forms import InternshipForm, RestaurantProfileForm

@bp.route('/dashboard')
@login_required
def dashboard():
    """Restaurant dashboard."""
    if not current_user.restaurant_owner:
        flash('Access denied. Restaurant owner profile required.', 'error')
        return redirect(url_for('main.index'))
    
    restaurant_owner = current_user.restaurant_owner
    restaurant = restaurant_owner.restaurant
    
    # Get active internships
    active_internships = restaurant.internships.filter_by(is_active=True).all()
    
    # Get recent applications
    recent_applications = Application.query.join(Internship)\
        .filter(Internship.restaurant_id == restaurant.id)\
        .order_by(Application.created_at.desc()).limit(10).all()
    
    # Get statistics
    total_internships = restaurant.internships.count()
    total_applications = Application.query.join(Internship)\
        .filter(Internship.restaurant_id == restaurant.id).count()
    pending_applications = Application.query.join(Internship)\
        .filter(Internship.restaurant_id == restaurant.id)\
        .filter(Application.status.in_(['submitted', 'under_review'])).count()
    
    return render_template('restaurant/dashboard.html',
                         restaurant=restaurant,
                         restaurant_owner=restaurant_owner,
                         active_internships=active_internships,
                         recent_applications=recent_applications,
                         total_internships=total_internships,
                         total_applications=total_applications,
                         pending_applications=pending_applications)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Restaurant profile management."""
    if not current_user.restaurant_owner:
        flash('Access denied. Restaurant owner profile required.', 'error')
        return redirect(url_for('main.index'))
    
    restaurant = current_user.restaurant_owner.restaurant
    form = RestaurantProfileForm(obj=restaurant)
    
    if form.validate_on_submit():
        form.populate_obj(restaurant)
        db.session.commit()
        flash('Restaurant profile updated successfully!', 'success')
        return redirect(url_for('restaurant.profile'))
    
    return render_template('restaurant/profile.html', form=form, restaurant=restaurant)

@bp.route('/internships')
@login_required
def internships():
    """View all restaurant internships."""
    if not current_user.restaurant_owner:
        flash('Access denied. Restaurant owner profile required.', 'error')
        return redirect(url_for('main.index'))
    
    restaurant = current_user.restaurant_owner.restaurant
    page = request.args.get('page', 1, type=int)
    
    internships = restaurant.internships.order_by(Internship.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('restaurant/internships.html', internships=internships)

@bp.route('/internships/create', methods=['GET', 'POST'])
@login_required
def create_internship():
    """Create a new internship posting."""
    if not current_user.restaurant_owner or not current_user.restaurant_owner.can_post_internships:
        flash('Access denied. Permission to post internships required.', 'error')
        return redirect(url_for('main.index'))
    
    form = InternshipForm()
    
    if form.validate_on_submit():
        internship = Internship(
            restaurant_id=current_user.restaurant_owner.restaurant.id,
            contact_email=current_user.email
        )
        form.populate_obj(internship)
        
        db.session.add(internship)
        db.session.commit()
        
        flash('Internship posted successfully!', 'success')
        return redirect(url_for('restaurant.internships'))
    
    return render_template('restaurant/create_internship.html', form=form)

@bp.route('/internships/<int:internship_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_internship(internship_id):
    """Edit an internship posting."""
    if not current_user.restaurant_owner:
        flash('Access denied. Restaurant owner profile required.', 'error')
        return redirect(url_for('main.index'))
    
    internship = Internship.query.filter_by(
        id=internship_id,
        restaurant_id=current_user.restaurant_owner.restaurant.id
    ).first_or_404()
    
    form = InternshipForm(obj=internship)
    
    if form.validate_on_submit():
        form.populate_obj(internship)
        db.session.commit()
        flash('Internship updated successfully!', 'success')
        return redirect(url_for('restaurant.internships'))
    
    return render_template('restaurant/edit_internship.html', form=form, internship=internship)

@bp.route('/internships/<int:internship_id>/applications')
@login_required
def internship_applications(internship_id):
    """View applications for a specific internship."""
    if not current_user.restaurant_owner:
        flash('Access denied. Restaurant owner profile required.', 'error')
        return redirect(url_for('main.index'))
    
    internship = Internship.query.filter_by(
        id=internship_id,
        restaurant_id=current_user.restaurant_owner.restaurant.id
    ).first_or_404()
    
    page = request.args.get('page', 1, type=int)
    applications = internship.applications.order_by(Application.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('restaurant/internship_applications.html', 
                         internship=internship, applications=applications)

@bp.route('/applications/<int:application_id>')
@login_required
def application_detail(application_id):
    """View application details."""
    if not current_user.restaurant_owner:
        flash('Access denied. Restaurant owner profile required.', 'error')
        return redirect(url_for('main.index'))
    
    application = Application.query.join(Internship)\
        .filter(Application.id == application_id,
                Internship.restaurant_id == current_user.restaurant_owner.restaurant.id)\
        .first_or_404()
    
    return render_template('restaurant/application_detail.html', application=application)

@bp.route('/applications/<int:application_id>/update_status', methods=['POST'])
@login_required
def update_application_status(application_id):
    """Update application status."""
    if not current_user.restaurant_owner or not current_user.restaurant_owner.can_review_applications:
        return jsonify({'error': 'Access denied'}), 403
    
    application = Application.query.join(Internship)\
        .filter(Application.id == application_id,
                Internship.restaurant_id == current_user.restaurant_owner.restaurant.id)\
        .first_or_404()
    
    new_status = request.json.get('status')
    notes = request.json.get('notes', '')
    
    if new_status not in ['under_review', 'interview_scheduled', 'accepted', 'rejected']:
        return jsonify({'error': 'Invalid status'}), 400
    
    application.update_status(new_status, notes)
    
    return jsonify({'success': True, 'message': f'Application status updated to {new_status}'})

@bp.route('/internships/<int:internship_id>/toggle_active', methods=['POST'])
@login_required
def toggle_internship_active(internship_id):
    """Toggle internship active status."""
    if not current_user.restaurant_owner:
        return jsonify({'error': 'Access denied'}), 403
    
    internship = Internship.query.filter_by(
        id=internship_id,
        restaurant_id=current_user.restaurant_owner.restaurant.id
    ).first_or_404()
    
    internship.is_active = not internship.is_active
    db.session.commit()
    
    status = 'activated' if internship.is_active else 'deactivated'
    return jsonify({'success': True, 'message': f'Internship {status} successfully'})
