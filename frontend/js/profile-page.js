function togglePasswordVisibility(button) {
    event.preventDefault();
    const wrapper = button.closest('.input-wrapper');
    const input = wrapper.querySelector('.password-field');
    const icon = button.querySelector('i');

    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fa-solid fa-eye';
    } else {
        input.type = 'password';
        icon.className = 'fa-regular fa-eye-slash';
    }
}

let newProfilePhoto = null;

function getUserAvatar(name) {
    return (name || '?').charAt(0).toUpperCase();
}

async function handleProfilePhotoChange(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
        showAlert('error', 'Please select an image file');
        return;
    }

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
        showAlert('error', 'Image size must be less than 5MB');
        return;
    }

    try {
        // Upload avatar to backend database
        await ProfileAPI.uploadAvatar(file);

        // Show preview
        const reader = new FileReader();
        reader.onload = function(e) {
            const avatarElement = document.getElementById('userAvatar');
            avatarElement.innerHTML = `<img src="${e.target.result}" alt="Profile" style="width:100%; height:100%; object-fit:cover; border-radius:50%;"><div class="camera-badge"><i class="fa-solid fa-camera" style="font-size:0.7rem;"></i></div>`;
            document.getElementById('deletePhotoBtn').style.display = 'flex';
        };
        reader.readAsDataURL(file);

        showAlert('success', 'Profile photo uploaded to database!');
    } catch (error) {
        console.error('Failed to upload avatar:', error);
        showAlert('error', error.message || 'Failed to upload photo. Please try again.');
    }
}

async function deleteProfilePhoto() {
    if (!confirm('Are you sure you want to delete your profile photo?')) {
        return;
    }

    try {
        // Delete avatar from backend database
        await ProfileAPI.deleteAvatar();

        // Update UI
        const profile = await ProfileAPI.getProfile();
        const avatarElement = document.getElementById('userAvatar');
        avatarElement.innerHTML = `${getUserAvatar(profile.full_name)}<div class="camera-badge"><i class="fa-solid fa-camera" style="font-size:0.7rem;"></i></div>`;
        document.getElementById('deletePhotoBtn').style.display = 'none';

        showAlert('success', 'Profile photo deleted from database!');
    } catch (error) {
        console.error('Failed to delete avatar:', error);
        showAlert('error', 'Failed to delete photo. Please try again.');
    }
}

async function loadProfile() {
    if (!isLoggedIn()) {
        window.location.href = 'signin.html';
        return;
    }

    try {
        // Load profile from backend database
        const profile = await ProfileAPI.getProfile();

        // Update UI with profile data from database
        document.getElementById('userName').textContent = profile.full_name;
        document.getElementById('userEmail').textContent = profile.email;
        document.getElementById('usernameInput').value = profile.full_name;
        document.getElementById('phoneInput').value = profile.phone_number || '';

        // Try to load avatar from backend
        const avatarElement = document.getElementById('userAvatar');
        try {
            const avatarBlob = await ProfileAPI.getAvatar();
            if (avatarBlob) {
                const avatarUrl = URL.createObjectURL(avatarBlob);
                avatarElement.innerHTML = `<img src="${avatarUrl}" alt="${profile.full_name}" style="width:100%; height:100%; object-fit:cover; border-radius:50%;"><div class="camera-badge"><i class="fa-solid fa-camera" style="font-size:0.7rem;"></i></div>`;
                document.getElementById('deletePhotoBtn').style.display = 'flex';
            } else {
                throw new Error('No avatar');
            }
        } catch (err) {
            // No avatar, show initials
            avatarElement.innerHTML = `${getUserAvatar(profile.full_name)}<div class="camera-badge"><i class="fa-solid fa-camera" style="font-size:0.7rem;"></i></div>`;
            document.getElementById('deletePhotoBtn').style.display = 'none';
        }
    } catch (error) {
        console.error('Failed to load profile:', error);
        showAlert('error', 'Failed to load profile. Please try again.');
    }
}

function showAlert(type, message) {
    const successAlert = document.getElementById('successAlert');
    const errorAlert = document.getElementById('errorAlert');

    if (type === 'success') {
        document.getElementById('successMessage').textContent = message;
        successAlert.classList.add('show');
        errorAlert.classList.remove('show');
    } else {
        document.getElementById('errorMessage').textContent = message;
        errorAlert.classList.add('show');
        successAlert.classList.remove('show');
    }
}

async function resetForm() {
    await loadProfile();
    document.getElementById('newPasswordInput').value = '';
    document.getElementById('confirmPasswordInput').value = '';
}

function goToDashboard() {
    const user = getLoggedInUser();
    const dashboardLink = user.role === 'agency' ? 'agency-dashboard.html' : 'user-dashboard.html';
    window.location.href = dashboardLink;
}

async function handleSaveProfile(event) {
    event.preventDefault();

    const newUsername = document.getElementById('usernameInput').value.trim();
    const newPhone = document.getElementById('phoneInput').value.trim();
    const newPassword = document.getElementById('newPasswordInput').value.trim();
    const confirmPassword = document.getElementById('confirmPasswordInput').value.trim();

    // Validation
    if (!newUsername) {
        showAlert('error', 'Name cannot be empty');
        return;
    }

    if (newUsername.length < 2) {
        showAlert('error', 'Name must be at least 2 characters');
        return;
    }

    // Password validation (if changing password)
    if (newPassword || confirmPassword) {
        if (newPassword.length < 6) {
            showAlert('error', 'Password must be at least 6 characters');
            return;
        }

        if (newPassword !== confirmPassword) {
            showAlert('error', 'Passwords do not match');
            return;
        }

        showAlert('error', 'Password change is not yet implemented. Please contact support.');
        return;
    }

    try {
        // Update profile in backend database
        const updatedProfile = await ProfileAPI.updateProfile(newUsername, newPhone || null);

        // Update localStorage with new data from database
        await loadAndSaveCurrentUser();

        showAlert('success', 'Profile saved to database successfully!');

        // Reload profile to show updated data
        setTimeout(async () => {
            await loadProfile();
            showAlert('success', 'Profile data refreshed from database!');
        }, 500);

    } catch (error) {
        console.error('Failed to update profile:', error);
        showAlert('error', error.message || 'Failed to save profile. Please try again.');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', loadProfile);
