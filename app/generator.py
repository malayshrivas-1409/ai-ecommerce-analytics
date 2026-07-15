import json
import os
import random
import time

from datetime import datetime

from config import (
    LOG_DIRECTORY,
    MAX_EVENTS_PER_FILE
)

from uploader import upload_file


os.makedirs(LOG_DIRECTORY, exist_ok=True)

products = [
    {"id": 101, "category": "Electronics"},
    {"id": 102, "category": "Books"},
    {"id": 103, "category": "Shoes"},
    {"id": 104, "category": "Clothing"},
    {"id": 105, "category": "Sports"}
]

events = [
    "view",
    "cart",
    "purchase"
]


event_count = 0


def create_log_file():

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"orders_{timestamp}.json"

    path = os.path.join(LOG_DIRECTORY, filename)

    return path


current_log = create_log_file()

print(f"Writing to {current_log}")

while True:

    product = random.choice(products)

    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": random.randint(1000, 9999),
        "product_id": product["id"],
        "category": product["category"],
        "event": random.choice(events),
        "price": round(random.uniform(20, 1000), 2)
    }

    with open(current_log, "a") as file:

        file.write(json.dumps(record) + "\n")

    event_count += 1

    print(f"Generated Event {event_count}")

    if event_count >= MAX_EVENTS_PER_FILE:

        print("\nUploading Batch...\n")

        success = upload_file(current_log)

        if success:

            os.remove(current_log)

            current_log = create_log_file()

            event_count = 0

            print("New Batch Started\n")

    time.sleep(2)