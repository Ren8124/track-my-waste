from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session, jsonify
from models.user import User
from models.worker import Worker
from models.schedule import Schedule
from models.tip import Tip
from models.complaint import Complaint
from utils.auth_decorators import login_required, role_required
from bson.objectid import ObjectId
import json
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    complaint_model = Complaint(current_app.db)
    user_model = User(current_app.db)
    worker_model = Worker(current_app.db)
    
    # Get statistics
    total_complaints = current_app.db.complaints.count_documents({})
    total_users = current_app.db.users.count_documents({'role': 'resident'})
    total_workers = current_app.db.workers.count_documents({})
    pending_complaints = current_app.db.complaints.count_documents({'status': 'pending'})
    
    # Get all workers for the assignment dropdown
    workers = list(current_app.db.workers.find())
    
    # Get recent complaints
    recent_complaints = list(current_app.db.complaints.find().sort('created_at', -1).limit(5))
    
    stats = {
        'total_complaints': total_complaints,
        'total_users': total_users,
        'total_workers': total_workers,
        'pending_complaints': pending_complaints
    }
    
    return render_template('admin/dashboard.html', stats=stats, recent_complaints=recent_complaints, workers=workers)

@admin_bp.route('/dashboard/api/analytics/complaints-by-area')
@login_required
@role_required('admin')
def complaints_by_area():
    try:
        complaints_by_area = list(current_app.db.complaints.aggregate([
            {"$group": {"_id": "$area", "count": {"$sum": 1}}}
        ]))
        
        # Fallback data if no complaints exist
        if not complaints_by_area:
            complaints_by_area = [
                {"_id": "Zone A", "count": 5},
                {"_id": "Zone B", "count": 7},
                {"_id": "Zone C", "count": 3}
            ]
            
        return jsonify(complaints_by_area)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/dashboard/api/analytics/worker-performance')
