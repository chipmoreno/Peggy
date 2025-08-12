import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def extract_subject(message_payload):
    """
    Extracts the subject from a message payload's headers.
    """
    headers = message_payload.get('headers', [])
    for header in headers:
        if header.get('name') == 'Subject':
            return header.get('value')
    return "No Subject Found"

def get_gmail_processed_data():
  """
  Authenticates with Gmail API and lists the 10 most recent messages
  (including Spam and Trash), collecting their IDs and subject lines
  into a structured list of dictionaries.

  Returns:
      list: A list of dictionaries, where each dictionary contains
            'id' and 'subject' for a Gmail message. Returns an empty
            list on error or if no messages are found.
  """
  creds = None
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(
        userId="me",
        maxResults=10,          # Limit to the 10 most recent messages
        includeSpamTrash=True   # Include messages from Spam and Trash
        # q="is:unread"         # You can add this back if you still only want unread
    ).execute()

    messages_summary_list = results.get("messages", [])
    
    cleaned_messages_data = []

    if not messages_summary_list:
      print("No messages found matching the criteria.")
      return cleaned_messages_data
    
    print(f"Found {len(messages_summary_list)} messages. Fetching subjects...")

    for message_summary in messages_summary_list:
      message_id = message_summary['id']
      try:
          full_message = service.users().messages().get(
              userId="me",
              id=message_id,
              format="full"
          ).execute()
          
          subject_line = extract_subject(full_message['payload'])
          
          cleaned_messages_data.append({
              'id': message_id,
              'subject': subject_line
          })

      except HttpError as error:
          print(f"Error fetching full message for ID {message_id}: {error}")
      except Exception as e:
          print(f"An unexpected error occurred for ID {message_id}: {e}")
    
    return cleaned_messages_data

  except HttpError as error:
    print(f"An error occurred with the Gmail API: {error}")
    return []
  except Exception as e:
    print(f"An unexpected error occurred: {e}")
    return []


if __name__ == "__main__":
  # This block will ONLY run when peggy.py is executed directly (e.g., python peggy.py)
  # It will NOT run when get_gmail_processed_data is imported into another script.
  messages_for_testing = get_gmail_processed_data()
  if messages_for_testing:
      print("\n--- Messages Retrieved by peggy.py (for direct run testing) ---")
      for msg in messages_for_testing:
          print(f"ID: {msg['id']}, Subject: {msg['subject']}")
  else:
      print("\nNo messages were retrieved or an error occurred during direct run of peggy.py.")

