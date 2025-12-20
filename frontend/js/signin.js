function switchTab(tab) {
            const loginForm = document.getElementById('loginForm');
            const signupForm = document.getElementById('signupForm');
            const footerText = document.getElementById('footerText');
            const tabs = document.querySelectorAll('.tab-btn');

            if (tab === 'login') {
                loginForm.classList.remove('hidden');
                signupForm.classList.add('hidden');
                tabs[0].classList.add('active');
                tabs[1].classList.remove('active');
                footerText.innerHTML = `Don't have an account? <span class="auth-link" onclick="switchTab('signup')">Sign Up</span>`;
                document.title = "Sign In | Lumina Events";
            } else {
                loginForm.classList.add('hidden');
                signupForm.classList.remove('hidden');
                tabs[0].classList.remove('active');
                tabs[1].classList.add('active');
                footerText.innerHTML = `Already have an account? <span class="auth-link" onclick="switchTab('login')">Sign In</span>`;
                document.title = "Sign Up | Lumina Events";
            }
        }

        async function handleAuth(e, type) {
            e.preventDefault();
            const form = e.target;
            const btn = form.querySelector('button[type="submit"]');
            const originalText = btn.innerText;

            // Loading State
            btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Processing...';
            btn.disabled = true;
            btn.style.opacity = '0.7';

            try {
                if (type === 'Login') {
                    // Handle Login
                    const inputs = form.querySelectorAll('input');
                    const email = inputs[0].value;
                    const password = inputs[1].value;
                    
                    // Call backend API
                    await AuthAPI.login(email, password);
                    
                    // Load user profile
                    const userProfile = await ProfileAPI.getProfile();
                    
                    // Save user data to localStorage
                    saveUser(
                        userProfile.full_name,
                        userProfile.email,
                        userProfile.is_agency ? 'agency' : 'user',
                        userProfile.phone_number
                    );
                    
                    // Success state
                    btn.innerHTML = '<i class="fa-solid fa-check"></i> Success';
                    btn.style.backgroundColor = '#10b981';
                    
                    // Redirect based on role
                    setTimeout(() => {
                        if (userProfile.is_agency) {
                            window.location.href = 'agency-dashboard.html';
                        } else {
                            window.location.href = 'user-dashboard.html';
                        }
                    }, 1000);
                    
                } else {
                    // Handle Sign Up
                    const inputs = form.querySelectorAll('input, select');
                    const fullName = inputs[0].value;
                    const email = inputs[1].value;
                    const phone = inputs[2].value;
                    const role = inputs[3].value;
                    const password = inputs[4].value;
                    
                    const isAgency = role === 'agency';
                    
                    // Call backend API
                    const response = await AuthAPI.register(fullName, email, password, phone, isAgency);
                    
                    // Save user data to localStorage
                    saveUser(
                        response.user.full_name,
                        response.user.email,
                        response.user.is_agency ? 'agency' : 'user',
                        response.user.phone_number
                    );
                    
                    // Success state
                    btn.innerHTML = '<i class="fa-solid fa-check"></i> Success';
                    btn.style.backgroundColor = '#10b981';
                    
                    // Redirect based on role
                    setTimeout(() => {
                        if (isAgency) {
                            window.location.href = 'agency-dashboard.html';
                        } else {
                            window.location.href = 'user-dashboard.html';
                        }
                    }, 1000);
                }
            } catch (error) {
                console.error('Authentication error:', error);
                
                // Error state
                btn.innerHTML = '<i class="fa-solid fa-exclamation-circle"></i> Error';
                btn.style.backgroundColor = '#ef4444';
                
                // Show error message
                const errorMsg = document.createElement('div');
                errorMsg.style.cssText = 'color: #ef4444; margin-top: 10px; font-size: 14px; text-align: center;';
                errorMsg.textContent = error.message || 'Authentication failed. Please try again.';
                form.appendChild(errorMsg);
                
                // Reset button after 3 seconds
                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.style.backgroundColor = '';
                    btn.disabled = false;
                    btn.style.opacity = '1';
                    if (errorMsg.parentNode) {
                        errorMsg.remove();
                    }
                }, 3000);
            }
        }