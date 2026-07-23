import json
import os
import random
from datetime import datetime

from app.config import LOG_DIRECTORY
from app.logger import logger


# ============================================================================
# INITIALIZATION
# ============================================================================

os.makedirs(LOG_DIRECTORY, exist_ok=True)


# ============================================================================
# PRODUCT CATALOG
# ============================================================================

PRODUCTS_CATALOG = {
    "Electronics": [
        {"id": 101, "name": "MacBook Pro 14\"", "price_range": (1200, 2500)},
        {"id": 102, "name": "iPhone 15 Pro", "price_range": (800, 1200)},
        {"id": 103, "name": "iPad Air", "price_range": (600, 1000)},
        {"id": 104, "name": "Apple Watch Ultra", "price_range": (400, 800)},
        {"id": 105, "name": "Sony WH-1000XM5 Headphones", "price_range": (300, 400)},
        {"id": 106, "name": "Samsung 65\" 4K TV", "price_range": (800, 1500)},
        {"id": 107, "name": "Dell XPS 13 Laptop", "price_range": (1000, 1800)},
        {"id": 108, "name": "Google Pixel 8 Pro", "price_range": (700, 1100)},
    ],
    "Books": [
        {"id": 201, "name": "The Pragmatic Programmer", "price_range": (30, 50)},
        {"id": 202, "name": "Clean Code", "price_range": (40, 60)},
        {"id": 203, "name": "Design Patterns", "price_range": (45, 65)},
        {"id": 204, "name": "Python Crash Course", "price_range": (25, 40)},
        {"id": 205, "name": "The Art of Computer Programming", "price_range": (80, 150)},
        {"id": 206, "name": "Web Development with Django", "price_range": (35, 55)},
        {"id": 207, "name": "Atomic Habits", "price_range": (15, 25)},
        {"id": 208, "name": "The Lean Startup", "price_range": (20, 30)},
    ],
    "Shoes": [
        {"id": 301, "name": "Nike Air Max 90", "price_range": (80, 150)},
        {"id": 302, "name": "Adidas Ultraboost 22", "price_range": (100, 200)},
        {"id": 303, "name": "New Balance 990v6", "price_range": (150, 250)},
        {"id": 304, "name": "Puma RS-X", "price_range": (70, 130)},
        {"id": 305, "name": "ASICS Gel-Lyte III", "price_range": (80, 140)},
        {"id": 306, "name": "Converse Chuck Taylor", "price_range": (40, 80)},
        {"id": 307, "name": "Jordan Air Jordan 1", "price_range": (150, 300)},
        {"id": 308, "name": "Vans Old Skool", "price_range": (50, 100)},
    ],
    "Clothing": [
        {"id": 401, "name": "Supreme Box Logo T-Shirt", "price_range": (60, 150)},
        {"id": 402, "name": "The North Face Puffer Jacket", "price_range": (200, 400)},
        {"id": 403, "name": "Levi's 501 Jeans", "price_range": (50, 120)},
        {"id": 404, "name": "Ralph Lauren Polo Shirt", "price_range": (70, 150)},
        {"id": 405, "name": "Carhartt WIP Beanie", "price_range": (25, 50)},
        {"id": 406, "name": "Nike Dri-FIT Hoodie", "price_range": (60, 100)},
        {"id": 407, "name": "Stüssy Bucket Hat", "price_range": (40, 80)},
        {"id": 408, "name": "Champion Reverse Weave Hoodie", "price_range": (70, 120)},
    ],
    "Sports": [
        {"id": 501, "name": "Dumbbells Set 20kg", "price_range": (80, 150)},
        {"id": 502, "name": "Yoga Mat Premium", "price_range": (30, 80)},
        {"id": 503, "name": "Resistance Bands Set", "price_range": (20, 50)},
        {"id": 504, "name": "Treadmill Pro 3000", "price_range": (600, 1200)},
        {"id": 505, "name": "Exercise Bike", "price_range": (300, 800)},
        {"id": 506, "name": "Jump Rope Adjustable", "price_range": (15, 40)},
        {"id": 507, "name": "Pull-up Bar", "price_range": (25, 60)},
        {"id": 508, "name": "Kettlebell 16kg", "price_range": (40, 80)},
    ],
}


EVENT_TYPES = [
    "view",
    "cart",
    "purchase",
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_log_files() -> dict:
    """Create timestamped log file paths for each event type"""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    return {
        "view": os.path.join(LOG_DIRECTORY, f"clicks_{timestamp}.json"),
        "cart": os.path.join(LOG_DIRECTORY, f"carts_{timestamp}.json"),
        "purchase": os.path.join(LOG_DIRECTORY, f"orders_{timestamp}.json"),
    }


def get_random_product() -> dict:
    """Get a random product from the catalog"""

    category = random.choice(list(PRODUCTS_CATALOG.keys()))
    product = random.choice(PRODUCTS_CATALOG[category])

    return {
        "product_id": product["id"],
        "product_name": product["name"],
        "category": category,
        "price": round(random.uniform(*product["price_range"]), 2),
    }


# ============================================================================
# EVENT GENERATION
# ============================================================================

def generate_events(count: int) -> list:
    """
    Generate fake e-commerce events with realistic products and separate them
    into clicks, carts, and orders files.

    Args:
        count: Number of events to generate

    Returns:
        List of generated file paths
    """

    log_files = create_log_files()
    generated_files = set()

    for i in range(count):
        event_type = random.choice(EVENT_TYPES)
        product = get_random_product()

        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": random.randint(1000, 9999),
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "category": product["category"],
            "event": event_type,
            "price": product["price"],
        }

        file_path = log_files[event_type]

        with open(file_path, "a") as file:
            file.write(json.dumps(event) + "\n")

        generated_files.add(file_path)

        logger.info(
            f"Generated Event {i + 1}/{count}: {event_type} - {product['product_name']} (${product['price']})"
        )

    logger.info(f"Total events generated: {count}")

    return list(generated_files)
