import json
import os
import random
from datetime import datetime

from app.config import LOG_DIRECTORY

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


def create_log_files():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    return {
        "view": os.path.join(
            LOG_DIRECTORY,
            f"clicks_{timestamp}.json"
        ),
        "cart": os.path.join(
            LOG_DIRECTORY,
            f"carts_{timestamp}.json"
        ),
        "purchase": os.path.join(
            LOG_DIRECTORY,
            f"orders_{timestamp}.json"
        )
    }


def generate_events(count: int):
    """
    Generate fake e-commerce events and separate them
    into clicks, carts, and orders files.

    Returns the generated file paths.
    """

    log_files = create_log_files()

    generated_files = set()

    for i in range(count):

        product = random.choice(products)
        event_type = random.choice(events)

        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": random.randint(1000, 9999),
            "product_id": product["id"],
            "category": product["category"],
            "event": event_type,
            "price": round(random.uniform(20, 1000), 2)
        }

        file_path = log_files[event_type]

        with open(file_path, "a") as file:
            file.write(json.dumps(event) + "\n")

        generated_files.add(file_path)

        print(f"Generated Event {i + 1}: {event_type}")

    return list(generated_files)