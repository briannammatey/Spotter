// Main JavaScript for common functionality

// API Base URL
const API_BASE_URL = 'http://localhost:5001/api';

// Menu and Search button handlers
document.addEventListener('DOMContentLoaded', function() {
    const menuBtn = document.getElementById('menuBtn');
    const searchBtn = document.getElementById('searchBtn');

    if (menuBtn) {
        menuBtn.addEventListener('click', function() {
            alert('Menu functionality coming soon!');
        });
    }

    if (searchBtn) {
        searchBtn.addEventListener('click', function() {
            alert('Search functionality coming soon!');
        });
    }
});

// Utility function for API calls
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        const url = `${API_BASE_URL}${endpoint}`;
        console.log('Making API call to:', url, 'Method:', method);
        
        const response = await fetch(url, options);
        
        if (!response.ok) {
            let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorMessage;
            } catch (e) {
                // If response is not JSON, use status text
            }
            throw new Error(errorMessage);
        }

        const result = await response.json();
        return result;
    } catch (error) {
        console.error('API Error:', error);
        // If it's a network error, provide a more helpful message
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            throw new Error('Cannot connect to server. Please make sure the backend server is running on http://localhost:5000');
        }
        throw error;
    }
}

// Show error message
function showError(elementId, message) {
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        setTimeout(() => {
            errorElement.style.display = 'none';
        }, 5000);
    }
}

// Show success message
function showMessage(elementId, message, isSuccess = true) {
    const messageElement = document.getElementById(elementId);
    if (messageElement) {
        messageElement.textContent = message;
        messageElement.className = isSuccess ? 'message success' : 'message';
        messageElement.style.display = 'block';
        setTimeout(() => {
            messageElement.style.display = 'none';
        }, 5000);
    }
}

