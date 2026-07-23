from app.athena import execute_query
from app.logger import logger


# ============================================================================
# SUMMARY ANALYTICS
# ============================================================================

def get_summary() -> dict:
    """
    Get order summary: total orders, revenue, and average order value.

    Returns:
        Dictionary with summary metrics or empty dict if query fails
    """

    query = """
    SELECT
        COUNT(*) AS total_orders,
        ROUND(SUM(price), 2) AS total_revenue,
        ROUND(AVG(price), 2) AS average_order_value
    FROM orders
    WHERE event = 'PURCHASE'
    """

    try:
        result = execute_query(query)
    except Exception as e:
        logger.error(f"Failed to get summary: {e}")
        return {}

    if not result or len(result) == 0:
        logger.warning("Summary query returned no results")
        return {}

    try:
        summary = result[0]

        return {
            "total_orders": int(summary.get("total_orders", 0)),
            "total_revenue": float(summary.get("total_revenue", 0.0)),
            "average_order_value": float(summary.get("average_order_value", 0.0)),
        }

    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"Failed to parse summary result: {e}")
        return {}


# ============================================================================
# CATEGORY ANALYTICS
# ============================================================================

def get_category_sales() -> list:
    """
    Get sales breakdown by product category.

    Returns:
        List of dictionaries with category sales data
    """

    query = """
    SELECT
        category,
        COUNT(*) AS total_orders,
        ROUND(SUM(price), 2) AS revenue
    FROM orders
    WHERE event = 'PURCHASE'
    GROUP BY category
    ORDER BY revenue DESC
    """

    try:
        result = execute_query(query)
    except Exception as e:
        logger.error(f"Failed to get category sales: {e}")
        return []

    if not result:
        logger.warning("Category sales query returned no results")
        return []

    try:
        formatted_result = []

        for row in result:
            formatted_result.append(
                {
                    "category": row.get("category", "Unknown"),
                    "total_orders": int(row.get("total_orders", 0)),
                    "revenue": float(row.get("revenue", 0.0)),
                }
            )

        logger.info(f"Retrieved category sales for {len(formatted_result)} categories")

        return formatted_result

    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"Failed to parse category sales result: {e}")
        return []


# ============================================================================
# TIME-BASED ANALYTICS
# ============================================================================

def get_hourly_sales() -> list:
    """
    Get sales breakdown by hour of day.

    Returns:
        List of dictionaries with hourly sales data
    """

    query = """
    SELECT
        hour(from_iso8601_timestamp(timestamp)) AS hour,
        COUNT(*) AS total_orders,
        ROUND(SUM(price), 2) AS revenue
    FROM orders
    WHERE event = 'PURCHASE'
    GROUP BY hour(from_iso8601_timestamp(timestamp))
    ORDER BY hour
    """

    try:
        result = execute_query(query)
    except Exception as e:
        logger.error(f"Failed to get hourly sales: {e}")
        return []

    if not result:
        logger.warning("Hourly sales query returned no results")
        return []

    try:
        formatted_result = []

        for row in result:
            formatted_result.append(
                {
                    "hour": int(row.get("hour", 0)),
                    "total_orders": int(row.get("total_orders", 0)),
                    "revenue": float(row.get("revenue", 0.0)),
                }
            )

        logger.info(f"Retrieved hourly sales for {len(formatted_result)} hours")

        return formatted_result

    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"Failed to parse hourly sales result: {e}")
        return []


# ============================================================================
# PRODUCT ANALYTICS
# ============================================================================

def get_top_products(limit: int = 10) -> list:
    """
    Get top selling products by order count.

    Args:
        limit: Maximum number of products to return

    Returns:
        List of dictionaries with top product data
    """

    query = f"""
    SELECT
        product_id,
        product_name,
        category,
        COUNT(*) AS total_orders,
        ROUND(SUM(price), 2) AS total_revenue,
        ROUND(AVG(price), 2) AS avg_price
    FROM orders
    WHERE event = 'PURCHASE'
    GROUP BY product_id, product_name, category
    ORDER BY total_orders DESC
    LIMIT {limit}
    """

    try:
        result = execute_query(query)
    except Exception as e:
        logger.error(f"Failed to get top products: {e}")
        return []

    if not result:
        logger.warning("Top products query returned no results")
        return []

    try:
        formatted_result = []

        for row in result:
            formatted_result.append(
                {
                    "product_id": int(row.get("product_id", 0)),
                    "product_name": row.get("product_name", "Unknown"),
                    "category": row.get("category", "Unknown"),
                    "total_orders": int(row.get("total_orders", 0)),
                    "total_revenue": float(row.get("total_revenue", 0.0)),
                    "avg_price": float(row.get("avg_price", 0.0)),
                }
            )

        logger.info(f"Retrieved top {len(formatted_result)} products")

        return formatted_result

    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"Failed to parse top products result: {e}")
        return []


