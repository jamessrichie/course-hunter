import json

from automator import Automator
from listeners.email_listener import EmailListener
from listeners.imessage_listener import iMessageListener


def read_joint_registration():
    print("Automator will...")
    for joint_sln_codes in joint_registration_list:
        output = " - Add SLN(s): {}".format(", ".join(joint_sln_codes["add"]))
        if len(joint_sln_codes["add"]) > 0:
            output += " and drop SLN(s): {}".format(", ".join(joint_sln_codes["drop"]))
        output += " together"

        print(output)


if __name__ == "__main__":

    try:
        joint_registration_file = open("config/joint-registration.json", "r")
        joint_registration_list = list(filter(lambda elt: len(elt["add"]) > 0, json.load(joint_registration_file)["data"]))

        if len(joint_registration_list) > 0:
            read_joint_registration()
            input("Press enter to confirm this setting: ")
            print()

        # Initialize registration automator
        automator = Automator(joint_registration_list)

        # Initialize email listener
        email_listener = EmailListener(automator)
        email_listener.start()

        # Initialize iMessage listener
        iMessage_listener = iMessageListener(automator)
        iMessage_listener.start()

    except FileNotFoundError:
        print("Error: Could not find joint-registration.json. Check that the file exists in the config folder")
