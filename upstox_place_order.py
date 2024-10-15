import requests # type: ignore
import json
import threading
import time
from websocket import WebSocketApp # type: ignore
from selenium import webdriver # type: ignore
from selenium.webdriver.common.by import By # type: ignore
import logging

logging.basicConfig(level=logging.INFO)

class Upstox_Place_Order():

    #Initialise variables
    def __init__(self):
        self.client_id = 'ebc2b3f9-3b85-45fc-a691-79191b02697c'
        self.api_secret = 'zfi3xdy2b8'
        self.redirect_uri = 'https://api.upstox.com/v2/login'
        self.code = None
        self.access_token = None
        self.nifty_symbol = 'NSE_INDEX|NIFTY_50'
        self.auth_url = None
        self.generate_auth_url()
        self.get_auth_code()
        self.place_order()


    #Generate URL for Auth Code
    def generate_auth_url(self):

        self.auth_url = f'https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={self.client_id}&redirect_uri={self.redirect_uri}'
        print(f"Login URL: {self.auth_url}")
    

    #Log into Upstox and get Auth Code and get Auth Token
    def get_auth_code(self):

        #Use Selenium to open the browser and log in
        driver = webdriver.Chrome()  # Ensure ChromeDriver is installed
        driver.get(self.auth_url)

        # Wait for the user to log in manually or automate this step

        time.sleep(35)
        current_url = driver.current_url
        driver.quit()

        # Extract authorization code from the URL
        if "code=" in current_url:
            self.code = current_url.split("code=")[1]
            logging.info(f"Authorization code: {self.code}")
        else:
            raise Exception("Authorization code not found.")

        # Exchange the authorization code for an access token
        token_url = 'https://api.upstox.com/v2/login/authorization/token'

        # Headers and data for the token request
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            }

        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.api_secret,
            'code': self.code,
            'redirect_uri': self.redirect_uri,
            }

        response = requests.post(token_url, headers=headers, data=data)

        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            print(f"Access Token Status : RECIEVED")
        else:
            raise Exception(f"Error fetching access token: {response.status_code} - {response.text}")
        

    #Place Buy Order
    def place_order(self):
        
        url = 'https://api-hft.upstox.com/v2/order/place'
        headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {self.access_token}',
        }

        #Change "Instrument Token" as Required
        data = {
        'quantity': 1,
        'product': 'D',
        'validity': 'DAY',
        'price': 0,
        'tag': 'string',
        'instrument_token': 'NSE_EQ|INE669E01016',
        'order_type': 'MARKET',
        'transaction_type': 'BUY',
        'disclosed_quantity': 0,
        'trigger_price': 0,
        'is_amo': False,    #after market order
        }


        try:
            #Send POST request
            response = requests.post(url, json=data, headers=headers)
            logging.info('Response Code: %s', response.status_code)
            logging.info('Response Body: %s', response.json())

        except requests.exceptions.RequestException as e:
            logging.error('Error placing order: %s', e)
        
            
if __name__ == "__main__":
    order = Upstox_Place_Order()