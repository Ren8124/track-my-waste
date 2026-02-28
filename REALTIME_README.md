Real-time updates (Socket.IO + MongoDB)

What I changed
- Integrated Flask-SocketIO server-side (optional): adds websocket endpoints and a background task that emits analytics updates.
- Implemented a change-listener that tries MongoDB change streams (requires a replica set). If change streams aren't available, the server falls back to polling the database every 5 seconds and emits updates when data changes.
- Client-side (`static/js/charts.js`): connects to Socket.IO and listens for `analytics_update` events to update charts in real time.
- `templates/admin/dashboard.html` includes the Socket.IO client.
- `requirements.txt` updated to include `flask-socketio` and `eventlet`.

How to enable
1. Install new dependencies (activate your virtualenv first):

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2a. (Optional - recommended) Enable MongoDB change streams by running a local replica set. For development you can start a single-node replica set:

```powershell
# example for a MongoDB 6+ binary on Windows (run in a separate terminal)
mongod --dbpath C:\data\db --replSet rs0
# then in mongosh
rs.initiate()
```

2b. If you cannot use a replica set, the server will fallback to polling (every 5 seconds) to detect changes.

3. Run the app (Socket.IO will be used if installed):

```powershell
python app.py
```

Security notes
- The server currently restricts Socket.IO connections to users who have `session['role'] == 'admin'` at connect time. This relies on the Flask session cookie being available to the socket connection. For production consider a stronger auth scheme (token-based authentication for sockets).

Next steps / improvements
- Add finer-grained events (e.g., only send updated subset rather than full analytics) to reduce bandwidth.
- Add unit tests for compute_analytics and the polling logic.
- Consider using namespaces/rooms so only the admin UI receives analytics updates instead of broadcasting to every connection.
