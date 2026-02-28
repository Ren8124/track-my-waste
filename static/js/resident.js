// Resident dashboard real-time updates
document.addEventListener('DOMContentLoaded', function() {
    // Connect to Socket.IO
    const socket = io();

    // Listen for complaint updates
    socket.on('complaint_update', function(data) {
        updateOrCreateComplaint(data);
        updateStats(); // Update the statistics
    });

    // Helper function to get status badge class
    function getStatusClass(status) {
        switch (status) {
            case 'pending':
                return 'bg-warning';
            case 'in_progress':
                return 'bg-info';
            case 'completed':
                return 'bg-success';
            case 'assigned':
                return 'bg-primary';
            default:
                return 'bg-secondary';
        }
    }

    function updateOrCreateComplaint(complaint) {
        const listGroup = document.querySelector('.list-group');
        if (!listGroup) return;

        // Check if this complaint belongs to the current user
        if (complaint.user_id !== currentUserId) return;

        // Check if the complaint already exists
        const existingComplaint = document.querySelector(`[data-complaint-id="${complaint._id}"]`);
        if (existingComplaint) {
            // Update existing complaint
            const statusBadge = existingComplaint.querySelector('.badge');
            if (statusBadge) {
                statusBadge.className = `badge ${getStatusClass(complaint.status)}`;
                statusBadge.textContent = complaint.status;
            }

            // Update worker info
            const workerInfo = existingComplaint.querySelector('.worker-info');
            if (workerInfo) {
                if (complaint.worker_name) {
                    workerInfo.innerHTML = `<br>Assigned to: ${complaint.worker_name}`;
                    workerInfo.style.display = 'block';
                } else {
                    workerInfo.style.display = 'none';
                }
            }
        } else {
            // Create new complaint item
            const complaintItem = document.createElement('div');
            complaintItem.className = 'list-group-item';
            complaintItem.setAttribute('data-complaint-id', complaint._id);

            complaintItem.innerHTML = `
                <div class="d-flex justify-content-between">
                    <h6>${complaint.description.substring(0, 50)}...</h6>
                    <span class="badge ${getStatusClass(complaint.status)}">
                        ${complaint.status}
                    </span>
                </div>
                <small class="text-muted">
                    Area: ${complaint.area} | Priority: ${complaint.priority}
                    ${complaint.worker_name ? 
                        `<br><span class="worker-info">Assigned to: ${complaint.worker_name}</span>` : 
                        '<span class="worker-info" style="display: none;"></span>'}
                </small>
            `;

            // Insert at the beginning of the list
            listGroup.insertBefore(complaintItem, listGroup.firstChild);

            // If there's a "No complaints yet" message, remove it
            const noComplaints = listGroup.querySelector('.text-muted');
            if (noComplaints && noComplaints.textContent.includes('No complaints yet')) {
                const emptyState = listGroup.parentElement.querySelector('.text-muted').parentElement;
                if (emptyState) {
                    emptyState.remove();
                }
            }
        }
    }

    function updateStats() {
        fetch('/api/resident/stats')
            .then(response => response.json())
            .then(stats => {
                // Update the statistics cards
                document.querySelector('.bg-primary h2').textContent = stats.total;
                document.querySelector('.bg-warning h2').textContent = stats.pending;
                document.querySelector('.bg-info h2').textContent = stats.in_progress;
                document.querySelector('.bg-success h2').textContent = stats.completed;
            })
            .catch(console.error);
    }
});