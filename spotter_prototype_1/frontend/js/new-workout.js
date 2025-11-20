// New Workout Page JavaScript

let selectedBodyParts = [];
let selectedMuscles = [];

document.addEventListener('DOMContentLoaded', function() {
    const bodyPartButtons = document.querySelectorAll('.body-part-btn');
    const muscleSelect = document.getElementById('muscleSelect');
    const getWorkoutBtn = document.getElementById('getWorkoutBtn');

    // Body part selection
    bodyPartButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const bodyPart = this.dataset.bodyPart;
            
            // Toggle selection
            if (this.classList.contains('active')) {
                this.classList.remove('active');
                selectedBodyParts = selectedBodyParts.filter(bp => bp !== bodyPart);
            } else {
                this.classList.add('active');
                selectedBodyParts.push(bodyPart);
            }

            // Update muscle dropdown based on selected body parts
            updateMuscleDropdown();
        });
    });

    // Get workout button
    if (getWorkoutBtn) {
        getWorkoutBtn.addEventListener('click', async function() {
            if (selectedBodyParts.length === 0) {
                showError('errorMessage', 'Please select at least one body part');
                return;
            }

            // Get selected muscles from dropdown
            const muscleOptions = muscleSelect.selectedOptions;
            selectedMuscles = Array.from(muscleOptions).map(opt => opt.value).filter(v => v);

            try {
                getWorkoutBtn.disabled = true;
                getWorkoutBtn.textContent = 'LOADING...';

                const result = await apiCall('/weightlifting-suggestions', 'POST', {
                    body_parts: selectedBodyParts,
                    muscles: selectedMuscles
                });

                displayWorkoutResults(result.routine);
                document.getElementById('errorMessage').style.display = 'none';
            } catch (error) {
                showError('errorMessage', error.message);
            } finally {
                getWorkoutBtn.disabled = false;
                getWorkoutBtn.textContent = 'GET WORKOUT';
            }
        });
    }
});

async function updateMuscleDropdown() {
    const muscleSelect = document.getElementById('muscleSelect');
    muscleSelect.innerHTML = '<option value="" disabled>SELECT MUSCLES</option>';

    if (selectedBodyParts.length === 0) {
        return;
    }

    // Get all unique muscles from selected body parts
    const allMuscles = new Set();
    
    for (const bodyPart of selectedBodyParts) {
        try {
            const result = await apiCall(`/muscles?body_part=${bodyPart.toLowerCase()}`);
            if (result.muscles) {
                result.muscles.forEach(muscle => {
                    // Format muscle name for display
                    const displayName = muscle.split('_').map(word => 
                        word.charAt(0).toUpperCase() + word.slice(1)
                    ).join(' ');
                    allMuscles.add({ value: muscle, display: displayName });
                });
            }
        } catch (error) {
            console.error('Error fetching muscles:', error);
        }
    }

    // Add muscles to dropdown
    Array.from(allMuscles).forEach(({ value, display }) => {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = display.toUpperCase();
        muscleSelect.appendChild(option);
    });
}

function displayWorkoutResults(routine) {
    const resultsContainer = document.getElementById('workoutResults');
    const routineList = document.getElementById('routineList');

    if (!routine || routine.length === 0) {
        showError('errorMessage', 'No exercises found for your selection');
        return;
    }

    routineList.innerHTML = '';
    
    routine.forEach((exercise, index) => {
        const exerciseItem = document.createElement('div');
        exerciseItem.className = 'routine-item';
        exerciseItem.innerHTML = `
            <h4>${index + 1}. ${exercise.exercise}</h4>
            <p><strong>Sets:</strong> ${exercise.sets}</p>
            <p><strong>Reps:</strong> ${exercise.reps}</p>
            <p><strong>Rest Time:</strong> ${exercise.rest_time}</p>
        `;
        routineList.appendChild(exerciseItem);
    });

    resultsContainer.style.display = 'block';
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

