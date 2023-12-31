import os
import json
import main
import firebase_admin
from firebase_functions import db_fn, https_fn  # Cloud functions for firebase SDK
from firebase_admin import credentials, storage, db, initialize_app
from firebase.firebase import FirebaseApplication
from typing import TypedDict, List, Optional, Callable, Any

def quick_sort(datos: List, key: Optional[Callable[[Any], Any]] = None, reverse=False) -> List:

  if not key:
      def key(value):
          return value

  if len(datos) <= 1:
      return datos

  pivot = datos.pop()

  mayores = []
  menores = []
  for elemento in datos:
      if key(elemento) < key(pivot):
          menores.append(elemento)
      else:
          mayores.append(elemento)
  sorted_menores = quick_sort(menores, key=key, reverse=reverse)
  sorted_mayores = quick_sort(mayores, key=key, reverse=reverse)

  if reverse:
      return sorted_mayores + [pivot] + sorted_menores
  else:
      return sorted_menores + [pivot] + sorted_mayores


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

username = main.name.lower()
bucket = storage.bucket()
users_ref = db.reference("Users")


def database_listener(event: db.Event) -> None:
    if event.event_type != "patch":
        print("Loading messages...")
        # print(event.data)
        delete_chat()
        load_messages(event.data)
        return
    data: dict = event.data
    msg: Message = list(data.values())[0][-1]  #
    receiver = msg["receiver"]
    sender = msg["sender"]
    if username == receiver or username == sender:
        if sender == username:
            msg = build_message(msg, end="\n")
            create_msg(msg, receiver, sender)
            return
        print(f"Message received from {sender}")
        msg = build_message(msg)
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
    #print(data)
    adrian_isaac_chat = []
    adrian_hector_chat = []
    hector_isaac_chat = []
    try:
        for user in data:
            for msg in data[user]["messages"]:
                if msg["sender"] == "adrian" and msg["receiver"] == "isaac" or msg["sender"] == "isaac" and msg["receiver"] == "adrian":
                    adrian_isaac_chat.append(msg)
                elif msg["sender"] == "adrian" and msg["receiver"] == "hector" or msg["sender"] == "hector" and msg["receiver"] == "adrian":
                    adrian_hector_chat.append(msg)
                elif msg["sender"] == "hector" and msg["receiver"] == "isaac" or msg["sender"] == "isaac" and msg["receiver"] == "hector":
                    hector_isaac_chat.append(msg)
        # Quick sort the messages by time
        adrian_isaac_chat = quick_sort(adrian_isaac_chat, key=lambda x: x["time"])
        #adrian_hector_chat = quick_sort(adrian_hector_chat, key=lambda x: x["time"])
        hector_isaac_chat = quick_sort(hector_isaac_chat, key=lambda x: x["time"])
        create_chat_file(adrian_isaac_chat, "adrian_isaac.txt", "adrian", "isaac")
        create_chat_file(hector_isaac_chat, "hector_isaac.txt", "hector", "isaac")
        #create_chat_file(adrian_hector_chat, "adrian_hector.txt", "adrian", "hector")
    except Exception as e:
        print("No data was found!")
        return
def create_chat_file(chat_messages: list, filename: str, reciver: str, sender: str) -> None:
    print(f"Creating chat file {filename}...")
    folder = "./Chat/"
    for msg in chat_messages:
        msg = build_message(msg)
        create_msg(msg, reciver, sender) # msg, adrian_isaac.txt, "", build=True


def build_message(msg: Message, end="\n") -> str:
    new_msg = msg["msg"].replace("\n", "")
    return f'!{new_msg}*{msg["sender"]}+{msg["time"]};{end}'


def create_msg(msg: str, receiver: str, sender: str, build=False) -> None:
    folder = "./Chat/"
    # Ommit this part if you are not hardcoding the users, else, change the if statements to match your users
    filename = ""
    if receiver == "adrian" and sender == "isaac" or receiver == "isaac" and sender == "adrian":
        filename = "adrian_isaac.txt"
    elif receiver == "adrian" and sender == "hector" or receiver == "hector" and sender == "adrian":
        filename = "adrian_hector.txt"
    elif receiver == "hector" and sender == "isaac" or receiver == "isaac" and sender == "hector":
        filename = "hector_isaac.txt"
    if not build:
        with open(folder + filename, "a") as f:
            print("Writing message...")
            f.write(msg)
        print("Message written!")
    else:
        with open(folder + filename, "a") as f:
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
        # Create a file in ./Chat/ with the message
        #create_msg(file_data["msg"], receiver, sender)
    except Exception as e:
        print(e)

users_ref.listen(database_listener)
