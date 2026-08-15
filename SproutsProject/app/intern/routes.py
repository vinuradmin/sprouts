from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.intern import bp
from app.models import Intern, Internship, Application, Restaurant
from app.intern.forms import InternProfileForm, ApplicationForm

@bp.route('/dashboard')
@login_required
def dashboard():
    """Intern dashboard."""
    if not current_user.intern:
        flash('Access denied. Intern profile required.', 'error')
        return redirect(url_for('main.index'))
    
    intern = current_user.intern
    
    # Get recent applications
    recent_applications = Application.query.filter_by(intern_id=intern.id)\
        .order_by(Application.created_at.desc()).limit(5).all()
    
    # Get recommended internships (simple matching for now)
    recommended_internships = Internship.query.filter_by(is_active=True)\
        .limit(6).all()
    
    # Get application statistics
    total_applications = Application.query.filter_by(intern_id=intern.id).count()
    pending_applications = Application.query.filter_by(intern_id=intern.id)\
        .filter(Application.status.in_(['submitted', 'under_review', 'interview_scheduled'])).count()
    accepted_applications = Application.query.filter_by(intern_id=intern.id, status='accepted').count()
    
    return render_template('intern/dashboard.html',
                         intern=intern,
                         recent_applications=recent_applications,
                         recommended_internships=recommended_internships,
                         total_applications=total_applications,
                         pending_applications=pending_applications,
                         accepted_applications=accepted_applications)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Intern profile management."""
    if not current_user.intern:
        flash('Access denied. Intern profile required.', 'error')
        return redirect(url_for('main.index'))
    
    form = InternProfileForm(obj=current_user.intern)
    
    if form.validate_on_submit():
        # Update user information
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone = form.phone.data
        
        # Update intern profile
        intern = current_user.intern
        form.populate_obj(intern)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('intern.profile'))
    
    return render_template('intern/profile.html', form=form)

@bp.route('/applications')
@login_required
def applications():
    """View all applications."""
    if not current_user.intern:
        flash('Access denied. Intern profile required.', 'error')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    applications = Application.query.filter_by(intern_id=current_user.intern.id)\
        .order_by(Application.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('intern/applications.html', applications=applications)

@bp.route('/apply/<int:internship_id>', methods=['GET', 'POST'])
@login_required
def apply(internship_id):
    """Apply to an internship."""
    if not current_user.intern:
        flash('Access denied. Intern profile required.', 'error')
        return redirect(url_for('main.index'))
    
    internship = Internship.query.get_or_404(internship_id)
    
    # Check if already applied
    existing_application = Application.query.filter_by(
        intern_id=current_user.intern.id,
        internship_id=internship_id
    ).first()
    
    if existing_application:
        flash('You have already applied to this internship.', 'warning')
        return redirect(url_for('main.internship_detail', id=internship_id))
    
    # Check if internship is still active and accepting applications
    if not internship.is_active or internship.is_expired or internship.is_full:
        flash('This internship is no longer accepting applications.', 'error')
        return redirect(url_for('main.internship_detail', id=internship_id))
    
    form = ApplicationForm()
    
    if form.validate_on_submit():
        application = Application(
            intern_id=current_user.intern.id,
            internship_id=internship_id,
            cover_letter=form.cover_letter.data,
            additional_notes=form.additional_notes.data
        )
        
        db.session.add(application)
        db.session.commit()
        
        flash('Application submitted successfully!', 'success')
        return redirect(url_for('intern.applications'))
    
    return render_template('intern/apply.html', form=form, internship=internship)

@bp.route('/application/<int:application_id>')
@login_required
def application_detail(application_id):
    """View application details."""
    if not current_user.intern:
        flash('Access denied. Intern profile required.', 'error')
        return redirect(url_for('main.index'))
    
    application = Application.query.filter_by(
        id=application_id,
        intern_id=current_user.intern.id
    ).first_or_404()
    
    return render_template('intern/application_detail.html', application=application)

@bp.route('/withdraw_application/<int:application_id>', methods=['POST'])
@login_required
def withdraw_application(application_id):
    """Withdraw an application."""
    if not current_user.intern:
        return jsonify({'error': 'Access denied'}), 403
    
    application = Application.query.filter_by(
        id=application_id,
        intern_id=current_user.intern.id
    ).first_or_404()
    
    if application.status in ['accepted', 'rejected']:
        return jsonify({'error': 'Cannot withdraw a decided application'}), 400
    
    application.update_status('withdrawn')
    
    return jsonify({'success': True, 'message': 'Application withdrawn successfully'})

@bp.route('/saved_internships')
@login_required
def saved_internships():
    """View saved internships (placeholder for future feature)."""
    if not current_user.intern:
        flash('Access denied. Intern profile required.', 'error')
        return redirect(url_for('main.index'))
    
    # This would be implemented with a SavedInternship model in the future
    saved_internships = []
    
    return render_template('intern/saved_internships.html', saved_internships=saved_internships)
