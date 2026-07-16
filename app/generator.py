import json
import os
import random

from datetime import datetime

from app.config import LOG_DIRECTORY
from app.uploader import upload_file

os.makedirs(LOG_DIRECTORY, exist_ok=True)

products = [
    {"id":101,"category":"Electronics"},
    {"id":102,"category":"Books"},
    {"id":103,"category":"Shoes"},
    {"id":104,"category":"Clothing"},
    {"id":105,"category":"Sports"}
]

events = [
    "view",
    "cart",
    "purchase"
]


def create_log_file():

    filename = datetime.now().strftime(
        "orders_%Y%m%d_%H%M%S.json"
    )

    return os.path.join(LOG_DIRECTORY, filename)


def generate_events(count):

    logfile = create_log_file()

    for i in range(count):

        product = random.choice(products)

        event = {

            "timestamp": datetime.utcnow().isoformat(),

            "user_id": random.randint(1000,9999),

            "product_id": product["id"],

            "category": product["category"],

            "event": random.choice(events),

            "price": round(random.uniform(20,1000),2)

        }

        with open(logfile,"a") as file:

            file.write(json.dumps(event)+"\n")

    print("Uploading batch...")

    success = upload_file(logfile)

    if success:

        os.remove(logfile)

    return success