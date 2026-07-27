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

    // Phase 3: Initialize theme, scroll reveal, and tooltips
    enhanceInitialization();

    // Load initial data
    loadMetrics();
    loadSchedulerStatus();
    initializeAIInsights();
    loadAIRecommendations();

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
        
        // Load hourly sales separately
        const hourlyResponse = await fetch("/analytics/hourly-sales", {
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        });
        
        if (hourlyResponse.ok) {
            const hourlyData = await hourlyResponse.json();
            displayHourlySales(hourlyData);
        }
    } catch (error) {
        console.error("Failed to load metrics:", error);
    }
}


function displayMetrics(data) {
    // Display fetched metrics on dashboard with smooth animations

    // Summary metrics
    const summary = data.summary || {};
    
    // Use counter animations
    const ordersElement = document.getElementById("metric-orders");
    const revenueElement = document.getElementById("metric-revenue");
    const avgElement = document.getElementById("metric-avg");
    
    if (ordersElement) {
        const currentValue = parseInt(ordersElement.innerText) || 0;
        animateValue(ordersElement, currentValue, summary.total_orders || 0, 800);
    }
    
    if (revenueElement) {
        const currentValue = parseInt(revenueElement.innerText.replace('₹', '').replace(/,/g, '')) || 0;
        animateCurrency(revenueElement, currentValue, summary.total_revenue || 0, 800);
    }
    
    if (avgElement) {
        const currentValue = parseInt(avgElement.innerText.replace('₹', '').replace(/,/g, '')) || 0;
        animateCurrency(avgElement, currentValue, summary.average_order_value || 0, 800);
    }

    // Conversion funnel
    const funnel = data.conversion_funnel || {};
    const conversionElement = document.getElementById("metric-conversion");
    if (conversionElement) {
        const currentValue = parseFloat(conversionElement.innerText) || 0;
        animatePercentage(conversionElement, currentValue, funnel.overall_conversion_rate || 0, 800);
    }

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
    // Display category sales list with animated progress bars

    const container = document.getElementById("category-sales");

    if (!categories || categories.length === 0) {
        container.innerHTML = "<p class='empty-state'>No categories yet</p>";
        return;
    }

    let html = "<div class='list'>";
    
    // Calculate total revenue for percentage calculation
    const totalRevenue = categories.reduce((sum, c) => sum + c.revenue, 0);

    categories.forEach((category, index) => {
        const percentage = ((category.revenue / totalRevenue) * 100).toFixed(1);

        html += `
            <div class="category-item" style="animation: slideInUp ${0.3 + index * 0.05}s ease-out;">
                <div class="category-header">
                    <span class="category-name">${category.category}</span>
                    <span class="category-stats">${category.total_orders} orders • ₹${category.revenue.toFixed(2)}</span>
                </div>
                <div class="progress-label">
                    <span></span>
                    <span class="progress-value">${percentage}%</span>
                </div>
                <div class="progress-container">
                    <div class="progress-bar" style="--progress-width: ${percentage}%;"></div>
                </div>
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


function displayHourlySales(hourlyData) {
    // Display hourly sales breakdown with animated progress bars

    const container = document.getElementById("hourly-sales");

    if (!hourlyData || hourlyData.length === 0) {
        container.innerHTML = "<p class='empty-state'>No hourly sales data available</p>";
        return;
    }

    let html = "<div class='hourly-sales-list'>";

    hourlyData.forEach((hour, index) => {
        const hour_label = String(hour.hour).padStart(2, "0") + ":00";
        const max_revenue = Math.max(...hourlyData.map(h => h.revenue));
        const percentage = (hour.revenue / max_revenue) * 100;

        html += `
            <div class="hourly-item" style="animation: slideInUp ${0.2 + index * 0.03}s ease-out;">
                <div class="hourly-header">
                    <span class="hour-time">${hour_label}</span>
                    <span class="hour-stats">${hour.total_orders} orders • ₹${hour.revenue.toFixed(2)}</span>
                </div>
                <div class="progress-label">
                    <span></span>
                    <span class="progress-value">${percentage.toFixed(1)}%</span>
                </div>
                <div class="progress-container">
                    <div class="progress-bar" style="--progress-width: ${percentage}%;"></div>
                </div>
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


// ============================================================================
// NUMBER COUNTER ANIMATION
// ============================================================================

function animateValue(element, start, end, duration) {
    if (!element) return;
    
    let startTimestamp = null;
    const initialValue = end;
    
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        
        // Use easing function for smooth acceleration
        const easeOutQuad = 1 - (1 - progress) * (1 - progress);
        const value = Math.floor(start + (end - start) * easeOutQuad);
        
        element.innerText = value.toLocaleString();
        
        if (progress < 1) {
            requestAnimationFrame(step);
        } else {
            element.innerText = end.toLocaleString();
        }
    };
    
    requestAnimationFrame(step);
}

function animateCurrency(element, start, end, duration) {
    if (!element) return;
    
    let startTimestamp = null;
    
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        
        const easeOutQuad = 1 - (1 - progress) * (1 - progress);
        const value = Math.floor(start + (end - start) * easeOutQuad);
        
        element.innerText = '₹' + value.toLocaleString() + '.00';
        
        if (progress < 1) {
            requestAnimationFrame(step);
        } else {
            element.innerText = '₹' + end.toLocaleString() + '.00';
        }
    };
    
    requestAnimationFrame(step);
}

function animatePercentage(element, start, end, duration) {
    if (!element) return;
    
    let startTimestamp = null;
    
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        
        const easeOutQuad = 1 - (1 - progress) * (1 - progress);
        const value = (start + (end - start) * easeOutQuad).toFixed(2);
        
        element.innerText = value + '%';
        
        if (progress < 1) {
            requestAnimationFrame(step);
        } else {
            element.innerText = end.toFixed(2) + '%';
        }
    };
    
    requestAnimationFrame(step);
}


