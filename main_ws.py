from flask import Flask, request, jsonify
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv

app = Flask(__name__)
@app.route('/webhook', methods=['POST'])
def webhook_receiver():
    data = request.json  # Get the JSON data from the incoming request
    # Process the data and perform actions based on the event

    # List of URLs to scrape
    urls = [
        "https://www.zomato.com/nagpur/restaurants?place_name=Nagpur&dishv2_id=30308&category=1",
        "https://www.zomato.com/nagpur/restaurants?place_name=Nagpur&dishv2_id=68987&category=1",
        "https://www.zomato.com/nagpur/restaurants?place_name=Nagpur&dishv2_id=9055&category=1",
        "https://www.zomato.com/nagpur/restaurants?place_name=Nagpur&dishv2_id=55280&category=1",
        "https://www.zomato.com/nagpur/restaurants?place_name=Nagpur&dishv2_id=35013&category=1",
        "https://www.zomato.com/nagpur/restaurants?place_name=Nagpur&dishv2_id=56691&category=1",
        "https://www.zomato.com/nagpur/restaurants?place_name=Nagpur&dishv2_id=39212&category=1",
        "https://www.zomato.com/nagpur/restaurants?place_name=Nagpur&dishv2_id=35798&category=1",
        "https://www.zomato.com/nagpur/restaurants?place_name=Nagpur&dishv2_id=64088&category=1",
        "https://www.zomato.com/nagpur/restaurants?place_name=Nagpur&dishv2_id=8497&category=1",
        "https://www.zomato.com/nagpur/restaurants?place_name=Nagpur&dishv2_id=19315&category=1",
        "https://www.zomato.com/nagpur/restaurants?place_name=Nagpur&dishv2_id=11035&category=1"
    ]

    # Initialize the WebDriver with the service
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Initialize lists to store the combined data
    all_restaurants = []
    all_ratings = []
    all_cuisines = []
    all_prices = []

    # Loop over each URL
    for url in urls:
        driver.get(url)
        time.sleep(2)  # Wait for the page to load

        # Setup for scrolling
        scroll_pause_time = 3
        screen_height = driver.execute_script("return window.screen.height;")
        i = 1

        # Temporary lists to store data for each URL
        restaurants = []
        ratings = []
        cuisines = []
        prices = []

        while len(restaurants) < 100:  # Collect 100 items
            driver.execute_script(f"window.scrollTo(0, {screen_height}*{i});")
            i += 1
            time.sleep(scroll_pause_time)

            # Extract page source after scrolling
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # Extract restaurant information
            for item in soup.select('.jumbo-tracker'):
                # Extract restaurant name
                name_ele = item.select_one('.sc-1hp8d8a-0')
                if name_ele:
                    restaurants.append(name_ele.get_text(strip=True))
                else:
                    restaurants.append(None)

                # Extract rating
                rating_ele = item.select_one('.sc-1q7bklc-1')
                if rating_ele:
                    ratings.append(rating_ele.get_text(strip=True))
                else:
                    ratings.append(None)

                # Extract cuisine
                cuisine_ele = item.select_one('.sc-gUlUPW.gQHQnh')
                if cuisine_ele:
                    cuisines.append(cuisine_ele.get_text(strip=True))
                else:
                    cuisines.append(None)

                # Extract price
                price_ele = item.select_one('.sc-gUlUPW.iMvhva')
                if price_ele:
                    prices.append(price_ele.get_text(strip=True))
                else:
                    prices.append(None)

                # Check if we have collected 100 items
                if len(restaurants) >= 100:
                    break

        # Ensure all lists are of the same length by truncating to the first 100 entries if necessary
        restaurants = restaurants[:100]
        ratings = ratings[:100]
        cuisines = cuisines[:100]
        prices = prices[:100]

        # Append the collected data to the combined lists
        all_restaurants.extend(restaurants)
        all_ratings.extend(ratings)
        all_cuisines.extend(cuisines)
        all_prices.extend(prices)

    # Print extracted information
    print("Restaurants:", all_restaurants)
    print("Ratings:", all_ratings)
    print("Cuisines:", all_cuisines)
    print("Prices:", all_prices)

    # Create a DataFrame and save to CSV
    data = pd.DataFrame({
        'Restaurant': all_restaurants,
        'Rating': all_ratings,
        'Cuisine': all_cuisines,
        'Price': all_prices
    })

    data.to_csv('Zomato_Restaurants.csv', index=False)

    # Close the browser
    driver.quit()
    
    

    # Load environment variables
    load_dotenv()

    # Mailgun API credentials
    MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')
    MAILGUN_DOMAIN = os.getenv('MAILGUN_DOMAIN')
    MAILGUN_RECIPIENT = os.getenv('MAILGUN_RECIPIENT')
    MAILGUN_SENDER = os.getenv('MAILGUN_SENDER')







# Function to send email with attachment using Mailgun
    def send_email_with_attachment(subject, body, attachment_path):
        try:
            response = requests.post(
                f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
                auth=("api", MAILGUN_API_KEY),
                files=[("attachment", open(attachment_path, "rb"))],
                data={"from": MAILGUN_SENDER,
                      "to": MAILGUN_RECIPIENT,
                      "subject": subject,
                      "text": body})
            if response.status_code == 200:
                print("Email sent successfully!")
            else:
                print(f"Failed to send email. Status code: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

# Example usage

    subject = "Sample CSV Attachment"
    body = "Please find the attached CSV file."
    attachment_path = "Zomato_Restaurants.csv"  # Replace with the path to your CSV file

    send_email_with_attachment(subject, body, attachment_path)


    print("Received webhook data:", data)
    return jsonify({'message': 'Webhook received successfully'}), 200
if __name__ == '__main__':
    app.run(port=5000,debug=True,use_reloader=False)