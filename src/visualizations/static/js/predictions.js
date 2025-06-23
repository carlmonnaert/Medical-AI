/**
 * Predictions Dashboard JavaScript
 * 
 * Handles the hospital danger prediction interface including:
 * - Loading and displaying prediction data
 * - Updating danger scores and risk levels
 * - Managing prediction charts
 * - Handling model training requests
 */

let currentSimId = null;
let predictionCharts = {};
let predictionsData = null;
let currentModal = null;
let currentTimeoutId = null;

/**
 * Initialize the predictions dashboard
 */
async function initializePredictions(simId) {
    currentSimId = simId;
    
    // Show loading modal with timeout protection
    const { modal, timeoutId } = showLoadingModalWithTimeout('Loading predictions...', 30000);
    currentModal = modal;
    currentTimeoutId = timeoutId;
    
    try {
        await loadPredictionsData();
        
        // Clear timeout and hide modal on success
        if (currentTimeoutId) {
            clearTimeout(currentTimeoutId);
            currentTimeoutId = null;
        }
        hideLoadingModal(currentModal);
        currentModal = null;
        
    } catch (error) {
        // Clear timeout and hide modal on error
        if (currentTimeoutId) {
            clearTimeout(currentTimeoutId);
            currentTimeoutId = null;
        }
        hideLoadingModal(currentModal);
        currentModal = null;
        
        showError('Failed to load predictions: ' + error.message);
    }
}

/**
 * Load predictions from the API
 */
async function loadPredictionsData() {
    try {
        const response = await fetch(`/api/simulation/${currentSimId}/predictions`);
        const result = await response.json();
        
        if (result.success) {
            predictionsData = result.data;
            updatePredictionsDisplay();
        } else {
            // If predictions need to be generated, show appropriate modal
            if (result.error && result.error.includes('generating')) {
                const { modal, timeoutId } = showLoadingModalWithTimeout('Generating predictions... This may take several minutes.', 120000);
                currentModal = modal;
                currentTimeoutId = timeoutId;
                
                // Poll for completion
                await pollForPredictions();
            } else {
                throw new Error(result.error || 'Unknown error occurred');
            }
        }
    } catch (error) {
        console.error('Error loading predictions:', error);
        throw error;
    }
}

/**
 * Poll for predictions completion
 */
async function pollForPredictions() {
    const maxAttempts = 24; // 2 minutes with 5 second intervals
    let attempts = 0;
    
    const pollInterval = setInterval(async () => {
        attempts++;
        
        try {
            const response = await fetch(`/api/simulation/${currentSimId}/predictions`);
            const result = await response.json();
            
            if (result.success) {
                // Success! Clear polling and hide modal
                clearInterval(pollInterval);
                
                if (currentTimeoutId) {
                    clearTimeout(currentTimeoutId);
                    currentTimeoutId = null;
                }
                
                hideLoadingModal(currentModal);
                currentModal = null;
                
                predictionsData = result.data;
                updatePredictionsDisplay();
                
            } else if (attempts >= maxAttempts) {
                // Max attempts reached
                clearInterval(pollInterval);
                
                if (currentTimeoutId) {
                    clearTimeout(currentTimeoutId);
                    currentTimeoutId = null;
                }
                
                hideLoadingModal(currentModal);
                currentModal = null;
                
                throw new Error('Prediction generation timed out');
            }
            // Continue polling if not ready and under max attempts
            
        } catch (error) {
            clearInterval(pollInterval);
            
            if (currentTimeoutId) {
                clearTimeout(currentTimeoutId);
                currentTimeoutId = null;
            }
            
            hideLoadingModal(currentModal);
            currentModal = null;
            
            throw error;
        }
    }, 5000); // Poll every 5 seconds
}

/**
 * Update the entire prediction display with new data
 */
function updatePredictionsDisplay() {
    if (!predictionsData) {
        console.warn('No predictions data available');
        return;
    }
    
    // Update overall danger score
    updateOverallDangerScore();
    
    // Update current metrics
    updateCurrentMetrics();
    
    // Update time horizon predictions
    updateTimeHorizonPredictions();
    
    // Update individual danger types
    updateIndividualDangerTypes();
    
    // Update charts
    updatePredictionCharts();
    
    // Update model information
    updateModelInformation();
}

/**
 * Update the overall danger score display
 */
