from __future__ import print_function
import httplib2
import os

from apiclient import discovery, errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from datetime import datetime, timedelta

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


# Returns true if message is the last message in its thread
# False otherwise
def message_last_in_thread(service, message):
    thread_id = message["threadId"]
    # https://developers.google.com/gmail/api/v1/reference/users/threads/get
    try:
        thread = service.users().threads().get(userId='me', id=thread_id).execute()
        all_messages = thread['messages']
        print("Current message ID is " + message["id"] + " and last message in thread ID is " + all_messages[-1]["id"])
        return message["id"] == all_messages[-1]["id"]
    except errors.HttpError, error:
        print('An error occurred: %s' % error)


# from https://developers.google.com/gmail/api/v1/reference/users/messages/list
def get_old_messages(service):
    try:
        one_week = (datetime.today() - timedelta(days=7)).strftime("%Y/%m/%d")
        two_weeks = (datetime.today() - timedelta(days=14)).strftime("%Y/%m/%d")
        query = "from:me before:" + one_week + " after:" + two_weeks

        response = service.users().messages().list(userId='me',
                                                   q=query).execute()
        messages = []
        if 'messages' in response:
            # make sure current message is last message in thread
            for message in response['messages']:
                thread_id = message["threadId"]
                print("Message id is " + message["id"] + ", thread id " + thread_id + ", last in thread is %r" % message_last_in_thread(service, message))

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId='me', q=query,
                                             pageToken=page_token).execute()
            for message in response['messages']:
                print(message)

        return messages
    except errors.HttpError, error:
        print('An error occurred: %s' % error)


def main():
    # Get credentials
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    get_old_messages(service)

if __name__ == '__main__':
    main()