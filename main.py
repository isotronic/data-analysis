import requests
import os
import time
import pprint
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def fetch_reviews(payload):
    """Get amazon reviews from oxylabs API"""
    response = requests.request(
        "POST",
        "https://realtime.oxylabs.io/v1/queries",
        auth=(os.getenv("API_USER"), os.getenv("API_PW")),
        json=payload
    )
    return response.json()["results"]


if __name__ == '__main__':
    for i in range(1, 2):
        settings = {
            "source": "amazon_reviews",
            "domain": "co.uk",
            "query": "B00TFB0YTM",
            "start_page": i,
            "pages": 5,
            "parse": True,
        }
        results = fetch_reviews(settings)
        reviews = []
        for result in results:
            reviews.append(result["content"]["reviews"])

        pprint.pprint(reviews)

        print(f"Page {i} saved to file successfully.")

        time.sleep(1)