// ============================================================================
// PROGRESS BAR ANIMATION
// ============================================================================

function animateProgressBar(container, percentage, duration = 1000) {
    if (!container) return;
    
    const bar = container.querySelector('.progress-bar');
    if (!bar) return;
    
    bar.style.setProperty('--progress-width', percentage + '%');
    bar.classList.add('animated');
    
    setTimeout(() => {
        bar.classList.remove('animated');
    }, duration);
}


// ============================================================================
// SKELETON LOADER
// ============================================================================

function createSkeletonLoader(count = 6) {
    let html = '';
    for (let i = 0; i < count; i++) {
        html += `
            <div class="skeleton-card">
                <div class="skeleton-icon"></div>
                <div style="flex: 1;">
                    <div class="skeleton skeleton-text-line" style="width: 80%;"></div>
                    <div class="skeleton skeleton-text-line short"></div>
                </div>
            </div>
        `;
    }
    return html;
}

function showSkeletonLoader(container, count = 6) {
    if (!container) return;
    container.innerHTML = createSkeletonLoader(count);
}

function hideSkeletonLoader(container) {
    if (!container) return;
    const skeletons = container.querySelectorAll('.skeleton-card');
    skeletons.forEach(skeleton => {
        skeleton.style.animation = 'fadeIn 0.3s ease-in-out reverse';
    });
    setTimeout(() => {
        container.innerHTML = '';
    }, 300);
}

/* ============================================================================
   PHASE 3: THEME TOGGLE & SCROLL REVEAL ANIMATIONS
   ============================================================================ */

// Initialize theme on page load
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    applyTheme(savedTheme);
}

// Apply theme
function applyTheme(theme) {
    const html = document.documentElement;
    if (theme === 'light') {
        html.classList.add('light-theme');
        localStorage.setItem('theme', 'light');
        updateThemeIcon('☀️');
    } else {
        html.classList.remove('light-theme');
        localStorage.setItem('theme', 'dark');
        updateThemeIcon('🌙');
    }
}

// Toggle between light and dark themes
function toggleTheme() {
    const html = document.documentElement;
    const isLight = html.classList.contains('light-theme');
    applyTheme(isLight ? 'dark' : 'light');
}

// Update theme toggle icon
function updateThemeIcon(icon) {
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        themeIcon.textContent = icon;
    }
}

// Initialize scroll reveal animations
function initScrollReveal() {
    const sections = document.querySelectorAll('.section');
    
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('scroll-reveal');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    sections.forEach(section => {
        observer.observe(section);
    });
}

