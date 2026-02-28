from flask import Flask, render_template, redirect, url_for, session
# Prefer real pymongo, but fall back to mongomock for local development/tests if pymongo isn't installed.
try:
    from pymongo import MongoClient
except ImportError:
    try:
        from mongomock import MongoClient  # in-memory fallback for development
        print("Info: 'pymongo' not installed, using 'mongomock' as an in-memory fallback.")
    except ImportError:
        raise ImportError(
            "The 'pymongo' package is required. Install it with 'pip install pymongo' "
            "or install 'mongomock' for a development fallback: 'pip install mongomock'."
        )

from config import Config
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config.from_object(Config)

# Feature toggle: enable realtime via environment variable ENABLE_REALTIME=1
app.config['ENABLE_REALTIME'] = os.environ.get('ENABLE_REALTIME', os.getenv('ENABLE_REALTIME', '0'))

# Initialize Socket.IO
from flask_socketio import SocketIO, disconnect
socketio = SocketIO(app, cors_allowed_origins="*")
app.socketio = socketio  # Make socketio accessible via current_app

# Ensure DEBUG is set so errors show up while developing
app.config.setdefault('DEBUG', True)

# Ensure SECRET_KEY is set so session access doesn't raise a RuntimeError
# Priority: Config -> ENV -> fallback dev secret (only for local/dev use)
app.secret_key = app.config.get('SECRET_KEY') or os.environ.get('SECRET_KEY') or 'dev-secret-key'

# MongoDB Connection with safe fallbacks and short timeout so the app still runs even if MongoDB is unreachable.
mongo_uri = app.config.get('MONGODB_URI') or os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017'
db_name = app.config.get('DATABASE_NAME') or os.environ.get('DATABASE_NAME') or 'trackmywaste'

# Use a short server selection timeout to avoid long hangs on startup
client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
try:
    # Force a server selection to surface connection errors early
    client.server_info()
except Exception as e:
    # Print a clear warning to the terminal; app will continue and use the client object (may be unusable until Mongo is available)
    print('Warning: MongoDB connection failed or timed out:', e)

db = client[db_name]

# Make db available on app
app.db = db

# Register Blueprints
from routes.auth import auth_bp
from routes.complaints import complaints_bp
from routes.workers import workers_bp
from routes.admin import admin_bp
from routes.dashboard import dashboard_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(complaints_bp, url_prefix='/complaints')
app.register_blueprint(workers_bp, url_prefix='/workers')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')


def compute_analytics(db):
    """Compute analytics payload used by admin charts."""
    try:
        complaints_by_area = list(db.complaints.aggregate([
            {"$group": {"_id": "$area", "count": {"$sum": 1}}}
        ]))
        workers = list(db.workers.find())
        performance = []
        for worker in workers:
            total = db.complaints.count_documents({"assigned_worker_id": worker.get("_id")})
            completed = db.complaints.count_documents({"assigned_worker_id": worker.get("_id"), "status": "completed"})
            performance.append({"worker_name": worker.get("name", "Unknown"), "total": total, "completed": completed})

        # Ensure sensible defaults
        if not complaints_by_area:
            complaints_by_area = [{"_id": "Zone A", "count": 0}]
        if not performance:
            performance = [{"worker_name": "N/A", "total": 0, "completed": 0}]

        return {
            "complaints_by_area": complaints_by_area,
            "worker_performance": performance
        }
    except Exception as e:
        return {"error": str(e)}


def start_change_listener(app, socketio_instance, poll_interval=5):
    """Background task: try MongoDB change streams, otherwise poll periodically.

    Emits 'analytics_update' events (payload from compute_analytics) via Socket.IO.
    """
    db = app.db

    def emit_analytics():
        payload = compute_analytics(db)
        # Broadcast to all connected clients; client-side should only process if on admin dashboard
        try:
            socketio_instance.emit('analytics_update', payload, broadcast=True)
        except Exception:
            # fallback to non-broadcast emit (older socketio versions)
            try:
                socketio_instance.emit('analytics_update', payload)
            except Exception:
                pass

    # Try change stream first (requires replica set)
    try:
        # watch complaints and workers
        with db.complaints.watch([], full_document='updateLookup') as stream1:
            # emit initial snapshot first
            emit_analytics()
            for change in stream1:
                emit_analytics()
    except Exception:
        # Change streams unavailable, fall back to polling
        import time
        last_snapshot = None
        while True:
            try:
                payload = compute_analytics(db)
                if payload != last_snapshot:
                    emit_analytics()
                    last_snapshot = payload
            except Exception:
                pass
            time.sleep(poll_interval)


def _start_realtime():
    """Initialize Socket.IO and background listener at startup if socketio available.

    This function is invoked at import-time to be robust in different run modes; if
    Flask provides `before_first_request` it would be fine to call there instead.
    """
    global socketio
    # Respect the feature toggle
    if app.config.get('ENABLE_REALTIME') != '1':
        print('Realtime disabled by configuration (ENABLE_REALTIME != 1).')
        return

    if SocketIO is None:
        print('Warning: flask_socketio not installed; real-time features disabled.')
        return

    # Initialize SocketIO once and attach to app
    if socketio is None:
        socketio = SocketIO(app, cors_allowed_origins="*")
        # register a simple connect handler to reject non-admins
        try:
            from flask import session as flask_session

            @socketio.on('connect')
            def _on_connect():
                # Only allow admin users to stay connected for analytics
                role = flask_session.get('role')
                if role != 'admin':
                    # politely disconnect non-admins
                    try:
                        disconnect()
                    except Exception:
                        pass

        except Exception:
            # if session-based auth is not available, allow connection but it's the caller's responsibility
            pass

        # start background task
        socketio.start_background_task(start_change_listener, app, socketio)

# Try starting realtime immediately; if running under a WSGI runner this may be
# a no-op or will start background tasks when the process starts.
try:
    _start_realtime()
except Exception:
    # If startup fails here it's non-fatal; realtime will be attempted again in __main__.
    pass


# Inject ENABLE_REALTIME into templates so we can conditionally load client script
@app.context_processor
def inject_enable_realtime():
    return dict(ENABLE_REALTIME=app.config.get('ENABLE_REALTIME', '0'))



@app.route('/')
def index():
    print("Testing base route")
    # index = render_template('tempplates/index.html')
    # return index
    if 'user_id' in session:
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif role == 'worker':
            return redirect(url_for('workers.dashboard'))
        else:
            return redirect(url_for('dashboard.resident_dashboard'))
    return render_template('index.html')

@app.route('/tips')
def tips():
    tips_list = list(db.tips.find().sort('created_at', -1))
    return render_template('tips.html', tips=tips_list)

if __name__ == '__main__':
    socketio.run(app, debug=app.config['DEBUG'])
