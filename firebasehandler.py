import os
import json
import main
from datetime import datetime
import firebase_admin
from firebase_functions import db_fn, https_fn  # Cloud functions for firebase SDK
from firebase_admin import credentials, storage, db, initialize_app
from firebase.firebase import FirebaseApplication
from typing import TypedDict


class Message(TypedDict):
    msg: str
    receiver: str
    sender: str
    temporal: str


cred = credentials.Certificate("FirebaseCredentials/credentials.json")
app = initialize_app(
    cred,
    {
        "databaseURL": "https://assemblyhandler-default-rtdb.firebaseio.com/",
        "storageBucket": "assemblyhandler.appspot.com",
    },
)

username = main.name
bucket = storage.bucket()
users_ref = db.reference("Users")


def database_listener(event: db.Event) -> None:
    if event.event_type != "patch":
        print("Loading messages...")
        delete_chat()
        load_messages(event.data)
        return
    data: dict = event.data
    msg: Message = list(data.values())[0][-1]  #
    print(f"Message: {msg}")
    receiver = msg["receiver"]
    sender = msg["sender"]
    if username == receiver:
        print(f"Message received from {sender}")
        time = datetime.now().strftime("%H:%M:%S")
        msg = build_message(msg, time)
        create_msg(msg, receiver, sender)

def delete_chat():
    folder = "./Chat/"
    try:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                os.remove(folder + file)
    except fileNotFoundError:
        os.mkdir(folder)

def load_messages(data: dict) -> None:
    global username
    time = datetime.now().strftime("%H:%M:%S")
    try:
        for msg in data[username]["messages"]:
            message = build_message(msg, time)
            create_msg(message, username, msg["sender"], True)
    except Exception as e:
            print(e)
        return

def build_message(msg: Message, time: str, end = "\n") -> str:
    new_msg = msg["msg"].replace("\n", "")
    return f'!{new_msg}*{msg["sender"]}+{time};{end}'


def create_msg(msg: str, receiver: str, sender: str, build = False) -> None:
    folder = "./Chat/"
    if not build:
        with open(folder + f"{receiver}{sender}.txt", "a") as f:
            print("Writing message...")
            f.write(msg)
        print("Message written!")
    else:
        with open(folder + f"{receiver}{sender}.txt", "a") as f:
            f.write(msg)


def upload_file(file_data: dict, receiver: str) -> None:
    print(f"Uploading File to {receiver}...\n")
    sender = file_data["sender"]
    try:
        users_ref = db.reference("Users")
        users_ref = users_ref.child(receiver)

        current_data = users_ref.child("messages").get()
        if current_data is None:
            current_data = []
        current_data.append(file_data)
        users_ref.update({"messages": current_data})
        print("File uploaded!")
    except Exception as e:
        print(e)


users_ref.listen(database_listener)

