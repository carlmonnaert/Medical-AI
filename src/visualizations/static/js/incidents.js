// Incidents page JavaScript
let incidentsData = null;
let currentSimId = null;

document.addEventListener('DOMContentLoaded', function() {
    // Extract sim_id from URL
    const pathParts = window.location.pathname.split('/');
    currentSimId = parseInt(pathParts[pathParts.length - 1]);
    
    if (currentSimId) {
        loadIncidentsData();
    }
});

async function loadIncidentsData() {
    try {
        const response = await fetch(`/api/simulation/${currentSimId}/incidents`);
        const result = await response.json();
        
        if (result.success) {
            incidentsData = result.data;
            displayIncidentsSummary();
            displayHighWaitIncidents();
            displayHighOccupancyIncidents();
            displayEventsTimeline();
            displayLongWaitPatients();
            createIncidentsCharts();
        } else {
            showError('Failed to load incidents data: ' + result.error);
        }
    } catch (error) {
        showError('Error loading incidents data: ' + error.message);
    }
}

function displayIncidentsSummary() {
    const stats = incidentsData.statistics;
    
    document.getElementById('highWaitCount').textContent = stats.total_high_wait_periods;
    document.getElementById('highOccupancyCount').textContent = stats.total_high_occupancy_periods;
    document.getElementById('maxWaitingPatients').textContent = stats.max_waiting_patients;
    document.getElementById('activeEventsCount').textContent = incidentsData.active_events.length;
}

function displayHighWaitIncidents() {
    const container = document.getElementById('highWaitIncidents');
    container.innerHTML = '';
    
    if (incidentsData.high_wait_incidents.length === 0) {
        container.innerHTML = '<p class="text-muted">No high wait time incidents found.</p>';
        return;
    }
    
    incidentsData.high_wait_incidents.slice(0, 20).forEach(incident => {
        const incidentEl = document.createElement('div');
        incidentEl.className = 'incident-item medium-severity';
        
        const severity = getSeverity(incident.waiting_patients, 'waiting');
        incidentEl.className = `incident-item ${severity}-severity`;
        
        incidentEl.innerHTML = `
            <div class="incident-header">
                <div class="incident-time">${formatSimulationTime(incident.sim_minutes)}</div>
                <span class="incident-badge ${severity}">${severity.toUpperCase()}</span>
            </div>
            <h6><i class="fas fa-clock text-warning"></i> High Patient Wait Time</h6>
            <p><strong>${incident.waiting_patients}</strong> patients waiting for treatment</p>
            <small class="text-muted">
                Busy doctors: ${incident.busy_doctors} | 
                Total processed: ${incident.patients_total}
            </small>
        `;
        
        container.appendChild(incidentEl);
    });
}

function displayHighOccupancyIncidents() {
    const container = document.getElementById('highOccupancyIncidents');
    container.innerHTML = '';
    
    if (incidentsData.high_occupancy_incidents.length === 0) {
        container.innerHTML = '<p class="text-muted">No high occupancy incidents found.</p>';
        return;
    }
    
    incidentsData.high_occupancy_incidents.slice(0, 20).forEach(incident => {
        const incidentEl = document.createElement('div');
        const occupancyRate = (incident.occupancy_rate * 100).toFixed(1);
        const severity = getSeverity(incident.occupancy_rate, 'occupancy');
        
        incidentEl.className = `incident-item ${severity}-severity`;
        
        incidentEl.innerHTML = `
            <div class="incident-header">
                <div class="incident-time">${formatSimulationTime(incident.sim_minutes)}</div>
                <span class="incident-badge ${severity}">${severity.toUpperCase()}</span>
            </div>
            <h6><i class="fas fa-users text-danger"></i> High Doctor Occupancy</h6>
            <p><strong>${occupancyRate}%</strong> of doctors are busy (${incident.busy_doctors}/${incidentsData.statistics.total_doctors})</p>
            <small class="text-muted">
                Waiting patients: ${incident.waiting_patients} | 
                Total processed: ${incident.patients_total}
            </small>
        `;
        
        container.appendChild(incidentEl);
    });
}

function displayEventsTimeline() {
    const container = document.getElementById('eventsTimeline');
    container.innerHTML = '';
    
    if (incidentsData.active_events.length === 0) {
        container.innerHTML = '<p class="text-muted">No simulation events found.</p>';
        return;
    }
    
    incidentsData.active_events.forEach(event => {
        const eventEl = document.createElement('div');
        eventEl.className = 'incident-item low-severity';
        
        const duration = (event.end_sim_minutes - event.start_sim_minutes) / 60; // Convert to hours
        const params = JSON.parse(event.params || '{}');
        
        eventEl.innerHTML = `
            <div class="incident-header">
                <div class="incident-time">
                    ${formatSimulationTime(event.start_sim_minutes)} - 
                    ${formatSimulationTime(event.end_sim_minutes)}
                </div>
                <span class="incident-badge low">${event.event_type.toUpperCase()}</span>
            </div>
            <h6><i class="fas fa-bolt text-info"></i> ${capitalizeFirst(event.event_type)} Event</h6>
            <p>Duration: <strong>${duration.toFixed(1)} hours</strong></p>
            <small class="text-muted">${formatEventParams(params)}</small>
        `;
        
        container.appendChild(eventEl);
    });
}