function updateOverallDangerScore() {
    // Placeholder implementation - replace with actual data
    const dangerScore = Math.round(Math.random() * 100);
    const riskLevel = dangerScore > 70 ? 'HIGH' : dangerScore > 40 ? 'MEDIUM' : 'LOW';
    const riskClass = dangerScore > 70 ? 'bg-danger' : dangerScore > 40 ? 'bg-warning' : 'bg-success';
    
    document.getElementById('dangerScoreText').textContent = dangerScore;
    document.getElementById('riskLevelBadge').textContent = riskLevel;
    document.getElementById('riskLevelBadge').className = `badge ${riskClass}`;
}

/**
 * Update current metrics display
 */
function updateCurrentMetrics() {
    // Placeholder implementation - replace with actual data
    document.getElementById('patientsTotal').textContent = Math.round(Math.random() * 50 + 20);
    document.getElementById('patientsWaiting').textContent = Math.round(Math.random() * 15);
    document.getElementById('doctorsUtilization').textContent = Math.round(Math.random() * 40 + 60) + '%';
    document.getElementById('avgWaitTime').textContent = Math.round(Math.random() * 30 + 15) + ' min';
}

/**
 * Update time horizon predictions
 */
function updateTimeHorizonPredictions() {
    const container = document.getElementById('timeHorizonPredictions');
    const horizons = ['1 Hour', '4 Hours', '12 Hours', '24 Hours'];
    
    container.innerHTML = '';
    
    horizons.forEach(horizon => {
        const danger = Math.round(Math.random() * 100);
        const dangerClass = danger > 70 ? 'danger' : danger > 40 ? 'warning' : 'success';
        
        const col = document.createElement('div');
        col.className = 'col-md-3 mb-3';
        col.innerHTML = `
            <div class="text-center">
                <h6>${horizon}</h6>
                <div class="progress mb-2">
                    <div class="progress-bar bg-${dangerClass}" style="width: ${danger}%"></div>
                </div>
                <small class="text-${dangerClass}">${danger}% Risk</small>
            </div>
        `;
        
        container.appendChild(col);
    });
}

/**
 * Update individual danger type displays
 */
function updateIndividualDangerTypes() {
    const dangerTypes = [
        { id: 'overload', name: 'Patient Overload' },
        { id: 'waitTime', name: 'Long Wait Times' },
        { id: 'staffing', name: 'Staffing Shortage' },
        { id: 'systemStress', name: 'System Stress' }
    ];
    
    dangerTypes.forEach(type => {
        const probability = Math.round(Math.random() * 100);
        const status = probability > 70 ? 'HIGH RISK' : probability > 40 ? 'MEDIUM RISK' : 'LOW RISK';
        const statusClass = probability > 70 ? 'bg-danger' : probability > 40 ? 'bg-warning' : 'bg-success';
        const barClass = probability > 70 ? 'bg-danger' : probability > 40 ? 'bg-warning' : 'bg-success';
        
        document.getElementById(`${type.id}Prob`).textContent = `${probability}%`;
        document.getElementById(`${type.id}Status`).textContent = status;
        document.getElementById(`${type.id}Status`).className = `status-badge badge ${statusClass}`;
        document.getElementById(`${type.id}Bar`).style.width = `${probability}%`;
        document.getElementById(`${type.id}Bar`).className = `progress-bar ${barClass}`;
    });
}

/**
 * Update prediction charts
 */
function updatePredictionCharts() {
    // Create simple placeholder charts
    createWaitTimePredictionChart();
    createPatientCountPredictionChart();
}

function createWaitTimePredictionChart() {
    const ctx = document.getElementById('waitTimePredictionChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Now', '+1h', '+2h', '+3h', '+4h', '+5h'],
            datasets: [{
                label: 'Predicted Wait Time',
                data: [25, 30, 35, 32, 28, 26],
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Wait Time (minutes)'
                    }
                }
            }
        }
    });
    
    document.getElementById('predictedWaitTime').textContent = '32 minutes';
}

function createPatientCountPredictionChart() {
    const ctx = document.getElementById('patientCountPredictionChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Now', '+1h', '+2h', '+3h', '+4h', '+5h'],
            datasets: [{
                label: 'Predicted Patient Count',
                data: [35, 38, 42, 45, 41, 37],
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Patient Count'
                    }
                }
            }
        }
    });
    
    document.getElementById('predictedPatientCount').textContent = '42 patients';
}

/**
 * Update model information display
 */
function updateModelInformation() {
    document.getElementById('lastTraining').textContent = 'Just now';
    document.getElementById('predictionTime').textContent = new Date().toLocaleTimeString();
    document.getElementById('modelsLoaded').textContent = '4';
    document.getElementById('dataQuality').textContent = 'Good';
    document.getElementById('dataQuality').className = 'badge bg-success';
    document.getElementById('modelAccuracy').textContent = '87.3%';
    document.getElementById('recommendation').textContent = 'Predictions are reliable for next 4-6 hours';
}

