import re
from datetime import datetime, timedelta
from imessage_reader.fetch_data import FetchData

from listeners.listener import Listener


class iMessageListener(Listener):

    TARGET_SENDER = "22733"  # Notify.UW phone number
    TIME_REGEX = "(20[0-9]{2}-[0,1][0-9]-[0-3][0-9]) ([0-2][0-9]:[0-5][0-9]:[0-5][0-9])"

    # Initialize object and iMessage reader
    def __init__(self, automator):
        super().__init__("iMessage Listener", automator)

        self.previous_message = None
        self.iMessage = FetchData()

        print("iMessage Listener: Initialized")

    # Returns true iff the message is from Notify.UW and is less than 30 seconds old
    def extract(self, message):
        if self.TARGET_SENDER in message:
            regex_result = re.search(self.TIME_REGEX, str(message))

            if regex_result is not None:
                date = [int(i) for i in regex_result.group(1).split("-")]
                time = [int(i) for i in regex_result.group(2).split(":")]

                timestamp = datetime(date[0], date[1], date[2], time[0], time[1], time[2])

                if timestamp >= datetime.now() - timedelta(seconds=30):
                    return True

        return False

    # Scans inbox for unread Notify.UW messages
    def listener_task(self):
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

                    print(f"iMessage Listener: Course with SLN: {sln_code} has just opened up")

                    try:
                        self.automator.register(sln_code)
                    except Exception as e:
                        print(f"iMessage Listener: Could not register for SLN: {sln_code} since "
                              f"Email Listener is currently registering for SLN: {e}")

                index += 1

            self.previous_message = messages[-1]

        else:
            self.previous_message = None