# ============================================================================
# USER BEHAVIOR ANALYTICS
# ============================================================================

def get_conversion_funnel() -> dict:
    """
    Get conversion funnel: views -> cart -> purchases.
    Combines data from clicks, carts, and orders tables.

    Returns:
        Dictionary with funnel metrics and conversion rates
    """

    query = """
    SELECT
        'VIEW' AS event,
        COUNT(*) AS count
    FROM clicks
    
    UNION ALL
    
    SELECT
        'CART' AS event,
        COUNT(*) AS count
    FROM carts
    
    UNION ALL
    
    SELECT
        'PURCHASE' AS event,
        COUNT(*) AS count
    FROM orders
    """

    try:
        result = execute_query(query)
    except Exception as e:
        logger.error(f"Failed to get conversion funnel: {e}")
        return {}

    if not result:
        logger.warning("Conversion funnel query returned no results")
        return {}

    try:
        funnel = {"view": 0, "cart": 0, "purchase": 0}

        for row in result:
            event = row.get("event", "").upper()
            count = int(row.get("count", 0))

            if event == "VIEW":
                funnel["view"] = count
            elif event == "CART":
                funnel["cart"] = count
            elif event == "PURCHASE":
                funnel["purchase"] = count

        total_views = funnel["view"]

        view_to_cart_rate = (
            (funnel["cart"] / total_views * 100) if total_views > 0 else 0
        )
        cart_to_purchase_rate = (
            (funnel["purchase"] / funnel["cart"] * 100)
            if funnel["cart"] > 0
            else 0
        )
        overall_conversion_rate = (
            (funnel["purchase"] / total_views * 100) if total_views > 0 else 0
        )

        logger.info("Conversion funnel retrieved successfully")

        return {
            "views": funnel["view"],
            "cart_additions": funnel["cart"],
            "purchases": funnel["purchase"],
            "view_to_cart_rate": round(view_to_cart_rate, 2),
            "cart_to_purchase_rate": round(cart_to_purchase_rate, 2),
            "overall_conversion_rate": round(overall_conversion_rate, 2),
        }

    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"Failed to parse conversion funnel result: {e}")
        return {}


def get_user_insights() -> dict:
    """
    Get user engagement metrics: unique users, avg orders per user, etc.

    Returns:
        Dictionary with user insights
    """

    query = """
    SELECT
        COUNT(DISTINCT user_id) AS unique_users,
        COUNT(*) AS total_events,
        ROUND(COUNT(*) / COUNT(DISTINCT user_id), 2) AS avg_events_per_user
    FROM orders
    """

    try:
        result = execute_query(query)
    except Exception as e:
        logger.error(f"Failed to get user insights: {e}")
        return {}

    if not result or len(result) == 0:
        logger.warning("User insights query returned no results")
        return {}

    try:
        data = result[0]

        logger.info("User insights retrieved successfully")

        return {
            "unique_users": int(data.get("unique_users", 0)),
            "total_events": int(data.get("total_events", 0)),
            "avg_events_per_user": float(data.get("avg_events_per_user", 0.0)),
        }

    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"Failed to parse user insights result: {e}")
        return {}


# ============================================================================
# PRICE ANALYTICS
# ============================================================================

def get_price_distribution() -> dict:
    """
    Get price range distribution for purchases.

    Returns:
        Dictionary with price bucket distributions
    """

    query = """
    SELECT
        CASE
            WHEN price < 50 THEN 'Under ₹50'
            WHEN price >= 50 AND price < 100 THEN '₹50-₹100'
            WHEN price >= 100 AND price < 200 THEN '₹100-₹200'
            WHEN price >= 200 AND price < 500 THEN '₹200-₹500'
            WHEN price >= 500 THEN 'Over ₹500'
            ELSE 'Unknown'
        END AS price_range,
        COUNT(*) AS count,
        ROUND(SUM(price), 2) AS total_revenue
    FROM orders
    WHERE UPPER(event) = 'PURCHASE'
    GROUP BY 1
    """

    try:
        result = execute_query(query)
    except Exception as e:
        logger.error(f"Failed to get price distribution: {e}")
        return {}

    if not result:
        logger.warning("Price distribution query returned no results")
        return {}

    try:
        distribution = {}

        for row in result:
            price_range = row.get("price_range", "Unknown")
            distribution[price_range] = {
                "count": int(row.get("count", 0)),
                "revenue": float(row.get("total_revenue", 0.0)),
            }

        logger.info("Price distribution retrieved successfully")

        return distribution

    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"Failed to parse price distribution result: {e}")
        return {}


