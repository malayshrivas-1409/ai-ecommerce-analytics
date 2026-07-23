/**
 * AI Insights Module
 * Handles AI insights and recommendations loading and display
 * Completely isolated from existing dashboard.js
 */

let aiAccessToken = null;
let aiInsightsLoaded = false;

/**
 * Initialize AI Insights on dashboard load
 */
function initializeAIInsights() {
    aiAccessToken = localStorage.getItem("accessToken");
    if (aiAccessToken) {
        loadAIInsights();
    }
}

/**
 * Load AI Insights from backend
 */
async function loadAIInsights() {
    const container = document.getElementById("ai-insights-content");
    const section = document.getElementById("ai-insights-section");
    
    if (!section || aiInsightsLoaded) return;
    
    try {
        // Show loading state
        container.innerHTML = `
            <div class="ai-loading">
                <div class="spinner"></div>
                <p>Generating AI insights...</p>
            </div>
        `;
        
        const response = await fetch("/ai/insights", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${aiAccessToken}`,
                "Content-Type": "application/json"
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            displayAIInsights(data);
            aiInsightsLoaded = true;
        } else if (response.status === 429) {
            container.innerHTML = `
                <div class="ai-message ai-warning">
                    ⏱️ Rate limit reached. Try again in a few minutes.
                </div>
            `;
        } else {
            throw new Error(`API returned ${response.status}`);
        }
    } catch (error) {
        console.error("AI insights error:", error);
        container.innerHTML = `
            <div class="ai-message ai-error">
                ⚠️ Unable to load insights. Please try again later.
            </div>
        `;
    }
}

/**
 * Display AI Insights on dashboard
 */
function displayAIInsights(data) {
    const container = document.getElementById("ai-insights-content");
    
    if (data.status !== "success" || !data.data) {
        container.innerHTML = `
            <div class="ai-message ai-error">
                Unable to generate insights at this time.
            </div>
        `;
        return;
    }
    
    const insights = data.data.insights || [];
    const summary = data.data.summary || "";
    const cached = data.data.cached || false;
    
    if (insights.length === 0) {
        container.innerHTML = `
            <div class="ai-message ai-info">
                📊 No insights available yet. Check back after data is processed.
            </div>
        `;
        return;
    }
    
    // Build insights HTML
    let html = `<div class="insights-list">`;
    
    // Add cache badge if cached
    if (cached) {
        html += `<div class="cache-badge">📌 Cached Result (24h)</div>`;
    }
    
    // Add insights
    insights.forEach((insight, index) => {
        const severityClass = `severity-${insight.severity || "medium"}`;
        const severityEmoji = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }[insight.severity] || "🔵";
        
        html += `
            <div class="insight-card">
                <div class="insight-header">
                    <h3>${escapeHtml(insight.title)}</h3>
                    <span class="severity-badge ${severityClass}">
                        ${severityEmoji} ${insight.severity || "info"}
                    </span>
                </div>
                <p class="insight-description">${escapeHtml(insight.description)}</p>
            </div>
        `;
    });
    
    // Add summary if available
    if (summary) {
        html += `
            <div class="insight-summary">
                <h4>📋 Summary</h4>
                <p>${escapeHtml(summary)}</p>
            </div>
        `;
    }
    
    html += `</div>`;
    
    container.innerHTML = html;
}

/**
 * Load AI Recommendations
 */
async function loadAIRecommendations() {
    const container = document.getElementById("ai-recommendations-content");
    
    if (!container) return;
    
    try {
        // Show loading state
        container.innerHTML = `
            <div class="ai-loading">
                <div class="spinner"></div>
                <p>Generating recommendations...</p>
            </div>
        `;
        
        const response = await fetch("/ai/recommendations", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${aiAccessToken}`,
                "Content-Type": "application/json"
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            displayAIRecommendations(data);
        } else if (response.status === 429) {
            container.innerHTML = `
                <div class="ai-message ai-warning">
                    ⏱️ Rate limit reached. Try again in a few minutes.
                </div>
            `;
        } else {
            throw new Error(`API returned ${response.status}`);
        }
    } catch (error) {
        console.error("AI recommendations error:", error);
        container.innerHTML = `
            <div class="ai-message ai-error">
                ⚠️ Unable to load recommendations. Please try again later.
            </div>
        `;
    }
}

/**
 * Display AI Recommendations
 */
function displayAIRecommendations(data) {
    const container = document.getElementById("ai-recommendations-content");
    
    if (data.status !== "success" || !data.data) {
        container.innerHTML = `
            <div class="ai-message ai-error">
                Unable to generate recommendations at this time.
            </div>
        `;
        return;
    }
    
    const recommendations = data.data.recommendations || [];
    
    if (recommendations.length === 0) {
        container.innerHTML = `
            <div class="ai-message ai-info">
                No recommendations available yet.
            </div>
        `;
        return;
    }
    
    // Build recommendations HTML
    let html = `<div class="recommendations-list">`;
    
    recommendations.forEach((rec, index) => {
        const priorityClass = `priority-${rec.priority || "medium"}`;
        const priorityEmoji = {
            "high": "🔥",
            "medium": "⚡",
            "low": "💡"
        }[rec.priority] || "✨";
        
        html += `
            <div class="recommendation-card">
                <div class="recommendation-header">
                    <h4>${escapeHtml(rec.action)}</h4>
                    <span class="priority-badge ${priorityClass}">
                        ${priorityEmoji} ${rec.priority || "info"}
                    </span>
                </div>
                <p class="recommendation-impact">
                    💼 Expected Impact: ${escapeHtml(rec.impact || "TBD")}
                </p>
            </div>
        `;
    });
    
    html += `</div>`;
    
    container.innerHTML = html;
}

/**
 * Refresh AI Insights
 */
function refreshAIInsights() {
    aiInsightsLoaded = false;
    const container = document.getElementById("ai-insights-content");
    if (container) {
        container.innerHTML = `
            <div class="ai-loading">
                <div class="spinner"></div>
                <p>Refreshing insights...</p>
            </div>
        `;
    }
    loadAIInsights();
}

/**
 * Refresh AI Recommendations
 */
function refreshAIRecommendations() {
    loadAIRecommendations();
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
