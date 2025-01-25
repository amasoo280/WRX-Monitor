import os
from dotenv import load_dotenv

file_path = os.getenv("FILE_PATH")

def load_sent_listings(file_path):
    """Loads previously sent listings from the file."""
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            listings = set(line.strip() for line in file if line.strip())
            print(f"Loaded sent listings: {listings}")
            return listings
    return set()


def save_sent_listing(file_path, stock_number):
    """Saves a new stock number to the file to prevent duplicate notifications."""
    sent_listings = load_sent_listings(file_path)
    if stock_number in sent_listings:
        print(f"Listing {stock_number} already exists, skipping save.")
        return  # Don't save duplicate entries

    with open(file_path, "a") as file:
        file.write(f"{stock_number}\n")
        print(f"Saved listing: {stock_number}")
