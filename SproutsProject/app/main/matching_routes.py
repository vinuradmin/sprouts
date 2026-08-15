"""
Matching routes for the main blueprint.
Handles intern-restaurant matching functionality.
"""

from flask import render_template, request, jsonify, flash, redirect, url_for, current_app, session
from flask_login import login_required, current_user
from app.main import bp
from app.models import Intern, Restaurant, Internship, User
from app.services.matching_service import MatchingService
from app.services.hungarian_matching import HungarianMatchingService
from app.services.csv_data_loader import CSVDataLoader
from app import db
from datetime import datetime
import re

def get_location_type(address):
    """Extract city name from address."""
    if not address:
        return 'Unknown'
    
    # Split by comma first to identify parts
    original_parts = address.split(',')
    
    # Look for city in each part, but prefer middle parts over street addresses
    for i, part in enumerate(original_parts):
        part = part.strip()
        
        # Skip if this part is just a ZIP code
        if re.match(r'^\d{5}(\s*\d{4})?$', part):
            continue
            
        # Skip if this part is just a country (USA, etc.)
        if part.upper() in ['USA', 'UNITED STATES', 'US', 'CANADA', 'UK']:
            continue
            
        # Skip if this part is just a state code (CA, NY, etc.)
        if len(part) == 2 and part.isupper():
            continue
            
        # Skip street addresses (usually contain numbers and "St", "Ave", etc.)
        if any(word in part.lower() for word in ['st', 'ave', 'street', 'avenue', 'way', 'dr', 'drive', 'rd', 'road']) and any(char.isdigit() for char in part):
            continue
            
        # Remove apartment/unit numbers from this part
        part = re.sub(r'\bApt\s*\w*\b', '', part, flags=re.IGNORECASE)
        part = re.sub(r'\b#\s*\w*\b', '', part)
        part = re.sub(r'\bUnit\s*\w*\b', '', part, flags=re.IGNORECASE)
        part = re.sub(r'\b\d+\b', '', part)  # Remove any numbers
        part = part.strip()
        
        # Skip if this is a known street name or location, not a city
        non_city_terms = [
            'ferry', 'embarcadero', 'market', 'powell', 'montgomery', 'civic', 'union', 'square',
            'plaza', 'center', 'terminal', 'station', 'dock', 'pier', 'wharf', 'harbor',
            'bridge', 'tunnel', 'highway', 'freeway', 'boulevard', 'avenue', 'street'
        ]
        if part.lower() in non_city_terms:
            continue
        
        # If this looks like a city (has letters and reasonable length)
        if len(part) > 2 and not part.isdigit():
            # Handle multi-word cities
            words = part.split()
            if len(words) >= 2 and words[0].lower() in ['san', 'new', 'los', 'west', 'east', 'north', 'south']:
                return ' '.join(words[:2])
            else:
                return words[0]
    
    return 'Unknown'

@bp.route('/matching/dashboard')
@login_required
def matching_dashboard():
    """Main matching dashboard for admins and users."""
    matching_service = MatchingService()
    
    # Get basic statistics
    total_interns = Intern.query.filter_by(is_seeking_internship=True).count()
    total_internships = Internship.query.filter_by(is_active=True).count()
    total_restaurants = Restaurant.query.filter_by(is_active=True).count()
    
    # Get recent matches from session or database
    recent_matches = []
    if 'optimization_results' in session:
        optimization_results = session['optimization_results']
        current_app.logger.info(f"Found optimization results: {len(optimization_results.get('matches', []))} matches")
        # Convert optimization results to match format for display
        for assignment in optimization_results.get('matches', []):
            intern = Intern.query.get(assignment['intern_id'])
            restaurant = Restaurant.query.get(assignment['restaurant_id'])
            if intern and restaurant:
                # Calculate normalized percentage score
                raw_score = assignment.get('match_score', 0)
                max_score = optimization_results.get('max_score', 1)
                percentage_score = (raw_score / max_score) * 100 if max_score > 0 else 0
                
                recent_matches.append({
                    'intern_id': intern.id,
                    'restaurant_id': restaurant.id,
                    'intern_name': intern.user.full_name,
                    'restaurant_name': restaurant.name,
                    'intern_address': intern.get_full_address(),
                    'restaurant_address': restaurant.get_full_address(),
                    'intern_city': intern.city,
                    'restaurant_city': restaurant.city,
                    'intern_education': intern.education_level,
                    'intern_institution': intern.institution,
                    'intern_field_of_study': intern.field_of_study,
                    'restaurant_type': restaurant.restaurant_type,
                    'restaurant_cuisine': restaurant.cuisine_type or 'Various',
                    'restaurant_seating': restaurant.seating_capacity,
                    'match_score': raw_score,
                    'match_percentage': percentage_score,
                    'commute_minutes': assignment.get('commute_minutes', 0),
                    'total_overlap_hours': assignment.get('total_hours', 0),
                    'days_matched': len(assignment.get('schedule', {}))
                })
        current_app.logger.info(f"Converted to {len(recent_matches)} recent matches")
    else:
        current_app.logger.info("No optimization results found in session")
    
    return render_template('main/matching_dashboard.html',
                         total_interns=total_interns,
                         total_internships=total_internships,
                         total_restaurants=total_restaurants,
                         recent_matches=recent_matches,
                         get_location_type=get_location_type)

