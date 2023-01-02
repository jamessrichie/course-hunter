import re
from datetime import datetime, timedelta
from imessage_reader.fetch_data import FetchData

from listeners.listener import Listener


TARGET_SENDER = "22733"  # Notify.UW phone number

SLN_REGEX = "SLN: ([0-9]{5})"
TIME_REGEX = "(20[0-9]{2}-[0,1][0-9]-[0-3][0-9]) ([0-2][0-9]:[0-5][0-9]:[0-5][0-9])"


# Returns true iff the message is from Notify.UW and is less than 30 seconds old
def extract(message):
    if TARGET_SENDER in message:
        regex_result = re.search(TIME_REGEX, str(message))

        if regex_result is not None:
            date = [int(i) for i in regex_result.group(1).split("-")]
            time = [int(i) for i in regex_result.group(2).split(":")]

            timestamp = datetime(date[0], date[1], date[2], time[0], time[1], time[2])

            if timestamp >= datetime.now() - timedelta(seconds=30):
                return True

    return False


class iMessageListener(Listener):

    # Initialize object and iMessage reader
    def __init__(self, automator):
        super().__init__("iMessage Listener", automator)

        self.previous_message = None
        self.iMessage = FetchData()

        print("iMessage Listener: Initialized")

    # Scans inbox for unread Notify.UW messages
    def listener_task(self):
        # Extracts all Notify.UW messages that are less than 30 seconds old
        messages = list(filter(extract, self.iMessage.get_messages()))

        if len(messages) > 0:
            # Get index of oldest unread message
            try:
                index = messages.index(self.previous_message) + 1
            except ValueError:
                index = 0

            # Iterate through all unread messages
            while index < len(messages):
                message = messages[index]

                regex_result = re.search(SLN_REGEX, str(message))

                if regex_result is not None:
                    sln_code = regex_result.group(1)

                    print(f"iMessage Listener: Course with SLN: {sln_code} has just opened up")

                    try:
                        self.automator.register(sln_code)
                    except Exception:
                        print(f"iMessage Listener: Could not register for SLN: {sln_code} "
                              "since another listener is currently controlling Safari")

                index += 1

            self.previous_message = messages[-1]

        else:
            self.previous_message = None