// Add tooltip functionality to metric cards
function initTooltips() {
    const metricCards = document.querySelectorAll('.metric-card');
    
    metricCards.forEach(card => {
        const label = card.querySelector('.metric-label')?.textContent || 'Metric';
        const value = card.querySelector('.metric-value')?.textContent || '—';
        
        // Create tooltip if not exists
        if (!card.querySelector('.tooltip-text')) {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip-text';
            tooltip.textContent = `${label}: ${value}`;
            card.appendChild(tooltip);
        }
    });
}

// Enhanced initialization with Phase 3 features
function enhanceInitialization() {
    initTheme();
    initScrollReveal();
    initTooltips();
    
    // Add smooth color transitions to all elements
    document.documentElement.style.setProperty('--transition-smooth', 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)');
}

// Run Phase 3 initialization when DOM is ready
// Note: Already called from initializeDashboard(), removed duplicate


/* ============================================================================
   PHASE 4: ADVANCED ANALYTICS & DATA VISUALIZATION
   ============================================================================ */

// Chart instances
let salesTrendChart = null;
let categoryDistributionChart = null;

// Filter state
let currentFilters = {
    dateRange: '7days',
    category: ''
};

// Initialize Phase 4 analytics
// Initialize Phase 4 analytics
function initPhase4Analytics() {
    // Only load if we have the chart containers
    if (document.getElementById('sales-trend-chart')) {
        loadChartData();
    }
    populateCategoryFilter();
}

// Load chart data from API
async function loadChartData() {
    try {
        const response = await fetch('/api/analytics/charts', {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });

        if (!response.ok) throw new Error('Failed to load chart data');
        
        const data = await response.json();
        renderCharts(data);
    } catch (error) {
        console.error('Chart data error:', error);
        showChartPlaceholder();
    }
}

// Render both charts
function renderCharts(data) {
    renderSalesTrendChart(data.salesTrend || []);
    renderCategoryDistributionChart(data.categoryDistribution || []);
}

// Sales Trend Line Chart
function renderSalesTrendChart(trendData) {
    const ctx = document.getElementById('sales-trend-chart');
    if (!ctx) return;

    // Destroy existing chart if it exists
    if (salesTrendChart) {
        salesTrendChart.destroy();
    }

    const labels = trendData.map(item => item.date || 'N/A');
    const revenues = trendData.map(item => item.revenue || 0);

    salesTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Revenue',
                data: revenues,
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointBackgroundColor: '#6366f1',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverRadius: 7,
                pointHoverBackgroundColor: '#ec4899',
                pointHoverBorderColor: '#fff',
                pointHoverBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#f1f5f9',
                        font: { size: 12, weight: '600' },
                        padding: 16,
                        usePointStyle: true
                    }
                },
                filler: {
                    propagate: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#cbd5e1',
                        font: { size: 11 },
                        callback: (value) => '₹' + value.toLocaleString()
                    },
                    grid: {
                        color: 'rgba(148, 163, 184, 0.1)',
                        drawBorder: false
                    }
                },
                x: {
                    ticks: {
                        color: '#cbd5e1',
                        font: { size: 11 }
                    },
                    grid: {
                        display: false,
                        drawBorder: false
                    }
                }
            }
        }
    });

    document.getElementById('sales-chart-container').classList.add('loaded');
}

// Category Distribution Pie Chart
function renderCategoryDistributionChart(categoryData) {
    const ctx = document.getElementById('category-distribution-chart');
    if (!ctx) return;

    // Destroy existing chart if it exists
    if (categoryDistributionChart) {
        categoryDistributionChart.destroy();
    }

    const labels = categoryData.map(item => item.category || 'Unknown');
    const values = categoryData.map(item => item.value || 0);
    
    const colors = [
        '#6366f1', '#ec4899', '#10b981', '#f59e0b',
        '#ef4444', '#8b5cf6', '#06b6d4', '#f97316',
        '#14b8a6', '#d946ef'
    ];

    categoryDistributionChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors.slice(0, labels.length),
                borderColor: '#1e293b',
                borderWidth: 2,
                borderSkipped: false,
                hoverBorderColor: '#fff',
                hoverBorderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#f1f5f9',
                        font: { size: 12, weight: '500' },
                        padding: 16,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                }
            }
        }
    });

    document.getElementById('category-chart-container').classList.add('loaded');
}

