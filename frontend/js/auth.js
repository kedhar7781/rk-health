// Authentication controller class for RK Health patient portal

const Auth = {
    async register(username, email, phone, password) {
        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, phone, password })
            });
            const data = await response.json();
            
            if (response.ok) {
                this.showToast('Registration successful! Please login.', 'success');
                return true;
            } else {
                this.showToast(data.message || 'Registration failed', 'danger');
                return false;
            }
        } catch (error) {
            console.error('Registration error:', error);
            this.showToast('Network error during registration', 'danger');
            return false;
        }
    },

    async login(username, password) {
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await response.json();
            
            if (response.ok) {
                this.showToast('Login successful!', 'success');
                return true;
            } else {
                this.showToast(data.message || 'Invalid credentials', 'danger');
                return false;
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showToast('Network error during login', 'danger');
            return false;
        }
    },

    async logout() {
        try {
            const response = await fetch('/api/auth/logout', { method: 'POST' });
            if (response.ok) {
                window.location.href = '/login';
            }
        } catch (error) {
            console.error('Logout error:', error);
            window.location.href = '/login';
        }
    },

    async checkSession() {
        try {
            const response = await fetch('/api/auth/me');
            if (response.ok) {
                const data = await response.json();
                return data.user;
            }
            return null;
        } catch (error) {
            console.error('Session check error:', error);
            return null;
        }
    },

    showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        let icon = 'fa-circle-info';
        if (type === 'success') icon = 'fa-circle-check';
        if (type === 'warning') icon = 'fa-circle-exclamation';
        if (type === 'danger') icon = 'fa-triangle-exclamation';
        
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <i class="fa-solid ${icon}"></i>
                <span class="toast-message">${message}</span>
            </div>
            <button class="toast-close">&times;</button>
        `;
        
        container.appendChild(toast);
        
        toast.querySelector('.toast-close').addEventListener('click', () => {
            toast.remove();
        });
        
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }
};
