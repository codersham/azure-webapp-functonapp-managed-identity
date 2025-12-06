#########################################################################################################################
# Objective: This flask application is intended to test managed identity based authentication between a frontend Azure WebApp and a backend Azure Function App. This flask application code is for hosting in Azure WebApp.
# There are 3 routes in this application:
# 1. Default route: Displays text in the browser to debug application is working properly
# 2. Token route: Displays Entra ID token on the browser window, to ensure it is able to get the token from Entra
# 3. Function route: Calls the backend function app with Entra token in Authentication header and dispalys the output of the function.
#########################################################################################################################

import requests
from flask import Flask, jsonify, Response
from azure.identity import ManagedIdentityCredential
import config

app = Flask(__name__)


# Load the variables from config.py file
CLIENT_ID = config.UAMI_CLIENT_ID # UAMI of the Frontend WebApp
BACKEND_APP_URL = config.FUNCTION_APP_URL # Backend Application URL
BACKEND_APPID_URI = config.RESOURCE # Backend Application ID URI


# Default route
@app.route("/")
def index():
    return "Web App using User Assigned Managed Identity"



# Get Entra token with User Assigned Managed Identity (UAMI)
@app.route("/token")
def get_token():
    try:
        # Acquire token using UAMI. For SMI don't pass the client_id
        credential = ManagedIdentityCredential(client_id=CLIENT_ID)
        token = credential.get_token(BACKEND_APPID_URI + "/.default")
        
        # Display the raw token in the browser
        return Response(
            f"Access Token:<br><br>{token.token}",
            status=200,
            mimetype="text/html"
        )
    except Exception as e:
        return Response(f"Error acquiring token: {str(e)}", status=500)
    


@app.route("/call-function")
def call_function():
    try:
        # Acquire token using UAMI. For SMI don't pass the client_id
        credential = ManagedIdentityCredential(client_id=CLIENT_ID)
        token = credential.get_token(BACKEND_APPID_URI + "/.default")

        headers = {
            "Authorization": f"Bearer {token.token}"
        }
        payload = {"name": "James Bond"}
        
        response = requests.get(BACKEND_APP_URL, headers=headers, params=payload)

        return jsonify({
            "status_code": response.status_code,
            "response": response.text
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)