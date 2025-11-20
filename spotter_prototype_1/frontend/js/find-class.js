// Find Class Page JavaScript

let selectedLocation = 'on_campus';
let selectedClassTypes = [];

document.addEventListener('DOMContentLoaded', function() {
    const locationButtons = document.querySelectorAll('.location-btn');
    const classTypeSelect = document.getElementById('classTypeSelect');
    const findClassBtn = document.getElementById('findClassBtn');

    // Location selection
    locationButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            locationButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            selectedLocation = this.dataset.location;
        });
    });

    // Class type selection (multi-select)
    if (classTypeSelect) {
        classTypeSelect.addEventListener('change', function() {
            const selectedOptions = Array.from(this.selectedOptions);
            selectedClassTypes = selectedOptions.map(opt => opt.value).filter(v => v);
        });
    }

    // Find class button
    if (findClassBtn) {
        findClassBtn.addEventListener('click', async function() {
            try {
                findClassBtn.disabled = true;
                findClassBtn.textContent = 'LOADING...';

                // For this implementation, we'll use liked_classes as selected classes
                const result = await apiCall('/exercise-class-suggestions', 'POST', {
                    liked_classes: selectedClassTypes,
                    disliked_classes: [],
                    distance: '5 miles',
                    location: selectedLocation
                });

                displayClassResults(result.suggestions);
                document.getElementById('errorMessage').style.display = 'none';
            } catch (error) {
                showError('errorMessage', error.message);
            } finally {
                findClassBtn.disabled = false;
                findClassBtn.textContent = 'FIND CLASS';
            }
        });
    }
});

function displayClassResults(suggestions) {
    const resultsContainer = document.getElementById('classResults');
    const classList = document.getElementById('classList');

    if (!suggestions || suggestions.length === 0) {
        showError('errorMessage', 'No classes found matching your preferences');
        return;
    }

    classList.innerHTML = '';
    
    suggestions.forEach((suggestion, index) => {
        const classItem = document.createElement('div');
        classItem.className = 'class-item';
        classItem.innerHTML = `
            <h4>${suggestion.name}</h4>
            <p><strong>Location:</strong> ${suggestion.location}</p>
            <p><strong>Distance:</strong> ${suggestion.distance}</p>
            <p><strong>Time:</strong> ${suggestion.time}</p>
            <p><strong>Instructor:</strong> ${suggestion.instructor}</p>
        `;
        classList.appendChild(classItem);
    });

    resultsContainer.style.display = 'block';
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

