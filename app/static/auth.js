// ============================================================================
// AUTHENTICATION LOGIC (LOGIN & SIGNUP PAGES)
// ============================================================================

/**
 * Handle signup form submission
 */
async function handleSignup(event) {
    event.preventDefault();

    const username = document.getElementById("signup-username").value.trim();
    const email = document.getElementById("signup-email").value.trim();
    const password = document.getElementById("signup-password").value;

    const messageElement = document.getElementById("signup-message");

    // Validation
    if (!username || !email || !password) {
        showMessage(messageElement, "All fields are required", "error");
        return;
    }

    if (password.length < 6) {
        showMessage(messageElement, "Password must be at least 6 characters", "error");
        return;
    }

    try {
        const response = await fetch("/signup", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password,
            }),
        });

        const data = await response.json();

        if (response.ok) {
            showMessage(messageElement, data.message, "success");

            // Clear form
            document.getElementById("signup-form").reset();

            // Redirect to login after 2 seconds
            setTimeout(() => {
                window.location.href = "/login";
            }, 2000);
        } else {
            showMessage(messageElement, data.detail || "Signup failed", "error");
        }
    } catch (error) {
        showMessage(messageElement, "Network error: " + error.message, "error");
    }
}


/**
 * Handle login form submission
 */
async function handleLogin(event) {
    event.preventDefault();

    const username = document.getElementById("login-username").value.trim();
    const password = document.getElementById("login-password").value;

    const messageElement = document.getElementById("login-message");

    // Validation
    if (!username || !password) {
        showMessage(messageElement, "Username and password are required", "error");
        return;
    }

    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                username: username,
                password: password,
            }),
        });

        const data = await response.json();

        if (response.ok) {
            showMessage(messageElement, "Login successful! Redirecting...", "success");

            // Store token and username in localStorage
            localStorage.setItem("accessToken", data.access_token);
            localStorage.setItem("username", username);

            // Redirect to dashboard after 1 second
            setTimeout(() => {
                window.location.href = "/dashboard";
            }, 1000);
        } else {
            showMessage(messageElement, data.detail || "Login failed", "error");
        }
    } catch (error) {
        showMessage(messageElement, "Network error: " + error.message, "error");
    }
}


/**
 * Display message in UI
 */
function showMessage(element, message, type) {
    element.innerText = message;
    element.className = `form-message message-${type}`;
    element.style.display = "block";
}
