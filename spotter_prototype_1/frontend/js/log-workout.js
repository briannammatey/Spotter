// Log Workout Page JavaScript

let selectedPrivacy = null;
let mediaFile = null;

document.addEventListener('DOMContentLoaded', function() {
    const workoutDescription = document.getElementById('workoutDescription');
    const personalRecord = document.getElementById('personalRecord');
    const privacyButtons = document.querySelectorAll('.privacy-btn');
    const cameraBtn = document.getElementById('cameraBtn');
    const cameraRollBtn = document.getElementById('cameraRollBtn');
    const mediaInput = document.getElementById('mediaInput');
    const postToFeedBtn = document.getElementById('postToFeedBtn');
    const saveToProfileBtn = document.getElementById('saveToProfileBtn');

    // Privacy selection
    privacyButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            privacyButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            selectedPrivacy = this.dataset.privacy;
        });
    });

    // Camera button
    if (cameraBtn) {
        cameraBtn.addEventListener('click', function() {
            // In a real app, this would open the camera
            alert('Camera functionality would open here. For now, use Camera Roll.');
        });
    }

    // Camera roll button
    if (cameraRollBtn && mediaInput) {
        cameraRollBtn.addEventListener('click', function() {
            mediaInput.click();
        });
    }

    // Media input change
    if (mediaInput) {
        mediaInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                mediaFile = file;
                displayMediaPreview(file);
            }
        });
    }

    // Post to feed button
    if (postToFeedBtn) {
        postToFeedBtn.addEventListener('click', async function() {
            await saveWorkout('public');
        });
    }

    // Save to profile button
    if (saveToProfileBtn) {
        saveToProfileBtn.addEventListener('click', async function() {
            // Automatically set privacy to private for profile saves
            if (!selectedPrivacy) {
                privacyButtons.forEach(b => b.classList.remove('active'));
                const privateBtn = Array.from(privacyButtons).find(b => b.dataset.privacy === 'private');
                if (privateBtn) {
                    privateBtn.classList.add('active');
                    selectedPrivacy = 'private';
                }
            }
            await saveWorkout('private');
        });
    }
});

function displayMediaPreview(file) {
    const preview = document.getElementById('mediaPreview');
    preview.innerHTML = '';

    if (file.type.startsWith('image/')) {
        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        preview.appendChild(img);
    } else if (file.type.startsWith('video/')) {
        const video = document.createElement('video');
        video.src = URL.createObjectURL(file);
        video.controls = true;
        preview.appendChild(video);
    }

    preview.style.display = 'block';
}

async function saveWorkout(privacy) {
    const description = document.getElementById('workoutDescription').value.trim();
    const personalRecord = document.getElementById('personalRecord').value.trim();

    // Validation
    if (!description) {
        showError('message', 'Please enter a description of your workout', false);
        return;
    }

    // Convert media file to data URL for storage/display
    let photoUrl = '';
    if (mediaFile) {
        try {
            photoUrl = await fileToDataURL(mediaFile);
        } catch (error) {
            console.error('Error converting file to data URL:', error);
            photoUrl = mediaFile.name; // Fallback to filename
        }
    }

    try {
        console.log('Saving workout with data:', {
            description: description,
            privacy: privacy,
            photo_url: photoUrl ? 'Photo provided' : 'No photo',
            personal_record: personalRecord,
            user_id: 'default_user'
        });
        
        const result = await apiCall('/log-workout', 'POST', {
            description: description,
            privacy: privacy,
            photo_url: photoUrl,
            personal_record: personalRecord,
            user_id: 'default_user' // In production, get from session
        });

        console.log('Workout saved successfully:', result);
        showMessage('message', result.message + ' - You can now view it on your Profile page!', true);
        
        // Clear form
        document.getElementById('workoutDescription').value = '';
        document.getElementById('personalRecord').value = '';
        document.getElementById('mediaInput').value = '';
        document.getElementById('mediaPreview').style.display = 'none';
        document.querySelectorAll('.privacy-btn').forEach(btn => btn.classList.remove('active'));
        selectedPrivacy = null;
        mediaFile = null;
    } catch (error) {
        console.error('Error saving workout:', error);
        showError('message', error.message);
    }
}

function fileToDataURL(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