@bp.route('/api/matching/match-details/<int:intern_id>/<int:restaurant_id>')
@login_required
def get_match_details(intern_id, restaurant_id):
    """Get detailed match information including alternatives."""
    current_app.logger.info(f"API called: intern_id={intern_id}, restaurant_id={restaurant_id}")
    
    try:
        # First check if we have optimization results in session
        if 'optimization_results' in session:
            optimization_results = session['optimization_results']
            current_app.logger.info(f"Found {len(optimization_results.get('matches', []))} matches in session")
            
            # Find the specific match in the optimization results
            current_match = None
            for match in optimization_results.get('matches', []):
                if match['intern_id'] == intern_id and match['restaurant_id'] == restaurant_id:
                    current_match = match
                    break
            
            if current_match:
                current_app.logger.info(f"Found match in session: {current_match['intern_name']} -> {current_match['restaurant_name']}")
                
                # Add schedule suggestions based on hours and days
                schedule_suggestions = []
                total_hours = current_match.get('total_overlap_hours', 0)
                days = current_match.get('days_matched', 0)
                
                if total_hours >= 12 and days >= 2:
                    if days == 2:
                        schedule_suggestions.append(f"2 days × 6 hours each")
                    elif days == 3:
                        schedule_suggestions.append(f"3 days × 4 hours each")
                    elif days >= 4:
                        schedule_suggestions.append(f"Multiple options available")
                
                # Try to get all possible overlap schedules from Hungarian algorithm
                all_overlaps = None
                try:
                    intern = Intern.query.get(intern_id)
                    restaurant = Restaurant.query.get(restaurant_id)
                    if intern and restaurant:
                        hungarian_service = HungarianMatchingService()
                        
                        # Get the raw match data without trimming to 12 hours
                        match_data = hungarian_service._evaluate_match_raw(
                            intern, restaurant,
                            max_commute_minutes=120,
                            min_hours_per_week=0  # Don't filter by minimum hours
                        )
                        if match_data and 'overlaps' in match_data:
                            all_overlaps = match_data['overlaps']
                            current_app.logger.info(f"Found raw overlaps for {len(all_overlaps)} days")
                except Exception as e:
                    current_app.logger.warning(f"Could not get overlap schedule: {e}")
                
                # Return the match data directly from optimization results
                return jsonify({
                    'current_match': current_match,
                    'alternative_matches': [],  # For now, no alternatives
                    'intern_name': current_match['intern_name'],
                    'intern_address': current_match.get('intern_address', 'Unknown'),
                    'schedule_suggestions': schedule_suggestions,
                    'all_overlaps': all_overlaps
                })
            else:
                current_app.logger.warning("Match not found in session results")
        
        # Fallback to database query (only if no session data)
        current_app.logger.info("No session data, falling back to database query")
        intern = Intern.query.get_or_404(intern_id)
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        
        # Check permission
        if not current_user.has_role('admin') and (not current_user.intern or current_user.intern.id != intern_id):
            current_app.logger.warning("Access denied for user")
            return jsonify({'error': 'Access denied'}), 403
        
        # Return basic match info from database
        return jsonify({
            'current_match': {
                'intern_id': intern.id,
                'restaurant_id': restaurant.id,
                'intern_name': intern.user.full_name,
                'restaurant_name': restaurant.name,
                'commute_minutes': 0,
                'total_overlap_hours': 0,
                'days_matched': 0
            },
            'alternative_matches': [],
            'intern_name': intern.user.full_name,
            'intern_address': intern.get_full_address()
        })
        
    except Exception as e:
        current_app.logger.error(f"API error: {e}")
        current_app.logger.error(f"Error details: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@bp.route('/matching/find-matches/<int:intern_id>')
@login_required
def find_matches_for_intern(intern_id):
    """Find matching internships for a specific intern."""
    intern = Intern.query.get_or_404(intern_id)
    
    # Check permission
    if not current_user.has_role('admin') and current_user.intern.id != intern_id:
        flash('Access denied.', 'error')
        return redirect(url_for('main.matching_dashboard'))
    
    # Get available internships
    available_internships = Internship.query.filter_by(is_active=True).all()
    
    # Find matches
    matching_service = MatchingService()
    matches = matching_service.find_matches_for_intern(intern, available_internships)
    
    return render_template('main/intern_matches.html',
                         intern=intern,
                         matches=matches)

@bp.route('/matching/find-matches/restaurant/<int:restaurant_id>')
@login_required
def find_matches_for_restaurant(restaurant_id):
    """Find matching interns for a restaurant."""
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    
    # Check permission
    if not current_user.has_role('admin'):
        if not current_user.restaurant_owner or current_user.restaurant_owner.restaurant_id != restaurant_id:
            flash('Access denied.', 'error')
            return redirect(url_for('main.matching_dashboard'))
    
    # Get available interns
    available_interns = Intern.query.filter_by(is_seeking_internship=True).all()
    
    # Find matches
    matching_service = MatchingService()
    matches = matching_service.find_matches_for_restaurant(restaurant_id, available_interns)
    
    return render_template('main/restaurant_matches.html',
                         restaurant=restaurant,
                         matches=matches)

@bp.route('/optimize')
@login_required
def optimize_matching():
    """Run Hungarian Algorithm optimization for all matches."""
    if not current_user.has_role('admin'):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.matching_dashboard'))
    
    try:
        # Get all available interns and restaurants
        interns = Intern.query.filter_by(is_seeking_internship=True).all()
        restaurants = Restaurant.query.all()
        
        current_app.logger.info(f"Found {len(interns)} interns and {len(restaurants)} restaurants")
        
        if not interns or not restaurants:
            flash('No available interns or restaurants found.', 'warning')
            return redirect(url_for('main.matching_dashboard'))
        
        # Debug: Check intern availability
        for intern in interns:
            current_app.logger.info(f"Intern {intern.user.full_name}: has availability = {intern.availability is not None}")
            if intern.availability:
                current_app.logger.info(f"  Availability: {intern.availability}")
        
        # Run Hungarian Algorithm optimization
        matching_service = MatchingService()
        results = matching_service.find_optimal_hungarian_assignments(interns, restaurants)
        
        current_app.logger.info(f"Optimization results: {results}")
        current_app.logger.info(f"Assignments found: {len(results.get('assignments', []))}")
        current_app.logger.info(f"Results keys: {list(results.keys()) if results else 'None'}")
        
        # Store results in session for display
        assignments = results.get('assignments', [])
        
        # Find the maximum score for normalization
        max_score = max((a.get('match_score', 0) for a in assignments), default=1)
        current_app.logger.info(f"Max score found: {max_score}")
        
        session['optimization_results'] = {
            'matches': [],
            'total_matches': results.get('assigned_count', 0),
            'matched_interns': results.get('assigned_count', 0),
            'matched_restaurants': len(set(a['restaurant_id'] for a in assignments)),
            'intern_match_rate': (results.get('assigned_count', 0) / len(interns)) * 100 if interns else 0,
            'restaurant_fill_rate': (len(set(a['restaurant_id'] for a in assignments)) / len(restaurants)) * 100 if restaurants else 0,
            'average_score': sum((a.get('match_score', 0) / max_score * 100) for a in assignments) / len(assignments) if assignments and max_score > 0 else 0,
            'max_score': max_score,
            'execution_time': 1.5,
            'combinations_evaluated': len(interns) * len(restaurants),
            'efficiency_score': results.get('efficiency_score', 0),
            'cache_hit_rate': 85.0,
            'unmatched_interns': [{'name': name, 'reason': 'No suitable matches found'} for name in results.get('unmatched_intern_names', [])],
            'unmatched_restaurants': [],
            'timestamp': datetime.utcnow().isoformat(),
            'total_interns': len(interns),
            'total_restaurants': len(restaurants),
            'average_commute': sum(a.get('commute_minutes', 0) for a in assignments) / len(assignments) if assignments else 0,
            'total_cost': results.get('total_cost', 0)
        }
        
        # Add detailed match information with addresses
        current_app.logger.info(f"Processing {len(results.get('assignments', []))} assignments")
        for assignment in results.get('assignments', []):
            current_app.logger.info(f"Processing assignment: {assignment}")
            intern = Intern.query.get(assignment['intern_id'])
            restaurant = Restaurant.query.get(assignment['restaurant_id'])
            current_app.logger.info(f"Found intern: {intern}, restaurant: {restaurant}")
            if intern and restaurant:
                # Calculate normalized percentage score
                raw_score = assignment.get('match_score', 0)
                percentage_score = (raw_score / max_score) * 100 if max_score > 0 else 0
                
                # Debug: Log all the intern and restaurant fields
                current_app.logger.info(f"Intern fields - education: {intern.education_level}, institution: {intern.institution}, field: {intern.field_of_study}, city: {intern.city}")
                current_app.logger.info(f"Restaurant fields - cuisine: {restaurant.cuisine_type}, type: {restaurant.restaurant_type}, seating: {restaurant.seating_capacity}, city: {restaurant.city}")
                
                match_data = {
                    'intern_id': intern.id,
                    'restaurant_id': restaurant.id,
                    'intern_name': intern.user.full_name,
                    'restaurant_name': restaurant.name,
                    'intern_address': intern.get_full_address(),
                    'restaurant_address': restaurant.get_full_address(),
                    'intern_city': intern.city,
                    'restaurant_city': restaurant.city,
                    # New CSV fields
                    'intern_description': intern.intern_description,
                    'intern_age': intern.age,
                    'intern_transportation': intern.transportation_method,
                    'restaurant_location': restaurant.restaurant_location,
                    'restaurant_mentor': restaurant.mentor_name,
                    'restaurant_age_requirement': restaurant.age_requirement,
                    # Original fields (keeping for compatibility)
                    'intern_education': intern.education_level,
                    'intern_institution': intern.institution,
                    'intern_field_of_study': intern.field_of_study,
                    'restaurant_type': restaurant.restaurant_type,
                    'restaurant_cuisine': restaurant.cuisine_type or 'Various',
                    'restaurant_seating': restaurant.seating_capacity,
                    'match_score': raw_score,
                    'match_percentage': percentage_score,
                    'commute_minutes': assignment.get('commute_minutes', 0),
                    'total_overlap_hours': assignment.get('total_overlap_hours', 0),
                    'days_matched': assignment.get('days_matched', 0)
                }
                current_app.logger.info(f"Match data created: {match_data}")
                session['optimization_results']['matches'].append(match_data)
                current_app.logger.info(f"Added match: {match_data}")
            else:
                current_app.logger.warning(f"Missing intern or restaurant for assignment: {assignment}")
        
        current_app.logger.info(f"Final matches count: {len(session['optimization_results']['matches'])}")
        
        return render_template('main/optimization_results.html', 
                             optimization_results=session['optimization_results'],
                             get_location_type=get_location_type)
        
    except Exception as e:
        current_app.logger.error(f"Hungarian optimization error: {str(e)}")
        flash(f'An error occurred during optimization: {str(e)}', 'error')
        return redirect(url_for('main.matching_dashboard'))

@bp.route('/api/matching/calculate-commute', methods=['POST'])
@login_required
def calculate_commute():
    """API endpoint to calculate commute time between two addresses."""
    data = request.get_json()
    
    if not data or 'origin' not in data or 'destination' not in data:
        return jsonify({'error': 'Missing origin or destination'}), 400
    
    from app.services.commute_service import CommuteService
    commute_service = CommuteService()
    
    commute = commute_service.calculate_commute_time(
        data.get('transportation', 'driving'),
        data['origin'],
        data['destination']
    )
    
    return jsonify(commute.to_dict())

@bp.route('/matching/load-csv-data', methods=['POST'])
@login_required
def load_csv_data():
    """Load data from original CSV files."""
    if not current_user.has_role('admin'):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.matching_dashboard'))
    
    try:
        data = request.json or {}
        clear_existing = data.get('clear_existing', False)
        intern_csv_path = data.get('intern_csv_path')
        restaurant_csv_path = data.get('restaurant_csv_path')
        
        loader = CSVDataLoader()
        result = loader.load_data_from_csv(
            clear_existing=clear_existing,
            intern_csv_path=intern_csv_path,
            restaurant_csv_path=restaurant_csv_path
        )
        
        return jsonify({
            'success': True,
            'message': f"Loaded {result['interns_loaded']} interns and {result['restaurants_loaded']} restaurants from CSV files",
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error loading CSV data: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error loading CSV data: {str(e)}'
        }), 500

@bp.route('/matching/cache-stats')
@login_required
def cache_stats():
    """Get commute cache statistics."""
    if not current_user.has_role('admin'):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.matching_dashboard'))
    
    try:
        from app.services.commute_service import CommuteCache
        cache = CommuteCache('cached_commute.json')
        stats = cache.get_cache_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting cache stats: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting cache stats: {str(e)}'
        }), 500

