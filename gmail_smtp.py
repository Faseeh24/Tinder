import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()
SMTP_CREDENTIALS = os.getenv('path_to_smtp_key')
USER_EMAIL = os.getenv('user_email')

# If modifying these SCOPES, delete the file tokens_smtp.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    """Authenticate the user and get the Gmail API service."""
    creds = None
    # The file tokens_smtp.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('./KEYS/tokens_smtp.json'):
        creds = Credentials.from_authorized_user_file('./KEYS/tokens_smtp.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                SMTP_CREDENTIALS, SCOPES)  # Path to your credentials.json file
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('./KEYS/tokens_smtp.json', 'w') as token:
            token.write(creds.to_json())
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        print(f'An error occurred: {error}')

def create_message(sender, to, subject, body):
    """Create a message for sending via Gmail API."""
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = to
    message['Subject'] = subject
    # Attach the email body
    msg = MIMEText(body)
    message.attach(msg)
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_email(service, sender, to, subject, body):
    """Send the email."""
    try:
        message = create_message(sender, to, subject, body)
        service.users().messages().send(userId="me", body=message).execute()
    except HttpError as error:
        return f'An error occurred: {error}'


def send_sign_up_email(email):
    # Authenticate and get the Gmail service
    service = authenticate_gmail()
    
    # Email details
    sender = USER_EMAIL  # write your own email address
    to = email
    subject = 'Welcome to Tinder! 🎉'
    body = 'Hi there! Welcome to Tinder, The ultimate match-making platform. We are excited to have you on board. 🚀\n\n Happy Matching! 😊'
    
    # Send the email
    send_email(service, sender, to, subject, body)
