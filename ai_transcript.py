###
# alternatively use the following prompt in aic and copy paste in chatdata/chat_data.json
# Generate a chat transcript between two users.  
""" 
The output should be a strict json format, each message will contain the following fields 'timestamp' (in this format 2023-10-01T10:07:45Z
), 'sender_email','recipient_email','text'. 
Both emails should always be different. 
This output will be used by another software to be injected in a chat software. You should only output json data. 
Please generate a transcript between {USER1} ({EMAIL_USER1}) and {USER2} ({EMAIL_USER2}). {name1} is the end user, and {name2} the helpdesk specialist. 
They are having a chat discussion to resolve a technical issue when configuring a Zoom webinar, to use an external sso for authentication, please imagine a chat discussion between these two person.
"""

from openai import OpenAI
import json
import argparse
import os
from pathlib import Path

client = OpenAI()


# use path of file in config.json or in parameter
parser = argparse.ArgumentParser(description="Process command-line arguments.")
parser.add_argument("--file", type=str, help="path of the output transcript file default to chatdata/chat_data.json")
parser.add_argument("--mail1", type=str, help="email of user 1")
parser.add_argument("--mail2", type=str, help="email of user 2")
parser.add_argument("--name1", type=str, help="name of user 2")
parser.add_argument("--name2", type=str, help="name of user 2")

args = parser.parse_args()

filepath = args.file if args.file else "chatdata/chat_data.json"
mail1 = args.mail1 if args.mail1 else "amiller@uc.jchodlewski.com"
mail2 = args.mail2 if args.mail2 else "julien@uc.jchodlewski.com"
name1 = args.name1 if args.name1 else "Amelia"
name2 = args.name2 if args.name2 else "Julien"

prompt=f"Please generate a transcript between {name1} ({mail1}) and {name2} ({mail2}). {name1} is the end user, and {name2} the helpdesk specialist. They are having a chat discussion to resolve a technical issue when configuring a Zoom webinar, to use an external sso for authentication, please imagine a chat discussion between these two person."

print(f"This is the default prompt:\n {prompt}")
response=input("if you want to use it, press y or yes, otherwise write youry new prompt\n")
if response.lower() in ["y", "yes"]:
  print("Generating the transcript")
else:
    prompt=response


# ask for name and email of user 1
#ask for name and email of user 2
# ask for the topic of the discussion
completion = client.chat.completions.create(
  model="gpt-4o-mini",
  messages=[
    {"role": "developer", "content": """Generate a chat transcript between two users. 
    The output should be a strict json format, each message will contain the following fields 'timestamp' (in this format 2023-10-01T10:07:45Z
), 'sender_email','recipient_email','text'. 
Both emails should always be different. 
This output will be used by another software to be injected in a chat software. You should only output json data.
    """},
    {"role": "user", "content": prompt}
  ]
)

json_data = completion.choices[0].message.content.encode().decode('unicode_escape')
# clean the output
start = json_data.find("[")   # Find first '['
end = json_data.rfind("]") +1      # Find last ']'
    
json_data = json_data[start:end]

print(f"json_data: {json_data}")
json_dict = json.loads(json_data)

if filepath.split("/")[0]:
  directory = Path(filepath.split("/")[0])
  directory.mkdir(parents=True, exist_ok=True)  # Create dir, ignore if exists


with open(filepath, "w", encoding="utf-8") as json_file:
    json.dump(json_dict, json_file, indent=4)