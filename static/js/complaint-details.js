function showComplaintDescription(description, area, priority, date) {
    // Set the content in the modal
    const descEl = document.getElementById('complaintFullDescription');
    const areaEl = document.getElementById('complaintArea');
    const priorityEl = document.getElementById('complaintPriority');
    const dateEl = document.getElementById('complaintDate');

    if (descEl) descEl.textContent = description || '';
    if (areaEl) areaEl.textContent = area || '';
    if (priorityEl) priorityEl.textContent = priority || '';
    if (dateEl) dateEl.textContent = date || '';

    // Show the modal (in case caller wants to programmatically open it)
    if (typeof bootstrap !== 'undefined' && document.getElementById('complaintDescriptionModal')) {
        const modal = new bootstrap.Modal(document.getElementById('complaintDescriptionModal'));
        modal.show();
    }
}

// Attach click handlers to elements that carry complaint data via data-* attributes.
// This supports the worker dashboard which uses data-description / data-area etc.
document.addEventListener('DOMContentLoaded', function () {
    const descriptions = document.querySelectorAll('.complaint-description');
    if (!descriptions || descriptions.length === 0) return;

    descriptions.forEach(function (el) {
        el.addEventListener('click', function (e) {
            // Read values from data attributes. Use empty string as fallback.
            const description = el.getAttribute('data-description') || '';
            const area = el.getAttribute('data-area') || '';
            const priority = el.getAttribute('data-priority') || '';
            const date = el.getAttribute('data-date') || '';

            // Populate modal fields (without re-opening if Bootstrap handles it via data-bs-toggle)
            const descEl = document.getElementById('complaintFullDescription');
            const areaEl = document.getElementById('complaintArea');
            const priorityEl = document.getElementById('complaintPriority');
            const dateEl = document.getElementById('complaintDate');

            if (descEl) descEl.textContent = description;
            if (areaEl) areaEl.textContent = area;
            if (priorityEl) priorityEl.textContent = priority;
            if (dateEl) dateEl.textContent = date;

            // If Bootstrap modal is not triggered automatically (no data-bs-toggle), open it.
            // But in our template we use data-bs-toggle, so this is optional.
            if (!el.hasAttribute('data-bs-toggle') && typeof bootstrap !== 'undefined') {
                const modal = new bootstrap.Modal(document.getElementById('complaintDescriptionModal'));
                modal.show();
            }
        });
    });
});