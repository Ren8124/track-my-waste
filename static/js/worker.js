// Worker dashboard real-time updates
document.addEventListener('DOMContentLoaded', function() {
    // Connect to Socket.IO
    const socket = io();

    // Listen for complaint updates
    socket.on('complaint_update', function(data) {
        // Update task in the table if it exists
        const taskRow = document.querySelector(`tr[data-task-id="${data._id}"]`);
        if (taskRow) {
            // Update status badge
            const statusCell = taskRow.querySelector('td:nth-child(4)');
            if (statusCell) {
                const statusClass = getStatusClass(data.status);
                statusCell.innerHTML = `<span class="badge bg-${statusClass}">${data.status}</span>`;
            }

            // Update status select
            const statusSelect = taskRow.querySelector('select[name="status"]');
            if (statusSelect) {
                statusSelect.value = data.status;
            }
        }

        // Update statistics
        updateStats();
    });

    function getStatusClass(status) {
        switch (status) {
            case 'pending':
                return 'warning';
            case 'in_progress':
                return 'info';
            case 'completed':
                return 'success';
            default:
                return 'secondary';
        }
    }

    function updateStats() {
        const table = document.querySelector('table tbody');
        if (!table) return;

        const rows = table.querySelectorAll('tr');
        let pending = 0;
        let inProgress = 0;
        let completed = 0;

        rows.forEach(row => {
            const statusBadge = row.querySelector('td:nth-child(4) .badge');
            if (statusBadge) {
                const status = statusBadge.textContent.trim();
                switch (status) {
                    case 'pending':
                        pending++;
                        break;
                    case 'in_progress':
                        inProgress++;
                        break;
                    case 'completed':
                        completed++;
                        break;
                }
            }
        });

        // Update the stats cards
        document.querySelector('.bg-warning h2').textContent = pending;
        document.querySelector('.bg-info h2').textContent = inProgress;
        document.querySelector('.bg-success h2').textContent = completed;
    }
});