@login_required
@role_required('admin')
def worker_performance():
    try:
        workers = list(current_app.db.workers.find())
        performance_data = []
        
        for worker in workers:
            total_tasks = current_app.db.complaints.count_documents({"assigned_worker_id": worker["_id"]})
            completed_tasks = current_app.db.complaints.count_documents({
                "assigned_worker_id": worker["_id"],
                "status": "completed"
            })
            performance_data.append({
                "worker_name": worker.get("name", "Unknown"),
                "total": total_tasks,
                "completed": completed_tasks
            })
        
        # Fallback data if no workers exist
        if not performance_data:
            performance_data = [
                {"worker_name": "John", "total": 12, "completed": 10},
                {"worker_name": "Amit", "total": 8, "completed": 6},
                {"worker_name": "Sara", "total": 10, "completed": 9}
            ]
            
        return jsonify(performance_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# User Management
@admin_bp.route('/users')
@login_required
@role_required('admin')
def manage_users():
    # Get only residents from the users collection
    residents = list(current_app.db.users.find({'role': 'resident'}).sort('username', 1))
    return render_template('admin/manage_users.html', users=residents)

@admin_bp.route('/users/<user_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_user(user_id):
    user_model = User(current_app.db)
    user_model.delete(user_id)
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.manage_users'))

# Worker Management
@admin_bp.route('/workers')
@login_required
@role_required('admin')
def manage_workers():
    worker_model = Worker(current_app.db)
    workers = worker_model.get_all()
    return render_template('admin/manage_workers.html', workers=workers)

@admin_bp.route('/workers/add', methods=['POST'])
@login_required
@role_required('admin')
def add_worker():
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    areas = request.form.get('areas', '').split(',')
    vehicle_info = request.form.get('vehicle_info', '')
    
    # Create user account
    user_model = User(current_app.db)
    username = name.lower().replace(' ', '') if name else (email.split('@')[0] if email else 'worker')
    user_id = user_model.create(username, email, 'worker123', 'worker', phone)
    
    # Create worker profile
    worker_model = Worker(current_app.db)
    worker_model.create(user_id, name, phone, [a.strip() for a in areas if a.strip()], vehicle_info)
    
    flash('Worker added successfully!', 'success')
    return redirect(url_for('admin.manage_workers'))

@admin_bp.route('/workers/<worker_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_worker(worker_id):
    worker_model = Worker(current_app.db)
    worker_model.delete(worker_id)
    flash('Worker deleted successfully!', 'success')
    return redirect(url_for('admin.manage_workers'))

# Schedule Management
@admin_bp.route('/schedules')
@login_required
@role_required('admin')
def manage_schedules():
    schedule_model = Schedule(current_app.db)
    schedules = schedule_model.get_all()
    worker_model = Worker(current_app.db)
    workers = worker_model.get_all()
    return render_template('admin/manage_schedules.html', schedules=schedules, workers=workers)

@admin_bp.route('/schedules/add', methods=['POST'])
@login_required
@role_required('admin')
def add_schedule():
    area = request.form.get('area')
    day_of_week = int(request.form.get('day_of_week'))
    time = request.form.get('time')
    worker_id = request.form.get('worker_id')
    
    schedule_model = Schedule(current_app.db)
    schedule_model.create(area, day_of_week, time, worker_id if worker_id else None)
    
    flash('Schedule added successfully!', 'success')
    return redirect(url_for('admin.manage_schedules'))

@admin_bp.route('/schedules/<schedule_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_schedule(schedule_id):
    schedule_model = Schedule(current_app.db)
    schedule_model.delete(schedule_id)
    flash('Schedule deleted successfully!', 'success')
    return redirect(url_for('admin.manage_schedules'))

# Tips Management
@admin_bp.route('/tips')
@login_required
@role_required('admin')
def manage_tips():
    tip_model = Tip(current_app.db)
    tips = tip_model.get_all(active_only=False)
    return render_template('admin/manage_tips.html', tips=tips)

@admin_bp.route('/tips/add', methods=['POST'])
@login_required
@role_required('admin')
def add_tip():
    title = request.form.get('title')
    content = request.form.get('content')
    category = request.form.get('category', 'general')
    
    tip_model = Tip(current_app.db)
    tip_model.create(title, content, category)
    
    flash('Tip added successfully!', 'success')
    return redirect(url_for('admin.manage_tips'))

@admin_bp.route('/tips/<tip_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_tip(tip_id):
    tip_model = Tip(current_app.db)
    tip_model.delete(tip_id)
    flash('Tip deleted successfully!', 'success')
    return redirect(url_for('admin.manage_tips'))

# Complaint Assignment
@admin_bp.route('/complaints/<complaint_id>/assign', methods=['POST'])
@login_required
@role_required('admin')
def assign_complaint(complaint_id):
    try:
        data = request.get_json()
        worker_id = data.get('worker_id')
        
        if not worker_id:
            return jsonify({'error': 'Worker ID is required'}), 400

        # Validate worker exists
        worker = current_app.db.workers.find_one({'_id': ObjectId(worker_id)})
        if not worker:
            return jsonify({'error': 'Worker not found'}), 404

        # Update complaint with worker assignment
        result = current_app.db.complaints.update_one(
            {'_id': ObjectId(complaint_id)},
            {
                '$set': {
                    'assigned_worker_id': ObjectId(worker_id),
                    'worker_name': worker.get('name', 'Unknown'),
                    'status': 'assigned'
                }
            }
        )

        if result.modified_count == 0:
            return jsonify({'error': 'Complaint not found or no changes made'}), 404

        return jsonify({'message': 'Worker assigned successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/complaints/<complaint_id>/status', methods=['POST'])
@login_required
@role_required('admin')
def update_complaint_status(complaint_id):
    try:
        data = request.get_json()
        status = data.get('status')

        valid_statuses = ['pending', 'assigned', 'in_progress', 'completed', 'cancelled']
        if status not in valid_statuses:
            return jsonify({'error': 'Invalid status'}), 400

        result = current_app.db.complaints.update_one(
            {'_id': ObjectId(complaint_id)},
            {'$set': {'status': status}}
        )

        if result.modified_count == 0:
            return jsonify({'error': 'Complaint not found or no changes made'}), 404

        return jsonify({'message': 'Status updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
