import re
import email
import imaplib
import json
from email import policy
from threading import Thread


class EmailListener:

    TARGET_SENDER = "\"Notify.UW\" <notify-noreply@uw.edu>"  # Notify.UW email address

    SLN_REGEX = "SLN: ([0-9]{5})"

    # Initialize object and establish connection to Gmail server
    def __init__(self, automator):
        self.automator = automator
        self.thread = None
        self.is_running = False

        # Establish an IMAP connection to Gmail server
        self.mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)

        # Load JSON file containing credentials and log into Gmail account
        try:
            credentials_file = open("credentials.json", "r")
            credentials = json.load(credentials_file)
            credentials_file.close()

            self.mail.login(credentials["gmail_user"], credentials["gmail_app_password"])
            print("Email Listener: Initialized")

        except imaplib.IMAP4.error:
            print("Email Listener: Incorrect setup. Check your Gmail credentials")
            exit()

        except FileNotFoundError:
            print("Could not find credentials.json. Check that the file exists in the root directory")
            exit()

        except KeyError:
            print("credentials.json is missing one or more important key-values")
            exit()

    # Scans inbox for unread Notify.UW emails
    def listener(self, is_running):
        while is_running():
            # Extracts all unread messages
            self.mail.select('Inbox')
            status, data = self.mail.search(None, '(UNSEEN)')

            for index in data[0].split():
                # Get a single message and parse it by policy.SMTP (RFC compliant)
                status, payload = self.mail.fetch(index, '(RFC822)')
                message = email.message_from_bytes(payload[0][1], policy=policy.SMTP)

                if message['From'] == self.TARGET_SENDER:
                    regex_result = re.search(self.SLN_REGEX, str(message))

                    if regex_result is not None:
                        sln_code = regex_result.group(1)

                        print(f"Email Listener: Course with SLN: {sln_code} has just opened up")

                        try:
                            self.automator.register(sln_code)
                        except Exception as e:
                            print(f"Email Listener: Could not register for SLN: {sln_code} since "
                                  f"iMessage Listener is currently registering for SLN: {e}")

    # Starts listener in a new thread
    def start(self):
        if self.thread is not None or self.is_running:
            print("Email Listener: Already listening for incoming Notify.UW emails")
            return

        self.is_running = True
        self.thread = Thread(target=self.listener, args=(lambda: self.is_running,))
        self.thread.start()
        print("Email Listener: Now listening for incoming Notify.UW emails")

    # Stops listener
    def stop(self):
        if self.thread is None or not self.is_running:
            print("Email Listener: Already stopped listening for incoming Notify.UW emails")
            return

        self.is_running = False
        self.thread.join()
        self.thread = None
        print("Email Listener: Stopped listening for incoming Notify.UW emails")
