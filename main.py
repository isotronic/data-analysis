import requests
import os
import time
import pprint
import pandas as pd
from dotenv import load_dotenv

# Load API credentials from .env file for security
load_dotenv()


def fetch_reviews(payload):
    """Get amazon reviews from Oxylabs API

    Args:
        payload (dict): The request parameters and authentication for the API call.

    Returns:
        dict: The results from the API call, specifically the reviews.
    """
    # Make a POST request to Oxylabs API with authentication and payload
    response = requests.request(
        "POST",
        "https://realtime.oxylabs.io/v1/queries",
        auth=(os.getenv("API_USER"), os.getenv("API_PW")),
        json=payload
    )
    # Return the 'results' portion of the JSON response
    return response.json()["results"]


def save_reviews(asins):
    """Fetch and save reviews for a list of Amazon Standard Identification Numbers (ASINs).

    Args:
        asins (list): A list of ASINs for which to fetch and save reviews.
    """
    for asin in asins:
        reviews = []
        start_page = 1

        # Iterate twice to fetch reviews from up to 10 pages (2 iterations * 5 pages each)
        for _ in range(1, 3):
            # Configure request payload for the API
            settings = {
                "source": "amazon_reviews",
                "domain": "co.uk",
                "query": asin,
                "start_page": start_page,
                "pages": 5,
                "parse": True,
            }
            try:
                # Fetch reviews and append to the list
                results = fetch_reviews(settings)
                for result in results:
                    reviews.append(result["content"]["reviews"])
            except Exception as e:
                print(f"An error occurred while fetching reviews for {asin}: {e}")
                continue

            print(f"Pages {start_page} to {start_page + 4} collected successfully.")
            start_page += 5

            # Pause to avoid hitting API rate limits
            time.sleep(1)

        # Flatten the list of lists into a single list of reviews
        reviews_merged = [item for nestedlist in reviews for item in nestedlist]
        if len(reviews_merged) > 0:
            # Convert reviews into a DataFrame
            df = pd.DataFrame(reviews_merged)

            # Determine file handling mode (append or write) based on file existence
            file_mode = "a" if os.path.isfile(f"{asin}_reviews.csv") else "w"
            header = not os.path.isfile(f"{asin}_reviews.csv")

            # Save reviews to a CSV file, appending if it already exists
            try:
                df.to_csv(f"{asin}_reviews.csv", mode=file_mode, header=header, index=False, encoding='utf-8-sig')
            except Exception as e:
                print(f"An error occurred while saving reviews for {asin}: {e}")
                continue

            print(f"{len(reviews_merged)} Reviews saved to '{asin}_reviews.csv' successfully.")

    print("All reviews saved successfully.")


if __name__ == '__main__':
    amazon_asins = ["B00TFB0YTM", "B093CTNFG7", "B00XLGV8H4", "B09P46J359",
                    "B07R678B98", "B07L323676", "B009WP0OJ6", "B01NAHWMBI", "B079P64MPB"]

    save_reviews(amazon_asins)
