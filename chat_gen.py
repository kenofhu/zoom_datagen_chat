import requests
import json
import base64
import sys
import os

# use path of file in config.json or in parameter
transcript_file_path=""
with open('config.json') as f:
    credentials = json.load(f)
    basic_credentials = f"{credentials['username']}:{credentials['password']}"

# Check argument
if len(sys.argv) > 1:
    if os.path.exists(sys.argv[1]):
        transcript_file_path=sys.argv[1]
        print(f"Using {transcript_file_path} as transcript for the chat")
    else:
        print(f" {transcript_file_path} File does not exist.")
        exit()
else:
    transcript_file_path=credentials['transcript_file']
    if transcript_file_path:
        print("Using transcript_file from config.json : {transcript_file_path}")
    else:
        print(f" {transcript_file_path} File from config.json does not exist.")
        exit()

contacts=[]


auth_header=f"Basic {base64.b64encode(basic_credentials.encode()).decode()}"
# S2S Authentication

url_token = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={credentials['account_id']}"

auth_header=f"Basic {base64.b64encode(basic_credentials.encode()).decode()}"
payload = {}
headers = {
  'Authorization': auth_header,
}

response = requests.request("POST", url_token, headers=headers, data=payload)
auth_token= 'Bearer ' + response.json()['access_token']

def get_user_id(email, contacts):
    for user in contacts:
        if user['email']==email:
            return user
    else:
        url_user1=f"https://api.zoom.us/v2/users/{email}"
        payload = ""
        headers = {
        'Authorization': auth_token,
        }

        user1_response = requests.request("GET", url_user1, headers=headers, data=payload)
        ## store in contact dict
        ## test that user exsist
        user1={"email":email, "user_id":user1_response.json()['id']}
        contacts.append(user1)
    return user1

## Loading Json data, the format should be 
# [
#     {
#         "timestamp": "2023-11-05T09:05:00Z",
#         "sender_email": "",
#         "recipient_email": "",
#         "text": ""
#     },
#    {
#         "timestamp": "2023-11-05T09:07:15Z",
#         "sender_email": "",
#         "recipient_email": "a",
#         "text": ""
#     }
#   ]
with open(transcript_file_path) as f:
    chat_data = json.load(f)


inc=0
mainMessage=0
for message in chat_data:
    sender=get_user_id(message['sender_email'],contacts)
    recipient=get_user_id(message['recipient_email'],contacts)
    url = f"https://api.zoom.us/v2/chat/users/{sender['user_id']}/messages"
    if mainMessage == 0 :
        payload = json.dumps({
            "message": message['text'],
            "to_contact": recipient['email']
        })
    else:
        payload = json.dumps({
            "message": message['text'],
            "reply_main_message_id": mainMessage,
            "to_contact": recipient['email']
        })

    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth_token,
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if inc == 0:
        mainMessage=response.json()['id']
    if response.status_code==201:
        print(f"Message {inc}/{len(chat_data)}")
    else:
        print(f"Message {inc}/{len(chat_data)}: error: {response.status_code} / {response.text}")
        # we may want to wait a bit and try again if the main message is not available yet
    inc+=1


