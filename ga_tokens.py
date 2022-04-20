#!/usr/bin/env python3

# Python utility libraries
import os.path
import sys

# Google auth libraries
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the scopes you want to have access to. If you want to experiment with writing to google analytics, then you
# can change the scope here. Having scopes here that do not match the scopes granted access to leads to an error.
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/analytics.readonly",
                 "https://www.googleapis.com/auth/userinfo.profile",
                 "https://www.googleapis.com/auth/userinfo.email",
                 "openid"]


# Class to handle the two incompatible Google Analytics APIs automatically depending on if the account is a Universal
# Analytics (GA3) or a Google Analytics 4 (GA4) account.
class GoogleAnalyticsAccount:

    def __init__(self, account_id, account_name, version):
        self.account_id = account_id
        self.account_name = account_name
        if version not in [3, 4]:
            raise ValueError("Only supported version numbers for Google Analytics are 3 or 4.")
        self.version = version


# Class that gets all Google Analytics accounts associated with a user.
class GoogleAnalyticsUser:

    def __init__(self, credentials=None):
        self.credentials = credentials if credentials is not None else get_credentials_from_file()
        self.accounts = []

    def load_google_analytics_accounts(self):
        self.accounts = []
        # Get all Universal Analytics accounts using the analytics management api
        google_analytics_3_service = build(serviceName='analytics', version='v3', credentials=credentials)
        google_analytics_3_accounts = google_analytics_3_service.management().accounts().list().execute()
        for account in google_analytics_3_accounts['items']:




# Load the access tokens from your local file or get new tokens using your secrets
def get_credentials_from_file(secrets_file='.secrets', token_file='.tokens'):
    credentials = None
    # Check if access token file already exists
    if os.path.exists(token_file):
        credentials = Credentials.from_authorized_user_file(filename=token_file, scopes=GOOGLE_SCOPES)
    # If tokens have expired or do not exist then refresh tokens or get tokens from user
    if not credentials or not credentials.valid:
        # If token expired refresh the tokens
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        # If no refresh tokens exists get new tokens
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file=secrets_file, scopes=GOOGLE_SCOPES)
            credentials = flow.run_local_server(port=0)
        # Save the new access tokens
        with open(token_file, 'w') as token:
            token.write(credentials.to_json())
    return credentials


# Get the service api from Google to use in requests
def get_google_analytics_service(credentials, version=3):
    if version not in [3, 4]:
        return None
    if version == 3:
        return build(serviceName='analytics', version='v3', credentials=credentials)
    if version == 4:
        return build(serviceName='analyticsadmin', version='v1alpha', credentials=credentials)


def main():
    # Get the access token
    credentials = get_credentials_from_file()

    service3 = get_google_analytics_service(credentials, version=3)
    # Get a list of all Google Analytics accounts for this user
    accounts3 = service3.management().accounts().list().execute()
    print(accounts3)

    service4 = get_google_analytics_service(credentials, version=4)
    accounts4 = service4.accounts().list().execute()
    print(accounts4)



if __name__ == '__main__':
    sys.exit(main())