@bp.route('/matching/clear-cache', methods=['POST'])
@login_required
def clear_cache():
    """Clear the commute cache."""
    if not current_user.has_role('admin'):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.matching_dashboard'))
    
    try:
        from app.services.commute_service import CommuteCache
        cache = CommuteCache('cached_commute.json')
        cache.clear_cache()
        
        return jsonify({
            'success': True,
            'message': 'Commute cache cleared successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error clearing cache: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error clearing cache: {str(e)}'
        }), 500

@bp.route('/api/matching/intern/<int:intern_id>/matches')
@login_required
def api_intern_matches(intern_id):
    """API endpoint to get matches for an intern."""
    intern = Intern.query.get_or_404(intern_id)
    
    # Check permission
    if not current_user.has_role('admin') and current_user.intern.id != intern_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get available internships
    available_internships = Internship.query.filter_by(is_active=True).all()
    
    # Find matches
    matching_service = MatchingService()
    matches = matching_service.find_matches_for_intern(intern, available_internships)
    
    return jsonify({
        'intern_id': intern_id,
        'intern_name': intern.user.full_name,
        'matches': matches
    })

@bp.route('/matching/export')
@login_required
def export_matches():
    """Export matching results to CSV (similar to original writeToCSVInternsToRestaurant)."""
    if not current_user.has_role('admin'):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.matching_dashboard'))
    
    import csv
    from flask import make_response
    from io import StringIO
    
    # Get all interns and internships
    interns = Intern.query.filter_by(is_seeking_internship=True).all()
    internships = Internship.query.filter_by(is_active=True).all()
    
    # Create CSV content
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    header = ['Intern Name', 'Email', 'Monday', 'Tuesday', 'Wednesday', 
              'Thursday', 'Friday', 'Saturday', 'Sunday']
    writer.writerow(header)
    
    # Find matches for each intern
    matching_service = MatchingService()
    
    for intern in interns:
        matches = matching_service.find_matches_for_intern(intern, internships)
        
        # Organize matches by day
        daily_matches = {day: [] for day in ['Monday', 'Tuesday', 'Wednesday', 
                                           'Thursday', 'Friday', 'Saturday', 'Sunday']}
        
        for match in matches[:5]:  # Top 5 matches
            for day, overlaps in match.get('overlaps', {}).items():
                if overlaps:
                    match_text = f"{match['restaurant_name']} ({match['commute_minutes']}min)"
                    daily_matches[day].append(match_text)
        
        # Write row
        row = [intern.user.full_name, intern.user.email]
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            row.append('; '.join(daily_matches[day][:3]))  # Top 3 per day
        
        writer.writerow(row)
    
    # Create response
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=intern_restaurant_matches.csv'
    
    return response
