import os, json, secrets, requests, redis
from dotenv import load_dotenv
from src.services.email.email_sender import EmailSender

load_dotenv()

class XeroAuth:
    def __init__(self):
        self.redis_client = redis.from_url(os.environ['REDIS_URL'])
        self.auth_url = os.environ['AUTH_URL']
        self.token_url = os.environ['TOKEN_URL']
        self.client_id = os.environ['XERO_CLIENT_ID']
        self.client_secret = os.environ['XERO_CLIENT_SECRET']
        self.redirect_uri = os.environ['REDIRECT_URI']
        self.scopes = os.environ['SCOPES']
        self.sender = EmailSender()

    def save_tokens_to_redis(self, tokens):
        self.redis_client.set('xero_tokens', json.dumps(tokens))

    def get_tokens_from_redis(self):
        tokens = self.redis_client.get('xero_tokens')
        return json.loads(tokens) if tokens else None

    def generate_auth_url(self):
        state = secrets.token_hex(16)
        auth_request_url = f"{self.auth_url}?response_type=code&client_id={self.client_id}&redirect_uri={self.redirect_uri}&scope={self.scopes}&state={state}"
        return auth_request_url

    def exchange_code_for_tokens(self, auth_code):
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        response = requests.post(self.token_url, data=data)
        if response.status_code == 200:
            print("Authorization code exchanged successfully.")
            self.save_tokens_to_redis(response.json())
            print("Tokens saved to Redis.")
        else:
            print("Error exchanging authorization code. Response:")
            print(response.text)
            raise Exception("Error exchanging authorization code")

    def refresh_token(self):
        stored_tokens = self.get_tokens_from_redis()
        if not stored_tokens or 'refresh_token' not in stored_tokens:
            print("Error: Refresh token not found in Redis")
            self.sender.send_email("Error: Refresh token not found in Redis", "Error: Refresh token not found in Redis")
            return

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': stored_tokens['refresh_token'],
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        try:
            response = requests.post(self.token_url, data=data)
            if response.status_code == 200:
                new_tokens = response.json()
                self.save_tokens_to_redis(new_tokens)
                print("Token refreshed successfully and saved to Redis.")
            else:
                print(f"Error refreshing token. Status code: {response.status_code}")
                print("Response:", response.text)
                self.sender.send_email("Error refreshing token", f"Error refreshing token. Re-authorize <a href='{self.generate_auth_url()}'>here</a>")
        except requests.RequestException as e:
            print(f"An error occurred while refreshing the token: {e}")
            self.sender.send_email("Error refreshing token", f"Error refreshing token. Re-authorize <a href='{self.generate_auth_url()}'>here</a>")

    def run(self, command=None):
        if command == '--refresh':
            self.refresh_token()
        else:
            auth_url = self.generate_auth_url()
            print("Please visit this URL in a browser on your local machine to authorize the application:")
            print(auth_url)
            print(f"\nAfter authorization, you will be redirected to a URL starting with {self.redirect_uri}")
            print("Look for the 'code' parameter in this URL.")
            auth_code = input("\nEnter the authorization code from the redirect URL: ")
            self.exchange_code_for_tokens(auth_code)

if __name__ == "__main__":
    import sys
    xero_auth = XeroAuth()
    if len(sys.argv) > 1:
        xero_auth.run(sys.argv[1])
    else:
        xero_auth.run()