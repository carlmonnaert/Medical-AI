// Analytics page JavaScript
let analyticsData = null;
let charts = {};
let currentSimId = null;

function initializeAnalytics(simId) {
    currentSimId = simId;
    loadAnalyticsData();
    setupEventListeners();
}

async function loadAnalyticsData() {
    try {
        const response = await fetch(`/api/simulation/${currentSimId}/analytics`);
        const result = await response.json();
        
        if (result.success) {
            analyticsData = result.data;
            createCharts();
            populateDoctorPerformance();
        } else {
            showError('Failed to load analytics data: ' + result.error);
        }
    } catch (error) {
        showError('Error loading analytics data: ' + error.message);
    }
}

function setupEventListeners() {
    // Chart controls
    document.getElementById('timeRangeSelect').addEventListener('change', function() {
        console.log('Time range changed to:', this.value);
        updateChartsWithFilters();
    });
    
    document.getElementById('granularitySelect').addEventListener('change', function() {
        console.log('Granularity changed to:', this.value);
        updateChartsWithFilters();
    });
    
    document.getElementById('chartTypeSelect').addEventListener('change', function() {
        console.log('Chart type changed to:', this.value);
        updateChartTypes(this.value);
    });
    
    // Show/hide data series
    document.getElementById('showTotal').addEventListener('change', updatePatientsChart);
    document.getElementById('showTreated').addEventListener('change', updatePatientsChart);
    document.getElementById('showWaiting').addEventListener('change', updatePatientsChart);
}

function updateChartsWithFilters() {
    if (!analyticsData) return;
    
    const timeRange = document.getElementById('timeRangeSelect').value;
    const granularity = document.getElementById('granularitySelect').value;
    
    console.log('Applying filters - Time range:', timeRange, 'Granularity:', granularity);
    
    // Filter hospital states data
    let filteredStates = getFilteredData(analyticsData.hospital_states, timeRange);
    filteredStates = aggregateData(filteredStates, granularity);
    
    // Update patients chart
    if (charts.patients) {
        charts.patients.data.labels = filteredStates.map(state => formatTimeLabel(state.sim_minutes));
        charts.patients.data.datasets[0].data = filteredStates.map(state => state.patients_total);
        charts.patients.data.datasets[1].data = filteredStates.map(state => state.patients_treated);
        charts.patients.data.datasets[2].data = filteredStates.map(state => state.waiting_patients);
        charts.patients.update();
    }
    
    // Update doctors chart
    if (charts.doctors) {
        charts.doctors.data.labels = filteredStates.map(state => formatTimeLabel(state.sim_minutes));
        charts.doctors.data.datasets[0].data = filteredStates.map(state => state.busy_doctors);
        charts.doctors.update();
    }
    
    console.log('Charts updated with', filteredStates.length, 'data points');
}

function updateChartTypes(newType) {
    console.log('Updating chart types to:', newType);
    
    // Only update line/bar/area compatible charts (not pie/doughnut charts)
    const compatibleCharts = ['patients', 'doctors', 'hourly', 'daily'];
    
    compatibleCharts.forEach(chartKey => {
        if (charts[chartKey] && charts[chartKey].config.type !== 'doughnut') {
            charts[chartKey].config.type = newType;
            charts[chartKey].update();
        }
    });
}

function getFilteredData(data, timeRange) {
    if (!data || timeRange === 'all') {
        return data;
    }
    
    console.log('Filtering data with time range:', timeRange);
    
    // Get the maximum sim_minutes in the data
    const maxMinutes = Math.max(...data.map(item => item.sim_minutes || 0));
    let cutoffMinutes;
    
    switch (timeRange) {
        case '24h':
            cutoffMinutes = maxMinutes - (24 * 60); // Last 24 hours
            break;
        case '7d':
            cutoffMinutes = maxMinutes - (7 * 24 * 60); // Last 7 days
            break;
        case '30d':
            cutoffMinutes = maxMinutes - (30 * 24 * 60); // Last 30 days
            break;
        default:
            return data;
    }
    
    const filtered = data.filter(item => (item.sim_minutes || 0) >= Math.max(0, cutoffMinutes));
    console.log('Filtered from', data.length, 'to', filtered.length, 'data points');
    return filtered;
}

