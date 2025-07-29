## NEW - for comments 


import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from urllib.parse import urlencode
from base64 import b64encode
import requests
from dotenv import load_dotenv
import streamlit

## ENV FILE comments
load_dotenv()
## for branch
APP_KEY = os.getenv("AppKey")
APP_SECRET = os.getenv("AppSecret")
REDIRECT_URL = os.getenv("RedirectUrl")  # note
AUTHORIZATION_URL = os.getenv("AuthorizationUrl")
TOKEN_URL = os.getenv("TokenUrl")

FULL_AUTH_URL = f"{AUTHORIZATION_URL}?response_type=code&client_id={APP_KEY}&redirect_uri={REDIRECT_URL}"

unpacked_response = {}

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
  
        global unpacked_response
        parsed_path = urlparse(self.path)
        path = parsed_path.path
    
        if path == "/":
            print(f"\nRedirecting to authorization endpoint ({FULL_AUTH_URL}):")
            print(unpacked_response)
            self.send_response(302)
            self.send_header("Location", FULL_AUTH_URL)
            self.end_headers()

        elif path == "/" + REDIRECT_URL.split("/")[-1]:
            print("\nRequesting tokens...")
            unpacked_response = self.get_tokens(parsed_path)
            print("Response:")
            print(unpacked_response)


            print("\nRenewing tokens...")
            unpacked_response = self.renew_tokens()
            print("Response:")
            print(unpacked_response)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Tokens received and refreshed. Check console output.")

    def get_tokens(self, parsed_path):
        query = parse_qs(parsed_path.query)
        code = query.get("code", [None])[0]

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URL,
        }

        return self.token_request(data)

    def renew_tokens(self):
        data = {
            "grant_type": "refresh_token",
            "refresh_token": unpacked_response.get("refresh_token"),
            "redirect_uri": REDIRECT_URL,
        }

        return self.token_request(data)

    def token_request(self, data):
        basic_token = b64encode(f"{APP_KEY}:{APP_SECRET}".encode()).decode()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {basic_token}",
        }

        response = requests.post(TOKEN_URL, headers=headers, data=urlencode(data))
        return response.json()

def run(server_class=HTTPServer, handler_class=OAuthHandler, port=3000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server is running on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
