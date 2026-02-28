from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, session
from models.complaint import Complaint
from models.user import User
from utils.auth_decorators import login_required, role_required
from utils.email_service import send_complaint_status_email
from bson.objectid import ObjectId

complaints_bp = Blueprint('complaints', __name__)

@complaints_bp.route('/submit', methods=['GET', 'POST'])
@login_required
@role_required('resident')
def submit():
    if request.method == 'POST':
        description = request.form.get('description')
        area = request.form.get('area')
        priority = request.form.get('priority', 'medium')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        
        complaint_model = Complaint(current_app.db)
        complaint_id = complaint_model.create(
            session['user_id'],
            description,
            area,
            priority,
            float(latitude) if latitude else None,
            float(longitude) if longitude else None
        )
        
        # Fetch the complete complaint data and emit socket event
        complaint = complaint_model.find_by_id(complaint_id)
        if complaint:
            current_app.socketio.emit('complaint_update', {
                '_id': str(complaint['_id']),
                'description': complaint['description'],
                'area': complaint['area'],
                'priority': complaint['priority'],
                'status': complaint['status'],
                'created_at': complaint['created_at'].isoformat(),
                'user_id': str(complaint['user_id']),
                'worker_name': complaint.get('worker_name'),
            })
        
        flash('Complaint submitted successfully!', 'success')
        return redirect(url_for('dashboard.resident_dashboard'))
    
    return render_template('resident/submit_complaint.html')

@complaints_bp.route('/my-complaints')
@login_required
@role_required('resident')
def my_complaints():
    complaint_model = Complaint(current_app.db)
    complaints = complaint_model.find_by_user(session['user_id'])
    
    return render_template('resident/complaints.html', complaints=complaints)

@complaints_bp.route('/<complaint_id>/update', methods=['POST'])
@login_required
def update(complaint_id):
    data = request.get_json() if request.is_json else request.form.to_dict()
    
    complaint_model = Complaint(current_app.db)
    complaint = complaint_model.find_by_id(complaint_id)
    
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404
    
    # Authorization check
    if session.get('role') == 'resident' and str(complaint['user_id']) != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    update_data = {}
    if 'description' in data:
        update_data['description'] = data['description']
    if 'status' in data:
        update_data['status'] = data['status']
        
        # Send email notification
        user_model = User(current_app.db)
        user = user_model.find_by_id(str(complaint['user_id']))
        if user:
            send_complaint_status_email(user['email'], complaint_id, data['status'])
    
    complaint_model.update(complaint_id, update_data)
    
    # Emit socket event for the update
    updated_complaint = complaint_model.find_by_id(complaint_id)
    if updated_complaint:
        current_app.socketio.emit('complaint_update', {
            '_id': str(updated_complaint['_id']),
            'description': updated_complaint['description'],
            'area': updated_complaint['area'],
            'priority': updated_complaint['priority'],
            'status': updated_complaint['status'],
            'created_at': updated_complaint['created_at'].isoformat(),
            'user_id': str(updated_complaint['user_id']),
            'worker_name': updated_complaint.get('worker_name'),
        })
    
    if request.is_json:
        return jsonify({'success': True})
    
    flash('Complaint updated successfully!', 'success')
    return redirect(url_for('complaints.my_complaints'))

@complaints_bp.route('/<complaint_id>/delete', methods=['POST'])
@login_required
@role_required('resident')
def delete(complaint_id):
    complaint_model = Complaint(current_app.db)
    complaint = complaint_model.find_by_id(complaint_id)
    
    if complaint and str(complaint['user_id']) == session['user_id']:
        complaint_model.delete(complaint_id)
        flash('Complaint deleted successfully!', 'success')
    else:
        flash('Unauthorized or complaint not found.', 'danger')
    
    return redirect(url_for('complaints.my_complaints'))

@complaints_bp.route('/api/all')
@login_required
@role_required('admin')
def api_all():
    complaint_model = Complaint(current_app.db)
    complaints = complaint_model.get_all()
    
    # Convert ObjectId to string for JSON serialization
    for c in complaints:
        c['_id'] = str(c['_id'])
        c['user_id'] = str(c['user_id'])
        if c.get('assigned_worker_id'):
            c['assigned_worker_id'] = str(c['assigned_worker_id'])
    
    return jsonify(complaints)
