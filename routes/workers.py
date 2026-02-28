from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from models.complaint import Complaint
from models.worker import Worker
from utils.auth_decorators import login_required, role_required

workers_bp = Blueprint('workers', __name__)

@workers_bp.route('/dashboard')
@login_required
@role_required('worker')
def dashboard():
    worker_model = Worker(current_app.db)
    complaint_model = Complaint(current_app.db)
    
    worker = worker_model.find_by_user_id(session['user_id'])
    
    if worker:
        tasks = complaint_model.find_by_worker(str(worker['_id']))
    else:
        tasks = []
    
    # Statistics
    pending = len([t for t in tasks if t.get('status') == 'pending'])
    in_progress = len([t for t in tasks if t.get('status') == 'in_progress'])
    completed = len([t for t in tasks if t.get('status') == 'completed'])
    
    return render_template('worker/dashboard.html', 
                         tasks=tasks,
                         stats={'pending': pending, 'in_progress': in_progress, 'completed': completed})

@workers_bp.route('/tasks')
@login_required
@role_required('worker')
def tasks():
    worker_model = Worker(current_app.db)
    complaint_model = Complaint(current_app.db)
    
    worker = worker_model.find_by_user_id(session['user_id'])
    
    if worker:
        tasks = complaint_model.find_by_worker(str(worker['_id']))
    else:
        tasks = []
    
    return render_template('worker/tasks.html', tasks=tasks, str=str)

@workers_bp.route('/task/<task_id>/update-status', methods=['POST'])
@login_required
@role_required('worker')
def update_task_status(task_id):
    new_status = request.form.get('status')
    
    complaint_model = Complaint(current_app.db)
    complaint_model.update(task_id, {'status': new_status})
    
    # Get the referrer to determine which page to return to
    referrer = request.referrer
    
    complaint = complaint_model.find_by_id(task_id)
    if complaint:
        # Emit socket event for real-time updates
        current_app.socketio.emit('complaint_update', {
            '_id': str(complaint['_id']),
            'description': complaint['description'],
            'area': complaint['area'],
            'priority': complaint['priority'],
            'status': new_status,
            'user_id': str(complaint['user_id']),
            'worker_name': complaint.get('worker_name'),
            'created_at': complaint['created_at'].isoformat() if complaint.get('created_at') else None
        })
    
    flash('Task status updated!', 'success')
    
    # Return to the dashboard if that's where we came from, otherwise go to tasks
    if referrer and 'dashboard' in referrer:
        return redirect(url_for('workers.dashboard'))
    return redirect(url_for('workers.tasks'))
