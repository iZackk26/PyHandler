class Person:
    def __init__(self, sender, receiver, temporal, msg = ""):
        self.sender = sender
        self.receiver = receiver
        self.temporal = temporal
        self.msg = msg
        self.time = ""
    def __str__(self):
        return (
            "Sender: "
            + self.sender
            + "\nReceiver: "
            + self.receiver
            + "\nTemporal: "
            + self.temporal
            + "\nMsg: "
            + self.msg
        )
