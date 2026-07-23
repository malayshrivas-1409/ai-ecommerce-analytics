// ============================================================================
// DASHBOARD LOGIC
// ============================================================================

let accessToken = null;
let schedulerInterval = null;


// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener("DOMContentLoaded", function () {
    initializeDashboard();
});


function initializeDashboard() {
    // Initialize dashboard on page load

    // Check if user is logged in
    accessToken = localStorage.getItem("accessToken");

    if (!accessToken) {
        // Redirect to login if not authenticated
        window.location.href = "/login";
        return;
    }

    // Display username
    const username = localStorage.getItem("username") || "User";
    document.getElementById("user-info").innerText = `Welcome, ${username}`;

    // Load initial data
    loadMetrics();
    loadSchedulerStatus();

    // Refresh metrics every 5 seconds
    setInterval(loadMetrics, 5000);

    // Refresh scheduler status every 2 seconds
    setInterval(loadSchedulerStatus, 2000);
}


// ============================================================================
// SCHEDULER CONTROL
// ============================================================================

async function startScheduler() {
    // Start automatic event generation

    try {
        const response = await fetch("/scheduler/start", {
            method: "POST",
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        });

        const data = await response.json();

        if (response.ok) {
            showSchedulerMessage("Event generation started!", "success");
            updateSchedulerUI(data);
        } else {
            showSchedulerMessage("Failed to start scheduler", "error");
        }
    } catch (error) {
        showSchedulerMessage("Network error: " + error.message, "error");
    }
}


async function pauseScheduler() {
    // Pause automatic event generation

    try {
        const response = await fetch("/scheduler/pause", {
            method: "POST",
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        });

        const data = await response.json();

        if (response.ok) {
            showSchedulerMessage("Event generation paused", "warning");
            updateSchedulerUI(data);
        } else {
            showSchedulerMessage("Failed to pause scheduler", "error");
        }
    } catch (error) {
        showSchedulerMessage("Network error: " + error.message, "error");
    }
}


async function resumeScheduler() {
    // Resume paused event generation

    try {
        const response = await fetch("/scheduler/resume", {
            method: "POST",
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        });

        const data = await response.json();

        if (response.ok) {
            showSchedulerMessage("Event generation resumed!", "success");
            updateSchedulerUI(data);
        } else {
            showSchedulerMessage("Failed to resume scheduler", "error");
        }
    } catch (error) {
        showSchedulerMessage("Network error: " + error.message, "error");
    }
}


async function stopScheduler() {
    // Stop automatic event generation

    try {
        const response = await fetch("/scheduler/stop", {
            method: "POST",
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        });

        const data = await response.json();

        if (response.ok) {
            showSchedulerMessage("Event generation stopped", "warning");
            updateSchedulerUI(data);
        } else {
            showSchedulerMessage("Failed to stop scheduler", "error");
        }
    } catch (error) {
        showSchedulerMessage("Network error: " + error.message, "error");
    }
}


async function loadSchedulerStatus() {
    // Fetch and display scheduler status

    try {
        const response = await fetch("/scheduler/status", {
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        });

        if (response.ok) {
            const data = await response.json();
            updateSchedulerUI(data);
        }
    } catch (error) {
        console.error("Failed to fetch scheduler status:", error);
    }
}


function updateSchedulerUI(status) {
    // Update scheduler UI based on status

    const statusBadge = document.getElementById("scheduler-status");
    const totalEvents = document.getElementById("total-events");
    const btnStart = document.getElementById("btn-start");
    const btnPause = document.getElementById("btn-pause");
    const btnResume = document.getElementById("btn-resume");
    const btnStop = document.getElementById("btn-stop");

    totalEvents.innerText = status.total_events_generated;

    // Update status badge and buttons
    if (status.is_running) {
        if (status.is_paused) {
            statusBadge.innerText = "Paused";
            statusBadge.className = "status-badge status-paused";

            btnStart.disabled = true;
            btnPause.disabled = true;
            btnResume.disabled = false;
            btnStop.disabled = false;
        } else {
            statusBadge.innerText = "Running";
            statusBadge.className = "status-badge status-running";

            btnStart.disabled = true;
            btnPause.disabled = false;
            btnResume.disabled = true;
            btnStop.disabled = false;
        }
    } else {
        statusBadge.innerText = "Stopped";
        statusBadge.className = "status-badge status-stopped";

        btnStart.disabled = false;
        btnPause.disabled = true;
        btnResume.disabled = true;
        btnStop.disabled = true;
    }
}


function showSchedulerMessage(message, type) {
    // Display scheduler message

    const messageElement = document.getElementById("scheduler-message");
    messageElement.innerText = message;
    messageElement.className = `scheduler-message message-${type}`;

    setTimeout(() => {
        messageElement.innerText = "";
        messageElement.className = "scheduler-message";
    }, 3000);
}