function aggregateData(data, granularity) {
    if (!data || granularity === 'minute') {
        return data;
    }
    
    console.log('Aggregating data by:', granularity);
    
    const aggregated = {};
    let stepSize;
    
    switch (granularity) {
        case 'hour':
            stepSize = 60; // 60 minutes
            break;
        case 'day':
            stepSize = 1440; // 24 hours * 60 minutes
            break;
        default:
            return data;
    }
    
    data.forEach(item => {
        const timeSlot = Math.floor((item.sim_minutes || 0) / stepSize) * stepSize;
        
        if (!aggregated[timeSlot]) {
            aggregated[timeSlot] = {
                sim_minutes: timeSlot,
                patients_total: [],
                patients_treated: [],
                busy_doctors: [],
                waiting_patients: []
            };
        }
        
        aggregated[timeSlot].patients_total.push(item.patients_total || 0);
        aggregated[timeSlot].patients_treated.push(item.patients_treated || 0);
        aggregated[timeSlot].busy_doctors.push(item.busy_doctors || 0);
        aggregated[timeSlot].waiting_patients.push(item.waiting_patients || 0);
    });
    
    // Convert to array and calculate averages
    const result = Object.values(aggregated).map(item => ({
        sim_minutes: item.sim_minutes,
        patients_total: Math.round(item.patients_total.reduce((a, b) => a + b, 0) / item.patients_total.length),
        patients_treated: Math.round(item.patients_treated.reduce((a, b) => a + b, 0) / item.patients_treated.length),
        busy_doctors: Math.round(item.busy_doctors.reduce((a, b) => a + b, 0) / item.busy_doctors.length),
        waiting_patients: Math.round(item.waiting_patients.reduce((a, b) => a + b, 0) / item.waiting_patients.length)
    })).sort((a, b) => a.sim_minutes - b.sim_minutes);
    
    console.log('Aggregated to', result.length, 'data points');
    return result;
}

function createCharts() {
    createPatientsChart();
    createDoctorsChart();
    createHourlyChart();
    createDiseaseChart();
    createDailyChart();
}

function createPatientsChart() {
    const ctx = document.getElementById('patientsChart').getContext('2d');
    
    const data = {
        labels: analyticsData.hospital_states.map(state => formatTimeLabel(state.sim_minutes)),
        datasets: [
            {
                label: 'Total Patients',
                data: analyticsData.hospital_states.map(state => state.patients_total),
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.1
            },
            {
                label: 'Patients Treated',
                data: analyticsData.hospital_states.map(state => state.patients_treated),
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                tension: 0.1
            },
            {
                label: 'Waiting Patients',
                data: analyticsData.hospital_states.map(state => state.waiting_patients),
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                tension: 0.1
            }
        ]
    };
    
    charts.patients = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Patients'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Simulation Time'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Patient Flow Over Time'
                }
            }
        }
    });
}

function createDoctorsChart() {
    const ctx = document.getElementById('doctorsChart').getContext('2d');
    
    const data = {
        labels: analyticsData.hospital_states.map(state => formatTimeLabel(state.sim_minutes)),
        datasets: [{
            label: 'Busy Doctors',
            data: analyticsData.hospital_states.map(state => state.busy_doctors),
            borderColor: 'rgb(255, 159, 64)',
            backgroundColor: 'rgba(255, 159, 64, 0.2)',
            tension: 0.1,
            fill: true
        }]
    };
    
    charts.doctors = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Doctors'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Simulation Time'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Doctor Utilization Over Time'
                }
            }
        }
    });
}

function createHourlyChart() {
    const ctx = document.getElementById('hourlyChart').getContext('2d');
    
    const data = {
        labels: analyticsData.hourly_treatments.map(item => `${item.hour}:00`),
        datasets: [
            {
                label: 'Patients Treated',
                data: analyticsData.hourly_treatments.map(item => item.count),
                backgroundColor: 'rgba(54, 162, 235, 0.8)',
                yAxisID: 'y'
            },
            {
                label: 'Avg Wait Time (min)',
                data: analyticsData.hourly_treatments.map(item => item.avg_wait_time),
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                type: 'line',
                yAxisID: 'y1'
            }
        ]
    };
    
    charts.hourly = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Number of Patients'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Wait Time (minutes)'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Hourly Treatment Patterns'
                }
            }
        }
    });
}

