from flask import Blueprint, render_template, current_app, session, redirect, url_for, jsonify
from models.complaint import Complaint
from models.schedule import Schedule
from utils.auth_decorators import login_required
from bson.objectid import ObjectId

dashboard_bp = Blueprint('dashboard', __name__)

# @dashboard_bp.route('/resident')
# @login_required
# def resident_dashboard():
#     complaint_model = Complaint(current_app.db)
#     schedule_model = Schedule(current_app.db)
    
#     complaints = complaint_model.find_by_user(session['user_id'])
#     schedules = schedule_model.find_by_area(session.get('area', ''))
    
#     return render_template('resident/dashboard.html', complaints=complaints, schedules=schedules)

@dashboard_bp.route('/resident')
def resident_dashboard():
    db = current_app.db
    user_id = session.get('user_id')
    
    if not user_id:
        return redirect(url_for('auth.login'))

    # Convert user_id to ObjectId for MongoDB queries
    user_id = ObjectId(user_id)

    # Get all complaints by the user
    recent_complaints = list(db.complaints.find(
        {'user_id': user_id}
    ).sort('created_at', -1))  # Sort by newest first

    # Get complaint statistics
    total = len(recent_complaints)
    in_progress = sum(1 for c in recent_complaints if c.get('status') == 'in_progress')
    completed = sum(1 for c in recent_complaints if c.get('status') == 'completed')
    pending = sum(1 for c in recent_complaints if c.get('status') == 'pending')

    stats = {
        'total': total,
        'in_progress': in_progress,
        'completed': completed,
        'pending': pending
    }

    # Get schedules for the user's area
    schedules = list(db.schedules.find())

    return render_template('resident/dashboard.html', 
                         stats=stats, 
                         recent_complaints=recent_complaints, 
                         schedules=schedules)

@dashboard_bp.route('/api/resident/stats')
@login_required
def get_resident_stats():
    db = current_app.db
    user_id = ObjectId(session.get('user_id'))

    # Get all complaints by the user
    recent_complaints = list(db.complaints.find({'user_id': user_id}))

    # Calculate statistics
    total = len(recent_complaints)
    in_progress = sum(1 for c in recent_complaints if c.get('status') == 'in_progress')
    completed = sum(1 for c in recent_complaints if c.get('status') == 'completed')
    pending = sum(1 for c in recent_complaints if c.get('status') == 'pending')

    stats = {
        'total': total,
        'in_progress': in_progress,
        'completed': completed,
        'pending': pending
    }

    return jsonify(stats)