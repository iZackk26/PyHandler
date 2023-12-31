from Person import Person
from datetime import datetime
import firebasehandler
import os
import json
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

name = "Isaac"  # Change this with your name


class MyHandler(FileSystemEventHandler):
    def __init__(self, folder_to_track):
        self.folder_to_track = folder_to_track
        self.person = Person("", "", "", "")
        self.size = 0
        self.printed_data = False
        self.printed_msg = False
        self.printed_cloud = False
        self.fully_filled_msg = False

    # On modified Event
    def on_modified(self, event):
        # global temp_Msg
        if event.is_directory:
            return None
        filename = os.path.basename(event.src_path)  # **File name**
        print(filename)

        # Functions that check if the instance is fully filled
        if check(self.person):
            print("Uploading File...\n")
            print(self.person)
            file_data = write_data(self.person)
            print(file_data)
            firebasehandler.upload_file(file_data, self.person.receiver)
            self.person = Person("", "", "", "")
            self.printed_data = False
            self.printed_msg = False
        # Fill the instance with the data from the file
        elif filename == "data.txt":
            print("Reading data")
            self.person = read_data(self.folder_to_track + filename, self.person)
            if not self.printed_data:
                print(self.person)
                self.printed_data = True
                # Test
                if self.fully_filled_msg:
                    file_data = write_data(self.person)
                    firebasehandler.upload_file(file_data, self.person.receiver)
                    self.person = Person("", "", "", "")
                    self.printed_data = False
                    self.printed_msg = False
                    self.fully_filled_msg = False

        elif filename == "msg.txt":
            print("Reading message")
            self.person.msg = read_msg(self.folder_to_track + filename)
            if not self.printed_msg:
                print(self.person.msg)
                self.printed_msg = True
                self.fully_filled_msg = True


def read_data(filename, person: Person) -> Person:
    try:
        with open(filename, "r") as f:
            data = f.read()
            elements = data.split("*")
            elements[-1] = elements[-1].strip()
            person.sender = elements[0].lower()
            person.receiver = elements[1].lower()
            person.temporal = elements[2].replace("\x00", "")
            return person
    except Exception as e:
        print(e)
        return None

def censure_words(msg: str) -> str:
    index = msg.find("///")
    msg_to_analize = msg[:index]
    word_list = msg_to_analize.split("//")

    try:
        with open("banned_words.txt", "r") as file:
            banned_word = file.read()
            banned_word = banned_word.split(",")
            for word in word_list:
                if word in banned_word:
                    censured_word = "###///"
                    return censured_word
            return msg
    except Exception as e:
        print(e)
        return None

def read_msg(filename) -> Person:
    try:
        with open(filename, "r") as f:
            data = f.read().replace("\x00", "")
            return censure_words(data)
    except Exception as e:
        print(e)
        return None


def check(person: Person) -> bool:
    if person is None:
        return False
    elif (
        person.sender != ""
        and person.receiver != ""
        and person.temporal != ""
        and person.msg != ""
    ):
        return True
    return False


def write_data(person: Person) -> dict:
    time = datetime.now().strftime("%H:%M:%S")
    filename = f"{person.sender}-Chat.json"
    info = {
        "sender": person.sender,
        "receiver": person.receiver,
        "temporal": person.temporal,
        "msg": person.msg,
        "time": time,
    }
    # with open(filename, "w") as f:
    #     json.dump(info, f, indent=4)
    print(f"\nFile {filename} created!")
    print("Waiting for upload...\n")
    return info


def main():
    print("Running...")
    name.lower()
    folder = "./Data/"
    chat = "./Chat/"
    observer = Observer()
    event_handler = MyHandler(folder)
    event_handler_chats = MyHandler(chat)

    try:
        observer.schedule(event_handler, folder, recursive=True)
        observer.schedule(event_handler_chats, chat, recursive=True)
        observer.start()
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
