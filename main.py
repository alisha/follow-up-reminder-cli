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

SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Follow Up Reminder'


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
                                   'follow-up-reminder.json')

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
                if message_last_in_thread(service, message):
                    messages.append(message["id"])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId='me', q=query,
                                             pageToken=page_token).execute()
            for message in response['messages']:
                thread_id = message["threadId"]
                if message_last_in_thread(service, message):
                    messages.append(message["id"])

        return messages
    except errors.HttpError, error:
        print('An error occurred: %s' % error)


# Given messages, an array of message IDs, print info to get user to follow up
def print_followup_info(service, messages):
    for message_id in messages:
        try:
            message_info = service.users().messages().get(userId='me', id=message_id, format="metadata").execute()

            # Find message subject, sent date, and URL
            desired_info = ["Subject", "To", "Date"]
            message_headers = message_info["payload"]["headers"]
            for info in desired_info:
                for header in message_headers:
                    if header["name"] == info:
                        print("%s: %s" % (info, header["value"]))
            print("Message ID: %s\n" % message_id)

        except errors.HttpError, error:
            print('An error occurred: %s' % error)


# Given messages (array of message IDs) and a label, add label to each message
def add_label(service, label, messages):
    # Check if label already exists, if not then create it
    user_labels = service.users().labels().list(userId='me').execute()
    label_id = 0
    for user_label in user_labels['labels']:
        if user_label["name"] == label:
            label_id = user_label["id"]

    if label_id == 0:
        label_obj = {   'name': label,
                        'labelListVisibility': 'labelShow'
                    }
        new_label = service.users().labels().create(userId='me', body=label_obj).execute()
        label_id = new_label["id"]

    # Add label to messages
    for message_id in messages:
        service.users().messages().modify(userId='me', id=message_id, body={"addLabelIds": [label_id]}).execute()


def main():
    # Get credentials
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    
    messages = get_old_messages(service)
    print_followup_info(service, messages)
    add_label(service, "Follow Up", messages)

if __name__ == '__main__':
    main()