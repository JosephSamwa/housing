import requests
from requests.auth import HTTPBasicAuth
import base64
from datetime import datetime

def get_mpesa_access_token(consumer_key, consumer_secret):
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    return response.json()['access_token']

def lipa_na_mpesa_online(access_token, business_short_code, passkey, phone_number, amount, callback_url):
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    payload = {
        "BusinessShortCode": business_short_code,
        "Password": passkey,
        "Timestamp": timestamp,  
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": business_short_code,
        "PhoneNumber": phone_number,
        "CallBackURL": callback_url,
        "AccountReference": "SmartHousing Rent",
        "TransactionDesc": "Property Rent Payment"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()