from google import genai
from google.genai import types
import asyncio # Needed for running async functions
import sys
import os
client = genai.Client()
# Import the function from peggy.py
# The 'from peggy import' syntax assumes peggy.py is in the same directory
from peggy import get_gmail_processed_data
def process_subjects():
    print("Attempting to retrieve Gmail subjects from peggy.py...")
    # Call the function from peggy.py to get the list of dictionaries
    subject_data_list = get_gmail_processed_data()

    if subject_data_list:
        print("\n--- Retrieved Subject Lines from Gmail ---")
        # Instantiate a dictionary of subject lines, if needed
        # For example, mapping ID to Subject
        subjects_dict_by_id = {msg['subject'] for msg in subject_data_list}

        # Or simply print them out for now
        #for msg in subject_data_list:
            #print(f"Subject: {msg['subject']}")

       # print("\n--- Subject Data as a Dictionary (ID to Subject) ---")
        #print(subjects_dict_by_id) # This is your dictionary of subject lines!
        return(subjects_dict_by_id)
    else:
        print("No subject data received from peggy.py.")
        print("Please ensure your Gmail credentials are set up and valid by running peggy.py directly at least once.")
dict = process_subjects()
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=["Analyze the subject lines. Determine if any sent by a human. Determine if any require an email response. Provide only a sentence or two, be brief. Summarize list.", str(dict)]
)
print("\n")
print("\n")
print("\n")

print(response.text)