// ============================================================================
// METRICS & ANALYTICS
// ============================================================================

async function loadMetrics() {
    // Load and display analytics metrics

    try {
        const response = await fetch("/analytics/dashboard", {
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        });

        if (response.ok) {
            const data = await response.json();
            displayMetrics(data);
        }
    } catch (error) {
        console.error("Failed to load metrics:", error);
    }
}


function displayMetrics(data) {
    // Display fetched metrics on dashboard with smooth animations

    // Summary metrics
    const summary = data.summary || {};
    updateMetricValue("metric-orders", summary.total_orders || 0);
    updateMetricValue("metric-revenue", "₹" + (summary.total_revenue || 0).toFixed(2));
    updateMetricValue("metric-avg", "₹" + (summary.average_order_value || 0).toFixed(2));

    // Conversion funnel
    const funnel = data.conversion_funnel || {};
    document.getElementById("metric-conversion").innerText =
        (funnel.overall_conversion_rate || 0).toFixed(2) + "%";

    // User insights
    const users = data.user_insights || {};
    document.getElementById("metric-users").innerText = users.unique_users || 0;

    // Top category
    const categories = data.category_sales || [];
    if (categories.length > 0) {
        document.getElementById("metric-category").innerText = categories[0].category || "—";
    }

    // Top products list
    displayTopProducts(data.top_products || []);

    // Category sales list
    displayCategorySales(data.category_sales || []);

    // Conversion funnel
    displayConversionFunnel(data.conversion_funnel || {});
}


function displayTopProducts(products) {
    // Display top products list

    const container = document.getElementById("top-products");

    if (!products || products.length === 0) {
        container.innerHTML = "<p class='empty-state'>No products yet</p>";
        return;
    }

    let html = "<div class='list'>";

    products.forEach((product, index) => {
        html += `
            <div class="list-item">
                <span class="rank">#${index + 1}</span>
                <span class="name">${product.product_name}</span>
                <span class="value">${product.total_orders} orders</span>
                <span class="price">₹${product.total_revenue.toFixed(2)}</span>
            </div>
        `;
    });

    html += "</div>";
    container.innerHTML = html;
}


function displayCategorySales(categories) {
    // Display category sales list

    const container = document.getElementById("category-sales");

    if (!categories || categories.length === 0) {
        container.innerHTML = "<p class='empty-state'>No categories yet</p>";
        return;
    }

    let html = "<div class='list'>";

    categories.forEach((category) => {
        const percentage = ((category.revenue / categories.reduce((sum, c) => sum + c.revenue, 0)) * 100).toFixed(1);

        html += `
            <div class="list-item">
                <span class="name">${category.category}</span>
                <span class="value">${category.total_orders} orders</span>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${percentage}%"></div>
                </div>
                <span class="price">₹${category.revenue.toFixed(2)}</span>
            </div>
        `;
    });

    html += "</div>";
    container.innerHTML = html;
}


function displayConversionFunnel(funnel) {
    // Display conversion funnel

    const container = document.getElementById("conversion-funnel");

    const funnelData = [
        { label: "Views", value: funnel.views || 0 },
        { label: "Cart Adds", value: funnel.cart_additions || 0 },
        { label: "Purchases", value: funnel.purchases || 0 },
    ];

    let html = "<div class='funnel'>";

    funnelData.forEach((step) => {
        html += `
            <div class="funnel-step">
                <span class="step-label">${step.label}</span>
                <span class="step-value">${step.value}</span>
            </div>
        `;
    });

    html += "</div>";
    container.innerHTML = html;
}


// ============================================================================
// LOGOUT
// ============================================================================

function logout() {
    // Logout user and clear session

    localStorage.removeItem("accessToken");
    localStorage.removeItem("username");

    window.location.href = "/login";
}


// ============================================================================
// UTILITY FUNCTIONS FOR SMOOTH ANIMATIONS
// ============================================================================

function updateMetricValue(elementId, newValue) {
    // Update metric value with smooth animation
    
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const oldValue = element.innerText;
    
    // Add fade animation
    element.style.transition = 'opacity 0.3s ease';
    element.style.opacity = '0.7';
    
    setTimeout(() => {
        element.innerText = newValue;
        element.style.opacity = '1';
    }, 150);
}

function displayListItemsWithAnimation(container, items, renderFunction) {
    // Display list items with staggered animation
    
    if (!items || items.length === 0) {
        container.innerHTML = "<p class='empty-state'>No data available</p>";
        return;
    }
    
    let html = "<div class='list'>";
    
    items.forEach((item, index) => {
        html += renderFunction(item, index);
    });
    
    html += "</div>";
    
    // Clear and set with animation
    container.style.opacity = '0.8';
    container.innerHTML = html;
    container.style.opacity = '1';
    container.style.transition = 'opacity 0.3s ease';
}
