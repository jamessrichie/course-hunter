import re
import email
import imaplib
import json
from email import policy

from listeners.listener import Listener


TARGET_SENDER = "\"Notify.UW\" <notify-noreply@uw.edu>"  # Notify.UW email address

SLN_REGEX = "SLN: ([0-9]{5})"


class EmailListener(Listener):

    # Initialize object and establish connection to Gmail server
    def __init__(self, automator):
        super().__init__("Email Listener", automator)

        # Establish an IMAP connection to Gmail server
        self.mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)

        # Load JSON file containing credentials and log into Gmail account
        try:
            credentials_file = open("config/credentials.json", "r")
            credentials = json.load(credentials_file)
            credentials_file.close()

            self.mail.login(credentials["gmail_user"], credentials["gmail_app_password"])
            print("Email Listener: Initialized")

        except imaplib.IMAP4.error:
            print("Email Listener: Incorrect setup. Check your Gmail credentials")
            exit()

        except FileNotFoundError:
            print("Error: Could not find credentials.json. Check that the file exists in the config folder")
            exit()

        except KeyError:
            print("Error: credentials.json is missing one or more important key-values")
            exit()

    # Scans inbox for unread Notify.UW emails
    def listener_task(self):
        # Extracts all unread messages
        self.mail.select('Inbox')
        status, data = self.mail.search(None, '(UNSEEN)')

        for index in data[0].split():
            # Get a single message and parse it by policy.SMTP (RFC compliant)
            status, payload = self.mail.fetch(index, '(RFC822)')
            message = email.message_from_bytes(payload[0][1], policy=policy.SMTP)

            if message['From'] == TARGET_SENDER:
                regex_result = re.search(SLN_REGEX, str(message))

                if regex_result is not None:
                    sln_code = regex_result.group(1)

                    print(f"Email Listener: Course with SLN: {sln_code} has just opened up")

                    try:
                        self.automator.register(sln_code)
                    except Exception as e:
                        print(f"Email Listener: Could not register for SLN: {sln_code} since "
                              f"iMessage Listener is currently registering for SLN: {e}")
