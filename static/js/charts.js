// Chart.js configurations for analytics
let complaintsChart = null;
let workerChart = null;

const chartColors = {
    green: 'rgba(40, 167, 69, 0.7)',
    blue: 'rgba(0, 123, 255, 0.7)',
    yellow: 'rgba(255, 193, 7, 0.7)',
    red: 'rgba(220, 53, 69, 0.7)',
    purple: 'rgba(111, 66, 193, 0.7)',
    teal: 'rgba(23, 162, 184, 0.7)'
};

const sampleComplaints = {
    labels: ["Zone A", "Zone B", "Zone C"],
    data: [5, 7, 3]
};

const sampleWorkers = {
    labels: ["John", "Amit", "Sara"],
    data: [12, 8, 10]
};

function destroyExistingChart(chart) {
    if (chart) {
        chart.destroy();
    }
}

async function fetchAnalytics(endpoint) {
    try {
        const response = await fetch(endpoint);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Error fetching data from ${endpoint}:`, error);
        return null;
    }
}

function createComplaintsChart(data) {
    const ctx = document.getElementById('complaintsByAreaChart');
    if (!ctx) {
        console.error('Complaints chart canvas not found');
        return;
    }

    destroyExistingChart(complaintsChart);

    const chartData = data || sampleComplaints;
    const labels = data ? data.map(item => item._id || 'Unknown') : chartData.labels;
    const values = data ? data.map(item => item.count) : chartData.data;

    complaintsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Complaints',
                data: values,
                backgroundColor: chartColors.green,
                borderColor: chartColors.green.replace('0.7', '1'),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Complaints by Area',
                    font: {
                        size: 16
                    }
                },
                legend: {
                    display: true,
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function createWorkerChart(data) {
    const ctx = document.getElementById('workerPerformanceChart');
    if (!ctx) {
        console.error('Worker performance chart canvas not found');
        return;
    }

    destroyExistingChart(workerChart);

    const labels = data ? data.map(item => item.worker_name) : sampleWorkers.labels;
    const values = data ? data.map(item => item.completed) : sampleWorkers.data;

    const colors = Object.values(chartColors);
    const backgroundColors = colors.slice(0, values.length);
    const borderColors = backgroundColors.map(color => color.replace('0.7', '1'));

    workerChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Completed Tasks by Worker',
                    font: {
                        size: 16
                    }
                },
                legend: {
                    display: true,
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed;
                            const label = context.label || '';
                            return `${label}: ${value} completed tasks`;
                        }
                    }
                }
            }
        }
    });
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Fetch complaints data
        const complaintsData = await fetchAnalytics('/admin/dashboard/api/analytics/complaints-by-area');
        createComplaintsChart(complaintsData);

        // Fetch worker performance data
        const workerData = await fetchAnalytics('/admin/dashboard/api/analytics/worker-performance');
        createWorkerChart(workerData);

        // Real-time updates via Socket.IO (enabled by server-side config)
        try {
            // Only attempt to connect if the Socket.IO client script was loaded by the template
            if (typeof io !== 'undefined') {
                const socket = io();
                socket.on('connect', () => {
                    console.log('Socket connected for realtime analytics');
                });
                socket.on('analytics_update', (payload) => {
                    if (!payload) return;
                    if (payload.complaints_by_area) {
                        createComplaintsChart(payload.complaints_by_area);
                    }
                    if (payload.worker_performance) {
                        createWorkerChart(payload.worker_performance);
                    }
                });
            } else {
                console.log('Socket.IO client not loaded; realtime disabled.');
            }
        } catch (e) {
            console.warn('Socket.IO realtime error', e);
        }
    } catch (error) {
        console.error('Error initializing charts:', error);
        // Use sample data as fallback
        createComplaintsChart(null);
        createWorkerChart(null);
    }
});

