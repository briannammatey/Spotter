// Profile Page JavaScript

const USER_ID = 'default_user'; // In production, get from session

document.addEventListener('DOMContentLoaded', function() {
    // First check if backend is running
    checkBackendConnection().then(() => {
        loadWorkouts();
        loadChallenges();
    }).catch(() => {
        // Backend not running, show helpful message
        const workoutsContainer = document.getElementById('workoutsContainer');
        const challengesContainer = document.getElementById('challengesContainer');
        workoutsContainer.innerHTML = '<p class="empty-message">Cannot connect to server. Please start the backend server by running: <code>cd backend && python3 app.py</code> (should run on port 5001)</p>';
        challengesContainer.innerHTML = '<p class="empty-message">Cannot connect to server. Please start the backend server on port 5001.</p>';
    });
});

async function checkBackendConnection() {
    try {
        const response = await fetch('http://localhost:5001/api/debug');
        if (!response.ok) {
            throw new Error('Backend server returned an error');
        }
        const data = await response.json();
        console.log('Backend connection successful:', data);
        return true;
    } catch (error) {
        console.error('Backend connection failed:', error);
        throw error;
    }
}

async function loadWorkouts() {
    try {
        console.log('Loading workouts for user:', USER_ID);
        const result = await apiCall(`/workouts?user_id=${USER_ID}`, 'GET');
        console.log('Workouts API response:', result);
        
        const workoutsContainer = document.getElementById('workoutsContainer');
        
        if (!result.workouts || result.workouts.length === 0) {
            console.log('No workouts found for user:', USER_ID);
            workoutsContainer.innerHTML = '<p class="empty-message">No workouts saved yet. Log a workout to see it here!</p>';
            return;
        }

        console.log(`Found ${result.workouts.length} workout(s)`);
        workoutsContainer.innerHTML = '';
        result.workouts.forEach(workout => {
            console.log('Creating card for workout:', workout);
            const workoutCard = createWorkoutCard(workout);
            workoutsContainer.appendChild(workoutCard);
        });
    } catch (error) {
        console.error('Error loading workouts:', error);
        const workoutsContainer = document.getElementById('workoutsContainer');
        const errorMsg = error.message || 'Unknown error';
        workoutsContainer.innerHTML = `<p class="empty-message">Error loading workouts: ${errorMsg}. Please check if the backend server is running.</p>`;
    }
}

async function loadChallenges() {
    try {
        const result = await apiCall(`/challenges?user_id=${USER_ID}`, 'GET');
        const challengesContainer = document.getElementById('challengesContainer');
        
        if (!result.challenges || result.challenges.length === 0) {
            challengesContainer.innerHTML = '<p class="empty-message">No challenges created yet. Create a challenge to see it here!</p>';
            return;
        }

        challengesContainer.innerHTML = '';
        result.challenges.forEach(challenge => {
            const challengeCard = createChallengeCard(challenge);
            challengesContainer.appendChild(challengeCard);
        });
    } catch (error) {
        console.error('Error loading challenges:', error);
        const challengesContainer = document.getElementById('challengesContainer');
        const errorMsg = error.message || 'Unknown error';
        challengesContainer.innerHTML = `<p class="empty-message">Error loading challenges: ${errorMsg}. Please check if the backend server is running.</p>`;
    }
}

function createWorkoutCard(workout) {
    const card = document.createElement('div');
    card.className = 'workout-card';

    // Format date
    const date = formatDate(workout.timestamp);

    // Build card content
    let cardHTML = `
        <div class="workout-card-header">
            <div class="workout-card-title">WORKOUT</div>
            <div class="workout-card-date">${date}</div>
        </div>
        <div class="workout-card-content">
    `;

    // Description field
    if (workout.description) {
        cardHTML += `
            <div class="workout-field">
                <span class="workout-field-label">DESCRIPTION</span>
                <div class="workout-field-value">${escapeHtml(workout.description)}</div>
            </div>
        `;
    }

    // Photo field
    if (workout.photo_url) {
        // Check if it's a data URL or just a filename
        const isDataURL = workout.photo_url.startsWith('data:');
        cardHTML += `
            <div class="workout-field">
                <span class="workout-field-label">PICTURE</span>
                <div class="workout-photo">
                    ${isDataURL 
                        ? `<img src="${escapeHtml(workout.photo_url)}" alt="Workout photo">`
                        : `<div class="workout-photo-placeholder">Photo: ${escapeHtml(workout.photo_url)}</div>`
                    }
                </div>
            </div>
        `;
    }

    // Personal Record field
    if (workout.personal_record) {
        cardHTML += `
            <div class="workout-field">
                <span class="workout-field-label">PERSONAL RECORD</span>
                <div class="workout-field-value">${escapeHtml(workout.personal_record)}</div>
            </div>
        `;
    }

    cardHTML += `
        </div>
    `;

    card.innerHTML = cardHTML;
    return card;
}

function createChallengeCard(challenge) {
    const card = document.createElement('div');
    card.className = 'challenge-card';

    // Format date
    const date = formatDate(challenge.timestamp);

    // Build card content
    let cardHTML = `
        <div class="challenge-card-header">
            <div class="challenge-card-title">CHALLENGE</div>
            <div class="challenge-card-date">${date}</div>
        </div>
        <div class="challenge-card-content">
    `;

    // Dates field
    cardHTML += `
        <div class="challenge-field">
            <span class="challenge-field-label">DATES</span>
            <div class="challenge-dates">
                <div class="challenge-date-item">
                    <div class="challenge-field-value"><strong>START:</strong> ${escapeHtml(challenge.start_date)}</div>
                </div>
                <div class="challenge-date-item">
                    <div class="challenge-field-value"><strong>END:</strong> ${escapeHtml(challenge.end_date)}</div>
                </div>
            </div>
        </div>
    `;

    // Goals field
    if (challenge.goals && challenge.goals.length > 0) {
        cardHTML += `
            <div class="challenge-field">
                <span class="challenge-field-label">CHALLENGE GOALS</span>
                <ul class="challenge-goals-list">
                    ${challenge.goals.map(goal => `<li>${escapeHtml(goal)}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    // Description field
    if (challenge.description) {
        cardHTML += `
            <div class="challenge-field">
                <span class="challenge-field-label">DESCRIPTION</span>
                <div class="challenge-field-value">${escapeHtml(challenge.description)}</div>
            </div>
        `;
    }

    cardHTML += `
        </div>
    `;

    card.innerHTML = cardHTML;
    return card;
}

function formatDate(isoString) {
    if (!isoString) return '';
    try {
        const date = new Date(isoString);
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const year = date.getFullYear();
        return `${month}/${day}/${year}`;
    } catch (e) {
        return '';
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

