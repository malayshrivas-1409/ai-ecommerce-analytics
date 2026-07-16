import json
import os
import random
from datetime import datetime

from app.config import LOG_DIRECTORY

# Ensure logs directory exists
os.makedirs(LOG_DIRECTORY, exist_ok=True)

products = [
    {"id": 101, "category": "Electronics"},
    {"id": 102, "category": "Books"},
    {"id": 103, "category": "Shoes"},
    {"id": 104, "category": "Clothing"},
    {"id": 105, "category": "Sports"},
]

events = [
    "view",
    "cart",
    "purchase"
]


def create_log_file():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"orders_{timestamp}.json"
    return os.path.join(LOG_DIRECTORY, filename)


def generate_events(count: int):
    """
    Generate fake e-commerce events.
    Returns the generated log file path.
    """

    log_file = create_log_file()

    with open(log_file, "a") as file:

        for i in range(count):

            product = random.choice(products)

            event = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": random.randint(1000, 9999),
                "product_id": product["id"],
                "category": product["category"],
                "event": random.choice(events),
                "price": round(random.uniform(20, 1000), 2)
            }

            file.write(json.dumps(event) + "\n")

            print(f"Generated Event {i+1}")

    return log_file