// Populate category filter
async function populateCategoryFilter() {
    try {
        const filterSelect = document.getElementById('category-filter');
        if (!filterSelect) return; // Element doesn't exist on page
        
        const response = await fetch('/api/categories', {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });

        if (!response.ok) throw new Error('Failed to load categories');
        
        const categories = await response.json();
        
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            filterSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Category filter error:', error);
    }
}

// Apply filters
async function applyFilters() {
    currentFilters.dateRange = document.getElementById('date-range-filter').value;
    currentFilters.category = document.getElementById('category-filter').value;

    try {
        const response = await fetch('/api/analytics/charts?' + new URLSearchParams({
            dateRange: currentFilters.dateRange,
            category: currentFilters.category
        }), {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });

        if (!response.ok) throw new Error('Failed to apply filters');
        
        const data = await response.json();
        renderCharts(data);
        showStatusMessage('Filters applied successfully', 'success');
    } catch (error) {
        console.error('Filter error:', error);
        showStatusMessage('Failed to apply filters', 'error');
    }
}

// Reset filters
function resetFilters() {
    document.getElementById('date-range-filter').value = '7days';
    document.getElementById('category-filter').value = '';
    currentFilters = { dateRange: '7days', category: '' };
    loadChartData();
    showStatusMessage('Filters reset', 'success');
}

// Export to CSV
function exportToCSV() {
    try {
        // Collect data from metrics and lists
        const data = collectDashboardData();
        const csv = convertToCSV(data);
        downloadCSV(csv, 'dashboard-export.csv');
        showStatusMessage('Data exported to CSV successfully', 'success');
    } catch (error) {
        console.error('CSV export error:', error);
        showStatusMessage('Failed to export CSV', 'error');
    }
}

// Export to PDF (requires print styles)
function exportToPDF() {
    try {
        window.print();
        showStatusMessage('Opening print dialog', 'success');
    } catch (error) {
        console.error('PDF export error:', error);
        showStatusMessage('Failed to export PDF', 'error');
    }
}

// Print dashboard
function printDashboard() {
    window.print();
}

// Collect all dashboard data
function collectDashboardData() {
    const data = [];
    
    // Collect metrics
    const metrics = {
        'Total Orders': document.getElementById('metric-orders')?.textContent || '0',
        'Total Revenue': document.getElementById('metric-revenue')?.textContent || '₹0.00',
        'Avg Order Value': document.getElementById('metric-avg')?.textContent || '₹0.00',
        'Conversion Rate': document.getElementById('metric-conversion')?.textContent || '0%',
        'Unique Users': document.getElementById('metric-users')?.textContent || '0',
        'Top Category': document.getElementById('metric-category')?.textContent || '—'
    };
    
    data.push(metrics);
    return data;
}

// Convert data to CSV format
function convertToCSV(data) {
    if (!data || data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csv = [headers.join(',')];
    
    data.forEach(row => {
        const values = headers.map(header => {
            const value = row[header];
            return typeof value === 'string' && value.includes(',') ? `"${value}"` : value;
        });
        csv.push(values.join(','));
    });
    
    return csv.join('\n');
}

// Download CSV file
function downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Show status message
function showStatusMessage(message, type = 'success') {
    const status = document.createElement('div');
    status.className = `export-status ${type === 'error' ? 'error' : ''}`;
    status.textContent = message;
    document.body.appendChild(status);
    
    setTimeout(() => {
        status.style.animation = 'slideInUp 0.4s ease-out reverse';
        setTimeout(() => status.remove(), 400);
    }, 3000);
}

// Show chart placeholder while loading
function showChartPlaceholder() {
    const containers = ['sales-chart-container', 'category-chart-container'];
    containers.forEach(containerId => {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-tertiary);">Unable to load chart data</div>';
        }
    });
}

// Initialize Phase 4 on dashboard load
document.addEventListener('DOMContentLoaded', () => {
    // Only init Phase 4 if we're on the dashboard page
    if (document.getElementById('sales-trend-chart')) {
        // Delay to allow other initializations first
        setTimeout(initPhase4Analytics, 1000);
    }
});
