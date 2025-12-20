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