# ============================================================================
# PERFORMANCE METRICS
# ============================================================================

def get_revenue_metrics() -> dict:
    """
    Get detailed revenue metrics including min, max, median prices.

    Returns:
        Dictionary with revenue statistics
    """

    query = """
    SELECT
        ROUND(SUM(price), 2) AS total_revenue,
        ROUND(AVG(price), 2) AS avg_price,
        ROUND(MIN(price), 2) AS min_price,
        ROUND(MAX(price), 2) AS max_price,
        COUNT(*) AS total_purchases
    FROM orders
    WHERE event = 'PURCHASE'
    """

    try:
        result = execute_query(query)
    except Exception as e:
        logger.error(f"Failed to get revenue metrics: {e}")
        return {}

    if not result or len(result) == 0:
        logger.warning("Revenue metrics query returned no results")
        return {}

    try:
        data = result[0]

        logger.info("Revenue metrics retrieved successfully")

        return {
            "total_revenue": float(data.get("total_revenue", 0.0)),
            "avg_price": float(data.get("avg_price", 0.0)),
            "min_price": float(data.get("min_price", 0.0)),
            "max_price": float(data.get("max_price", 0.0)),
            "total_purchases": int(data.get("total_purchases", 0)),
        }

    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"Failed to parse revenue metrics result: {e}")
        return {}


# ============================================================================
# TRENDING ANALYTICS
# ============================================================================

def get_trending_categories(limit: int = 5) -> list:
    """
    Get fastest growing categories by recent sales.

    Args:
        limit: Maximum number of categories to return

    Returns:
        List of trending category data
    """

    query = f"""
    SELECT
        category,
        COUNT(*) AS recent_orders,
        ROUND(SUM(price), 2) AS recent_revenue
    FROM orders
    WHERE event = 'PURCHASE'
    GROUP BY category
    ORDER BY recent_orders DESC
    LIMIT {limit}
    """

    try:
        result = execute_query(query)
    except Exception as e:
        logger.error(f"Failed to get trending categories: {e}")
        return []

    if not result:
        logger.warning("Trending categories query returned no results")
        return []

    try:
        trending = []

        for row in result:
            trending.append(
                {
                    "category": row.get("category", "Unknown"),
                    "recent_orders": int(row.get("recent_orders", 0)),
                    "recent_revenue": float(row.get("recent_revenue", 0.0)),
                }
            )

        logger.info(f"Retrieved {len(trending)} trending categories")

        return trending

    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"Failed to parse trending categories result: {e}")
        return []


def get_low_performing_products(limit: int = 10) -> list:
    """
    Get products with lowest sales for optimization/removal consideration.

    Args:
        limit: Maximum number of products to return

    Returns:
        List of low performing product data
    """

    query = f"""
    SELECT
        product_id,
        product_name,
        category,
        COUNT(*) AS total_orders,
        ROUND(SUM(price), 2) AS total_revenue
    FROM orders
    WHERE event = 'PURCHASE'
    GROUP BY product_id, product_name, category
    ORDER BY total_orders ASC
    LIMIT {limit}
    """

    try:
        result = execute_query(query)
    except Exception as e:
        logger.error(f"Failed to get low performing products: {e}")
        return []

    if not result:
        logger.warning("Low performing products query returned no results")
        return []

    try:
        low_performers = []

        for row in result:
            low_performers.append(
                {
                    "product_id": int(row.get("product_id", 0)),
                    "product_name": row.get("product_name", "Unknown"),
                    "category": row.get("category", "Unknown"),
                    "total_orders": int(row.get("total_orders", 0)),
                    "total_revenue": float(row.get("total_revenue", 0.0)),
                }
            )

        logger.info(f"Retrieved {len(low_performers)} low performing products")

        return low_performers

    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"Failed to parse low performing products result: {e}")
        return []
