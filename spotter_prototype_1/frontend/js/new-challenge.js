// New Challenge Page JavaScript

let selectedPrivacy = null;
let attachRoutine = null;
let goals = [];
let friends = [];

document.addEventListener('DOMContentLoaded', function() {
    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');
    const attachButtons = document.querySelectorAll('.yes-no-btn');
    const privacyButtons = document.querySelectorAll('.privacy-btn');
    const addGoalBtn = document.querySelector('.section-title .plus-icon');
    const addFriendBtn = document.querySelectorAll('.section-title .plus-icon')[1];
    const goalInput = document.getElementById('goalInput');
    const friendInput = document.getElementById('friendInput');
    const saveChallengeBtn = document.getElementById('saveChallengeBtn');

    // Date formatting
    if (startDate) {
        startDate.addEventListener('input', function(e) {
            formatDateInput(e.target);
        });
    }

    if (endDate) {
        endDate.addEventListener('input', function(e) {
            formatDateInput(e.target);
        });
    }

    // Attach routine buttons
    attachButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            attachButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            attachRoutine = this.dataset.attach === 'yes';
        });
    });

    // Privacy selection
    privacyButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            privacyButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            selectedPrivacy = this.dataset.privacy;
        });
    });

    // Add goal
    if (addGoalBtn) {
        addGoalBtn.addEventListener('click', function() {
            const input = document.getElementById('goalInput');
            if (input.style.display === 'none') {
                input.style.display = 'block';
                input.focus();
            } else {
                input.style.display = 'none';
            }
        });
    }

    if (goalInput) {
        goalInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && this.value.trim()) {
                addGoal(this.value.trim());
                this.value = '';
                this.style.display = 'none';
            }
        });
    }

    // Add friend
    if (addFriendBtn) {
        addFriendBtn.addEventListener('click', function() {
            const input = document.getElementById('friendInput');
            if (input.style.display === 'none') {
                input.style.display = 'block';
                input.focus();
            } else {
                input.style.display = 'none';
            }
        });
    }

    if (friendInput) {
        friendInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && this.value.trim()) {
                addFriend(this.value.trim());
                this.value = '';
                this.style.display = 'none';
            }
        });
    }

    // Save challenge button
    if (saveChallengeBtn) {
        saveChallengeBtn.addEventListener('click', async function() {
            await saveChallenge();
        });
    }
});

function formatDateInput(input) {
    let value = input.value.replace(/\D/g, '');
    
    if (value.length >= 2) {
        value = value.substring(0, 2) + '/' + value.substring(2);
    }
    if (value.length >= 5) {
        value = value.substring(0, 5) + '/' + value.substring(5, 9);
    }
    
    input.value = value;
}

function addGoal(goal) {
    if (goals.includes(goal)) {
        return;
    }
    
    goals.push(goal);
    updateGoalsList();
}

function removeGoal(goal) {
    goals = goals.filter(g => g !== goal);
    updateGoalsList();
}

function updateGoalsList() {
    const goalsList = document.getElementById('goalsList');
    goalsList.innerHTML = '';
    
    goals.forEach(goal => {
        const goalItem = document.createElement('div');
        goalItem.className = 'goal-item';
        goalItem.innerHTML = `
            <span>${goal}</span>
            <button class="remove-btn" onclick="removeGoal('${goal}')">×</button>
        `;
        goalsList.appendChild(goalItem);
    });
}

function addFriend(friend) {
    if (friends.includes(friend)) {
        return;
    }
    
    friends.push(friend);
    updateFriendsList();
}

function removeFriend(friend) {
    friends = friends.filter(f => f !== friend);
    updateFriendsList();
}

function updateFriendsList() {
    const friendsList = document.getElementById('friendsList');
    friendsList.innerHTML = '';
    
    friends.forEach(friend => {
        const friendItem = document.createElement('div');
        friendItem.className = 'friend-item';
        friendItem.innerHTML = `
            <span>${friend}</span>
            <button class="remove-btn" onclick="removeFriend('${friend}')">×</button>
        `;
        friendsList.appendChild(friendItem);
    });
}

// Make functions available globally for onclick handlers
window.removeGoal = removeGoal;
window.removeFriend = removeFriend;

async function saveChallenge() {
    const startDate = document.getElementById('startDate').value.trim();
    const endDate = document.getElementById('endDate').value.trim();
    const description = document.getElementById('challengeDescription').value.trim();

    // Validation
    if (!startDate || !endDate) {
        showError('message', 'Please enter both start and end dates', false);
        return;
    }

    if (!description) {
        showError('message', 'Please enter a challenge description', false);
        return;
    }

    if (!selectedPrivacy) {
        showError('message', 'Please select whether the challenge should be private or public', false);
        return;
    }

    try {
        const result = await apiCall('/create-challenge', 'POST', {
            start_date: startDate,
            end_date: endDate,
            description: description,
            privacy: selectedPrivacy,
            goals: goals,
            friends: friends,
            routine_id: attachRoutine ? 1 : null, // In production, get actual routine ID
            user_id: 'default_user'
        });

        showMessage('message', result.message, true);
        
        // Clear form
        document.getElementById('startDate').value = '';
        document.getElementById('endDate').value = '';
        document.getElementById('challengeDescription').value = '';
        document.querySelectorAll('.privacy-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.yes-no-btn').forEach(btn => btn.classList.remove('active'));
        goals = [];
        friends = [];
        updateGoalsList();
        updateFriendsList();
        selectedPrivacy = null;
        attachRoutine = null;
    } catch (error) {
        showError('message', error.message);
    }
}