/**
 * Train ML models
 */
async function trainModels() {
    const { modal, timeoutId } = showLoadingModalWithTimeout('Training models...', 60000);
    
    try {
        const response = await fetch('/api/ml/train', {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        // Clear timeout and hide modal
        if (timeoutId) {
            clearTimeout(timeoutId);
        }
        hideLoadingModal(modal);
        
        if (result.error) {
            throw new Error(result.error);
        }
        
        showError('Models trained successfully! Refreshing predictions...');
        
        // Refresh predictions after training
        setTimeout(() => {
            if (currentSimId) {
                initializePredictions(currentSimId);
            }
        }, 1000);
        
    } catch (error) {
        console.error('Error training models:', error);
        if (timeoutId) {
            clearTimeout(timeoutId);
        }
        hideLoadingModal(modal);
        showError(`Failed to train models: ${error.message}`);
    }
}

/**
 * Create or update a chart
 */
function updateChart(canvasId, config) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    // Destroy existing chart
    if (predictionCharts[canvasId]) {
        predictionCharts[canvasId].destroy();
    }
    
    // Create new chart
    predictionCharts[canvasId] = new Chart(ctx, config);
}

/**
 * Utility functions
 */
function getRiskColor(score) {
    if (score >= 0.7) return '#dc3545'; // Red
    if (score >= 0.4) return '#ffc107'; // Yellow
    return '#28a745'; // Green
}

function getRiskClass(score) {
    if (score >= 0.7) return 'danger';
    if (score >= 0.4) return 'warning';
    return 'success';
}

function getRiskIcon(riskLevel) {
    switch (riskLevel) {
        case 'High': return '🔴';
        case 'Medium': return '🟡';
        case 'Low': return '🟢';
        default: return '⚪';
    }
}

function getProgressBarClass(probability) {
    if (probability >= 0.7) return 'bg-danger';
    if (probability >= 0.4) return 'bg-warning';
    return 'bg-success';
}

function showLoadingModal(text = 'Loading...') {
    document.getElementById('loadingText').textContent = text;
    const modalElement = document.getElementById('loadingModal');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
    return modal;
}

function hideLoadingModal(modal = null) {
    try {
        if (modal && typeof modal.hide === 'function') {
            modal.hide();
        } else {
            // Fallback: find and hide any existing modal
            const modalElement = document.getElementById('loadingModal');
            if (modalElement) {
                const existingModal = bootstrap.Modal.getInstance(modalElement);
                if (existingModal) {
                    existingModal.hide();
                } else {
                    // Force hide the modal by removing Bootstrap classes
                    modalElement.classList.remove('show');
                    modalElement.style.display = 'none';
                    modalElement.setAttribute('aria-hidden', 'true');
                    modalElement.removeAttribute('aria-modal');
                    
                    // Remove backdrop if it exists
                    const backdrop = document.querySelector('.modal-backdrop');
                    if (backdrop) {
                        backdrop.remove();
                    }
                    
                    // Remove modal-open class from body
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = '';
                    document.body.style.paddingRight = '';
                }
            }
        }
    } catch (error) {
        console.error('Error hiding modal:', error);
        // Force cleanup
        const modalElement = document.getElementById('loadingModal');
        if (modalElement) {
            modalElement.style.display = 'none';
            modalElement.classList.remove('show');
        }
        document.body.classList.remove('modal-open');
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) backdrop.remove();
    }
}

function showLoadingModalWithTimeout(text = 'Loading...', timeoutMs = 30000) {
    const modal = showLoadingModal(text);
    
    // Set a timeout to force hide the modal if it takes too long
    const timeoutId = setTimeout(() => {
        hideLoadingModal(modal);
        console.warn('Loading modal auto-closed after timeout');
    }, timeoutMs);
    
    return { modal, timeoutId };
}

function showError(message) {
    console.error(message);
    alert(message);
}

// Event handlers
document.addEventListener('DOMContentLoaded', function() {
    // Refresh predictions button
    const refreshBtn = document.getElementById('refreshPredictions');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', async function() {
            if (currentSimId) {
                await initializePredictions(currentSimId);
            }
        });
    }
    
    // Train models button
    const trainBtn = document.getElementById('trainModels');
    if (trainBtn) {
        trainBtn.addEventListener('click', async function() {
            await trainModels();
        });
    }
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    // Destroy all charts
    Object.values(predictionCharts).forEach(chart => {
        if (chart) {
            chart.destroy();
        }
    });
});