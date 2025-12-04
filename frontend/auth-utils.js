// Auth utility functions to be included in all protected pages

// API base URL
const API_BASE = "";

// Get stored token
function getToken() {
    return localStorage.getItem("spotterToken");
}

// Get stored email
function getEmail() {
    return localStorage.getItem("spotterEmail");
}

// Add auth header to fetch requests
function authFetch(url, options = {}) {
    const token = getToken();
    
    if (!options.headers) {
        options.headers = {};
    }
    
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }
    
    return fetch(url, options);
}

// Check if user is authenticated and redirect if not
async function requireAuth() {
    const token = getToken();
    
    if (!token) {
        window.location.href = "login.html";
        return false;
    }
    
    try {
        const res = await fetch(`${API_BASE}/api/verify`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!res.ok) {
            // Token invalid
            localStorage.removeItem("spotterToken");
            localStorage.removeItem("spotterEmail");
            window.location.href = "login.html";
            return false;
        }
        
        return true;
    } catch (err) {
        console.error("Auth check failed:", err);
        return false;
    }
}

// Logout function
async function logout() {
    const token = getToken();
    
    if (token) {
        try {
            await fetch(`${API_BASE}/api/logout`, {
                method: "POST",
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
        } catch (err) {
            console.error("Logout error:", err);
        }
    }
    
    localStorage.removeItem("spotterToken");
    localStorage.removeItem("spotterEmail");
    window.location.href = "login.html";
}
