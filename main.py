import requests
import os
from dotenv import load_dotenv
from listing_storage import load_sent_listings, save_sent_listing


class CarScraper:
    def __init__(self):
        load_dotenv()
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        if not self.discord_webhook_url:
            raise ValueError("No DISCORD_WEBHOOK_URL found in environment variables")
        
        self.carmax_uri = os.getenv("CARMAX_URI")
        self.zipcode = os.getenv("ZIPCODE")
        self.visitor_ID = os.getenv("VISITOR_ID")
        self.url = "https://www.carmax.com/cars/api/search/run"
        self.params = {
            "uri": self.carmax_uri,
            "skip": "0",
            "take": "0",
            "zipCode": self.zipcode,
            "shipping": "-1",
            "sort": "price-asc",
            "yearRange": "2018-2025",
            "visitorID": self.visitor_ID
        }
        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "referer": "https://www.carmax.com/cars/subaru/wrx",
            "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": os.getenv("USER_AGENT")
        }
        self.sent_listings_file = "sent_listings.txt"

    def fetch_car_listings(self):
        response = requests.get(self.url, headers=self.headers, params=self.params)
        if response.status_code == 200:
            return response.json().get('items', [])
        else:
            response.raise_for_status()

    def send_to_discord(self, car):
        image_url = car.get('imageUrl', 'https://www.carmax.com/favicon.ico')
        embed = {
            "embeds": [
                {
                    "title": f"🚗 New {os.getenv('VEHICLE')} Listing!",
                    "description": f"**Stock Number:** {car.get('stockNumber')}\n"
                                   f"**Year:** {car.get('year')}\n"
                                   f"**Make:** {car.get('make')}\n"
                                   f"**Model:** {car.get('model')}\n"
                                   f"**Price:** ${car.get('basePrice')}\n"
                                   f"**Mileage:** {car.get('mileage')} miles\n"
                                   f"**Store:** {car.get('storeName')} ({car.get('storeCity')}, {car.get('state')})\n",
                    "url": f"https://www.carmax.com/car/{car.get('stockNumber')}",
                    "color": 0x00ADEF,  # CarMax blue color
                    "thumbnail": {
                        "url": car.get('imageUrl', 'https://www.carmax.com/favicon.ico')
                    },
                    "image": {
                        "url": image_url  # Full-size image below the embed description
                    },
                    "footer": {
                        "text": "Listing provided by CarMax API",
                        "icon_url": "https://www.carmax.com/favicon.ico"
                    }
                }
            ]
        }
        response = requests.post(self.discord_webhook_url, json=embed)
        if response.status_code == 204:
            print(f"Listing Sent to Webhook: {car.get('stockNumber')}")
        else:
            print(f"Failed to send webhook: {response.status_code}")


    def format_car_details(self, car):
        vehicle = os.getenv("VEHICLE")
        return (f"New {vehicle} Listing:\n"
                f"Stock Number: {car.get('stockNumber')}\n"
                f"Year: {car.get('year')}\n"
                f"Make: {car.get('make')}\n"
                f"Model: {car.get('model')}\n"
                f"Price: ${car.get('basePrice')}\n"
                f"Mileage: {car.get('mileage')} miles\n"
                f"Store: {car.get('storeName')} ({car.get('storeCity')}, {car.get('state')})\n"
                f"URL: https://www.carmax.com/car/{car.get('stockNumber')}\n")

    def run(self):
        sent_listings = load_sent_listings(self.sent_listings_file)
        print(f"Initial sent listings: {sent_listings}")
        car_listings = self.fetch_car_listings()
        for car in car_listings:
            stock_number = car.get('stockNumber')
            if stock_number not in sent_listings:
                car_details = self.format_car_details(car)
                self.send_to_discord(car)
                save_sent_listing(self.sent_listings_file, stock_number)
                sent_listings.add(stock_number)  # Add to the set to avoid duplicates in the same run
                print(f"Listing Sent to Webhook: {stock_number}")
            else:
                print(f"Skipping duplicate listing: {stock_number}")

if __name__ == "__main__":
    scraper = CarScraper()
    scraper.run()