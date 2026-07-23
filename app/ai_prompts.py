"""
Prompt Templates for AI Generation
Separated from logic for easy maintenance
"""

INSIGHTS_PROMPT = """You are a business analyst analyzing e-commerce data. Provide 3-5 key insights about business performance.

DATA:
- Total Orders: {total_orders}
- Total Revenue: ₹{total_revenue}
- Average Order Value: ₹{avg_order_value}
- Conversion Rate: {conversion_rate}%
- Unique Users: {unique_users}
- Top Category: {top_category}

Categories Performance:
{categories}

Respond ONLY in valid JSON (no markdown, no extra text):
{{
  "insights": [
    {{"title": "Insight Title", "description": "Detailed insight...", "severity": "high"}},
    {{"title": "Another Insight", "description": "Description...", "severity": "medium"}},
    {{"title": "Third Insight", "description": "Description...", "severity": "low"}}
  ],
  "summary": "Overall business summary..."
}}"""

RECOMMENDATIONS_PROMPT = """You are a business strategist. Based on e-commerce metrics, provide 5 strategic recommendations.

PERFORMANCE DATA:
- Total Orders: {total_orders}
- Total Revenue: ₹{total_revenue}
- Conversion Rate: {conversion_rate}%
- Low Performing Products: {low_products}

Respond ONLY in valid JSON (no markdown, no extra text):
{{
  "recommendations": [
    {{"action": "Recommendation 1", "priority": "high", "impact": "Increase revenue"}},
    {{"action": "Recommendation 2", "priority": "medium", "impact": "Improve user engagement"}},
    {{"action": "Recommendation 3", "priority": "high", "impact": "Reduce cart abandonment"}}
  ]
}}"""
