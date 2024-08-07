import requests
import urllib.parse
import json
from dotenv import load_dotenv
import os

load_dotenv()

class EmailSender:
    def __init__(self, recipients="ivor@g2i.co", subject="XOAuth Token Service Update!"):
        # Email parameters
        self.recipients = recipients
        self.subject = subject
        # API parameters
        self.email_transport_api_url = os.getenv("AWS_LAMBDA_SEND_EMAIL")
        self.from_email = "G2i Support (Staging) <auth@g2i.co>"

    def urlencode(self, string):
        return urllib.parse.quote(string)

    def send_email(self, text, html):
        if not text or not html:
            print("Error: Both text and HTML messages must be provided")
            return False

        # URL encode the parameters
        encoded_recipients = self.urlencode(self.recipients)
        encoded_subject = self.urlencode(self.subject)
        encoded_text = self.urlencode(text)
        encoded_html = self.urlencode(html)
        encoded_from_email = self.urlencode(self.from_email)

        # Construct the API request URL
        request_url = (f"{self.email_transport_api_url}?"
                       f"toAddress={encoded_recipients}&"
                       f"text={encoded_text}&"
                       f"html={encoded_html}&"
                       f"subject={encoded_subject}&"
                       f"replyTo={encoded_from_email}&"
                       f"source={encoded_from_email}")

        print(f"Sending request to: {request_url}")

        # Send the request
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        data = {
            "multiValueHeaders": ["Content-Type: application/json"],
            "resource": "/send-email",
            "path": "/send-email",
            "isBase64Encoded": True
        }
        response = requests.post(request_url, headers=headers, json=data)

        # Print full response for debugging
        print("Full API Response:")
        print(response.text)
        print(f"HTTP Status Code: {response.status_code}")

        if response.status_code == 200:
            print("Email sent successfully! (Status code 200)")
            if response.text:
                print("Response Body:")
                print(json.dumps(response.json(), indent=2))
            else:
                print("No response body received, but operation was successful.")
            return True
        else:
            print(f"Failed to send email. HTTP Status: {response.status_code}")
            if response.text:
                print("Response Body:")
                print(json.dumps(response.json(), indent=2))
            else:
                print("No response body received.")
            return False
