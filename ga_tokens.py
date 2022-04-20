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


def main():
    # Get the access token
    credentials = get_credentials_from_file()

    # Core building blocks for accessing a Google API are:
    # 1) Creating access to the service. This requires the serviceName and version. Both can be found in the request URL
    #    Keep in mind the version here corresponds to the API version. Not the analytics version.

    # Get accounts that have type GA3/UA
    # API doc: https://developers.google.com/analytics/devguides/config/mgmt/v3/account-management
    # Base url:
    analytics_service = build(serviceName='analytics', version='v3', credentials=credentials)
    # Get a list of all Google Analytics accounts for this user
    analytics_accounts = analytics_service.management().accounts().list().execute()
    print(analytics_accounts)

    # TODO extract view IDs

    # # Access data for account of type GA3/UA
    # # API doc: https://developers.google.com/analytics/devguides/reporting/core/v4/rest
    # # Base url: https://analyticsreporting.googleapis.com
    # # analyticsreporting_service = build(serviceName='analyticsreporting', version='v4', credentials=credentials)
    # view_id = analytics_accounts
    # analyticsreporting_service.reports().batchGet(
    #     body={
    #         'reportRequests': [
    #             {
    #                 # TODO enter extracted view ID
    #                 'viewId': VIEW_ID,
    #                 'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'today'}],
    #                 'metrics': [{'expression': 'ga:sessions'}],
    #                 'dimensions': [{'name': 'ga:country'}]
    #             }]
    #     }
    # ).execute()

    # Get accounts that have type GA4
    # API doc: https://developers.google.com/analytics/devguides/config/admin/v1/rest/v1alpha/accounts/list
    # Base url: https://analyticsadmin.googleapis.com/v1alpha/
    analyticsadmin_service = build(serviceName='analyticsadmin', version='v1alpha', credentials=credentials)
    analyticsadmin_accounts = analyticsadmin_service.accounts().list().execute()
    print(analyticsadmin_accounts)

    # # Get data from a GA4 account
    # # API doc: https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties?hl=en
    # # Base url: https://analyticsdata.googleapis.com/v1beta/
    # analyticsdata_service = build(serviceName='analyticsadmin', version='v1beta', credentials=credentials)


if __name__ == '__main__':
    sys.exit(main())
