from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from models.user import User
from models.worker import Worker

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone', '')
        area = request.form.get('area', '')
        role = request.form.get('role', 'resident')
        
        user_model = User(current_app.db)
        
        try:
            user_id = user_model.create(username, email, password, role, phone, area)
            
            if role == 'worker':
                worker_model = Worker(current_app.db)
                worker_model.create(user_id, username, phone, [area])
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_model = User(current_app.db)
        user = user_model.verify_password(username, password)
        
        if user:
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['role'] = user['role']
            
            flash('Login successful!', 'success')
            
            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user['role'] == 'worker':
                return redirect(url_for('workers.dashboard'))
            else:
                return redirect(url_for('dashboard.resident_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))
