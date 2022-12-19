import re
from threading import Thread
from imessage_reader.fetch_data import FetchData

from datetime import datetime, timedelta


class iMessageListener:

    TARGET_SENDER = "22733"  # Notify.UW phone number

    TIME_REGEX = "(20[0-9]{2}-[0,1][0-9]-[0-3][0-9]) ([0-2][0-9]:[0-5][0-9]:[0-5][0-9])"
    SLN_REGEX = "SLN: ([0-9]{5})"

    # Initialize object and iMessage reader
    def __init__(self, automator):
        self.automator = automator
        self.thread = None
        self.is_running = False

        self.previous_message = None
        self.iMessage = FetchData()

        print("iMessage listener has been initialized")

    # Returns true iff the message is from Notify.UW and is less than 30 seconds old
    def extract(self, message):
        if self.TARGET_SENDER in message:
            regex_result = re.search(self.TIME_REGEX, str(message))

            if regex_result is not None:
                date = [int(i) for i in regex_result.group(1).split("-")]
                time = [int(i) for i in regex_result.group(2).split(":")]

                dt = datetime(date[0], date[1], date[2], time[0], time[1], time[2])

                if dt >= datetime.now() - timedelta(seconds=30):
                    return True

        return False

    # Scans inbox for unread Notify.UW messages
    def listener(self, is_running):
        while is_running():
            # Extracts all Notify.UW messages that are less than 30 seconds old
            messages = list(filter(self.extract, self.iMessage.get_messages()))

            if len(messages) > 0:
                # Get index of oldest unread message
                try:
                    index = messages.index(self.previous_message) + 1
                except ValueError:
                    index = 0

                # Iterate through all unread messages
                while index < len(messages):
                    message = messages[index]

                    regex_result = re.search("SLN: ([0-9]{5})", str(message))

                    if regex_result is not None:
                        sln_code = regex_result.group(1)

                        print(f"Course with SLN: {sln_code} has just opened up")

                        self.automator.register(sln_code)

                    index += 1

                self.previous_message = messages[-1]

            else:
                self.previous_message = None

    # Starts listener in a new thread
    def start(self):
        if self.thread is not None or self.is_running:
            print("Already listening for incoming Notify.UW texts")
            return

        self.is_running = True
        self.thread = Thread(target=self.listener, args=(lambda: self.is_running,))
        self.thread.start()
        print("Now listening for incoming Notify.UW texts")

    # Stops listener
    def stop(self):
        if self.thread is None or not self.is_running:
            print("Already stopped listening for incoming Notify.UW texts")
            return

        self.is_running = False
        self.thread.join()
        self.thread = None
        print("Stopped listening for incoming Notify.UW texts")
