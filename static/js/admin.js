// Admin dashboard worker assignment functions
function openAssignWorkerModal(complaintId) {
    document.getElementById('complaintId').value = complaintId;
    const modal = new bootstrap.Modal(document.getElementById('assignWorkerModal'));
    modal.show();
}

function updateStatus(complaintId) {
    document.getElementById('statusComplaintId').value = complaintId;
    const modal = new bootstrap.Modal(document.getElementById('updateStatusModal'));
    modal.show();
}

async function assignWorker() {
    const complaintId = document.getElementById('complaintId').value;
    const workerId = document.getElementById('workerId').value;
    
    if (!workerId) {
        alert('Please select a worker');
        return;
    }

    try {
        const response = await fetch(`/admin/complaints/${complaintId}/assign`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ worker_id: workerId })
        });

        if (!response.ok) {
            throw new Error('Failed to assign worker');
        }

        // Close modal and refresh page to show updates
        bootstrap.Modal.getInstance(document.getElementById('assignWorkerModal')).hide();
        window.location.reload();
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to assign worker: ' + error.message);
    }
}

async function submitStatusUpdate() {
    const complaintId = document.getElementById('statusComplaintId').value;
    const status = document.getElementById('status').value;

    try {
        const response = await fetch(`/admin/complaints/${complaintId}/status`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: status })
        });

        if (!response.ok) {
            throw new Error('Failed to update status');
        }

        // Close modal and refresh page to show updates
        bootstrap.Modal.getInstance(document.getElementById('updateStatusModal')).hide();
        window.location.reload();
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to update status: ' + error.message);
    }
}

// Function to show complaint description in modal
function showComplaintDescription(description, area, priority, date) {
    // Set the content in the modal
    document.getElementById('complaintFullDescription').textContent = description;
    document.getElementById('complaintArea').textContent = area;
    document.getElementById('complaintPriority').textContent = priority;
    document.getElementById('complaintDate').textContent = date;

    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('complaintDescriptionModal'));
    modal.show();
}