import json
from datetime import time

from automator import Automator
from listeners.email_listener import EmailListener
from listeners.imessage_listener import iMessageListener
from listeners.time_listener import TimeListener


TARGET_TIME_05_59_55 = time(hour=5, minute=59, second=55)  # Registration systems open ~5 seconds before 6 AM
TARGET_TIME_06_00_00 = time(hour=6, minute=0, second=0)  # Registration officially opens at 6 AM
TARGET_TIME_CUSTOM = time(hour=0, minute=0, second=0)  # Enter your custom time here


# Prints out the contents of joint-registration.json
def read_joint_registration():
    print("Automator will...")
    for joint_sln_codes in joint_registration_list:
        output = " - Add SLN(s): {}".format(", ".join(joint_sln_codes["add"]))
        if len(joint_sln_codes["drop"]) > 0:
            output += " and drop SLN(s): {}".format(", ".join(joint_sln_codes["drop"]))
        output += " together"

        print(output)


# Checks if any listeners were initialized. Highly specific to this current implementation of
# the program. Will break if the code is changed, though this does not affect functionality
def check_listeners():
    if len(globals()) == 23:
        print("Error: No listeners were initialized")


if __name__ == "__main__":
    try:
        joint_registration_file = open("config/joint-registration.json", "r")
        joint_registration_list = list(filter(lambda elt: len(elt["add"]) > 0, json.load(joint_registration_file)["data"]))

        # Ask user to confirm the contents of joint-registration.json
        if len(joint_registration_list) > 0:
            read_joint_registration()
            input("Press enter to confirm this setting: ")
            print()

        # Initialize registration automator
        automator = Automator(joint_registration_list)

        # Initialize time listener. Registers at a specified time
        # time_listener = TimeListener(automator, joint_registration_list, TARGET_TIME_06_00_00)
        # time_listener.start()

        # Initialize email listener. Registers when a Notify.UW email arrives
        email_listener = EmailListener(automator)
        email_listener.start()

        # Initialize iMessage listener. Registers when a Notify.UW text arrives
        # iMessage_listener = iMessageListener(automator)
        # iMessage_listener.start()

        check_listeners()

    except FileNotFoundError:
        print("Error: Could not find joint-registration.json. Check that the file exists in the config folder")
