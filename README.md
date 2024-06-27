# Amazon Reviews Fetcher

This script fetches Amazon reviews for a list of Amazon Standard Identification Numbers (ASINs) using the Oxylabs API and saves them into CSV files. The script is designed to handle large volumes of data and save the results incrementally.

## Features

- Fetches reviews from Amazon for a given list of ASINs.
- Utilizes the Oxylabs API to retrieve review data.
- Saves reviews into CSV files for each ASIN.
- Handles API rate limits by pausing between requests.

## Prerequisites

- Python 3.6+
- An Oxylabs API account
- `.env` file with your Oxylabs API credentials

## Setup

1. Clone the repository:
    ```sh
    git clone https://github.com/your-username/amazon-reviews-fetcher.git
    cd amazon-reviews-fetcher
    ```

2. Install the required packages:
    ```sh
    pip install requests pandas python-dotenv
    ```

3. Create a `.env` file in the project directory with your Oxylabs API credentials:
    ```sh
    touch .env
    ```

    Add the following lines to the `.env` file:
    ```sh
    API_USER=your_oxylabs_username
    API_PW=your_oxylabs_password
    ```

4. Replace the placeholder ASINs in the script with your own list of ASINs if needed.

## Usage

1. Run the script:
    ```sh
    python fetch_reviews.py
    ```

    This will fetch reviews for the specified ASINs and save them into separate CSV files.

## Script Breakdown

### Load API Credentials

The script starts by loading the API credentials from the `.env` file for security purposes.

```python
from dotenv import load_dotenv
load_dotenv()
```

### Fetch Reviews

The `fetch_reviews` function makes a POST request to the Oxylabs API to retrieve reviews for a given ASIN.

```python
def fetch_reviews(payload):
    response = requests.request(
        "POST",
        "https://realtime.oxylabs.io/v1/queries",
        auth=(os.getenv("API_USER"), os.getenv("API_PW")),
        json=payload
    )
    return response.json()["results"]
```

### Save Reviews

The `save_reviews` function fetches and saves reviews for a list of ASINs. It handles pagination and saves reviews in batches to avoid overwhelming the API.

```python
def save_reviews(asins):
    for asin in asins:
        reviews = []
        start_page = 1

        for _ in range(1, 3):
            settings = {
                "source": "amazon_reviews",
                "domain": "co.uk",
                "query": asin,
                "start_page": start_page,
                "pages": 5,
                "parse": True,
            }
            try:
                results = fetch_reviews(settings)
                for result in results:
                    reviews.append(result["content"]["reviews"])
            except Exception as e:
                print(f"An error occurred while fetching reviews for {asin}: {e}")
                continue

            print(f"Pages {start_page} to {start_page + 4} collected successfully.")
            start_page += 5
            time.sleep(1)

        reviews_merged = [item for nestedlist in reviews for item in nestedlist]
        if len(reviews_merged) > 0:
            df = pd.DataFrame(reviews_merged)
            file_mode = "a" if os.path.isfile(f"{asin}_reviews.csv") else "w"
            header = not os.path.isfile(f"{asin}_reviews.csv")
            try:
                df.to_csv(f"{asin}_reviews.csv", mode=file_mode, header=header, index=False, encoding='utf-8-sig')
            except Exception as e:
                print(f"An error occurred while saving reviews for {asin}: {e}")
                continue

            print(f"{len(reviews_merged)} Reviews saved to '{asin}_reviews.csv' successfully.")

    print("All reviews saved successfully.")
```

### Main Execution

The script executes the `save_reviews` function for a predefined list of ASINs when run directly.

```python
if __name__ == '__main__':
    amazon_asins = ["B00TFB0YTM", "B093CTNFG7", "B00XLGV8H4", "B09P46J359",
                    "B07R678B98", "B07L323676", "B009WP0OJ6", "B01NAHWMBI", "B079P64MPB"]

    save_reviews(amazon_asins)
```

## Notes

- Review the Oxylabs API documentation for detailed information on API usage and limits.
