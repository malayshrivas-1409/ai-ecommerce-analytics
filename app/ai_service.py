"""
AI Insight Service - Core business logic
Completely independent from analytics
"""

import json
from app.groq_client import GroqClient
from app.ai_cache import insights_cache
from app.ai_prompts import INSIGHTS_PROMPT, RECOMMENDATIONS_PROMPT
from app.logger import logger


class AIService:
    def __init__(self):
        try:
            self.groq = GroqClient()
            logger.info("AIService initialized with GROQ client")
        except Exception as e:
            logger.error(f"Failed to initialize GROQ client: {e}")
            raise
    
    def generate_insights(self, analytics_data: dict) -> dict:
        """
        Generate insights from analytics data
        Uses cache to avoid redundant API calls
        """
        try:
            # Create cache key from data
            cache_key = insights_cache.get_key(analytics_data)
            
            # Check cache first
            if cache_key:
                cached = insights_cache.get(cache_key)
                if cached:
                    logger.info("Returning cached insights")
                    return {"cached": True, **cached}
            
            # Build prompt
            prompt = INSIGHTS_PROMPT.format(
                total_orders=analytics_data.get('total_orders', 0),
                total_revenue=round(analytics_data.get('total_revenue', 0), 2),
                avg_order_value=round(analytics_data.get('avg_order_value', 0), 2),
                conversion_rate=round(analytics_data.get('conversion_rate', 0), 2),
                unique_users=analytics_data.get('unique_users', 0),
                top_category=analytics_data.get('top_category', 'N/A'),
                categories=json.dumps(analytics_data.get('categories', []), indent=2)
            )
            
            # Call GROQ
            logger.info("Calling GROQ API for insights generation")
            response = self.groq.invoke(prompt, max_tokens=800)
            
            # Parse response
            insights = json.loads(response)
            
            # Cache result
            if cache_key:
                insights_cache.set(cache_key, insights)
            
            logger.info(f"Generated {len(insights.get('insights', []))} insights")
            return {"cached": False, **insights}
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GROQ response as JSON: {e}")
            return {"error": "Invalid response format", "insights": []}
        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            return {"error": str(e), "insights": []}
    
    def generate_recommendations(self, analytics_data: dict) -> dict:
        """Generate recommendations from analytics data"""
        try:
            # Build prompt
            prompt = RECOMMENDATIONS_PROMPT.format(
                total_orders=analytics_data.get('total_orders', 0),
                total_revenue=round(analytics_data.get('total_revenue', 0), 2),
                conversion_rate=round(analytics_data.get('conversion_rate', 0), 2),
                low_products=json.dumps(analytics_data.get('low_products', []), indent=2)
            )
            
            # Call GROQ
            logger.info("Calling GROQ API for recommendations")
            response = self.groq.invoke(prompt, max_tokens=800)
            
            # Parse response
            recommendations = json.loads(response)
            
            logger.info(f"Generated {len(recommendations.get('recommendations', []))} recommendations")
            return recommendations
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse recommendations response: {e}")
            return {"error": "Invalid response format", "recommendations": []}
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return {"error": str(e), "recommendations": []}


# Create singleton instance
ai_service = AIService()