function createDiseaseChart() {
    const ctx = document.getElementById('diseaseChart').getContext('2d');
    
    const colors = [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 205, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)',
        'rgba(199, 199, 199, 0.8)',
        'rgba(83, 102, 255, 0.8)'
    ];
    
    const data = {
        labels: analyticsData.disease_distribution.map(item => item.disease),
        datasets: [{
            data: analyticsData.disease_distribution.map(item => item.count),
            backgroundColor: colors.slice(0, analyticsData.disease_distribution.length),
            borderWidth: 2,
            borderColor: '#fff'
        }]
    };
    
    charts.disease = new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                },
                title: {
                    display: true,
                    text: 'Disease Distribution'
                }
            }
        }
    });
}

function createDailyChart() {
    const ctx = document.getElementById('dailyChart').getContext('2d');
    
    const data = {
        labels: analyticsData.daily_patterns.map(item => item.date),
        datasets: [
            {
                label: 'Patients per Day',
                data: analyticsData.daily_patterns.map(item => item.patients),
                backgroundColor: 'rgba(75, 192, 192, 0.8)',
                yAxisID: 'y'
            },
            {
                label: 'Avg Wait Time (min)',
                data: analyticsData.daily_patterns.map(item => item.avg_wait_time),
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                type: 'line',
                yAxisID: 'y1'
            }
        ]
    };
    
    charts.daily = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Number of Patients'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Wait Time (minutes)'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Daily Performance Metrics'
                }
            }
        }
    });
}

function populateDoctorPerformance() {
    const tbody = document.getElementById('doctorPerformanceBody');
    tbody.innerHTML = '';
    
    analyticsData.doctor_performance.forEach(doctor => {
        const efficiency = calculateEfficiencyScore(doctor);
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>Doctor ${doctor.doctor_id}</td>
            <td>${doctor.doctor_specialty}</td>
            <td>${doctor.patients_treated}</td>
            <td>${doctor.avg_treatment_time.toFixed(1)} min</td>
            <td>${doctor.avg_wait_time.toFixed(1)} min</td>
            <td>
                <div class="d-flex align-items-center">
                    <div class="progress flex-grow-1 me-2" style="height: 20px;">
                        <div class="progress-bar ${getEfficiencyColor(efficiency)}" 
                             style="width: ${efficiency}%">${efficiency.toFixed(0)}%</div>
                    </div>
                </div>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

function calculateEfficiencyScore(doctor) {
    // Simple efficiency calculation - could be improved
    const avgTreatmentTime = doctor.avg_treatment_time;
    const avgWaitTime = doctor.avg_wait_time;
    const patientsHandled = doctor.patients_treated;
    
    // Lower treatment time and wait time = higher efficiency
    const timeScore = Math.max(0, 100 - (avgTreatmentTime + avgWaitTime) / 2);
    
    // More patients handled = higher efficiency (up to a point)
    const volumeScore = Math.min(100, patientsHandled * 2);
    
    return (timeScore + volumeScore) / 2;
}

function getEfficiencyColor(efficiency) {
    if (efficiency >= 80) return 'bg-success';
    if (efficiency >= 60) return 'bg-warning';
    return 'bg-danger';
}

function updateCharts() {
    // This function is now replaced by updateChartsWithFilters
    updateChartsWithFilters();
}

function updatePatientsChart() {
    const showTotal = document.getElementById('showTotal').checked;
    const showTreated = document.getElementById('showTreated').checked;
    const showWaiting = document.getElementById('showWaiting').checked;
    
    charts.patients.data.datasets[0].hidden = !showTotal;
    charts.patients.data.datasets[1].hidden = !showTreated;
    charts.patients.data.datasets[2].hidden = !showWaiting;
    
    charts.patients.update();
}

function formatTimeLabel(minutes) {
    const days = Math.floor(minutes / 1440);
    const hours = Math.floor((minutes % 1440) / 60);
    
    if (days > 0) {
        return `Day ${days}, ${hours}:00`;
    } else {
        return `${hours}:00`;
    }
}

function showError(message) {
    console.error(message);
    alert(message);
}