function displayLongWaitPatients() {
    const tbody = document.getElementById('longWaitPatientsBody');
    tbody.innerHTML = '';
    
    incidentsData.long_wait_patients.forEach(patient => {
        const row = document.createElement('tr');
        const severity = getWaitTimeSeverity(patient.wait_time);
        
        row.innerHTML = `
            <td>Patient ${patient.patient_id}</td>
            <td>${patient.disease}</td>
            <td>
                <span class="badge ${severity === 'high' ? 'bg-danger' : severity === 'medium' ? 'bg-warning' : 'bg-primary'}">
                    ${patient.wait_time.toFixed(1)} min
                </span>
            </td>
            <td>${patient.start_treatment}</td>
            <td>${patient.doctor_specialty}</td>
            <td>
                <span class="badge ${severity === 'high' ? 'bg-danger' : severity === 'medium' ? 'bg-warning text-dark' : 'bg-success'}">
                    ${severity.toUpperCase()}
                </span>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

function createIncidentsCharts() {
    createIncidentsByHourChart();
    createIncidentTypesChart();
}

function createIncidentsByHourChart() {
    const ctx = document.getElementById('incidentsByHourChart').getContext('2d');
    
    // Process incidents by hour
    const hourlyIncidents = {};
    for (let i = 0; i < 24; i++) {
        hourlyIncidents[i] = { wait: 0, occupancy: 0 };
    }
    
    incidentsData.high_wait_incidents.forEach(incident => {
        const hour = Math.floor((incident.sim_minutes % 1440) / 60);
        hourlyIncidents[hour].wait++;
    });
    
    incidentsData.high_occupancy_incidents.forEach(incident => {
        const hour = Math.floor((incident.sim_minutes % 1440) / 60);
        hourlyIncidents[hour].occupancy++;
    });
    
    const labels = Array.from({length: 24}, (_, i) => `${i}:00`);
    const waitData = labels.map((_, i) => hourlyIncidents[i].wait);
    const occupancyData = labels.map((_, i) => hourlyIncidents[i].occupancy);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'High Wait Incidents',
                    data: waitData,
                    backgroundColor: 'rgba(255, 193, 7, 0.8)',
                    borderColor: 'rgba(255, 193, 7, 1)',
                    borderWidth: 1
                },
                {
                    label: 'High Occupancy Incidents',
                    data: occupancyData,
                    backgroundColor: 'rgba(220, 53, 69, 0.8)',
                    borderColor: 'rgba(220, 53, 69, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Incidents'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Hour of Day'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Incidents by Hour of Day'
                }
            }
        }
    });
}

function createIncidentTypesChart() {
    const ctx = document.getElementById('incidentTypesChart').getContext('2d');
    
    const incidentCounts = {
        'High Wait Time': incidentsData.high_wait_incidents.length,
        'High Occupancy': incidentsData.high_occupancy_incidents.length,
        'Long Patient Waits': incidentsData.long_wait_patients.length
    };
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(incidentCounts),
            datasets: [{
                data: Object.values(incidentCounts),
                backgroundColor: [
                    'rgba(255, 193, 7, 0.8)',
                    'rgba(220, 53, 69, 0.8)',
                    'rgba(255, 99, 132, 0.8)'
                ],
                borderColor: [
                    'rgba(255, 193, 7, 1)',
                    'rgba(220, 53, 69, 1)',
                    'rgba(255, 99, 132, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Incident Types Distribution'
                },
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Utility functions
function getSeverity(value, type) {
    if (type === 'waiting') {
        if (value > 20) return 'high';
        if (value > 10) return 'medium';
        return 'low';
    } else if (type === 'occupancy') {
        if (value > 0.95) return 'high';
        if (value > 0.85) return 'medium';
        return 'low';
    }
    return 'low';
}

function getWaitTimeSeverity(waitTime) {
    if (waitTime > 120) return 'high';
    if (waitTime > 60) return 'medium';
    return 'low';
}

function formatSimulationTime(minutes) {
    const days = Math.floor(minutes / 1440);
    const hours = Math.floor((minutes % 1440) / 60);
    const mins = Math.floor(minutes % 60);
    
    if (days > 0) {
        return `Day ${days + 1}, ${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
    } else {
        return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
    }
}

function formatEventParams(params) {
    const formatted = [];
    for (const [key, value] of Object.entries(params)) {
        if (typeof value === 'number') {
            formatted.push(`${key}: ${value.toFixed(2)}`);
        } else {
            formatted.push(`${key}: ${value}`);
        }
    }
    return formatted.join(', ') || 'No parameters';
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function showError(message) {
    console.error(message);
    alert(message);
}