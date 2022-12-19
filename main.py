from automator import Automator
from listeners.email_listener import EmailListener
from listeners.imessage_listener import iMessageListener


if __name__ == "__main__":

    # List of SLN codes that must be added and dropped jointly. See README for more details
    JOINT_SLN_CODES_LIST = []

    # Initialize registration automator
    automator = Automator(JOINT_SLN_CODES_LIST)

    # Initialize email listener
    email_listener = EmailListener(automator)
    email_listener.start()

    # Initialize iMessage listener
    iMessage_listener = iMessageListener(automator)
    iMessage_listener.start()
